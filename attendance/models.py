from django.db import models
from django.contrib.auth.models import User
import json


class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    face_encoding = models.TextField(blank=True, null=True)  # Store face encoding as JSON
    profile_image = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    def set_face_encoding(self, encoding_array):
        """Convert numpy array to JSON string for storage"""
        if encoding_array is not None:
            self.face_encoding = json.dumps(encoding_array.tolist())

    def get_face_encoding(self):
        """Convert JSON string back to numpy array"""
        if self.face_encoding:
            import numpy as np
            return np.array(json.loads(self.face_encoding))
        return None

    class Meta:
        db_table = 'employees'


class AttendanceRecord(models.Model):
    ATTENDANCE_TYPES = [
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    attendance_type = models.CharField(max_length=10, choices=ATTENDANCE_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=200, blank=True)
    confidence_score = models.FloatField(default=0.0)  # Face recognition confidence
    image_captured = models.ImageField(upload_to='attendance_photos/', blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.attendance_type} - {self.timestamp}"

    class Meta:
        db_table = 'attendance_records'
        ordering = ['-timestamp']


class AttendanceSummary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_present = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"

    class Meta:
        db_table = 'attendance_summary'
        unique_together = ['employee', 'date']
        ordering = ['-date']
