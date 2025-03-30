from django import forms
from .models import Subject, Department, Semester

from django import forms
from .models import Subject, Department, Semester

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'department', 'semester','full','code' ]

    # Customizing Department and Semester dropdowns
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label=None,  # Set to None to prevent default "---------"
        widget=forms.Select(attrs={"class": "form-control"})
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        empty_label=None,  # Set to None to prevent default "---------"
        widget=forms.Select(attrs={"class": "form-control"})
    )

    # Customizing Name input field
    widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter shot Name'}),
        'full': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'full Subject Name'}),
        'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subject code'}),
        
    }

def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Remove blank choice manually
    self.fields['department'].choices = [
        choice for choice in self.fields['department'].choices if choice[0] is not None
    ]
    self.fields['semester'].choices = [
        choice for choice in self.fields['semester'].choices if choice[0] is not None
    ]

from django import forms
from .models import Department, Semester, Subject, Teacher


# forms.py

from django import forms
from .models import AssignSubject, Department, Semester, Subject, Teacher

class AssignSubjectForm(forms.ModelForm):
    class Meta:
        model = AssignSubject
        fields = ['department', 'semester', 'subject', 'teacher']

    def __init__(self, *args, **kwargs):
        super(AssignSubjectForm, self).__init__(*args, **kwargs)

        # Set default empty queryset for dependent fields
        self.fields['subject'].queryset = Subject.objects.none()
        self.fields['teacher'].queryset = Teacher.objects.none()

        # Set custom empty labels to remove "--------"
        self.fields['department'].empty_label = "Department"
        self.fields['semester'].empty_label = "Semester"
        self.fields['subject'].empty_label = "Subject"
        self.fields['teacher'].empty_label = "Teacher"

        # When editing an existing instance, pre-populate the fields
        if self.instance.pk:
            self.fields['subject'].queryset = Subject.objects.filter(
                department=self.instance.department,
                semester=self.instance.semester
            )
            self.fields['teacher'].queryset = Teacher.objects.filter(
                department=self.instance.department
            )
        else:
            # Load subjects if department & semester are selected in the request
            if 'department' in self.data and 'semester' in self.data:
                try:
                    department_id = int(self.data.get('department'))
                    semester_id = int(self.data.get('semester'))
                    self.fields['subject'].queryset = Subject.objects.filter(
                        department_id=department_id, semester_id=semester_id
                    )
                except (ValueError, TypeError):
                    pass  # Ignore invalid data, keep queryset empty

            # Load teachers if department is selected in the request
            if 'department' in self.data:
                try:
                    department_id = int(self.data.get('department'))
                    self.fields['teacher'].queryset = Teacher.objects.filter(
                        department_id=department_id
                    )
                except (ValueError, TypeError):
                    pass  # Ignore invalid data, keep queryset empty
