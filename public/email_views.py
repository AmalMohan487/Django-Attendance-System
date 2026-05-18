from django.http import HttpResponse


def generate_report_and_send_alerts(request):
    try:
        from django.core.mail import send_mail
        from django.conf import settings

        send_mail(
            subject="Brevo Test Email",
            message="Your Attendance Management System email setup is working successfully.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["amalmohan487@gmail.com"],
            fail_silently=False,
        )

        return HttpResponse("Success! Test email sent successfully.")

    except Exception as e:
        return HttpResponse(f"<pre>{e}</pre>")