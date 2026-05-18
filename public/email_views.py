from django.http import HttpResponse
from django.conf import settings
import requests
import traceback


def generate_report_and_send_alerts(request):
    try:
        api_key = settings.BREVO_API_KEY

        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        }

        payload = {
            "sender": {
                "name": "Django Attendance System",
                "email": "amalmohan487@gmail.com",
            },
            "to": [
                {"email": "amalmohan487@gmail.com"}
            ],
            "subject": "Brevo API Test Email",
            "htmlContent": "<h1>Email API is working!</h1>",
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        return HttpResponse(
            f"Status Code: {response.status_code}<br><pre>{response.text}</pre>"
        )

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )