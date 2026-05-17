from django.http import HttpResponse
import traceback


def generate_report_and_send_alerts(request):
    try:
        # Step 1: Verify the view is reached
        return HttpResponse("Step 1: email view loaded successfully.")

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )