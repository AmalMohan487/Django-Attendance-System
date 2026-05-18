from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings


@login_required
def generate_report_and_send_alerts(request):
    try:
        send_mail(
            subject="Brevo Test Email",
            message="This is a test email from your Django Attendance System.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["amalmohan487@gmail.com"],  # Replace if needed
            fail_silently=False,
        )

        return HttpResponse(
            "Success! Test email sent successfully."
        )

    except Exception as e:
        return HttpResponse(
            f"<h1>Email Error</h1><pre>{str(e)}</pre>"
        )