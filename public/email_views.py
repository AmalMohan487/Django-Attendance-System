from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings


def generate_report_and_send_alerts(request):
    try:
        send_mail(
            subject="Brevo Test Email",
            message="Brevo is working.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["amalmohan487@gmail.com"],
            fail_silently=False,
        )
        return HttpResponse("Success! Test email sent.")
    except Exception as e:
        return HttpResponse(f"<pre>{e}</pre>")