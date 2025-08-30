"""
URL configuration for attendance_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from attendance import web_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('attendance.urls')),  # Include web interface URLs
    path('api/', include([
        path('admin/maintenance/status/', web_views.maintenance_status, name='api_maintenance_status'),
        path('admin/maintenance/toggle/', web_views.toggle_maintenance, name='api_toggle_maintenance'),
        path('admin/cache/clear/', web_views.clear_cache_view, name='api_clear_cache'),
    ])),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
