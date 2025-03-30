from django.urls import path
from . import views

urlpatterns = [
    path('subject_list/',views.subject_list, name='subject_list'),
    path('add-subject/',views.add_subject, name='add_subject'),
    path('assign-subject/', views.assign_subject_view, name='assign_subject'),
    path('ajax/load-subjects/', views.load_subjects, name='ajax_load_subjects'),
    path('ajax/load-teachers/', views.load_teachers, name='ajax_load_teachers'),
    path('Assignlist/', views.Asub, name='Asub'),
    path('assign_subject/edit/<int:pk>/', views.edit_assign_subject, name='edit_assign_subject'),
    path('assign_subject/delete/<int:pk>/',views.delete_assign_subject, name='delete_assign_subject'),
        path('delete/<int:sub_id>/', views.delete_Sub, name='delete_Sub'),


    
]