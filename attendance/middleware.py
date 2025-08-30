from django.http import HttpResponse, JsonResponse
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import json

class MaintenanceModeMiddleware(MiddlewareMixin):    
    def process_request(self, request):
        # Skip maintenance check for admin and API endpoints
        if request.path.startswith(reverse('admin:index')) or \
           request.path.startswith('/api/') or \
           request.path == reverse('maintenance_status') or \
           request.path == reverse('toggle_maintenance'):
            return None
            
        # Check if maintenance mode is active
        maintenance_mode = cache.get('maintenance_mode', False)
        
        # Allow staff users even in maintenance mode
        if maintenance_mode and not request.user.is_staff:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'System is currently under maintenance. Please try again later.'
                }, status=503)
            
            # Return maintenance page for regular requests
            from django.template.loader import render_to_string
            html = render_to_string('maintenance.html', {
                'title': 'System Maintenance',
                'message': 'We are currently performing scheduled maintenance. We\'ll be back shortly!'
            })
            return HttpResponse(html, status=503, content_type='text/html')
            
        return None
