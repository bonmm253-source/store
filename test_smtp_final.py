import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

print(f"Connecting to {EMAIL_HOST}:{EMAIL_PORT}...")
try:
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
    server.starttls()
    print(f"Logging in as {EMAIL_HOST_USER}...")
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    print("SMTP Login Successful!")
    server.quit()
except Exception as e:
    print(f"SMTP Test Failed: {e}")
