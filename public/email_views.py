from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import traceback


@login_required
def generate_report_and_send_alerts(request):
    try:
        from attendance.utils import (
            check_and_send_attendance_warnings,
            check_and_send_teacher_attendance_warnings,
            get_low_attendance_report_data,
        )

        student_count = check_and_send_attendance_warnings()
        teacher_count = check_and_send_teacher_attendance_warnings()

        report_data = get_low_attendance_report_data()

        return render(request, 'admin/attendance_report.html', {
            'report_data': report_data,
            'student_count': student_count,
            'teacher_count': teacher_count,
        })

    except Exception:
        return HttpResponse(
            '<pre>' + traceback.format_exc() + '</pre>'
        )
