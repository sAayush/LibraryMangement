from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role field for different user types in the library system.
    """
    
    class UserRole(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        USER = 'USER', 'Registered User'
    
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.USER,
        help_text='User role in the library system'
    )
    
    email = models.EmailField(unique=True, help_text='User email address')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user is an administrator"""
        return self.role == self.UserRole.ADMIN
    
    @property
    def is_registered_user(self):
        """Check if user is a registered user"""
        return self.role == self.UserRole.USER
