from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from public.models import Student
from subject.models import Subject
from attendance.utils import calculate_total_hours, student_attendance_hours


@login_required
def generate_report_and_send_alerts(request):
    try:
        LOW_ATTENDANCE_THRESHOLD = 75
        total_alerts_sent = 0

        students = Student.objects.filter(is_approved=True)

        for student in students:
            subjects = Subject.objects.filter(
                semester=student.semester,
                department=student.department
            )

            low_subjects = []

            for subject in subjects:
                total_hours = calculate_total_hours(
                    subject.id,
                    student.semester.id,
                    student.department.id
                )

                attended_hours = student_attendance_hours(
                    student.id,
                    subject.id
                )

                if total_hours == 0:
                    continue

                percentage = (attended_hours / total_hours) * 100

                if percentage < LOW_ATTENDANCE_THRESHOLD:
                    low_subjects.append(
                        f"{subject.name} ({percentage:.2f}%)"
                    )

            if not low_subjects:
                continue

            if not student.email:
                continue

            try:
                validate_email(student.email)
            except ValidationError:
                continue

            send_mail(
                "Attendance Warning",
                "Your attendance is below 75% in:\n\n"
                + "\n".join(low_subjects),
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=True,
            )

            total_alerts_sent += 1

        return HttpResponse(
            f"Success! Emails sent to {total_alerts_sent} students."
        )

    except Exception as e:
        return HttpResponse(f"<pre>{e}</pre>")