

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from django.db.models import Q, Count, Sum


def calculate_total_hours(subject_id, semester_id, department_id):
    """Returns the total hours a subject was taught in a semester and department, 
    ensuring each period is counted only once per day."""
    
    return Attendance.objects.filter(
        semester_id=semester_id, 
        department_id=department_id
    ).values('date').annotate(
        daily_hours=Count('date', filter=Q(p1=subject_id), distinct=True) +
                    Count('date', filter=Q(p2=subject_id), distinct=True) +
                    Count('date', filter=Q(p3=subject_id), distinct=True) +
                    Count('date', filter=Q(p4=subject_id), distinct=True) +
                    Count('date', filter=Q(p5=subject_id), distinct=True) +
                    Count('date', filter=Q(p6=subject_id), distinct=True) +
                    Count('date', filter=Q(p7=subject_id), distinct=True)
    ).aggregate(total=Sum('daily_hours'))['total'] or 0  # Returns 0 if no attendance found

def student_attendance_hours(student_id, subject_id):
    """Returns the total hours a student attended for a specific subject,
    ensuring each period is counted only once per day."""
    
    return Attendance.objects.filter(student_id=student_id).values('date').annotate(
        daily_hours=Count('date', filter=Q(p1=subject_id), distinct=True) +
                    Count('date', filter=Q(p2=subject_id), distinct=True) +
                    Count('date', filter=Q(p3=subject_id), distinct=True) +
                    Count('date', filter=Q(p4=subject_id), distinct=True) +
                    Count('date', filter=Q(p5=subject_id), distinct=True) +
                    Count('date', filter=Q(p6=subject_id), distinct=True) +
                    Count('date', filter=Q(p7=subject_id), distinct=True)
    ).aggregate(total=Sum('daily_hours'))['total'] or 0 

def send_low_attendance_email(student, subjects):
    """Send an email to a student if attendance falls below 75%."""
    subject = "Low Attendance Warning"
    from_email = settings.EMAIL_HOST_USER
    to_email = [student.email]

    # Render the email template
    html_content = render_to_string("email/low_attendance_email.html", {
        "name": student.name,
        "subjects": subjects
    })

    # Send Email
    email = EmailMultiAlternatives(subject, "", from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)

from attendance.models import Attendance, Student, Subject

def check_and_send_attendance_warnings():
    students = Student.objects.all()
    
    for student in students:
        low_attendance_subjects = []

        for subject in Subject.objects.filter(semester=student.semester, department=student.department):
            # ✅ Calculate total classes held using the `calculate_total_hours` function
            total_classes = calculate_total_hours(subject.id, student.semester_id, student.department_id)
            attended_classes = student_attendance_hours(student.id, subject.id)  # ✅ Fixed function call
            # ✅ Count attended classes for the student

            if total_classes > 0:
                attendance_percentage = (attended_classes / total_classes) * 100

                if attendance_percentage < 75:
                    low_attendance_subjects.append({
                        "subject": subject.name,
                        "attendance_percentage": round(attendance_percentage, 2),
                        "total_classes": total_classes,
                        "attended_classes": attended_classes
                    })

        # ✅ Send email if any subject has low attendance
        if low_attendance_subjects:
            send_low_attendance_email(student, low_attendance_subjects)


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Attendance
from public.models import Student,Teacher
from subject.models import AssignSubject,Subject

def send_low_attendance_email_to_teacher(teacher, students_info):
    """Send an email to the teacher if their students have low attendance."""
    subject = "Student Low Attendance Alert"
    from_email = settings.EMAIL_HOST_USER
    to_email = [teacher.email]

    # Render the email template
    html_content = render_to_string("email/low_attendance_teacher.html", {
        "teacher_name": teacher.name,
        "students_info": students_info
    })

    # Send Email
    email = EmailMultiAlternatives(subject, "", from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    try:
        email.send(fail_silently=True)
        print(f"Email sent to {teacher.email}")
    except Exception as e:
        print(f"Failed to send email to {teacher.email}: {e}")

def check_and_send_teacher_attendance_warnings():
    teachers = Teacher.objects.all()

    for teacher in teachers:
        assigned_subjects = AssignSubject.objects.filter(teacher=teacher)
        students_info = []

        for assigned in assigned_subjects:
            subject = assigned.subject
            students = Student.objects.filter(semester=assigned.semester, department=assigned.department)

            for student in students:  # ✅ Fixed student iteration
                total_classes = calculate_total_hours(subject.id, student.semester_id, student.department_id)
                attended_classes = student_attendance_hours(student.id, subject.id)  # ✅ Fixed function call

                if total_classes > 0:
                    attendance_percentage = (attended_classes / total_classes) * 100

                    if attendance_percentage < 75:
                        students_info.append({
                            "student_name": student.name,
                            "reg_no": student.reg_no,
                            "subject": subject.name,
                            "total_classes": total_classes,
                            "attended_classes": attended_classes,
                            "attendance_percentage": round(attendance_percentage, 2)
                        })

        # ✅ Send email if any student has low attendance
        if students_info:
            send_low_attendance_email_to_teacher(teacher, students_info)
