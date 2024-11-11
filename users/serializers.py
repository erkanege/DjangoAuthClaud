from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import Profile, CustomUser
from .validators import validate_phone_number, validate_social_media_links, validate_interests

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name')

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_active')
        read_only_fields = ('id', 'is_active')

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id', 'email', 'username', 'full_name', 'avatar', 'bio',
            'birth_date', 'phone_number', 'gender', 'address', 'city',
            'country', 'occupation', 'company', 'website', 'social_media_links',
            'interests', 'age', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'email', 'username', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_age(self, obj):
        return obj.age()

    def validate_phone_number(self, value):
        validate_phone_number(value)
        return value

    def validate_social_media_links(self, value):
        validate_social_media_links(value)
        return value

    def validate_interests(self, value):
        validate_interests(value)
        return value

    def validate_avatar(self, value):
        if value.size > 2 * 1024 * 1024:  # 2MB limit
            raise serializers.ValidationError(
                "Avatar file size cannot exceed 2MB."
            )
        return value