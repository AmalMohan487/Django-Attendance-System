from django.urls import path
from . import views
from .email_views import generate_report_and_send_alerts


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('AdminIndex', views.AdminIndex, name='AdminIndex'),
    path('SignIn', views.SignIn, name='SignIn'),
    path('adddepartment', views.adddepartment, name='adddepartment'),
    path('addsem', views.addsem, name='addsem'),
    path('user_logout', views.user_logout, name='user_logout'),
    
    path('increment-semester/', views.increment_semester, name='increment_semester'),
    path('view-report-card/', views.view_report_card, name='view_report_card'),
    
        path('select/', views.select_department_semester, name='select_department_semester'),
      path(
        'attendance-report-center/',
        views.attendance_report_center,
        name='attendance_report_center'
    ),
    # ==========================================================
    # Generate PDF and Send Alerts
    # ==========================================================
    path(
    'download-low-attendance-pdf/',
    views.download_low_attendance_pdf,
    name='download_low_attendance_pdf'
),
    path(
    'save-automation-settings/',
    views.save_automation_settings,
    name='save_automation_settings'
),
path(
    'generate-report-and-send-alerts/',
    generate_report_and_send_alerts,
    name='generate_report_and_send_alerts'
),
    path('Dept', views.Dept, name='Dept'),
    path('std', views.std, name='std'),
    path('tech', views.tech, name='tech'),
    path('register_student', views.register_student, name='register_student'),
    path('register_teacher', views.register_teacher, name='register_teacher'),
    path('student-login/',views.student_login, name='student_login'),
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('pending-students/', views.pending_students, name='pending_students'),
    path('pending-teachers/', views.pending_teachers, name='pending_teachers'),
    path('approve-student/<int:id>/', views.approve_student, name='approve_student'),
    path('reject-student/<int:id>/', views.reject_student, name='reject_student'),
    path('approve-teacher/<int:id>/', views.approve_teacher, name='approve_teacher'),
    path('reject-teacher/<int:id>/', views.reject_teacher, name='reject_teacher'),
    path('departments/edit/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('departments/delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    path('download_attendance/<int:department_id>/<int:semester_id>/',views.download_attendance_report, name='download_attendance_report'),
    path('sem-over/', views.over, name='over'),
    path('delete_user/<str:user_type>/<int:user_id>/', views.delete_user, name='delete_user'),
    
    path('view_students/', views.admin_view_students, name='view_students'),
    path('view_teachers/', views.admin_view_teachers, name='admin_view_teachers'),
    
    



    
    
    
    
    
    
    
]

