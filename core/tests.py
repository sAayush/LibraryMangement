from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the User model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, User.UserRole.USER)
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_admin_user(self):
        """Test creating an admin user"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        self.assertEqual(admin.role, User.UserRole.ADMIN)
        self.assertTrue(admin.is_admin)
    
    def test_user_str_representation(self):
        """Test the string representation of user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser (Registered User)')
    
    def test_is_admin_property(self):
        """Test is_admin property"""
        user = User.objects.create_user(**self.user_data)
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        self.assertFalse(user.is_admin)
        self.assertTrue(admin.is_admin)


class AuthenticationAPITest(APITestCase):
    """Test cases for authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.logout_url = '/api/auth/logout/'
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        }
    
    def test_user_registration(self):
        """Test user registration with valid data"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['role'], 'USER')
    
    def test_registration_password_mismatch(self):
        """Test registration fails with mismatched passwords"""
        data = self.user_data.copy()
        data['password2'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login with correct credentials"""
        # Register user first
        self.client.post(self.register_url, self.user_data)
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_invalid_credentials(self):
        """Test login fails with wrong password"""
        self.client.post(self.register_url, self.user_data)
        
        login_data = {
            'username': 'testuser',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_logout(self):
        """Test user logout"""
        # Register and login
        reg_response = self.client.post(self.register_url, self.user_data)
        refresh_token = reg_response.data['tokens']['refresh']
        access_token = reg_response.data['tokens']['access']
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.logout_url, {'refresh_token': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserManagementAPITest(APITestCase):
    """Test cases for user management endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        
        # Get tokens
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
    
    def test_get_current_user(self):
        """Test getting current user information"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_current_user_unauthorized(self):
        """Test getting current user without authentication"""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_password(self):
        """Test changing user password"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewTestPass123!',
            'new_password2': 'NewTestPass123!'
        }
        response = self.client.post('/api/users/change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewTestPass123!'))
    
    def test_change_password_wrong_old_password(self):
        """Test change password fails with wrong old password"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {
            'old_password': 'WrongPassword!',
            'new_password': 'NewTestPass123!',
            'new_password2': 'NewTestPass123!'
        }
        response = self.client.post('/api/users/change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_users_as_admin(self):
        """Test admin can see all users"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_list_users_as_regular_user(self):
        """Test regular user can only see themselves"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'testuser')


class AdminOperationsAPITest(APITestCase):
    """Test cases for admin-only operations"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
    
    def test_create_admin_as_admin(self):
        """Test admin can create another admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'AdminPass123!',
            'password2': 'AdminPass123!'
        }
        response = self.client.post('/api/admin/create-admin/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'ADMIN')
    
    def test_create_admin_as_regular_user(self):
        """Test regular user cannot create admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'AdminPass123!',
            'password2': 'AdminPass123!'
        }
        response = self.client.post('/api/admin/create-admin/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_promote_user_to_admin(self):
        """Test promoting a user to admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post('/api/admin/promote/', {'user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.UserRole.ADMIN)
    
    def test_promote_user_as_regular_user(self):
        """Test regular user cannot promote others"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.post('/api/admin/promote/', {'user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
