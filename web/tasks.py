from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
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
    try:
        subject = f'NEW ORDER PLACED - #{order_id}'
        message = (
            f"A new order has been placed and marked as PAID.\n\n"
            f"Order ID: #{order_id}\n"
            f"Total Amount: ₦{total}\n"
            f"Confirmed Account Number: {confirmed_acc}\n\n"
            f"Please check your dashboard to process this order."
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        return f"Order notification sent for #{order_id}"
    except Exception as exc:
        logger.error(f"Failed to send order notification for #{order_id}: {exc}")
        raise self.retry(exc=exc, countdown=300)