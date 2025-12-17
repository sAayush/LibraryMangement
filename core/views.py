from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer
)
from .permissions import IsOwnerOrAdmin


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Allows any user (anonymous) to register.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="""
        Register a new user account with username, email, and password.
        Upon successful registration, returns user details and JWT tokens.
        
        Default role for new users is 'USER'.
        """,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "johndoe",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "USER",
                            "created_at": "2024-01-01T12:00:00Z"
                        },
                        "message": "User registered successfully",
                        "tokens": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                        }
                    }
                }
            ),
            400: "Bad Request - Validation errors"
        },
        tags=['Auth']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the newly registered user
        refresh = RefreshToken.for_user(user)
        
        user_data = UserSerializer(user).data
        
        return Response({
            'user': user_data,
            'message': 'User registered successfully',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login.
    Returns JWT tokens upon successful authentication.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    @swagger_auto_schema(
        operation_summary="Login user",
        operation_description="""
        Authenticate a user with username and password.
        Returns user details and JWT tokens (access and refresh).
        
        Use the access token in the Authorization header for subsequent requests:
        `Authorization: Bearer <access_token>`
        """,
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "johndoe",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "USER",
                            "created_at": "2024-01-01T12:00:00Z"
                        },
                        "message": "Login successful",
                        "tokens": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid credentials"
        },
        tags=['Auth']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        user_data = UserSerializer(user).data
        
        return Response({
            'user': user_data,
            'message': 'Login successful',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    Blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Logout user",
        operation_description="""
        Logout the current user and blacklist their refresh token.
        After logout, the refresh token cannot be used to obtain new access tokens.
        
        Requires authentication.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Refresh token to blacklist'
                )
            },
            required=['refresh_token']
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "message": "Logout successful"
                    }
                }
            ),
            400: "Bad Request - Invalid token",
            401: "Unauthorized - Authentication required"
        },
        tags=['Auth'],
        security=[{'Bearer': []}]
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token or token already blacklisted'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update user profile.
    Users can only view/edit their own profile, admins can view/edit any profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    @swagger_auto_schema(
        operation_summary="Get/Update user profile",
        operation_description="""
        Retrieve or update user profile.
        - Without pk: Returns/updates current user's profile
        - With pk: Returns/updates specified user's profile (Admin only)
        
        Requires authentication.
        """,
        responses={
            200: UserSerializer,
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Not authorized to access this profile",
            404: "Not Found - User does not exist"
        },
        tags=['Users'],
        security=[{'Bearer': []}]
    )
    def get_object(self):
        # If pk is provided in URL, get that user (admin functionality)
        if 'pk' in self.kwargs:
            return super().get_object()
        # Otherwise, return the current user's profile
        return self.request.user


class CurrentUserView(APIView):
    """
    API endpoint to get current authenticated user's information.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get current user",
        operation_description="""
        Retrieve the authenticated user's profile information.
        
        Requires authentication.
        """,
        responses={
            200: UserSerializer,
            401: "Unauthorized - Authentication required"
        },
        tags=['Users'],
        security=[{'Bearer': []}]
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    API endpoint for changing user password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Change password",
        operation_description="""
        Change the password for the authenticated user.
        Requires the old password for verification and a new password.
        
        Requires authentication.
        """,
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                examples={
                    "application/json": {
                        "message": "Password changed successfully"
                    }
                }
            ),
            400: "Bad Request - Invalid old password or validation error",
            401: "Unauthorized - Authentication required"
        },
        tags=['Users'],
        security=[{'Bearer': []}]
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Set the new password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    API endpoint to list all users.
    Only accessible by administrators.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List users",
        operation_description="""
        List all users in the system.
        - Admins: See all users
        - Regular users: See only themselves
        
        Supports pagination (10 users per page by default).
        
        Requires authentication.
        """,
        responses={
            200: UserSerializer(many=True),
            401: "Unauthorized - Authentication required"
        },
        tags=['Users'],
        security=[{'Bearer': []}]
    )
    def get_queryset(self):
        # Only admins can see all users
        if self.request.user.is_admin:
            return User.objects.all()
        # Regular users can only see themselves
        return User.objects.filter(id=self.request.user.id)


class CreateAdminView(generics.CreateAPIView):
    """
    API endpoint to create admin users.
    Only accessible by existing administrators.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Create admin user",
        operation_description="""
        Create a new administrator account.
        Only existing administrators can create new admins.
        
        This endpoint creates a user with ADMIN role who has full access to:
        - Manage all users
        - Add/remove books (coming soon)
        - View all loans (coming soon)
        
        **Requires Admin privileges.**
        """,
        responses={
            201: openapi.Response(
                description="Admin user created successfully",
                examples={
                    "application/json": {
                        "user": {
                            "id": 2,
                            "username": "admin2",
                            "email": "admin2@example.com",
                            "first_name": "Admin",
                            "last_name": "User",
                            "role": "ADMIN",
                            "created_at": "2024-01-01T12:00:00Z"
                        },
                        "message": "Admin user created successfully",
                        "tokens": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                        }
                    }
                }
            ),
            400: "Bad Request - Validation errors",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin privileges required"
        },
        tags=['Admin'],
        security=[{'Bearer': []}]
    )
    def create(self, request, *args, **kwargs):
        # Check if user is admin
        if not request.user.is_admin:
            return Response({
                'error': 'Only administrators can create admin accounts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user with ADMIN role
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            role=User.UserRole.ADMIN  # Set as ADMIN
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        user_data = UserSerializer(user).data
        
        return Response({
            'user': user_data,
            'message': 'Admin user created successfully',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class PromoteToAdminView(APIView):
    """
    API endpoint to promote an existing user to admin.
    Only accessible by administrators.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Promote user to admin",
        operation_description="""
        Promote an existing regular user to administrator role.
        Only existing administrators can promote users.
        
        Provide the user ID in the request body to promote them to ADMIN role.
        
        **Requires Admin privileges.**
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the user to promote to admin'
                )
            },
            required=['user_id']
        ),
        responses={
            200: openapi.Response(
                description="User promoted successfully",
                examples={
                    "application/json": {
                        "message": "User promoted to admin successfully",
                        "user": {
                            "id": 3,
                            "username": "johndoe",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "ADMIN",
                            "created_at": "2024-01-01T12:00:00Z"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid user ID",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin privileges required",
            404: "Not Found - User does not exist"
        },
        tags=['Admin'],
        security=[{'Bearer': []}]
    )
    def post(self, request):
        # Check if user is admin
        if not request.user.is_admin:
            return Response({
                'error': 'Only administrators can promote users to admin'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'error': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already admin
        if user.is_admin:
            return Response({
                'error': 'User is already an administrator'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Promote to admin
        user.role = User.UserRole.ADMIN
        user.save()
        
        user_data = UserSerializer(user).data
        
        return Response({
            'message': 'User promoted to admin successfully',
            'user': user_data
        }, status=status.HTTP_200_OK)
