
import requests
from django.conf import settings
from attendance.models import Student, Attendance


PASS_PERCENTAGE = 75


def calculate_attendance_percentage(student):
    """
    Calculates overall attendance percentage for a student.
    Adjust this logic if your attendance model differs.
    """
    total_classes = Attendance.objects.filter(student=student).count()
    present_classes = Attendance.objects.filter(
        student=student,
        status=True
    ).count()

    if total_classes == 0:
        return 100

    return (present_classes / total_classes) * 100



def send_brevo_email(to_email, student_name, percentage):
    api_key = settings.BREVO_API_KEY

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": "Django Attendance System",
            "email": settings.DEFAULT_FROM_EMAIL,
        },
        "to": [
            {"email": to_email}
        ],
        "subject": "Low Attendance Warning",
        "htmlContent": f"""
        <h2>Attendance Warning</h2>
        <p>Dear {student_name},</p>
        <p>Your attendance percentage is <strong>{percentage:.2f}%</strong>.</p>
        <p>This is below the required minimum of 75%.</p>
        <p>Please improve your attendance to avoid academic issues.</p>
        <br>
        <p>Regards,<br>Administration</p>
        """,
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



def check_and_send_attendance_warnings():
    total_alerts_sent = 0

    students = Student.objects.exclude(email__isnull=True).exclude(email="")

    for student in students:
        percentage = calculate_attendance_percentage(student)

        if percentage < PASS_PERCENTAGE:
            send_brevo_email(
                to_email=student.email,
                student_name=student.name,
                percentage=percentage,
            )
            total_alerts_sent += 1

    return total_alerts_sent
