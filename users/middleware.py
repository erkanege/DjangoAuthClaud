from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse  # Import JsonResponse
from ipware import get_client_ip
from .models import LoginAttempt
from django.utils import timezone
from datetime import timedelta  # Import timedelta
from django.conf import settings  # Import settings module

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class LoginRateThrottleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/auth/jwt/create/':
            client_ip = get_client_ip(request)
            
            # Son 5 dakika içindeki başarısız denemeleri kontrol et
            recent_attempts = LoginAttempt.objects.filter(
                ip_address=client_ip,
                successful=False,
                timestamp__gte=timezone.now() - timedelta(minutes=5)
            ).count()

            if recent_attempts >= getattr(settings, 'MAX_LOGIN_ATTEMPTS', 3):
                return JsonResponse({
                    'detail': 'Too many failed login attempts. Please try again later.'
                }, status=403)

        return self.get_response(request)