from django.http import HttpResponse
import traceback


def generate_report_and_send_alerts(request):
    try:
        # Import inside the function so any import/config errors are caught
        from django.core.mail import send_mail
        from django.conf import settings

        # Send a test email
        send_mail(
            subject="Brevo Test Email",
            message="Brevo is working.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["amalmohan487@gmail.com"],
            fail_silently=False,
        )

        return HttpResponse("Success! Test email sent.")

    except Exception:
        # Show full error instead of generic Internal Server Error
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )