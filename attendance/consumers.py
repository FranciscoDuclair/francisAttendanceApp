import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Employee, AttendanceRecord, AttendanceSummary


class AttendanceNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join attendance notifications group
        self.group_name = 'attendance_notifications'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave attendance notifications group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming WebSocket messages if needed
        pass

    # Receive message from group
    async def attendance_notification(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'attendance_notification',
            'message': message
        }))


class DashboardUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join dashboard updates group
        self.group_name = 'dashboard_updates'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        await self.send_dashboard_stats()

    async def disconnect(self, close_code):
        # Leave dashboard updates group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming WebSocket messages if needed
        pass

    # Receive message from group
    async def dashboard_update(self, event):
        data = event['data']
        
        # Send updated data to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': data
        }))

    @database_sync_to_async
    def get_dashboard_stats(self):
        """Get current dashboard statistics"""
        today = timezone.now().date()
        
        total_employees = Employee.objects.count()
        present_today = AttendanceSummary.objects.filter(date=today, is_present=True).count()
        total_records_today = AttendanceRecord.objects.filter(date=today).count()
        
        return {
            'total_employees': total_employees,
            'present_today': present_today,
            'absent_today': total_employees - present_today,
            'total_records_today': total_records_today,
            'attendance_rate': round((present_today / total_employees * 100) if total_employees > 0 else 0, 1)
        }

    async def send_dashboard_stats(self):
        """Send current dashboard statistics to client"""
        stats = await self.get_dashboard_stats()
        
        await self.send(text_data=json.dumps({
            'type': 'dashboard_stats',
            'data': stats
        }))


class EmployeeDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get employee ID from URL route
        self.employee_id = self.scope['url_route']['kwargs'].get('employee_id')
        self.group_name = f'employee_{self.employee_id}_dashboard'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial employee data
        if self.employee_id:
            await self.send_employee_stats()

    async def disconnect(self, close_code):
        # Leave employee dashboard group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming WebSocket messages if needed
        pass

    # Receive message from group
    async def employee_update(self, event):
        data = event['data']
        
        # Send updated data to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'employee_update',
            'data': data
        }))

    @database_sync_to_async
    def get_employee_stats(self):
        """Get current employee statistics"""
        try:
            employee = Employee.objects.get(employee_id=self.employee_id)
            today = timezone.now().date()
            
            # Today's attendance
            today_summary = AttendanceSummary.objects.filter(
                employee=employee, 
                date=today
            ).first()
            
            # Recent records
            recent_records = list(AttendanceRecord.objects.filter(
                employee=employee
            ).order_by('-timestamp')[:5].values(
                'attendance_type', 'timestamp', 'confidence_score'
            ))
            
            return {
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'employee_id': employee.employee_id,
                'department': employee.department,
                'today_status': {
                    'is_present': today_summary.is_present if today_summary else False,
                    'check_in_time': today_summary.check_in_time.strftime('%H:%M') if today_summary and today_summary.check_in_time else None,
                    'check_out_time': today_summary.check_out_time.strftime('%H:%M') if today_summary and today_summary.check_out_time else None,
                    'total_hours': float(today_summary.total_hours) if today_summary else 0.0,
                    'is_late': today_summary.is_late if today_summary else False
                },
                'recent_records': recent_records
            }
        except Employee.DoesNotExist:
            return {'error': 'Employee not found'}

    async def send_employee_stats(self):
        """Send current employee statistics to client"""
        stats = await self.get_employee_stats()
        
        await self.send(text_data=json.dumps({
            'type': 'employee_stats',
            'data': stats
        }))
