"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core.dashboard import DashboardView

# Swagger/OpenAPI Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Library Management System API",
        default_version='v1',
        description="""
        # Library Management System API
        
        Comprehensive REST API for library management with JWT authentication and role-based access control.
        
        ## 🔐 Authentication
        
        This API uses **JWT (JSON Web Token)** authentication. To use protected endpoints:
        
        1. **Register** or **Login** to get your access token
        2. Click the **"Authorize"** button (🔓) at the top right
        3. Enter: `Bearer <your_access_token>`
        4. Click **"Authorize"** and close the dialog
        5. All authenticated requests will now include your token
        
        **Token Lifecycle:**
        - Access tokens expire after **1 hour**
        - Refresh tokens expire after **7 days**
        - Use `/api/auth/token/refresh/` to get a new access token
        
        ## 👥 User Roles
        
        | Role | Permissions |
        |------|-------------|
        | **Anonymous** | Browse books (read-only) |
        | **USER** | Browse and borrow books |
        | **ADMIN** | Full access: manage users and books |
        
        ## 📚 API Organization
        
        - **Auth**: Registration, login, logout, token management
        - **Users**: Profile management, password changes, user listing
        - **Admin**: Create admins, promote users (Admin only)
        - **Books**: Browse, search, and manage library catalog
        - **Loans**: Borrow, return, and track book loans
        
        ## 🚀 Quick Start
        
        1. Register: `POST /api/auth/register/`
        2. Login: `POST /api/auth/login/` (returns tokens)
        3. Use your access token for authenticated requests
        
        ---
        
        **Current Features:**
        - ✅ User authentication & role-based access
        - ✅ Book catalog management
        - ✅ Loan tracking & management
        - ✅ Advanced filtering & search
        - ✅ Secure API with CSRF, XSS, SQL injection protection
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@library.example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
    patterns=[
        path('api/', include('core.urls')),
        path('api/', include('library.urls')),
        path('api/', include('loan.urls')),
    ],  # Only include API endpoints, exclude Django admin
)

urlpatterns = [
    # Dashboard (Home)
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('core.urls')),
    path('api/', include('library.urls')),
    path('api/', include('loan.urls')),
    
    # Swagger/OpenAPI Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
