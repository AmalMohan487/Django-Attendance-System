from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from attendance.utils import check_and_send_attendance_warnings
import traceback


@login_required
def generate_report_and_send_alerts(request):
    try:
        # Send low attendance emails to students
        check_and_send_attendance_warnings()

        return HttpResponse(
            "Low attendance emails sent successfully!"
        )

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )