from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from public.models import Student
from subject.models import Subject
from attendance.models import Attendance


@login_required
def generate_report_and_send_alerts(request):
    try:
        LOW_ATTENDANCE_THRESHOLD = 75
        total_alerts_sent = 0

        # Get all approved students
        students = Student.objects.filter(is_approved=True)

        for student in students:
            # Get subjects for the student's semester and department
            subjects = Subject.objects.filter(
                semester=student.semester,
                department=student.department
            )

            low_subjects = []

            for subject in subjects:
                # Count total classes conducted for this student and subject
                total_classes = Attendance.objects.filter(
                    student=student
                ).filter(
                    p1=subject
                ).count()

                total_classes += Attendance.objects.filter(
                    student=student
                ).filter(
                    p2=subject
                ).count()

                total_classes += Attendance.objects.filter(
                    student=student
                ).filter(
                    p3=subject
                ).count()

                total_classes += Attendance.objects.filter(
                    student=student
                ).filter(
                    p4=subject
                ).count()

                total_classes += Attendance.objects.filter(
                    student=student
                ).filter(
                    p5=subject
                ).count()

                total_classes += Attendance.objects.filter(
                    student=student
                ).filter(
                    p6=subject
                ).count()

                total_classes += Attendance.objects.filter(
                    student=student
                ).filter(
                    p7=subject
                ).count()

                if total_classes == 0:
                    continue

                # Attended classes are based on saved period entries
                # Since attendance rows are created only for present students,
                # attended_classes = total_classes for this student.
                attended_classes = total_classes

                # Total hours conducted for the subject across all students
                total_hours = (
                    Attendance.objects.filter(p1=subject).count()
                    + Attendance.objects.filter(p2=subject).count()
                    + Attendance.objects.filter(p3=subject).count()
                    + Attendance.objects.filter(p4=subject).count()
                    + Attendance.objects.filter(p5=subject).count()
                    + Attendance.objects.filter(p6=subject).count()
                    + Attendance.objects.filter(p7=subject).count()
                )

                if total_hours == 0:
                    continue

                attendance_percentage = (
                    attended_classes / total_hours
                ) * 100

                if attendance_percentage < LOW_ATTENDANCE_THRESHOLD:
                    low_subjects.append(
                        f"{subject.name} ({attendance_percentage:.2f}%)"
                    )

            # Skip if no low attendance subjects
            if not low_subjects:
                continue

            # Skip invalid emails
            if not student.email:
                continue

            try:
                validate_email(student.email)
            except ValidationError:
                continue

            # Send email
            send_mail(
                "Attendance Warning",
                "Dear " + student.name + ",\n\n"
                "Your attendance is below 75% in:\n\n"
                + "\n".join(low_subjects)
                + "\n\nPlease improve your attendance.\n\n"
                "Regards,\nAdministration",
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )

            total_alerts_sent += 1

        return HttpResponse(
            f"Success! Emails sent to {total_alerts_sent} students."
        )

    except Exception as e:
        return HttpResponse(f"ERROR: {e}")