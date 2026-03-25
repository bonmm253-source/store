from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="home"),
    path("register/", views.register, name="register"),
    path("verify/", views.verify_code, name="verify_code"),
    path("login/", views.login_view, name="login"),
    path("login-phone/", views.login_with_phone, name="login_with_phone"),
    path("verify-phone/", views.verify_phone_login, name="verify_phone_login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Listings
    path("men/", views.men, name="men"),
    path("women/", views.women, name="women"),
    path("wrist/", views.wrist, name="wristcollection"),
    path("collection/", views.collection, name="collection"),
    path("search/", views.search, name="search"),
    
    # Product Detail
    path("product/<str:prod_type>/<int:pk>/", views.product_detail, name="product_detail"),
    
    # Cart
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/data/", views.get_cart_data, name="get_cart_data"),
    
    # Checkout & Orders
    path("pay/", views.pay, name="pay"),
    path("submit_order/", views.submit_order, name="submit_order"),
    
    # Dashboard & Account
    path("dashboard/", views.dashboard, name="dashboard"),
    path("wishlist/toggle/", views.toggle_wishlist, name="toggle_wishlist"),
    path("review/add/", views.add_review, name="add_review"),
    
    # Help & Info
    path("help/", views.help_center, name="help_center"),
    path("track-order/", views.track_order, name="track_order"),
    path("order-cancellation/", views.order_cancellation, name="order_cancellation"),
    path("returns-refunds/", views.returns_refunds, name="returns_refunds"),
    path("orders/", views.orders_view, name="orders"),
    path("orders/clear/", views.clear_order_history, name="clear_order_history"),
    path("orders/mark-paid/<int:order_id>/", views.mark_order_paid, name="mark_order_paid"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-register-home/", views.admin_register_home, name="admin_register_home"),
]