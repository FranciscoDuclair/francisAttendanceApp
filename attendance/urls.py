from django.urls import path
from django.views.decorators.http import require_http_methods
from . import web_views

urlpatterns = [
    # Web Interface URLs
    path('', web_views.home_view, name='home'),
    path('admin-dashboard/', web_views.admin_dashboard_view, name='admin_dashboard'),
    path('employee-dashboard/', web_views.employee_dashboard_view, name='employee_dashboard'),
    path('employee-dashboard/<str:employee_id>/', web_views.employee_dashboard_view, name='employee_dashboard_specific'),
    path('hr-dashboard/', web_views.hr_dashboard_view, name='hr_dashboard'),
    path('employees/', web_views.EmployeeWebListView.as_view(), name='employee_list'),
    path('employees/add/', web_views.EmployeeWebCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', web_views.EmployeeWebDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/edit/', web_views.EmployeeWebUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', web_views.EmployeeWebDeleteView.as_view(), name='employee_delete'),
    path('employees/<int:pk>/register-face/', web_views.register_face_view, name='register_face'),
    path('attendance/', web_views.attendance_check_view, name='attendance_check'),
    path('attendance/recognize/', web_views.face_recognition_web, name='face_recognition_web'),
    path('history/', web_views.attendance_history_view, name='attendance_history'),
    
    # Admin functionality URLs
    path('api/admin/maintenance/status/', web_views.maintenance_status, name='maintenance_status'),
    path('api/admin/maintenance/toggle/', web_views.toggle_maintenance, name='toggle_maintenance'),
    path('api/admin/cache/clear/', web_views.clear_cache_view, name='clear_cache'),
    path('admin/export-data/', web_views.export_data, name='export_data'),
]
