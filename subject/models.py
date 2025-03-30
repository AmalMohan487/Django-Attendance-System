from django.db import models
from public.models import Department,Semester,Teacher



class Subject(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    full= models.CharField(max_length=200,)
    code = models.CharField(max_length=200,)


    def __str__(self):
        return f"{self.name} ({self.full})"

# models.py

from django.db import models

class AssignSubject(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject.name} assigned to {self.teacher.name} in {self.department.name} - {self.semester.name}"
