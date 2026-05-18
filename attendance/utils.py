
import requests
from django.conf import settings
from django.db.models import Q, Count, Sum

from attendance.models import Attendance
from public.models import Student, Teacher
from subject.models import Subject, AssignSubject


PASS_PERCENTAGE = 75


# ==========================================================
# ATTENDANCE CALCULATION FUNCTIONS
# ==========================================================

def calculate_total_hours(subject_id, semester_id, department_id):
    """
    Returns the total number of hours a subject was taught.
    Each period (p1-p7) is counted once per day.
    """
    return (
        Attendance.objects.filter(
            semester_id=semester_id,
            department_id=department_id,
        )
        .values("date")
        .annotate(
            daily_hours=
                Count("date", filter=Q(p1_id=subject_id), distinct=True)
                + Count("date", filter=Q(p2_id=subject_id), distinct=True)
                + Count("date", filter=Q(p3_id=subject_id), distinct=True)
                + Count("date", filter=Q(p4_id=subject_id), distinct=True)
                + Count("date", filter=Q(p5_id=subject_id), distinct=True)
                + Count("date", filter=Q(p6_id=subject_id), distinct=True)
                + Count("date", filter=Q(p7_id=subject_id), distinct=True)
        )
        .aggregate(total=Sum("daily_hours"))["total"]
        or 0
    )



def student_attendance_hours(student_id, subject_id):
    """
    Returns the total number of hours attended by a student
    for a specific subject.
    """
    return (
        Attendance.objects.filter(student_id=student_id)
        .values("date")
        .annotate(
            daily_hours=
                Count("date", filter=Q(p1_id=subject_id), distinct=True)
                + Count("date", filter=Q(p2_id=subject_id), distinct=True)
                + Count("date", filter=Q(p3_id=subject_id), distinct=True)
                + Count("date", filter=Q(p4_id=subject_id), distinct=True)
                + Count("date", filter=Q(p5_id=subject_id), distinct=True)
                + Count("date", filter=Q(p6_id=subject_id), distinct=True)
                + Count("date", filter=Q(p7_id=subject_id), distinct=True)
        )
        .aggregate(total=Sum("daily_hours"))["total"]
        or 0
    )


# ==========================================================
# BREVO EMAIL FUNCTION
# ==========================================================

def send_brevo_email(to_email, subject, html_content):
    """
    Send an email using the Brevo API.
    """
    api_key = settings.BREVO_API_KEY

    if not api_key:
        raise Exception("BREVO_API_KEY is not configured.")

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": "Attendance Management System",
            "email": settings.DEFAULT_FROM_EMAIL,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 201:
        raise Exception(
            f"Brevo API Error {response.status_code}: {response.text}"
        )


# ==========================================================
# STUDENT EMAILS
# ==========================================================

def send_low_attendance_email(student, subjects):
    """
    Send low attendance warning email to a student.
    """
    subject_line = "Low Attendance Warning"

    rows = ""
    for item in subjects:
        rows += f"""
        <tr>
            <td>{item['subject']}</td>
            <td>{item['attendance_percentage']}%</td>
            <td>{item['attended_classes']}</td>
            <td>{item['total_classes']}</td>
        </tr>
        """

    html_content = f"""
    <h2>Low Attendance Warning</h2>
    <p>Dear {student.name},</p>
    <p>Your attendance is below {PASS_PERCENTAGE}% in the following subjects:</p>

    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Subject</th>
            <th>Attendance %</th>
            <th>Attended</th>
            <th>Total Classes</th>
        </tr>
        {rows}
    </table>

    <p>Please improve your attendance.</p>

    <p>Regards,<br>Administration</p>
    """

    send_brevo_email(
        to_email=student.email,
        subject=subject_line,
        html_content=html_content,
    )



def check_and_send_attendance_warnings():
    """
    Check all approved students and send emails if attendance is below 75%.

    Returns:
        int: Number of student emails sent.
    """
    total_alerts_sent = 0

    students = Student.objects.filter(
        is_approved=True,
    ).exclude(email__isnull=True).exclude(email="")

    for student in students:
        low_attendance_subjects = []

        subjects = Subject.objects.filter(
            semester=student.semester,
            department=student.department,
        )

        for subject in subjects:
            total_classes = calculate_total_hours(
                subject.id,
                student.semester_id,
                student.department_id,
            )

            attended_classes = student_attendance_hours(
                student.id,
                subject.id,
            )

            if total_classes > 0:
                attendance_percentage = (
                    attended_classes / total_classes
                ) * 100

                if attendance_percentage < PASS_PERCENTAGE:
                    low_attendance_subjects.append({
                        "subject": subject.name,
                        "attendance_percentage": round(
                            attendance_percentage, 2
                        ),
                        "total_classes": total_classes,
                        "attended_classes": attended_classes,
                    })

        if low_attendance_subjects:
            send_low_attendance_email(
                student,
                low_attendance_subjects,
            )
            total_alerts_sent += 1

    return total_alerts_sent


# ==========================================================
# TEACHER EMAILS
# ==========================================================

def send_low_attendance_email_to_teacher(teacher, students_info):
    """
    Send a summary email to a teacher containing students
    with attendance below 75%.
    """
    subject_line = "Student Low Attendance Alert"

    rows = ""
    for item in students_info:
        rows += f"""
        <tr>
            <td>{item['student_name']}</td>
            <td>{item['reg_no']}</td>
            <td>{item['subject']}</td>
            <td>{item['attendance_percentage']}%</td>
        </tr>
        """

    html_content = f"""
    <h2>Low Attendance Students</h2>
    <p>Dear {teacher.name},</p>
    <p>The following students have attendance below {PASS_PERCENTAGE}%:</p>

    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Student Name</th>
            <th>Register No</th>
            <th>Subject</th>
            <th>Attendance %</th>
        </tr>
        {rows}
    </table>

    <p>Regards,<br>Administration</p>
    """

    send_brevo_email(
        to_email=teacher.email,
        subject=subject_line,
        html_content=html_content,
    )



def check_and_send_teacher_attendance_warnings():
    """
    Check all approved teachers and send a summary email if any
    of their assigned students have attendance below 75%.

    Returns:
        int: Number of teacher emails sent.
    """
    total_teacher_alerts = 0

    teachers = Teacher.objects.filter(
        is_approved=True,
    ).exclude(email__isnull=True).exclude(email="")

    for teacher in teachers:
        assigned_subjects = AssignSubject.objects.filter(
            teacher=teacher,
        )

        students_info = []

        for assigned in assigned_subjects:
            subject = assigned.subject

            students = Student.objects.filter(
                semester=assigned.semester,
                department=assigned.department,
                is_approved=True,
            )

            for student in students:
                total_classes = calculate_total_hours(
                    subject.id,
                    student.semester_id,
                    student.department_id,
                )

                attended_classes = student_attendance_hours(
                    student.id,
                    subject.id,
                )

                if total_classes > 0:
                    attendance_percentage = (
                        attended_classes / total_classes
                    ) * 100

                    if attendance_percentage < PASS_PERCENTAGE:
                        students_info.append({
                            "student_name": student.name,
                            "reg_no": student.reg_no,
                            "subject": subject.name,
                            "attendance_percentage": round(
                                attendance_percentage, 2
                            ),
                        })

        if students_info:
            send_low_attendance_email_to_teacher(
                teacher,
                students_info,
            )
            total_teacher_alerts += 1

    return total_teacher_alerts


from collections import OrderedDict


def get_low_attendance_report_data():
    """
    Returns grouped report data.

    Structure:
    [
        {
            'department': 'Computer Science',
            'students': [
                {
                    'reg_no': 'CS001',
                    'name': 'John Doe',
                    'semester': 'S6',
                    'subjects': [
                        {'subject': 'DBMS', 'percentage': 72.5},
                        {'subject': 'FLAT', 'percentage': 68.0},
                    ]
                }
            ]
        }
    ]
    """

    department_map = OrderedDict()

    students = Student.objects.filter(
        is_approved=True,
    ).select_related('department', 'semester')

    for student in students:
        subjects = Subject.objects.filter(
            semester=student.semester,
            department=student.department,
        )

        low_subjects = []

        for subject in subjects:
            total_classes = calculate_total_hours(
                subject.id,
                student.semester_id,
                student.department_id,
            )

            attended_classes = student_attendance_hours(
                student.id,
                subject.id,
            )

            if total_classes > 0:
                percentage = (attended_classes / total_classes) * 100

                if percentage < PASS_PERCENTAGE:
                    low_subjects.append({
                        'subject': subject.name,
                        'percentage': round(percentage, 2),
                    })

        if not low_subjects:
            continue

        dept_name = student.department.name

        if dept_name not in department_map:
            department_map[dept_name] = []

        department_map[dept_name].append({
            'reg_no': student.reg_no,
            'name': student.name,
            'semester': student.semester.name,
            'subjects': low_subjects,
        })

    report_data = []

    for dept_name, students_list in department_map.items():
        report_data.append({
            'department': dept_name,
            'students': students_list,
        })

    return report_data