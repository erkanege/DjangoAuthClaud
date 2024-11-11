# users/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.db import models
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Profile, CustomUser, LoginAttempt
from .serializers import ProfileSerializer, UserSerializer
from .permissions import IsOwnerOrAdmin
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        client_ip = get_client_ip(request)
        email = request.data.get('email', '')

        try:
            user = CustomUser.objects.get(email=email)
            
            # Hesap kilitli mi kontrol et
            if user.is_locked and user.locked_until and user.locked_until > timezone.now():
                remaining_time = (user.locked_until - timezone.now()).total_seconds()
                return Response({
                    'detail': f'Account is locked. Try again in {int(remaining_time)} seconds.'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except CustomUser.DoesNotExist:
            pass

        # Login denemesi yap
        try:
            response = super().post(request, *args, **kwargs)
            
            # Başarılı giriş
            if response.status_code == 200:
                LoginAttempt.objects.create(
                    ip_address=client_ip,
                    username_attempt=email,
                    successful=True
                )
                
                # Başarılı girişte kullanıcının bilgilerini sıfırla
                try:
                    user = CustomUser.objects.get(email=email)
                    user.failed_login_attempts = 0
                    user.is_locked = False
                    user.locked_until = None
                    user.save()
                except CustomUser.DoesNotExist:
                    pass
                    
                return response
            
        except Exception as e:
            # Başarısız giriş
            try:
                user = CustomUser.objects.get(email=email)
                user.failed_login_attempts += 1
                
                # Maksimum deneme sayısı aşıldı mı?
                if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                    user.is_locked = True
                    user.locked_until = timezone.now() + timedelta(seconds=settings.ACCOUNT_LOCK_TIME)
                    
                user.save()
                
                LoginAttempt.objects.create(
                    ip_address=client_ip,
                    username_attempt=email,
                    successful=False,
                    failure_reason='Invalid credentials'
                )
                
                if user.is_locked:
                    return Response({
                        'detail': f'Account is locked for {settings.ACCOUNT_LOCK_TIME} seconds due to too many failed attempts.'
                    }, status=status.HTTP_403_FORBIDDEN)
                    
            except CustomUser.DoesNotExist:
                LoginAttempt.objects.create(
                    ip_address=client_ip,
                    username_attempt=email,
                    successful=False,
                    failure_reason='User not found'
                )
            
            return Response({
                'detail': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user profiles.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'country', 'city']
    search_fields = ['user__email', 'user__username', 'occupation', 'company']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Profile.objects.all().select_related('user')
        return Profile.objects.filter(user=user).select_related('user')

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management (admin only).
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login']
    
from rest_framework import views

class CustomLogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Token'ı blacklist'e ekle
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                # Kullanıcının son çıkış zamanını güncelle
                request.user.last_login = timezone.now()
                request.user.save()
                
                return Response(
                    {"detail": "Successfully logged out."}, 
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Refresh token is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
# users/views.py
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        client_ip = get_client_ip(request)
        email = request.data.get('email', '')

        try:
            user = CustomUser.objects.get(email=email)
            
            # Hesap kilitli mi kontrol et
            if user.is_locked and user.locked_until and user.locked_until > timezone.now():
                remaining_time = (user.locked_until - timezone.now()).total_seconds()
                # Login girişimini kaydet
                LoginAttempt.create_attempt(
                    ip_address=client_ip,
                    username=email,
                    success=False,
                    failure_reason='Account locked',
                    user=user
                )
                return Response({
                    'detail': f'Account is locked. Try again in {int(remaining_time)} seconds.'
                }, status=status.HTTP_403_FORBIDDEN)

        except CustomUser.DoesNotExist:
            pass

        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Başarılı giriş
                user = CustomUser.objects.get(email=email)
                LoginAttempt.create_attempt(
                    ip_address=client_ip,
                    username=email,
                    success=True,
                    user=user
                )
                user.reset_failed_attempts()
                return response
                
        except Exception as e:
            # Başarısız giriş
            try:
                user = CustomUser.objects.get(email=email)
                user.increment_failed_attempts()
                
                LoginAttempt.create_attempt(
                    ip_address=client_ip,
                    username=email,
                    success=False,
                    failure_reason=str(e),
                    user=user
                )
                
                if user.is_locked:
                    return Response({
                        'detail': f'Too many failed attempts. Account is locked for {settings.ACCOUNT_LOCK_TIME} seconds.'
                    }, status=status.HTTP_403_FORBIDDEN)
            except CustomUser.DoesNotExist:
                LoginAttempt.create_attempt(
                    ip_address=client_ip,
                    username=email,
                    success=False,
                    failure_reason='User not found'
                )
            
            return Response({
                'detail': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)