from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Profile, LoginAttempt


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _('Profile')
    fieldsets = (
        (None, {'fields': ('avatar', 'bio')}),
        (_('Personal Information'), {'fields': ('birth_date', 'phone_number', 'gender')}),
        (_('Location'), {'fields': ('address', 'city', 'country')}),
        (_('Professional'), {'fields': ('occupation', 'company', 'website')}),
        (_('Social Media'), {'fields': ('social_media_links',)}),
        (_('Interests'), {'fields': ('interests',)}),
    )

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_active', 'is_staff', 'date_joined', 'last_login')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'username_attempt', 'successful', 'timestamp')
    readonly_fields = ('ip_address', 'user_agent', 'timestamp', 'username_attempt')
    list_filter = ('successful', 'timestamp')
    search_fields = ('ip_address', 'username_attempt')
    ordering = ('-timestamp',)