from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import traceback


@login_required
def generate_report_and_send_alerts(request):
    try:
        # ======================================================
        # CHECK WHETHER AUTOMATION IS ENABLED
        # ======================================================
        from public.models import AutomationSettings

        settings_obj = AutomationSettings.objects.first()

        if not settings_obj or not settings_obj.is_enabled:
            return HttpResponse("Automation is currently disabled.")

        # ======================================================
        # IMPORT FUNCTIONS
        # ======================================================
        from attendance.utils import (
            check_and_send_attendance_warnings,
            check_and_send_teacher_attendance_warnings,
            get_low_attendance_report_data,
        )

        # ======================================================
        # SEND EMAILS
        # ======================================================
        student_count = check_and_send_attendance_warnings()
        teacher_count = check_and_send_teacher_attendance_warnings()

        # ======================================================
        # GET REPORT DATA
        # ======================================================
        report_data = get_low_attendance_report_data()

        # ======================================================
        # SHOW REPORT PAGE
        # ======================================================
        return render(
            request,
            'public/attendance_report.html',
            {
                'report_data': report_data,
                'student_count': student_count,
                'teacher_count': teacher_count,
            }
        )

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )