from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, UserViewSet, CustomLogoutView

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'users', UserViewSet, basename='user')

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', CustomLogoutView.as_view(), name='jwt-logout'),
]

# Available API endpoints:
# /api/v1/profiles/ - Profile list/create
# /api/v1/profiles/{id}/ - Profile detail/update/delete
# /api/v1/profiles/me/ - Current user's profile
# /api/v1/profiles/search/ - Search profiles (admin only)
# /api/v1/profiles/{id}/upload_avatar/ - Upload profile avatar
# /api/v1/profiles/{id}/remove_avatar/ - Remove profile avatar
# /api/v1/users/ - User list (admin only)
# /api/v1/users/{id}/ - User detail (admin only)