from django.http import HttpResponse
import traceback


def generate_report_and_send_alerts(request):
    try:
        from django.core.mail import send_mail
        from django.conf import settings

        result = send_mail(
            "Brevo Test Email",
            "Brevo is working.",
            settings.DEFAULT_FROM_EMAIL,
            ["amalmohan487@gmail.com"],
            fail_silently=False,
        )

        return HttpResponse(f"SUCCESS: send_mail returned {result}")

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )