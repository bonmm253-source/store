import random
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Avg, Sum, F
from django.contrib.admin.views.decorators import staff_member_required
from .models import User, OTP, shoe, watch, Category, Cart, CartItem, Order, Wishlist, Review, Expense
from .forms import RegistrationForm, LoginForm, PhoneLoginForm
from .tasks import send_otp_email, send_registration_email, send_sms_otp

logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def base(request):
    categories = Category.objects.all()
    featured_shoes = shoe.objects.all()[:8]
    featured_watches = watch.objects.all()[:8]
    flash_shoes = shoe.objects.filter(discount_price__isnull=False)[:8]
    top_watches = watch.objects.all()[:8]
    men_shoes = shoe.objects.filter(target_audience='Male')[:8]
    women_shoes = shoe.objects.filter(target_audience='Female')[:8]
    
    context = {
        'categories': categories,
        'featured_shoes': featured_shoes,
        'featured_watches': featured_watches,
        'flash_shoes': flash_shoes,
        'top_watches': top_watches,
        'men_shoes': men_shoes,
        'women_shoes': women_shoes,
    }

    # Add admin metrics if staff
    if request.user.is_authenticated and request.user.is_staff:
        # 1. Inventory Value (Selling)
        shoe_val = shoe.objects.aggregate(total=Sum(F('price') * F('stock')))['total'] or 0
        watch_val = watch.objects.aggregate(total=Sum(F('price') * F('stock')))['total'] or 0
        context['admin_total_goods_value'] = shoe_val + watch_val
        
        # 2. Total Collected (Revenue)
        context['admin_total_revenue'] = Order.objects.filter(complete=True).exclude(status='Cancelled').aggregate(total=Sum('total'))['total'] or 0
        
        # 3. Total Expenses
        total_exp = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        context['admin_total_expenses'] = total_exp
        
        # 4. Net Finance
        context['admin_net_finance'] = context['admin_total_revenue'] - total_exp
        
        # 5. Total Units in Stock
        shoe_units = shoe.objects.aggregate(total=Sum('stock'))['total'] or 0
        watch_units = watch.objects.aggregate(total=Sum('stock'))['total'] or 0
        context['admin_total_units'] = shoe_units + watch_units
        
        # 6. Admin Reg Form
        context['admin_reg_form'] = RegistrationForm()

    return render(request, 'base_home.html', context)

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False  # Deactivate until OTP is verified
            user.save()
            
            # Generate OTP
            code = generate_otp()
            OTP.objects.update_or_create(user=user, defaults={'code': code, 'created_at': timezone.now()})
            
            # Send OTP Email
            send_otp_email.delay(user.email, code)
            
            request.session['unverified_user_id'] = user.id
            messages.success(request, "Registration successful! Please enter the code sent to your email.")
            return redirect("verify_code")
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form": form})

@login_required
def admin_register_home(request):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_staff = True
            user.is_active = True # Active immediately for admin-created accounts
            user.save()
            messages.success(request, f"Admin account '{user.username}' created successfully!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return redirect("home")

def verify_code(request):
    user_id = request.session.get('unverified_user_id')
    if not user_id:
        return redirect("register")
    
    if request.method == "POST":
        code = request.POST.get("code")
        try:
            user = User.objects.get(id=user_id)
            otp = OTP.objects.get(user=user, code=code)
            
            # Check expiration (e.g., 5 minutes)
            if (timezone.now() - otp.created_at).total_seconds() > 300:
                messages.error(request, "Code expired. Please register again.")
                return redirect("register")
            
            user.is_active = True
            user.save()
            otp.delete()
            
            login(request, user)
            send_registration_email.delay(user.email, user.username)
            del request.session['unverified_user_id']
            messages.success(request, "Email verified successfully!")
            return redirect("home")
        except (User.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, "Invalid code.")
            
    return render(request, "verify.html")

def login_view(request):
    try:
        if request.method == "POST":
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect("home")
            else:
                logger.warning(f"Login failed for form: {form.errors}")
        else:
            form = LoginForm()
        return render(request, "login.html", {"form": form})
    except Exception as e:
        logger.error(f"Error in login_view: {e}", exc_info=True)
        # In a real app, you might show a generic error page.
        # Here we re-raise to see it if possible, or it will continue to 500.
        raise e

def login_with_phone(request):
    if request.method == "POST":
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            try:
                user = User.objects.get(phone=phone)
                code = generate_otp()
                OTP.objects.update_or_create(user=user, defaults={'code': code, 'created_at': timezone.now()})
                # In a real app, send SMS here. For now, we'll use email as fallback and console/flash for dev.
                print(f"DEBUG: Phone OTP for {phone} is {code}")
                
                # Send fallback email if user has one
                if user.email:
                    send_otp_email.delay(user.email, code)
                    messages.success(request, f"A login code has been sent to your registered email.")
                
                # Send SMS OTP if user has a phone
                if user.phone:
                    from .tasks import send_sms_otp
                    send_sms_otp.delay(user.phone, code)
                    messages.success(request, f"A login code has been sent to your phone number: {user.phone}")
                
                # Show flash message for development ease (User can see it on the verification page)
                messages.info(request, f"Development Tip: Your OTP code is {code}")
                
                request.session['phone_login_user_id'] = user.id
                return redirect("verify_phone_login")
            except User.DoesNotExist:
                messages.error(request, "No account found with this phone number.")
    else:
        form = PhoneLoginForm()
    return render(request, "login_phone.html", {"form": form})

def verify_phone_login(request):
    user_id = request.session.get('phone_login_user_id')
    if not user_id:
        return redirect("login_with_phone")
    
    if request.method == "POST":
        code = request.POST.get("code")
        try:
            user = User.objects.get(id=user_id)
            otp = OTP.objects.get(user=user, code=code)
            user.is_active = True
            user.save()
            otp.delete()
            login(request, user)
            del request.session['phone_login_user_id']
            return redirect("home")
        except User.DoesNotExist:
            messages.error(request, "User session expired. Please log in again.")
            return redirect("login_with_phone")
        except OTP.DoesNotExist:
            messages.error(request, "Invalid or expired code. Please try again.")
    return render(request, "verify_phone.html")

def logout_view(request):
    logout(request)
    return redirect("home")

def men(request):
    category_filter = request.GET.get('category', '')
    query = request.GET.get('q', '')
    shoes = shoe.objects.filter(target_audience='Male')
    if category_filter:
        shoes = shoes.filter(category__name__icontains=category_filter)
    if query:
        shoes = shoes.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    return render(request, 'men.html', {'shoes': shoes})

def women(request):
    category_filter = request.GET.get('category', '')
    query = request.GET.get('q', '')
    shoes = shoe.objects.filter(target_audience='Female')
    if category_filter:
        shoes = shoes.filter(category__name__icontains=category_filter)
    if query:
        shoes = shoes.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    return render(request, 'women.html', {'shoes': shoes})

def wrist(request):
    watches = watch.objects.all()
    return render(request, 'wristcollection.html', {'watches': watches})

@login_required
def orders_view(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
    else:
        orders = []
    return render(request, 'order.html', {'orders': orders})

def collection(request):
    shoes = shoe.objects.filter(target_audience='Collections')
    return render(request, 'collection.html', {'shoes': shoes})

def product_detail(request, prod_type, pk):
    if prod_type == 'shoe':
        product = get_object_or_404(shoe, pk=pk)
    else:
        product = get_object_or_404(watch, pk=pk)
    
    reviews = product.reviews.all().order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'prod_type': prod_type,
        'reviews': reviews,
        'average_rating': average_rating,
        'stars_range': range(1, 6),
    }
    return render(request, 'product_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    shoes = shoe.objects.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    watches = watch.objects.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    return render(request, 'search_results.html', {'shoes': shoes, 'watches': watches, 'query': query})

@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'orders': orders})

def cart_view(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return render(request, 'cart.html', {'cart': cart})

# Add other necessary views as placeholders for now to avoid 404s/AttributeErrors
def add_to_cart(request): return JsonResponse({'status': 'ok'})
def remove_from_cart(request): return JsonResponse({'status': 'ok'})
def get_cart_data(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'status': 'ok', 'cart': []})
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    
    items = []
    for item in cart.items.all():
        prod = item.shoe_item or item.watch_item
        if prod:
            items.append({
                'id': item.id,
                'name': prod.name,
                'quantity': item.quantity,
                'price': float(prod.discount_price or prod.price),
                'image': prod.image.url if prod.image else ''
            })
    return JsonResponse({'status': 'ok', 'cart': items})
@login_required
def pay(request): return render(request, 'pay.html')
@login_required
def submit_order(request):
    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('delivery_address')
        phone = request.POST.get('phone')
        confirmed_acc = request.POST.get('confirmed_account_number')
        payment_method = request.POST.get('payment_method', 'Bank Transfer')
        cart_json = request.POST.get('cart_json')
        
        if not cart_json or cart_json == 'null':
            messages.error(request, "Your cart data is missing. Please try again.")
            return redirect('cart')

        # Calculate total from cart_json
        try:
            cart_data = json.loads(cart_json)
            if not cart_data:
                messages.error(request, "Your cart is empty.")
                return redirect('cart')
                
            total_ngn = 0
            for item in cart_data:
                # Check for different property names in localStorage items
                price = float(item.get('watchPrice') or item.get('shoePrice') or item.get('price') or 0)
                qty = int(item.get('quantity') or 1)
                total_ngn += price * qty
            
            # Create Order
            order = Order.objects.create(
                user=request.user,
                items_json=cart_json,
                total=total_ngn,
                delivery_address=address,
                phone=phone,
                status='Processing', # Marked as processing since they clicked "paid"
                payment_method=payment_method,
                confirmed_account_number=confirmed_acc if payment_method == 'Bank Transfer' else None
            )
            
            # Trigger Notification
            from .tasks import send_order_notification
            send_order_notification.delay(order.id, total_ngn, confirmed_acc)
            
            messages.success(request, f"Order #{order.id} submitted successfully! The owner has been notified.")
            return redirect('orders')
            
        except Exception as e:
            messages.error(request, f"Error processing order: {str(e)}")
            return redirect('cart')
            
    return redirect('cart')

def toggle_wishlist(request): return JsonResponse({'status': 'ok'})
@login_required
def add_review(request):
    if request.method == "POST":
        try:
            # Handle both Form data and JSON (AJAX)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            prod_type = data.get('type') # 'shoe' or 'watch'
            prod_id = data.get('id')
            rating = int(data.get('rating', 5))
            comment = data.get('comment', '')
            
            if prod_type == 'shoe':
                item = get_object_or_404(shoe, id=prod_id)
                Review.objects.update_or_create(
                    user=request.user, 
                    shoe_item=item, 
                    defaults={'rating': rating, 'comment': comment}
                )
            elif prod_type == 'watch':
                item = get_object_or_404(watch, id=prod_id)
                Review.objects.update_or_create(
                    user=request.user, 
                    watch_item=item, 
                    defaults={'rating': rating, 'comment': comment}
                )
            else:
                raise Exception("Invalid product type")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'status': 'success'})
            
            messages.success(request, "Review submitted!")
            return redirect('orders')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f"Error: {str(e)}")
            return redirect('orders')
    return redirect('orders')
def help_center(request): return render(request, 'help_center.html')
def track_order(request): return render(request, 'track_order.html')
def order_cancellation(request): return render(request, 'order_cancellation.html')
def returns_refunds(request): return render(request, 'returns_refunds.html')

@login_required
def clear_order_history(request):
    if request.method == "POST":
        Order.objects.filter(user=request.user).delete()
        messages.success(request, "Order history cleared.")
    return redirect('orders')

@login_required
def mark_order_paid(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status == "Processing":
            order.status = "Completed"
            order.save()
            messages.success(request, f"Order #{order_id} marked as paid and completed!")
        else:
            messages.warning(request, "This order cannot be marked as paid.")
    return redirect('orders')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied
    # Calculations
    # 1. Total Inventory Selling Value
    shoe_inventory_value = shoe.objects.aggregate(total=Sum(F('price') * F('stock')))['total'] or 0
    watch_inventory_value = watch.objects.aggregate(total=Sum(F('price') * F('stock')))['total'] or 0
    total_inventory_value = shoe_inventory_value + watch_inventory_value

    # 2. Total Stock Cost (What you spent to get the stock currently sitting in inventory)
    shoe_stock_cost = shoe.objects.aggregate(total=Sum(F('cost_price') * F('stock')))['total'] or 0
    watch_stock_cost = watch.objects.aggregate(total=Sum(F('cost_price') * F('stock')))['total'] or 0
    total_stock_cost_in_inventory = shoe_stock_cost + watch_stock_cost

    # 3. Total Revenue (Goods Sold)
    total_revenue = Order.objects.filter(complete=True).exclude(status='Cancelled').aggregate(total=Sum('total'))['total'] or 0

    # 4. Total Expenses (Registered Expenses)
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0

    # 5. Total Units in Stock
    shoe_units = shoe.objects.aggregate(total=Sum('stock'))['total'] or 0
    watch_units = watch.objects.aggregate(total=Sum('stock'))['total'] or 0
    total_units = shoe_units + watch_units

    # Summary
    net_profit = total_revenue - total_expenses
    
    # Recent items
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    recent_expenses = Expense.objects.all().order_by('-date')[:10]
    
    context = {
        'total_inventory_value': total_inventory_value,
        'total_stock_cost_in_inventory': total_stock_cost_in_inventory,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'total_units': total_units,
        'recent_orders': recent_orders,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'admin_dashboard.html', context)
