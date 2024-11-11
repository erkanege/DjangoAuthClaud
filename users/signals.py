from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile, LoginAttempt
from django.core.cache import cache
from ipware import get_client_ip
from django.contrib.auth.signals import user_logged_in, user_login_failed
from datetime import datetime, timedelta

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def record_login_attempt(request, success):
    client_ip, _ = get_client_ip(request)
    LoginAttempt.objects.create(
        ip_address=client_ip,
        successful=success
    )
    
    if success:
        # Reset failed attempts on successful login
        cache.delete(f'failed_attempts_{client_ip}')
        cache.delete(f'ip_blocked_{client_ip}')
    else:
        # Increment failed attempts
        failed_attempts = LoginAttempt.objects.filter(
            ip_address=client_ip,
            successful=False,
            timestamp__gte=datetime.now() - timedelta(hours=1)
        ).count()
        
        # Update cache with failed attempts count
        cache.set(f'failed_attempts_{client_ip}', failed_attempts, 60 * 60)  # 1 hour expiry
        
        # If reached maximum attempts, block IP
        if failed_attempts >= 10:
            cache.set(f'ip_blocked_{client_ip}', True, 60 * 30)  # 30 minutes block

# Signal to handle successful login
@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    record_login_attempt(request, success=True)

# Signal to handle failed login
@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    record_login_attempt(request, success=False)

# Register the signals in the app's ready() method
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
        from django.contrib.auth.signals import user_logged_in, user_login_failed