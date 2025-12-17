from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow administrators to access.
    """
    message = "You must be an administrator to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsRegisteredUser(permissions.BasePermission):
    """
    Custom permission to only allow registered users to access.
    """
    message = "You must be a registered user to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_registered_user
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit/delete it.
    """
    message = "You must be the owner or an administrator to perform this action."
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions are only allowed to the owner or admin
        return (
            obj == request.user or
            (request.user.is_authenticated and request.user.is_admin)
        )


class ReadOnlyOrAuthenticated(permissions.BasePermission):
    """
    Custom permission to allow anonymous users to read, but authenticated users to write.
    This is useful for allowing anonymous users to browse books but not borrow them.
    """
    
    def has_permission(self, request, view):
        # Allow read-only access for anonymous users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated

