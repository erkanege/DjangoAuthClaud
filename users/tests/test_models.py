from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import Profile
from datetime import date

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(**self.user_data)
        self.assertEqual(admin_user.email, self.user_data['email'])
        self.assertEqual(admin_user.username, self.user_data['username'])
        self.assertTrue(admin_user.check_password(self.user_data['password']))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.profile_data = {
            'user': self.user,
            'bio': 'Test bio',
            'birth_date': date(1990, 1, 1),
            'phone_number': '+1234567890',
            'gender': 'M',
            'occupation': 'Developer'
        }

    def test_profile_creation(self):
        profile = Profile.objects.create(**self.profile_data)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, self.profile_data['bio'])
        self.assertEqual(profile.birth_date, self.profile_data['birth_date'])

    def test_profile_age_calculation(self):
        profile = Profile.objects.create(**self.profile_data)
        expected_age = date.today().year - self.profile_data['birth_date'].year
        self.assertEqual(profile.age(), expected_age)

    def test_profile_str_representation(self):
        profile = Profile.objects.create(**self.profile_data)
        expected_str = f"{self.user.email}'s Profile"
        self.assertEqual(str(profile), expected_str)