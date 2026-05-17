from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q, F, Sum, Count, Case, When, IntegerField
from django.db import transaction

# Models
from .models import Student, Teacher, Department, Semester
from subject.models import Subject
from attendance.models import Attendance

# Forms
from .forms import StudentLoginForm, TeacherLoginForm, DepartmentForm, SemesterForm

# Decorators
from .decorators import student_required, teacher_required, admin_required

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def homepage(request):
    return render(request, 'index.html')

@admin_required
def AdminIndex(request):
    return render(request,'admin/adminindex.html')

def SignIn(request):
    if request.method == "POST":
        username = request.POST["uname"]
        password = request.POST["pswd"]
        user = authenticate(request,username = username ,password = password)

        if user is not None:
            login(request,user)
            return redirect('AdminIndex')
        else:
            messages.info(request,"Username or Password incorrect")
            return redirect('SignIn')

    return render(request,'login.html')

@admin_required
def adddepartment(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Dept')
    else:
        form = DepartmentForm()
    return render(request, 'admin/addepartment.html', {'form': form})

@admin_required
def addsem(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('addsem')
    else:
        form = SemesterForm()
    return render(request, 'admin/addsdem.html', {'form': form})

def user_logout(request):
    logout(request)  # Logs out the user
    return redirect('homepage')

@admin_required
def Dept(request):
    dept = Department.objects.all()
    context={
        "items":dept

    }

    return render(request,'admin/department.html',context)


#login for teach and student

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
    ).aggregate(total=Sum('daily_hours'))['total'] or 0  # Returns 0 if no attendance found


def student_login_required(view_func):
    """ Custom decorator to check if the student is logged in. """
    def wrapper(request, *args, **kwargs):
        if 'student_id' not in request.session:
            return HttpResponseRedirect(reverse('student_login'))  # Redirect to student login
        return view_func(request, *args, **kwargs)
    return wrapper


@student_required
def std(request):
    """Displays student's attendance per subject."""
    student_id = request.session.get('student_id')
    student = get_object_or_404(Student, id=student_id)

    subjects = Subject.objects.filter(semester=student.semester)

    attendance_data = []
    for subject in subjects:
        total_hours = calculate_total_hours(subject.id, student.semester.id, student.department.id)
        attended_hours = student_attendance_hours(student.id, subject.id)
        attendance_percentage = (attended_hours / total_hours * 100) if total_hours > 0 else 0

        attendance_data.append({
            'subject_name': subject.name,
            'total_hours': total_hours,
            'attended_hours': attended_hours,
            'attendance_percentage': round(attendance_percentage, 2)
        })

    return render(request, 'student/studentindex.html', {
        'student': student,
        'attendance_data': attendance_data,
    })

  
from subject.models import AssignSubject 
from django.http import HttpResponse
  
def tech(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return redirect('teacher_login')  # Redirect to login if not logged in

    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return HttpResponse("Teacher not found.")

    # Get assigned subjects and semesters
    assigned_subjects = AssignSubject.objects.filter(teacher=teacher)
    semesters = Semester.objects.filter(id__in=assigned_subjects.values_list('semester_id', flat=True))

    context = {
        'teacher': teacher,
        'semesters': semesters,
        'assigned_subjects': assigned_subjects
    }
    return render(request, 'staff/teacherindex.html', context)

     
from django.shortcuts import render, redirect
from .forms import StudentForm, TeacherForm



def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')  
    else:
        form = StudentForm()
    return render(request, 'student/register.html', {'form': form})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = TeacherForm()
    return render(request, 'staff/register.html', {'form': form})


#login

def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                student = Student.objects.get(email=email, password=password)
                if student.is_approved:
                    # Set session or login logic
                    request.session['student_id'] = student.id  # Example of session usage
                    messages.success(request, "Login successful!")
                    return redirect('std')  # Change to your student dashboard URL
                else:
                    messages.error(request, "Your account is not approved yet.")
            except Student.DoesNotExist:
                messages.error(request, "Invalid email or password.")
    else:
        form = StudentLoginForm()
    return render(request, 'student/login.html', {'form': form})


def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                teacher = Teacher.objects.get(email=email, password=password)
                if teacher.is_approved:
                    # Set session or login logic
                    request.session['teacher_id'] = teacher.id  # Example of session usage
                    messages.success(request, "Login successful!")
                    return redirect('tech')  # Change to your teacher dashboard URL
                else:
                    messages.error(request, "Your account is not approved yet.")
            except Teacher.DoesNotExist:
                messages.error(request, "Invalid email or password.")
    else:
        form = TeacherLoginForm()
    return render(request, 'staff/login.html', {'form': form})


#approve

# Pending Students List

@admin_required
def pending_students(request):
    students = Student.objects.filter(is_approved=False)
    return render(request, 'admin/pending_students.html', {'students': students})

# Pending Teachers List

@admin_required
def pending_teachers(request):
    teachers = Teacher.objects.filter(is_approved=False)
    return render(request, 'admin/pending_teachers.html', {'teachers': teachers})

# Approve Student

@admin_required
def approve_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.is_approved = True
    student.save()
    messages.success(request, f"{student.name} approved successfully.")
    return redirect('pending_students')

# Reject Student (optional, can also delete)

@admin_required
def reject_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()  # Or you can add a rejected flag instead of deleting
    messages.warning(request, f"{student.name} rejected and removed.")
    return redirect('pending_students')

# Approve Teacher

@admin_required
def approve_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    teacher.is_approved = True
    teacher.save()
    messages.success(request, f"{teacher.name} approved successfully.")
    return redirect('pending_teachers')

# Reject Teacher (optional, can also delete)

@admin_required
def reject_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    teacher.delete()  # Or you can add a rejected flag instead of deleting
    messages.warning(request, f"{teacher.name} rejected and removed.")
    return redirect('pending_teachers')



def admin_view_students(request):
    query = request.GET.get('reg_no', '').strip()
    students = Student.objects.filter(reg_no__icontains=query) if query else Student.objects.all()

    return render(request, 'admin/admin_view_students.html', {'students': students, 'query': query})

def admin_view_teachers(request):
    teachers = Teacher.objects.all()
    return render(request, 'admin/admin_view_teachers.html', {'teachers': teachers})



def delete_user(request, user_type, user_id):
    if user_type == 'student':
        user = get_object_or_404(Student, id=user_id)
    elif user_type == 'teacher':
        user = get_object_or_404(Teacher, id=user_id)
    else:
        messages.error(request, "Invalid user type.")
        return redirect('admin_view_students')

    user.delete()
    messages.success(request, f"{user_type.capitalize()} deleted successfully.")
    return redirect(f'admin_view_{user_type}s')



def edit_department(request, dept_id):
    department = get_object_or_404(Department, id=dept_id)
    
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")

        # Update department details
        department.name = name
        department.code = code
        department.save()

        messages.success(request, "Department updated successfully!")
        return redirect("Dept")

    return render(request, "admin/edit_department.html", {"department": department})


def delete_department(request, dept_id):
    department = get_object_or_404(Department, id=dept_id)
    
    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted successfully!")
        return redirect("Dept")

    return render(request, "admin/delete_department.html", {"department": department})



#increment_semester_function_student


def increment_semester(request):
    if request.user.is_superuser:  # Ensure only admin can perform this action
        with transaction.atomic():  # Ensure atomicity
            # Get all semesters ordered by ID
            semesters = Semester.objects.order_by("id")
            last_semester = semesters.last()  # Get the final semester
            
            # Delete attendance records
            Attendance.objects.all().delete()
            
            # Delete students in the last semester
            Student.objects.filter(semester=last_semester).delete()
            
            # Update semester for remaining students
            for student in Student.objects.exclude(semester=last_semester):
                next_semester = semesters.filter(id=student.semester.id + 1).first()
                if next_semester:
                    student.semester = next_semester
                    student.save()

            messages.success(request, "Semester updated successfully! Attendance records cleared.")
    else:
        messages.error(request, "Unauthorized action.")

    return redirect('AdminIndex')  # Redirect to admin panel



#report card
from django.shortcuts import render

def select_department_semester(request):
    departments = Department.objects.all()
    semesters = Semester.objects.all()
    
    return render(request, 'admin/select_department_semester.html', {'departments': departments, 'semesters': semesters})


def view_report_card(request):
    if request.method == 'POST':
        department_id = request.POST.get('department')
        semester_id = request.POST.get('semester')

        # Fetch students based on selection
        students = Student.objects.filter(department_id=department_id, semester_id=semester_id)

        report_data = []
        for student in students:
            subjects = Subject.objects.filter(semester_id=semester_id)
            student_report = {
                "name": student.name,
                "reg_no": student.reg_no,
                "subjects": []
            }
            
            for subject in subjects:
                # Fetch attendance records for this subject across all periods
                total_hours = calculate_total_hours(subject.id, student.semester.id, student.department.id)
                attended_hours = student_attendance_hours(student.id, subject.id)
                attendance_percentage = (attended_hours / total_hours * 100) if total_hours > 0 else 0

    
                eligibility = "Eligible" if attendance_percentage >= 75 else "Not Eligible"

                student_report["subjects"].append({
                    "subject_name": subject.full,
                    "attendance_percentage": round(attendance_percentage, 2),
                    "eligibility": eligibility
                })
            
            report_data.append(student_report)

        return render(request, 'admin/report_card.html', {
            'report_data': report_data,
            'selected_semester': semester_id,
            "selected_department": department_id,
        })

    return render(request, 'admin/report_card.html', {'report_data': None})

def over(request):
    return render(request, 'admin/confirm.html')

#pdf download 



def download_attendance_report(request, department_id, semester_id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    # Create PDF in landscape mode for maximum width
    pdf = SimpleDocTemplate(response, pagesize=landscape(letter), rightMargin=2, leftMargin=2, topMargin=2, bottomMargin=2)

    elements = []
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["BodyText"]

    # Fetch Department Name
    department = Department.objects.get(id=department_id)
    semester = Semester.objects.get(id=semester_id)


    # Title
    title = Paragraph(f"<b>Department: {department.name}</b>", title_style)
    elements.append(title)
    title = Paragraph(f"<b>Semester: {semester.name}</b>", title_style)
    elements.append(title)

    # Fetch Students and Subjects
    students = Student.objects.filter(department_id=department_id, semester_id=semester_id)
    subjects = Subject.objects.filter(semester_id=semester_id)

    # ** Multi-Row Headers **
    header_1 = ["Student Name", "Reg No"]
    for subject in subjects:
        header_1.append(Paragraph(f"<b>{subject.name}</b>", normal_style))  # Wrapped text
        header_1.extend(["", ""])  # Extra columns for "Total", "Attended", "%"

    header_2 = ["", ""]  # Empty for "Student Name" & "Reg No"
    for _ in subjects:
        header_2.extend(["TH", "AH", "%"])

    # Data starts with headers
    data = [header_1, header_2]

    # Add Student Data
    for student in students:
        row = [student.name, student.reg_no]
        for subject in subjects:
            total_hours = calculate_total_hours(subject.id, student.semester.id, student.department.id)
            attended_hours = student_attendance_hours(student.id, subject.id)
            attendance_percentage = (attended_hours / total_hours * 100) if total_hours > 0 else 0

            row.extend([str(total_hours), str(attended_hours), f"{attendance_percentage:.2f}%"])

        data.append(row)

    # ** Adjust Column Widths for 8 Subjects **
    col_widths = [90, 70] + ([22, 22, 25] * len(subjects))  # Even smaller width to fit 8 subjects

    # Create Table
    table = Table(data, colWidths=col_widths)

    # ** Apply Styling **
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.blue),  # Header 1
        ("BACKGROUND", (0, 1), (-1, 1), colors.lightgrey),  # Header 2
        ("TEXTCOLOR", (0, 0), (-1, 1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 6),  # Smaller font to fit more data
    ])

    # ** Merge Subject Names Across 3 Columns **
    col_start = 2  # First subject starts at column 2
    for _ in subjects:
        style.add("SPAN", (col_start, 0), (col_start + 2, 0))  # Merge subject name across 3 columns
        col_start += 3  # Move to next subject's columns

    table.setStyle(style)
    elements.append(table)

    # Generate PDF
    pdf.build(elements)

    return response




# attendance/views.py

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required



# ==========================================================
# 1. Attendance Report Center Page
# ==========================================================
@login_required
def attendance_report_center(request):
    """
    Shows two options:
    1. View Attendance Report
    2. Generate PDF & Send Alerts
    """
    return render(request, 'admin/attendance.html')


# ==========================================================
# 2. Generate PDF and Send Alerts
# ==========================================================
# Add these imports at the top of views.py
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import traceback


@login_required
def generate_report_and_send_alerts(request):
    try:
        from attendance.utils import check_and_send_attendance_warnings

        check_and_send_attendance_warnings()

        return HttpResponse(
            "Low attendance emails sent successfully!"
        )

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>"
        )