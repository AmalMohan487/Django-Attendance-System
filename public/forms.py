from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student, Teacher, Department, Semester

class UserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name","email","username","password1","password2"]
        
        
from django import forms
from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code']


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ["name"]
 
 
from django import forms
from .models import Student, Teacher, Department, Semester

class StudentForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'input-box'})
    )

from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'input-box'})
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Department",  # Custom placeholder for dropdown
        widget=forms.Select(attrs={'class': 'select-box'})
    )

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        empty_label="Semester",  # Custom placeholder for dropdown
        widget=forms.Select(attrs={'class': 'select-box'})
    )

    class Meta:
        model = Student
        fields = ['reg_no', 'name', 'email', 'department', 'semester', 'password', 'confirm_password']
        widgets = {
            'reg_no': forms.TextInput(attrs={'placeholder': 'Registration Number', 'class': 'input-box'}),
            'name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'input-box'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'input-box'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-box'}),
        }

    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

class TeacherForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'input-box'})
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Department",  # Custom placeholder for dropdown
        widget=forms.Select(attrs={'class': 'select-box'})
    )
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'department', 'password', 'confirm_password']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'input-box'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'input-box'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-box'}),
            'confirm_password': forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'input-box'}),
        }

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.fields['department'].empty_label = None

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

from django import forms

class StudentLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class TeacherLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


from django import forms
from .models import AutomationSettings


class AutomationSettingsForm(forms.ModelForm):
    class Meta:
        model = AutomationSettings
        fields = ['is_enabled', 'frequency', 'run_time']
        widgets = {
            'run_time': forms.TimeInput(attrs={'type': 'time'}),
        }