from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@tcu.edu',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'student_id': '23-00001'
        }

    def test_user_registration(self):
        """Test user registration with valid data"""
        response = self.client.post('/api/auth/register/', {
            **self.user_data,
            'password_confirm': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_user_login(self):
        """Test user login with valid credentials"""
        # Create user first
        User.objects.create_user(**self.user_data)
        
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class UserModelTestCase(TestCase):
    def test_create_student_user(self):
        """Test creating a student user"""
        user = User.objects.create_user(
            username='student2',
            email='student2@tcu.edu',
            password='pass123',
            role='student',
            student_id='23-00003'
        )
        self.assertTrue(user.is_student())
        self.assertFalse(user.is_admin())
        self.assertEqual(user.student_id, '23-00003')

    def test_create_admin_user(self):
        """Test creating an admin user"""
        user = User.objects.create_user(
            username='admin1',
            email='admin1@tcu.edu',
            password='pass123',
            role='admin'
        )
        self.assertTrue(user.is_admin())
        self.assertFalse(user.is_student())
