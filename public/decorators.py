from django.shortcuts import redirect
from functools import wraps

def student_required(view_func):
    """ Restrict access to only logged-in students """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'student_id' not in request.session:
            return redirect('student_login')  # Redirect to student login if not logged in as a student
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_required(view_func):
    """ Restrict access to only logged-in teachers """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'teacher_id' not in request.session:
            return redirect('teacher_login')  # Redirect to teacher login if not logged in as a teacher
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """ Restrict access to only logged-in admin users """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('SignIn')  # Redirect to Django admin login if not an admin
        return view_func(request, *args, **kwargs)
    return wrapper
