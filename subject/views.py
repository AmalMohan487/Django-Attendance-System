from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import SubjectForm
from .models import Subject
from public.decorators import student_required, teacher_required, admin_required


@admin_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')  # Replace 'subject_list' with your URL name
    else:
        form = SubjectForm()

    return render(request, 'admin/add_subject.html', {'form': form})

def subject_list(request):
    query = request.GET.get('sub_code', '')  # Get search query from URL
    if query:
        items = Subject.objects.filter(code__icontains=query)  # Filter subjects
    else:
        items = Subject.objects.all()  # Show all if no query
    return render(request,'admin/subjectlist.html',{'items': items, 'query': query})
    

    #assign subject
    
from django.shortcuts import render
from django.http import JsonResponse
from .models import Subject

def get_subjects(request):
    department_id = request.GET.get("department_id")
    semester_id = request.GET.get("semester_id")
    
    subjects = Subject.objects.filter(department_id=department_id, semester_id=semester_id).values("id", "name")
    
    return JsonResponse(list(subjects), safe=False)


#assign
# views.py

from django.shortcuts import render
from django.http import JsonResponse
from .models import Subject, Teacher,AssignSubject
from .forms import AssignSubjectForm

@admin_required
def assign_subject_view(request):
    if request.method == 'POST':
        form = AssignSubjectForm(request.POST)
        if form.is_valid():
            form.save()  # Save the assignment
            return redirect('AdminIndex')  # Redirect to same page or success page
    else:
        form = AssignSubjectForm()
    return render(request, 'admin/assign_subject.html', {'form': form})
# AJAX endpoint for subjects

@admin_required
def load_subjects(request):
    department_id = request.GET.get('department_id')
    semester_id = request.GET.get('semester_id')
    subjects = Subject.objects.filter(department_id=department_id, semester_id=semester_id).all()
    return JsonResponse(list(subjects.values('id', 'name')), safe=False)

# AJAX endpoint for 

@admin_required
def load_teachers(request):
    department_id = request.GET.get('department_id')
    teachers = Teacher.objects.filter(department_id=department_id).all()
    return JsonResponse(list(teachers.values('id', 'name')), safe=False)


@admin_required
def Asub(request):
    sub = AssignSubject.objects.all()
    context = {
        "items": sub
    }
    return render(request, 'admin/viewassign.html', context)

#edit
from django.shortcuts import render,get_object_or_404

@admin_required
def edit_assign_subject(request, pk):
    assign_subject = get_object_or_404(AssignSubject, pk=pk)  # Fetch the record
    if request.method == "POST":
        form = AssignSubjectForm(request.POST, instance=assign_subject)  # Bind form with instance
        if form.is_valid():
            form.save()
            return redirect('Asub')  # Redirect to a list view or detail page
    else:
        form = AssignSubjectForm(instance=assign_subject)  # Load form with existing data
    return render(request, 'admin/edit_assign_subject.html', {'form': form})


@admin_required
def delete_assign_subject(request, pk):
    assign_subject = get_object_or_404(AssignSubject, pk=pk)  # Fetch the record
    if request.method == "POST":
        assign_subject.delete()
        return redirect('Asub')  # Redirect to the list page after deletion
    return render(request, 'admin/delete_assign_subject.html', {'assign_subject': assign_subject})

from django.contrib import messages
def delete_Sub(request, sub_id):
    department = get_object_or_404(Subject, id=sub_id)
    
    if request.method == "POST":
        department.delete()
        messages.success(request, "Subject deleted successfully!")
        return redirect("subject_list")

    return render(request, "admin/sub_dele.html", {"department": department})