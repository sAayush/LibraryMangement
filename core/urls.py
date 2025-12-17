from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    CurrentUserView,
    ChangePasswordView,
    UserListView,
    CreateAdminView,
    PromoteToAdminView,
)

app_name = 'core'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/profile/<int:pk>/', UserProfileView.as_view(), name='user-profile-detail'),
    path('users/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/', UserListView.as_view(), name='user-list'),
    
    # Admin endpoints
    path('admin/create-admin/', CreateAdminView.as_view(), name='create-admin'),
    path('admin/promote/', PromoteToAdminView.as_view(), name='promote-to-admin'),
]

