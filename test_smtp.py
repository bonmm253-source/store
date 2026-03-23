# test_smtp.py
import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    server.starttls()
    server.login('idemudiawisdom27@gmail.com', 'your-gmail-app-password')
    print("SMTP Connected!")
except Exception as e:
    print("Failed to connect:", e)
finally:
    server.quit()