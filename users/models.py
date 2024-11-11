from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache


# users/models.py

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    is_locked = models.BooleanField(default=False)  # Hesap kilitli mi?
    locked_until = models.DateTimeField(null=True, blank=True)  # Ne zamana kadar kilitli?
    failed_login_attempts = models.IntegerField(default=0)  # Başarısız giriş sayısı
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def lock_account(self):
        """Hesabı kilitle"""
        self.is_locked = True
        # Şu anki zamana ACCOUNT_LOCK_TIME kadar süre ekle
        self.locked_until = timezone.now() + timedelta(seconds=getattr(settings, 'ACCOUNT_LOCK_TIME', 300))
        self.save(update_fields=['is_locked', 'locked_until', 'failed_login_attempts'])

    def unlock_account(self):
        """Hesabın kilidini aç"""
        self.is_locked = False
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save()

    def increment_failed_attempts(self):
        """Başarısız giriş denemelerini artır"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            self.lock_account()
        self.save()

    def reset_failed_attempts(self):
        """Başarısız giriş denemelerini sıfırla"""
        self.failed_login_attempts = 0
        self.save()

    def check_lock_status(self):
        """Hesap kilit durumunu kontrol et"""
        if self.is_locked:
            if self.locked_until and timezone.now() >= self.locked_until:
                self.unlock_account()
                return False
            return True
        return False

class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    social_media_links = models.JSONField(default=dict, blank=True)
    interests = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

class LoginAttemptManager(models.Manager):
    def check_ip_attempts(self, ip_address):
        """IP adresinden yapılan başarısız giriş denemelerini kontrol et"""
        recent_attempts = self.filter(
            ip_address=ip_address,
            successful=False,
            timestamp__gte=timezone.now() - timedelta(minutes=settings.IP_BLOCK_DURATION)  # Settings'ten
        ).count()
        
        return recent_attempts < settings.MAX_LOGIN_ATTEMPTS

    def record_attempt(self, ip_address, success=False, user=None, username='', user_agent='', failure_reason=''):
        """
        Giriş denemesini kaydet.
        
        Args:
            ip_address (str): Kullanıcının IP adresi
            success (bool): Giriş başarılı mı?
            user (User): Giriş yapan kullanıcı (opsiyonel)  
            username (str): Denenen kullanıcı adı
            user_agent (str): Kullanıcının tarayıcı bilgisi
            failure_reason (str): Başarısızlık nedeni
        """
        attempt = self.create(
            ip_address=ip_address,
            successful=success,
            user=user,
            username_attempt=username,
            user_agent=user_agent,
            failure_reason=failure_reason
        )
        
        if not success:
            # IP bloklaması gerekiyorsa cache'e ekle
            if not self.check_ip_attempts(ip_address):
                cache.set(
                    f'ip_blocked_{ip_address}',
                    True,
                    settings.LOGIN_ATTEMPT_TIMEOUT
                )
        
        return attempt

    def is_ip_blocked(self, ip_address):
        """IP adresi bloklanmış mı kontrol et"""
        return cache.get(f'ip_blocked_{ip_address}', False)

# users/models.py
from django.utils import timezone

class LoginAttempt(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)  # auto_now_add yerine default=timezone.now kullanın
    successful = models.BooleanField(default=False)
    username_attempt = models.CharField(max_length=255, blank=True)
    failure_reason = models.CharField(max_length=100, blank=True)
    blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'

    @classmethod
    def create_attempt(cls, ip_address, success=False, user=None, username='', user_agent='', failure_reason=''):
        return cls.objects.create(
            ip_address=ip_address,
            successful=success,
            user=user,
            username_attempt=username,
            user_agent=user_agent,
            failure_reason=failure_reason,
            timestamp=timezone.now()  # Timezone-aware timestamp
        )