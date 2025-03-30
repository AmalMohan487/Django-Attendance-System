import json
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from .models import Attendance
from public.models import Student, Teacher, Semester, Department
from subject.models import Subject, AssignSubject
from public.decorators import student_required, teacher_required, admin_required
from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from public.models import Student
from attendance.models import Attendance
from subject.models import Subject

from django.db.models import Q, Sum, F
from django.shortcuts import render
from .models import Attendance

from django.db.models import Q, Count

from django.db.models import Q, Count, Sum


def teacher_login_required(view_func):
    """ Custom decorator to check if the teacher is logged in using session. """
    def wrapper(request, *args, **kwargs):
        if 'teacher_id' not in request.session:
            return HttpResponseRedirect(reverse('teacher_login'))  # Redirect to teacher login
        return view_func(request, *args, **kwargs)
    return wrapper

def student_login_required(view_func):
    """ Custom decorator to check if the student is logged in. """
    def wrapper(request, *args, **kwargs):
        if 'student_id' not in request.session:
            return HttpResponseRedirect(reverse('student_login'))  # Redirect to student login
        return view_func(request, *args, **kwargs)
    return wrapper

@teacher_login_required
def select_semester(request):
    """ Allows teachers to select a semester they are assigned to. """
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)

    assigned_semesters = AssignSubject.objects.filter(teacher=teacher).values_list('semester', flat=True).distinct()
    semesters = Semester.objects.filter(id__in=assigned_semesters)

    return render(request, 'staff/select_semester.html', {'semesters': semesters})


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
    ).aggregate(total=Sum('daily_hours'))['total'] or 0 
     # Returns 0 if no attendance found
    
    
@teacher_login_required
def attendance_page(request, semester_id):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    semester = get_object_or_404(Semester, id=semester_id)
    department = teacher.department

    students = Student.objects.filter(semester=semester, department=department)
    
    assigned_subject = AssignSubject.objects.filter(
        teacher=teacher, semester=semester, department=department
    ).first()
    
    subject = assigned_subject.subject if assigned_subject else None  

    # ✅ Use the corrected total hours calculation
    total_hours = calculate_total_hours(subject.id, semester.id, department.id) if subject else 0

    date = request.GET.get('date')
    selected_date = parse_date(date) if date else None
    attendance_records = Attendance.objects.filter(
        semester=semester, department=department, date=selected_date
    ) if selected_date else Attendance.objects.none()

    context = {
        "teacher": teacher,
        "semester": semester,
        "department": department,
        "subject": subject,
        "students": students,
        "attendance_records": attendance_records,
        "periods": range(1, 8),  
        "selected_date": date,
        "total_hours": total_hours,  # ✅ Now it counts each period only once per day
    }

    return render(request, "staff/attendance_page.html", context)



@csrf_exempt
@teacher_login_required
def mark_attendance(request):
    """
    Handles marking attendance for each period, ensuring that once a subject is marked
    for a period on a given date, no other subject can be marked for that period.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        date = data.get("date")
        attendance_data = data.get("attendance_data", [])

        if not date or not attendance_data:
            return JsonResponse({"error": "Missing date or attendance data"}, status=400)

        teacher_id = request.session.get('teacher_id')
        teacher = get_object_or_404(Teacher, id=teacher_id)

        for entry in attendance_data:
            student_id = entry.get("student_id")
            period = entry.get("period")  # Example: 'p1', 'p2', etc.
            subject_id = entry.get("subject_id")

            if not student_id or not period or not subject_id:
                continue  # Skip invalid entries

            student = get_object_or_404(Student, id=student_id)
            semester = student.semester
            department = student.department
            subject = get_object_or_404(Subject, id=subject_id)

            # 🔹 **Check if the period is already marked with a different subject for this semester & department**
            period_filter = {f"{period}__isnull": False}  # Check if period is already marked
            existing_attendance = Attendance.objects.filter(
                date=date, semester=semester, department=department, **period_filter
            ).exclude(**{period: subject})  # Exclude records where period is marked by the same subject

            if existing_attendance.exists():
                return JsonResponse({
                    "error": f"Period {period} is already marked by another subject on {date}."
                }, status=400)

            # ✅ Fetch or create the attendance record
            attendance, created = Attendance.objects.get_or_create(
                date=date, student=student, semester=semester, department=department,
                defaults={
                    "teacher": teacher,
                    "p1": None, "p2": None, "p3": None, "p4": None, "p5": None, "p6": None, "p7": None
                }
            )

            # ✅ Mark the subject for the period
            setattr(attendance, period, subject)
            attendance.save()

        return JsonResponse({"message": "Attendance marked successfully."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    
#student to view atte


@student_required
def student_attendance_detail(request):
    """Displays detailed attendance records for the student's semester."""

    student_id = request.session.get('student_id')
    student = get_object_or_404(Student, id=student_id)

    # Get all students in the same department and semester
    students_in_semester = Student.objects.filter(department=student.department, semester=student.semester)

    # Get all unique attendance dates for this semester
    all_attendance_dates = Attendance.objects.filter(student__in=students_in_semester).values_list('date', flat=True).distinct().order_by('-date')

    # Dictionary to store subjects taught per period for each date
    subjects_per_day = defaultdict(lambda: {f"p{i}": "Suspended" for i in range(1, 8)})  # Default to "Suspended"

    # Identify subjects taught for each period on each date
    for record in Attendance.objects.filter(student__in=students_in_semester):
        date = record.date
        for i in range(1, 8):  # P1 to P7
            period_attr = f"p{i}"
            period_subject = getattr(record, period_attr)
            if period_subject:
                subjects_per_day[date][period_attr] = period_subject.name  # Store subject name

    # Get attendance records for the logged-in student
    student_attendance = {record.date: record for record in Attendance.objects.filter(student=student)}

    # Prepare attendance data for template
    attendance_records = []
    for date in all_attendance_dates:
        if date in student_attendance:
            # If student has an attendance record for this date, use it
            record = student_attendance[date]
            attendance_data = {
                "date": date,
                "periods": []
            }

            for i in range(1, 8):  # P1 to P7
                period_attr = f"p{i}"
                attendance_status = getattr(record, period_attr)  # True (Present) or False (Absent)
                subject_taught = subjects_per_day[date][period_attr]  # Subject name

                attendance_data["periods"].append({
                    "present": bool(attendance_status),
                    "subject": subject_taught
                })
        else:
            # If student has no record for this date, mark all periods as absent
            attendance_data = {
                "date": date,
                "periods": []
            }
            for i in range(1, 8):  # P1 to P7
                attendance_data["periods"].append({
                    "present": False,  # Marked absent
                    "subject": subjects_per_day[date][f"p{i}"]  # Fill subject based on other students
                })

        attendance_records.append(attendance_data)

    return render(request, 'student/attendance_detail.html', {
        'student': student,
        'attendance_records': attendance_records,
    })





from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from .models import Attendance, Student, Subject

def send_low_attendance_emails():
    students = Student.objects.all()

    for student in students:
        low_attendance_subjects = []
        
        # Get all subjects assigned to the student
        subjects = Subject.objects.filter(semester=student.semester)

        for subject in subjects:
            # Get total classes conducted for the subject
            total_classes = Attendance.objects.filter(student=student, subject=subject).count()
            if total_classes == 0:
                continue  # Skip if no attendance records exist

            # Get attended classes
            attended_classes = Attendance.objects.filter(student=student, subject=subject, status="Present").count()

            # Calculate attendance percentage
            attendance_percentage = (attended_classes / total_classes) * 100

            if attendance_percentage < 75:
                low_attendance_subjects.append(subject.name)

        if low_attendance_subjects:
            subject_list = ", ".join(low_attendance_subjects)
            email_subject = "Attendance Warning!"
            email_body = f"""
            Hello {student.name},

            We are informing you that your attendance for the following subjects: {subject_list} has fallen below 75%. 
            If this continues, you will not be allowed to attend the regular exams.

            Please ensure you maintain the required attendance.

            Regards,
            Administration
            """

            send_mail(
                email_subject,
                email_body,
                settings.EMAIL_HOST_USER,
                [student.email],  # Send email to student's registered email
                fail_silently=False,
            )
