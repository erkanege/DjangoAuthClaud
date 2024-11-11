from django.test import TestCase
from django.contrib.auth import get_user_model
from users.serializers import ProfileSerializer, UserSerializer
from users.models import Profile
from datetime import date

User = get_user_model()

class ProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile_data = {
            'bio': 'Test bio',
            'birth_date': '1990-01-01',
            'phone_number': '+1234567890',
            'gender': 'M',
            'occupation': 'Developer',
            'country': 'Test Country',
            'city': 'Test City',
            'social_media_links': {
                'twitter': 'https://twitter.com/testuser',
                'linkedin': 'https://linkedin.com/in/testuser'
            },
            'interests': ['coding', 'testing']
        }
        self.profile = Profile.objects.create(user=self.user)

    def test_contains_expected_fields(self):
        serializer = ProfileSerializer(instance=self.profile)
        expected_fields = {
            'id', 'email', 'username', 'full_name', 'avatar', 'bio',
            'birth_date', 'phone_number', 'gender', 'address', 'city',
            'country', 'occupation', 'company', 'website', 'social_media_links',
            'interests', 'age', 'created_at', 'updated_at'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_validate_phone_number(self):
        # Valid phone number
        serializer = ProfileSerializer(data={'phone_number': '+1234567890'})
        self.assertTrue(serializer.is_valid())

        # Invalid phone number
        serializer = ProfileSerializer(data={'phone_number': 'invalid'})
        self.assertFalse(serializer.is_valid())

    def test_validate_social_media_links(self):
        # Valid social media links
        valid_data = {
            'social_media_links': {
                'twitter': 'https://twitter.com/test',
                'linkedin': 'https://linkedin.com/in/test'
            }
        }
        serializer = ProfileSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Invalid social media links
        invalid_data = {
            'social_media_links': {
                'invalid': 'not-a-url'
            }
        }
        serializer = ProfileSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

class UserSerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_contains_expected_fields(self):
        serializer = UserSerializer(instance=self.user)
        expected_fields = {
            'id', 'email', 'username', 'first_name', 'last_name', 'is_active'
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_read_only_fields(self):
        serializer = UserSerializer(instance=self.user)
        self.assertFalse(serializer.fields['id'].allow_modify_operations())
        self.assertFalse(serializer.fields['is_active'].allow_modify_operations())