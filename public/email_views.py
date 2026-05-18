from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import traceback


def generate_report_and_send_alerts(request):
    try:
        send_mail(
            subject="Brevo Test Email",
            message="This is a test email from Django Attendance System.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["amalmohan487@gmail.com"],
            fail_silently=False,
        )

        return HttpResponse("Success! Test email sent successfully.")

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )