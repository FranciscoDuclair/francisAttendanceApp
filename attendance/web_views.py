from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import time
import json
import base64
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Employee, AttendanceRecord, AttendanceSummary
from .face_recognition_service import face_service


def update_attendance_summary_local(employee, date):
    """Update or create attendance summary for an employee on a given date"""
    from datetime import datetime, time as dt_time
    
    # Get all records for this employee on this date
    records = AttendanceRecord.objects.filter(
        employee=employee,
        date=date
    ).order_by('timestamp')
    
    if not records.exists():
        return
    
    # Find check-in and check-out times
    check_in_record = records.filter(attendance_type='check_in').first()
    check_out_record = records.filter(attendance_type='check_out').last()
    
    check_in_time = check_in_record.timestamp.time() if check_in_record else None
    check_out_time = check_out_record.timestamp.time() if check_out_record else None
    
    # Calculate total hours
    total_hours = 0.0
    if check_in_time and check_out_time:
        # Convert to datetime for calculation
        check_in_dt = datetime.combine(date, check_in_time)
        check_out_dt = datetime.combine(date, check_out_time)
        
        # Handle case where check-out is next day
        if check_out_dt < check_in_dt:
            from datetime import timedelta
            check_out_dt += timedelta(days=1)
        
        duration = check_out_dt - check_in_dt
        total_hours = duration.total_seconds() / 3600
    
    # Determine if late (assuming 9:00 AM is standard start time)
    standard_start = dt_time(9, 0)
    is_late = check_in_time and check_in_time > standard_start
    
    # Update or create summary
    summary, created = AttendanceSummary.objects.update_or_create(
        employee=employee,
        date=date,
        defaults={
            'check_in_time': check_in_time,
            'check_out_time': check_out_time,
            'total_hours': total_hours,
            'is_present': bool(check_in_record),
            'is_late': is_late
        }
    )
    
    return summary


def send_attendance_notification(employee, action, confidence_score):
    """Send real-time attendance notification via WebSocket"""
    channel_layer = get_channel_layer()
    
    notification_data = {
        'employee_name': f'{employee.first_name} {employee.last_name}',
        'employee_id': employee.employee_id,
        'department': employee.department,
        'action': action.replace('_', ' ').title(),
        'timestamp': timezone.now().isoformat(),
        'confidence': confidence_score
    }
    
    # Send to attendance notifications group
    async_to_sync(channel_layer.group_send)(
        'attendance_notifications',
        {
            'type': 'attendance_notification',
            'message': notification_data
        }
    )
    
    # Send to dashboard updates group
    async_to_sync(channel_layer.group_send)(
        'dashboard_updates',
        {
            'type': 'dashboard_update',
            'data': {'type': 'attendance_event', 'event': notification_data}
        }
    )
    
    # Send to specific employee dashboard
    async_to_sync(channel_layer.group_send)(
        f'employee_{employee.employee_id}_dashboard',
        {
            'type': 'employee_update',
            'data': {'type': 'attendance_update', 'event': notification_data}
        }
    )


def home_view(request):
    """Dashboard home page"""
    today = timezone.now().date()
    
    # Get statistics
    total_employees = Employee.objects.count()
    present_today = AttendanceSummary.objects.filter(date=today, is_present=True).count()
    total_hours = AttendanceSummary.objects.filter(date=today).aggregate(
        total=Sum('total_hours')
    )['total'] or 0
    with_face_encoding = Employee.objects.exclude(face_encoding__isnull=True).exclude(face_encoding='').count()
    
    # Recent activity
    recent_records = AttendanceRecord.objects.select_related('employee').order_by('-timestamp')[:5]
    
    context = {
        'total_employees': total_employees,
        'present_today': present_today,
        'total_hours': round(total_hours, 1),
        'with_face_encoding': with_face_encoding,
        'recent_records': recent_records,
    }
    
    return render(request, 'home.html', context)


class EmployeeWebListView(ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'
    ordering = ['employee_id']


class EmployeeWebCreateView(CreateView):
    model = Employee
    template_name = 'employee_form.html'
    fields = ['employee_id', 'email', 'first_name', 'last_name', 'phone', 
              'department', 'position', 'hire_date', 'profile_image', 'is_active']
    success_url = reverse_lazy('employee_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add Employee'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create face encoding if profile image is provided
        if self.object.profile_image:
            try:
                # Convert image to base64
                with open(self.object.profile_image.path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    image_base64 = f"data:image/jpeg;base64,{img_data}"
                    
                    success, message = face_service.register_employee_face(self.object, image_base64)
                    if success:
                        messages.success(self.request, f'Employee created and face encoding registered successfully!')
                    else:
                        messages.warning(self.request, f'Employee created but face encoding failed: {message}')
            except Exception as e:
                messages.warning(self.request, f'Employee created but face encoding failed: {str(e)}')
        else:
            messages.success(self.request, 'Employee created successfully!')
        
        return response


class EmployeeWebUpdateView(UpdateView):
    model = Employee
    template_name = 'employee_form.html'
    fields = ['employee_id', 'email', 'first_name', 'last_name', 'phone', 
              'department', 'position', 'hire_date', 'profile_image', 'is_active']
    success_url = reverse_lazy('employee_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Employee'
        return context
    
    def form_valid(self, form):
        # Check if profile image was changed
        old_image = Employee.objects.get(pk=self.object.pk).profile_image
        response = super().form_valid(form)
        
        # If image was changed, update face encoding
        if self.object.profile_image and self.object.profile_image != old_image:
            try:
                with open(self.object.profile_image.path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    image_base64 = f"data:image/jpeg;base64,{img_data}"
                    
                    success, message = face_service.register_employee_face(self.object, image_base64)
                    if success:
                        messages.success(self.request, f'Employee updated and face encoding registered successfully!')
                    else:
                        messages.warning(self.request, f'Employee updated but face encoding failed: {message}')
            except Exception as e:
                messages.warning(self.request, f'Employee updated but face encoding failed: {str(e)}')
        else:
            messages.success(self.request, 'Employee updated successfully!')
        
        return response


class EmployeeWebDetailView(DetailView):
    model = Employee
    template_name = 'employee_detail.html'
    context_object_name = 'employee'


class EmployeeWebDeleteView(DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Employee deleted successfully!')
        return super().delete(request, *args, **kwargs)


def attendance_check_view(request):
    """Face recognition attendance check page"""
    return render(request, 'attendance_check.html')


@csrf_exempt
def face_recognition_web(request):
    """Handle face recognition for web interface"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_base64 = data.get('image_base64')
            
            if not image_base64:
                return JsonResponse({'success': False, 'message': 'No image provided'})
            
            # Recognize face
            employee, confidence_score, message = face_service.recognize_face(image_base64)
            
            if employee is None:
                return JsonResponse({
                    'success': False, 
                    'message': message,
                    'confidence': confidence_score
                })
            
            # Determine attendance action
            today = timezone.now().date()
            existing_records = AttendanceRecord.objects.filter(
                employee=employee, 
                date=today
            ).order_by('-timestamp')
            
            # Check current status
            latest_checkin = existing_records.filter(attendance_type='check_in').first()
            latest_checkout = existing_records.filter(attendance_type='check_out').first()
            
            if not latest_checkin:
                action = 'check_in'
            elif not latest_checkout or latest_checkout.timestamp < latest_checkin.timestamp:
                action = 'check_out'
            else:
                action = 'check_in'  # New check-in for the day
            
            # Create attendance record
            attendance_record = AttendanceRecord.objects.create(
                employee=employee,
                attendance_type=action,
                confidence_score=confidence_score
            )
            
            # Update summary
            update_attendance_summary_local(employee, today)
            
            # Send real-time notification
            send_attendance_notification(employee, action, confidence_score)
            
            return JsonResponse({
                'success': True,
                'employee_name': f'{employee.first_name} {employee.last_name}',
                'employee_id': employee.employee_id,
                'action': action.replace('_', ' ').title(),
                'timestamp': attendance_record.timestamp.isoformat(),
                'confidence': confidence_score
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def attendance_history_view(request):
    """Attendance history page"""
    records = AttendanceRecord.objects.select_related('employee').order_by('-timestamp')[:50]
    summaries = AttendanceSummary.objects.select_related('employee').order_by('-date')[:30]
    
    context = {
        'records': records,
        'summaries': summaries,
    }
    
    return render(request, 'attendance_history.html', context)


def register_face_view(request, pk):
    """Register face for existing employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if not employee.profile_image:
        messages.error(request, 'Employee must have a profile image to register face encoding.')
        return redirect('employee_list')
    
    try:
        with open(employee.profile_image.path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            image_base64 = f"data:image/jpeg;base64,{img_data}"
            
            success, message = face_service.register_employee_face(employee, image_base64)
            if success:
                messages.success(request, f'Face encoding registered successfully for {employee.first_name} {employee.last_name}!')
            else:
                messages.error(request, f'Face encoding failed: {message}')
    except Exception as e:
        messages.error(request, f'Error registering face: {str(e)}')
    
    return redirect('employee_list')


def admin_dashboard_view(request):
    """Admin dashboard with system overview"""
    if not request.user.is_staff:
        return redirect('home')
        
    today = timezone.now().date()
    
    # System statistics
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()
    with_face_encoding = Employee.objects.exclude(face_encoding__isnull=True).exclude(face_encoding='').count()
    face_encoding_percentage = round((with_face_encoding / total_employees * 100) if total_employees > 0 else 0, 1)
    
    # Today's stats
    present_today = AttendanceSummary.objects.filter(date=today, is_present=True).count()
    total_records_today = AttendanceRecord.objects.filter(date=today).count()
    
    # Average confidence
    from django.db.models import Avg
    avg_confidence = AttendanceRecord.objects.filter(confidence_score__isnull=False).aggregate(
        avg=Avg('confidence_score')
    )['avg'] or 0
    avg_confidence = round(avg_confidence, 1) if avg_confidence else 0
    
    # Recent activity
    recent_records = AttendanceRecord.objects.select_related('employee').order_by('-timestamp')[:10]
    
    # Department stats
    from django.db.models import Count, Q
    departments = Employee.objects.values('department').annotate(
        employee_count=Count('id'),
        present_today=Count('daily_summaries', filter=Q(daily_summaries__date=today, daily_summaries__is_present=True))
    ).exclude(department__isnull=True)
    
    # System status
    from django.core.cache import cache
    maintenance_mode = cache.get('maintenance_mode', False)
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'with_face_encoding': with_face_encoding,
        'face_encoding_percentage': face_encoding_percentage,
        'present_today': present_today,
        'total_records_today': total_records_today,
        'avg_confidence': avg_confidence,
        'recent_records': recent_records,
        'departments': departments,
        'maintenance_mode': maintenance_mode,
    }
    
    return render(request, 'admin_dashboard_new.html', context)


def maintenance_status(request):
    """Check if maintenance mode is active"""
    from django.core.cache import cache
    return JsonResponse({
        'maintenance_mode': cache.get('maintenance_mode', False)
    })


def toggle_maintenance(request):
    """Toggle maintenance mode"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        from django.core.cache import cache
        import json
        
        try:
            data = json.loads(request.body)
            maintenance_mode = data.get('maintenance_mode', False)
            cache.set('maintenance_mode', maintenance_mode, timeout=None)  # No expiration
            return JsonResponse({'success': True, 'maintenance_mode': maintenance_mode})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def clear_cache_view(request):
    """Clear the application cache"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        from django.core.cache import cache
        cache.clear()
        return JsonResponse({'success': True, 'message': 'Cache cleared successfully'})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def export_data(request):
    """Export attendance data"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'GET':
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_export_{timezone.now().date()}.csv"'
        
        # Create a CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Employee ID', 'Name', 'Date', 'Check In', 'Check Out', 'Total Hours', 'Status'])
        
        # Get attendance records
        from .models import AttendanceRecord, Employee
        from django.db.models import F, ExpressionWrapper, fields, Case, When, Value, BooleanField
        
        # Get all active employees
        employees = Employee.objects.filter(is_active=True)
        
        # Write data rows
        for emp in employees:
            records = AttendanceRecord.objects.filter(
                employee=emp
            ).order_by('date', 'timestamp')
            
            # Group by date
            dates = {}
            for record in records:
                date_str = record.date.strftime('%Y-%m-%d')
                if date_str not in dates:
                    dates[date_str] = {'check_in': None, 'check_out': None}
                
                if record.attendance_type == 'check_in':
                    dates[date_str]['check_in'] = record.timestamp.time()
                elif record.attendance_type == 'check_out':
                    dates[date_str]['check_out'] = record.timestamp.time()
            
            # Write each day's record
            for date_str, times in dates.items():
                check_in = times['check_in'].strftime('%H:%M:%S') if times['check_in'] else ''
                check_out = times['check_out'].strftime('%H:%M:%S') if times['check_out'] else ''
                
                # Calculate total hours if both check in and out exist
                total_hours = ''
                if times['check_in'] and times['check_out']:
                    from datetime import datetime, time
                    check_in_dt = datetime.combine(datetime.today(), times['check_in'])
                    check_out_dt = datetime.combine(
                        datetime.today() if times['check_out'] > times['check_in'] else datetime.today().replace(day=datetime.today().day + 1),
                        times['check_out']
                    )
                    delta = check_out_dt - check_in_dt
                    total_hours = round(delta.total_seconds() / 3600, 2)
                
                # Determine status
                status = 'Present' if times['check_in'] else 'Absent'
                if times['check_in'] and not times['check_out']:
                    status = 'Missing Check Out'
                
                writer.writerow([
                    emp.employee_id,
                    f"{emp.first_name} {emp.last_name}",
                    date_str,
                    check_in,
                    check_out,
                    total_hours if total_hours else '',
                    status
                ])
        
        return response
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def employee_dashboard_view(request, employee_id=None):
    """Employee dashboard with personal attendance"""
    # For demo, use first employee or specified employee
    if employee_id:
        employee = get_object_or_404(Employee, employee_id=employee_id)
    else:
        employee = Employee.objects.first()
    
    if not employee:
        return redirect('employee_create')
    
    today = timezone.now().date()
    
    # Personal stats
    today_summary = AttendanceSummary.objects.filter(employee=employee, date=today).first()
    recent_records = AttendanceRecord.objects.filter(employee=employee).order_by('-timestamp')[:10]
    
    # Monthly stats
    from datetime import datetime, timedelta
    month_start = today.replace(day=1)
    days_present_month = AttendanceSummary.objects.filter(
        employee=employee, date__gte=month_start, is_present=True
    ).count()
    
    total_work_days = 22  # Approximate
    attendance_percentage = round((days_present_month / total_work_days * 100) if total_work_days > 0 else 0, 1)
    
    # Week summary (placeholder)
    week_summary = [
        {'day_name': 'Mon', 'is_present': True, 'hours': 8},
        {'day_name': 'Tue', 'is_present': True, 'hours': 7.5},
        {'day_name': 'Wed', 'is_present': False, 'hours': 0},
        {'day_name': 'Thu', 'is_present': True, 'hours': 8.5},
        {'day_name': 'Fri', 'is_present': True, 'hours': 8},
        {'day_name': 'Sat', 'is_present': False, 'hours': 0},
        {'day_name': 'Sun', 'is_present': False, 'hours': 0},
    ]
    
    context = {
        'employee': employee,
        'today_summary': today_summary,
        'recent_records': recent_records,
        'days_present_month': days_present_month,
        'total_work_days': total_work_days,
        'attendance_percentage': attendance_percentage,
        'week_summary': week_summary,
        'hours_today': today_summary.total_hours if today_summary else 0,
        'status_today': 'Present' if today_summary and today_summary.is_present else 'Absent',
        'avg_hours_week': 7.5,
        'streak_days': 5,
        'total_hours_month': 160,
        'avg_daily_hours': 7.3,
        'ontime_percentage': 95,
    }
    
    return render(request, 'employee_dashboard.html', context)


def hr_dashboard_view(request):
    """HR dashboard with analytics and reports"""
    today = timezone.now().date()
    
    # HR metrics
    total_employees = Employee.objects.count()
    present_today = AttendanceSummary.objects.filter(date=today, is_present=True).count()
    absent_today = total_employees - present_today
    
    overall_attendance = round((present_today / total_employees * 100) if total_employees > 0 else 0, 1)
    absent_percentage = round((absent_today / total_employees * 100) if total_employees > 0 else 0, 1)
    
    # Department performance
    from django.db.models import Count, Q
    department_stats = Employee.objects.values('department').annotate(
        total_count=Count('id'),
        present_count=Count('daily_summaries', filter=Q(daily_summaries__date=today, daily_summaries__is_present=True))
    ).exclude(department__isnull=True)
    
    for dept in department_stats:
        dept['attendance_rate'] = round((dept['present_count'] / dept['total_count'] * 100) if dept['total_count'] > 0 else 0, 1)
        dept['performance_class'] = 'success' if dept['attendance_rate'] >= 90 else 'warning' if dept['attendance_rate'] >= 70 else 'danger'
        dept['avg_hours'] = 7.5  # Placeholder
        dept['name'] = dept['department']
    
    # Employee performance
    employees = Employee.objects.all()[:20]  # Limit for demo
    employee_performance = []
    for emp in employees:
        performance = {
            'id': emp.id,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'employee_id': emp.employee_id,
            'department': emp.department,
            'profile_image': emp.profile_image,
            'attendance_rate': 85,  # Placeholder
            'avg_hours': 7.5,
            'late_count': 2,
        }
        performance['attendance_class'] = 'success' if performance['attendance_rate'] >= 90 else 'warning' if performance['attendance_rate'] >= 70 else 'danger'
        employee_performance.append(performance)
    
    context = {
        'overall_attendance': overall_attendance,
        'avg_work_hours': 7.5,
        'absent_today': absent_today,
        'absent_percentage': absent_percentage,
        'late_arrivals': 5,
        'department_stats': department_stats,
        'employee_performance': employee_performance,
        'employees_no_face_encoding': Employee.objects.filter(Q(face_encoding__isnull=True) | Q(face_encoding='')).count(),
        'late_employees_today': 3,
        'absent_employees_today': absent_today,
        'top_performers': employee_performance[:5],
    }
    
    return render(request, 'hr_dashboard.html', context)
