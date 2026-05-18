from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import traceback

from attendance.utils import (
    check_and_send_attendance_warnings,
    check_and_send_teacher_attendance_warnings,
)


@login_required
def generate_report_and_send_alerts(request):
    try:
        student_count = check_and_send_attendance_warnings()
        teacher_count = check_and_send_teacher_attendance_warnings()

        return HttpResponse(
            f"Success! Emails sent to "
            f"{student_count} students and "
            f"{teacher_count} teachers."
        )

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )
