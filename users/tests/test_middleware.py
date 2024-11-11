from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from users.middleware import LoginRateThrottleMiddleware
from users.models import LoginAttempt
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta

User = get_user_model()

class LoginRateThrottleMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = LoginRateThrottleMiddleware(lambda x: x)
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def tearDown(self):
        cache.clear()

    def test_successful_login_attempt(self):
        request = self.factory.post('/auth/jwt/create/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        response = self.middleware(request)
        
        self.assertFalse(hasattr(request, 'captcha_required'))
        self.assertIsNone(cache.get('ip_blocked_127.0.0.1'))

    def test_failed_login_attempts_captcha(self):
        ip = '127.0.0.1'
        # Create failed login attempts
        for _ in range(settings.LOGIN_ATTEMPT_LIMIT):
            LoginAttempt.objects.create(
                ip_address=ip,
                successful=False,
                timestamp=datetime.now()
            )

        request = self.factory.post('/auth/jwt/create/')
        request.META['REMOTE_ADDR'] = ip
        response = self.middleware(request)
        
        self.assertTrue(hasattr(request, 'captcha_required'))

    def test_ip_blocking(self):
        ip = '127.0.0.1'
        # Create maximum failed login attempts
        for _ in range(settings.MAX_LOGIN_ATTEMPTS):
            LoginAttempt.objects.create(
                ip_address=ip,
                successful=False,
                timestamp=datetime.now()
            )

        request = self.factory.post('/auth/jwt/create/')
        request.META['REMOTE_ADDR'] = ip
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 403)
        self.assertTrue(cache.get(f'ip_blocked_{ip}'))

    def test_reset_on_successful_login(self):
        ip = '127.0.0.1'
        # Create some failed attempts
        for _ in range(2):
            LoginAttempt.objects.create(
                ip_address=ip,
                successful=False,
                timestamp=datetime.now()
            )

        # Create successful attempt
        LoginAttempt.objects.create(
            ip_address=ip,
            successful=True,
            timestamp=datetime.now()
        )

        request = self.factory.post('/auth/jwt/create/')
        request.META['REMOTE_ADDR'] = ip
        response = self.middleware(request)
        
        self.assertFalse(hasattr(request, 'captcha_required'))
        self.assertIsNone(cache.get(f'ip_blocked_{ip}'))