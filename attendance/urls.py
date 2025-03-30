from django.urls import path
from . import views

urlpatterns = [
    path('select_semester/', views.select_semester, name='select_semester'),
    
    path('attendance/<int:semester_id>/',views.attendance_page, name='attendance_page'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('attenance/', views.student_attendance_detail, name='student_attendance_detail'),


]