from django.contrib import admin
from .models import Employee, AttendanceRecord, AttendanceSummary


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'email', 'department', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'hire_date']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    readonly_fields = ['face_encoding', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Work Information', {
            'fields': ('department', 'position', 'hire_date', 'is_active')
        }),
        ('Face Recognition', {
            'fields': ('profile_image', 'face_encoding'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'attendance_type', 'timestamp', 'confidence_score', 'location']
    list_filter = ['attendance_type', 'date', 'employee__department']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['timestamp', 'date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in_time', 'check_out_time', 'total_hours', 'is_present', 'is_late']
    list_filter = ['date', 'is_present', 'is_late', 'employee__department']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')
