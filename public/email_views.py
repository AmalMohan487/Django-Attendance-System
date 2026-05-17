from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from public.models import Student, Teacher
from subject.models import Subject, AssignSubject
from attendance.models import Attendance


@login_required
def generate_report_and_send_alerts(request):
    try:
        LOW_ATTENDANCE_THRESHOLD = 75
        student_alerts_sent = 0
        teacher_alerts_sent = 0

        # =====================================================
        # 1. SEND EMAILS TO STUDENTS
        # =====================================================
        students = Student.objects.filter(is_approved=True)

        for student in students:
            subjects = Subject.objects.filter(
                semester=student.semester,
                department=student.department
            )

            low_subjects = []

            for subject in subjects:
                # Classes attended by this student
                attended_classes = (
                    Attendance.objects.filter(student=student, p1=subject).count() +
                    Attendance.objects.filter(student=student, p2=subject).count() +
                    Attendance.objects.filter(student=student, p3=subject).count() +
                    Attendance.objects.filter(student=student, p4=subject).count() +
                    Attendance.objects.filter(student=student, p5=subject).count() +
                    Attendance.objects.filter(student=student, p6=subject).count() +
                    Attendance.objects.filter(student=student, p7=subject).count()
                )

                # Total classes conducted for this subject
                total_classes = (
                    Attendance.objects.filter(p1=subject).count() +
                    Attendance.objects.filter(p2=subject).count() +
                    Attendance.objects.filter(p3=subject).count() +
                    Attendance.objects.filter(p4=subject).count() +
                    Attendance.objects.filter(p5=subject).count() +
                    Attendance.objects.filter(p6=subject).count() +
                    Attendance.objects.filter(p7=subject).count()
                )

                if total_classes == 0:
                    continue

                percentage = (attended_classes / total_classes) * 100

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
                f"Dear {student.name},\n\n"
                "Your attendance is below 75% in:\n\n"
                + "\n".join(low_subjects)
                + "\n\nPlease improve your attendance.\n\n"
                "Regards,\nAdministration",
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=True,
            )

            student_alerts_sent += 1

        # =====================================================
        # 2. SEND EMAILS TO TEACHERS
        # =====================================================
        teachers = Teacher.objects.filter(is_approved=True)

        for teacher in teachers:
            if not teacher.email:
                continue

            try:
                validate_email(teacher.email)
            except ValidationError:
                continue

            assignments = AssignSubject.objects.filter(teacher=teacher)

            teacher_report = []

            for assignment in assignments:
                subject = assignment.subject

                students_in_class = Student.objects.filter(
                    semester=assignment.semester,
                    department=assignment.department,
                    is_approved=True
                )

                for student in students_in_class:
                    attended_classes = (
                        Attendance.objects.filter(student=student, p1=subject).count() +
                        Attendance.objects.filter(student=student, p2=subject).count() +
                        Attendance.objects.filter(student=student, p3=subject).count() +
                        Attendance.objects.filter(student=student, p4=subject).count() +
                        Attendance.objects.filter(student=student, p5=subject).count() +
                        Attendance.objects.filter(student=student, p6=subject).count() +
                        Attendance.objects.filter(student=student, p7=subject).count()
                    )

                    total_classes = (
                        Attendance.objects.filter(p1=subject).count() +
                        Attendance.objects.filter(p2=subject).count() +
                        Attendance.objects.filter(p3=subject).count() +
                        Attendance.objects.filter(p4=subject).count() +
                        Attendance.objects.filter(p5=subject).count() +
                        Attendance.objects.filter(p6=subject).count() +
                        Attendance.objects.filter(p7=subject).count()
                    )

                    if total_classes == 0:
                        continue

                    percentage = (attended_classes / total_classes) * 100

                    if percentage < LOW_ATTENDANCE_THRESHOLD:
                        teacher_report.append(
                            f"{student.name} ({student.reg_no}) - "
                            f"{subject.name}: {percentage:.2f}%"
                        )

            if not teacher_report:
                continue

            send_mail(
                "Students with Low Attendance",
                f"Dear {teacher.name},\n\n"
                "The following students have attendance below 75%:\n\n"
                + "\n".join(teacher_report)
                + "\n\nRegards,\nAdministration",
                settings.EMAIL_HOST_USER,
                [teacher.email],
                fail_silently=True,
            )

            teacher_alerts_sent += 1

        return HttpResponse(
            f"Success! Emails sent to "
            f"{student_alerts_sent} students and "
            f"{teacher_alerts_sent} teachers."
        )

    except Exception as e:
        return HttpResponse(f"ERROR: {e}")