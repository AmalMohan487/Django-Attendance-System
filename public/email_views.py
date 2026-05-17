from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def generate_report_and_send_alerts(request):
    try:
        # Import inside the function
        from attendance.utils import check_and_send_attendance_warnings

        # Run the attendance warning function
        check_and_send_attendance_warnings()

        # Success response
        return HttpResponse("Low attendance emails sent successfully!")

    except Exception as e:
        # Return the exact error message
        return HttpResponse(f"ERROR: {str(e)}")