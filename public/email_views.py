from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import traceback

from public.models import AutomationSettings



from django.utils import timezone


def should_run_automation(settings_obj):
    """
    Return True if the automation should run now.
    """

    # Automation disabled
    if not settings_obj.is_enabled:
        return False

    # Current datetime
    now = timezone.now()
    current_time = now.time()

    # If current time has not reached the scheduled time
    if current_time < settings_obj.run_time:
        return False

    # If never run before, allow execution
    if not settings_obj.last_run_at:
        return True

    last_run = settings_obj.last_run_at

    # DAILY
    if settings_obj.frequency == "daily":
        return last_run.date() < now.date()

    # WEEKLY
    elif settings_obj.frequency == "weekly":
        return (
            last_run.isocalendar()[1] < now.isocalendar()[1]
            or last_run.year < now.year
        )

    # MONTHLY
    elif settings_obj.frequency == "monthly":
        return (
            last_run.year < now.year
            or last_run.month < now.month
        )

    return False


def generate_report_and_send_alerts(request):
    try:
        settings_obj, _ = AutomationSettings.objects.get_or_create(id=1)

        # Automation disabled
        if not settings_obj.is_enabled:
            return HttpResponse('Automation is disabled.')

        # Not scheduled to run yet
        if not should_run_automation(settings_obj):
            return HttpResponse('No automation needed at this time.')

        # Import utilities
        from attendance.utils import (
            check_and_send_attendance_warnings,
            check_and_send_teacher_attendance_warnings,
            get_low_attendance_report_data,
        )

        # Send emails
        student_count = check_and_send_attendance_warnings()
        teacher_count = check_and_send_teacher_attendance_warnings()

        # Update last run time
        settings_obj.last_run_at = timezone.now()
        settings_obj.save()

        # Report data
        report_data = get_low_attendance_report_data()

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
            '<pre>' + traceback.format_exc() + '</pre>'
        )