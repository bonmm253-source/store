from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_registration_email(self, user_email, username):
    try:
        subject = 'Welcome to MyStore'
        message = f'Hello {username}, your account has been provisioned successfully.'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f"Registration email sent to {user_email}"
    except Exception as exc:
        logger.error(f"Failed to send registration email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=300)

@shared_task(bind=True, max_retries=3)
def send_otp_email(self, user_email, otp_code):
    try:
        subject = 'Your Verification Code - MyStore'
        message = f'Your verification code is: {otp_code}. It will expire in {settings.OTP_EXPIRATION_MINUTES} minutes.'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f"OTP sent to {user_email}"
    except Exception as exc:
        logger.error(f"Failed to send OTP to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=300)

@shared_task(bind=True, max_retries=3)
def send_order_notification(self, order_id, total, confirmed_acc):
    from .models import Order
    try:
        order = Order.objects.select_related('user').get(id=order_id)
        customer_email = order.user.email if order.user else None
        
        subject = f'NEW ORDER PLACED - #{order_id}'
        admin_message = (
            f"A new order has been placed and marked as PAID.\n\n"
            f"Order ID: #{order_id}\n"
            f"Total Amount: ₦{total}\n"
            f"Payment Method: {order.payment_method}\n"
            f"Confirmed Account Number: {confirmed_acc}\n\n"
            f"Please check your dashboard to process this order."
        )
        
        customer_message = (
            f"Hello {order.user.username if order.user else 'Customer'},\n\n"
            f"Your order #{order_id} has been received and is now being processed.\n\n"
            f"Order Details:\n"
            f"- Order ID: #{order_id}\n"
            f"- Total Amount: ₦{total}\n"
            f"- Payment Method: {order.payment_method}\n\n"
            f"Thank you for shopping with MyStore!"
        )
        
        # Send to Admin
        send_mail(
            subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        # Send to Customer
        if customer_email:
            send_mail(
                f"Order Received - #{order_id} (MyStore)",
                customer_message,
                settings.DEFAULT_FROM_EMAIL,
                [customer_email],
                fail_silently=False,
            )
            
        return f"Order notifications sent for #{order_id}"
    except Exception as exc:
        logger.error(f"Failed to send order notification for #{order_id}: {exc}")
        raise self.retry(exc=exc, countdown=300)

@shared_task(bind=True, max_retries=3)
def send_sms_otp(self, phone, otp_code):
    try:
        # Since we don't have an SMS gateway, we log it to simulate sending.
        # In a real app, you would use Twilio, Vonage, etc. here.
        message = f"Your MyStore verification code is: {otp_code}. Valid for {settings.OTP_EXPIRATION_MINUTES} minutes."
        logger.info(f"SMS to {phone}: {message}")
        print(f"DEBUG: SMS to {phone}: {message}")
        return f"SMS OTP simulated for {phone}"
    except Exception as exc:
        logger.error(f"Failed to send SMS OTP to {phone}: {exc}")
        raise self.retry(exc=exc, countdown=300)