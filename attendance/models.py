
from django.db import models
from public.models import Student, Teacher, Semester, Department
from subject.models import Subject

from django.db.models import Q, Count

class Attendance(models.Model):
    date = models.DateField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    # Period-wise attendance (stores the subject ID)
    p1 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="p1_attendance")
    p2 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="p2_attendance")
    p3 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="p3_attendance")
    p4 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="p4_attendance")
    p5 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="p5_attendance")
    p6 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="p6_attendance")
    p7 = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="p7_attendance")

    def __str__(self):
        return f"{self.date} - {self.student.name} - {self.semester.name}"

