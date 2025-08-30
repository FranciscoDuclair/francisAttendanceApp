from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/attendance/notifications/$', consumers.AttendanceNotificationConsumer.as_asgi()),
    re_path(r'ws/dashboard/updates/$', consumers.DashboardUpdatesConsumer.as_asgi()),
    re_path(r'ws/employee/(?P<employee_id>\w+)/dashboard/$', consumers.EmployeeDashboardConsumer.as_asgi()),
]
