from django.http import HttpResponse
import traceback


def generate_report_and_send_alerts(request):
    try:
        from django.core.mail import get_connection, EmailMessage
        from django.conf import settings

        connection = get_connection(
            timeout=20,
            fail_silently=False,
        )

        email = EmailMessage(
            subject="Brevo Test Email",
            body="Brevo is working.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["amalmohan487@gmail.com"],
            connection=connection,
        )

        result = email.send()

        return HttpResponse(
            f"Success! Email sent. Result = {result}"
        )

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )