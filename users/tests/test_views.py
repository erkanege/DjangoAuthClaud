from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import Profile
import json
from datetime import date
import tempfile
from PIL import Image
import io

User = get_user_model()

def create_test_image():
    """Helper function to create a test image file"""
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), 'white')
    image.save(file, 'PNG')
    file.name = 'test.png'
    file.seek(0)
    return file

class ProfileViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create regular user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        # Create test profile
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Test bio',
            birth_date=date(1990, 1, 1),
            occupation='Developer',
            phone_number='+1234567890',
            country='Test Country'
        )

    def test_get_own_profile(self):
        """Test retrieving own profile"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('users:profile-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Test bio')
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_own_profile(self):
        """Test updating own profile"""
        self.client.force_authenticate(user=self.user)
        update_data = {
            'bio': 'Updated bio',
            'occupation': 'Senior Developer',
            'phone_number': '+9876543210'
        }
        response = self.client.patch(
            reverse('users:profile-update-me'),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        self.assertEqual(response.data['occupation'], 'Senior Developer')

    def test_admin_can_view_all_profiles(self):
        """Test admin user can view all profiles"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('users:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_regular_user_cannot_view_other_profiles(self):
        """Test regular user cannot view other users' profiles"""
        self.client.force_authenticate(user=self.user)
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='otherpass123'
        )
        other_profile = Profile.objects.create(user=other_user)
        response = self.client.get(
            reverse('users:profile-detail', kwargs={'pk': other_profile.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_avatar(self):
        """Test uploading profile avatar"""
        self.client.force_authenticate(user=self.user)
        image_file = create_test_image()
        upload_file = SimpleUploadedFile('test.png', image_file.getvalue())
        
        response = self.client.post(
            reverse('users:profile-upload-avatar', kwargs={'pk': self.profile.pk}),
            {'avatar': upload_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avatar', response.data)
        
        # Clean up
        self.profile.refresh_from_db()
        if self.profile.avatar:
            self.profile.avatar.delete()

    def test_remove_avatar(self):
        """Test removing profile avatar"""
        self.client.force_authenticate(user=self.user)
        # First upload an avatar
        image_file = create_test_image()
        self.profile.avatar = SimpleUploadedFile('test.png', image_file.getvalue())
        self.profile.save()
        
        response = self.client.post(
            reverse('users:profile-remove-avatar', kwargs={'pk': self.profile.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.profile.refresh_from_db()
        self.assertFalse(bool(self.profile.avatar))

    def test_search_profiles_as_admin(self):
        """Test searching profiles as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            reverse('users:profile-search'),
            {'q': 'developer'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_regular_user_cannot_search_profiles(self):
        """Test regular user cannot search profiles"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('users:profile-search'),
            {'q': 'test'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class UserViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='regularuser',
            password='userpass123'
        )

    def test_admin_can_list_users(self):
        """Test admin can list all users"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_regular_user_cannot_list_users(self):
        """Test regular user cannot list users"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_user(self):
        """Test admin can create new user"""
        self.client.force_authenticate(user=self.admin_user)
        new_user_data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(
            reverse('users:user-list'),
            new_user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_admin_can_update_user(self):
        """Test admin can update user"""
        self.client.force_authenticate(user=self.admin_user)
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(
            reverse('users:user-detail', kwargs={'pk': self.regular_user.pk}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'Updated')
        self.assertEqual(self.regular_user.last_name, 'Name')

    def test_admin_can_delete_user(self):
        """Test admin can delete user"""
        self.client.force_authenticate(user=self.admin_user)
        user_to_delete = User.objects.create_user(
            email='delete@example.com',
            username='deleteuser',
            password='deletepass123'
        )
        response = self.client.delete(
            reverse('users:user-detail', kwargs={'pk': user_to_delete.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=user_to_delete.pk).exists())

    def test_regular_user_cannot_delete_users(self):
        """Test regular user cannot delete users"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(
            reverse('users:user-detail', kwargs={'pk': self.regular_user.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access(self):
        """Test unauthenticated access is denied"""
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)