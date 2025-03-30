from django.core.mail import send_mail
from django.conf import settings

try:
    result = send_mail(
        "Test Email",
        "This is a test email from Django using Gmail SMTP.",
        settings.DEFAULT_FROM_EMAIL,
        ["amalmohan487@gmail.com"],  # Replace with your email
        fail_silently=False,  # Make sure it's False to see errors
    )
    print(f"✅ Email Sent Successfully! Return Value: {result}")
except Exception as e:
    print(f"❌ Email Failed: {e}")
    
