from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
    


class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    reg_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    is_approved = models.BooleanField(default=False) # Store hashed passwords

    def __str__(self):
        return f"{self.name} - {'Approved' if self.is_approved else 'Pending'}"

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    is_approved = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.name} - {'Approved' if self.is_approved else 'Pending'}"
    
class AutomationSettings(models.Model):
    is_enabled = models.BooleanField(default=False)

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='weekly'
    )

    run_time = models.TimeField(default='08:00')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Automation Settings' 