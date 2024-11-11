# core/middleware/rate_limit.py

from django.core.cache import cache
from django.http import HttpResponse
from django.utils.translation import gettext as _
import time

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        self.rate_limits = getattr(settings, 'RATE_LIMIT', {}).get('MAX_REQUESTS', {})
        self.cache_timeout = getattr(settings, 'RATE_LIMIT', {}).get('DEFAULT_TIMEOUT', 60)

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_staff:
            return self.get_response(request)

        ip = self.get_client_ip(request)
        method = 'JWT_LOGIN' if request.path.startswith('/auth/jwt/create') else request.method

        if not self.check_rate_limit(ip, method):
            return HttpResponseTooManyRequests(
                _('Rate limit exceeded. Please try again later.'),
                content_type='application/json'
            )

        response = self.get_response(request)
        limit = self.rate_limits.get(method, 30)
        remaining = self.get_remaining_requests(ip, method)
        
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(int(time.time()) + self.cache_timeout)
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def check_rate_limit(self, ip, method):
        cache_key = f"rate_limit:{ip}:{method}"
        try:
            current_count = cache.get(cache_key, 0)
            limit = self.rate_limits.get(method, 30)
            
            if current_count >= limit:
                return False
                
            cache.set(cache_key, current_count + 1, self.cache_timeout)
            return True
        except Exception:
            return True  # Fallback to allow request if cache fails

    def get_remaining_requests(self, ip, method):
        try:
            cache_key = f"rate_limit:{ip}:{method}"
            current_count = cache.get(cache_key, 0)
            limit = self.rate_limits.get(method, 30)
            return max(0, limit - current_count)
        except Exception:
            return 0  # Fallback to 0 if cache fails