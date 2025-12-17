# Library Management System - Authentication API Documentation

## Overview
This document describes the authentication and authorization system for the Library Management System. The system uses JWT (JSON Web Tokens) for secure authentication.

## User Roles

### 1. Anonymous Users
- Can browse and search for books
- Cannot borrow books
- No authentication required

### 2. Registered Users (USER)
- Can browse and search for books
- Can borrow books
- Requires authentication
- Default role for new registrations

### 3. Administrators (ADMIN)
- Full access to all features
- Can add/remove books
- Can manage users
- Requires authentication

## API Endpoints

### Base URL
All authentication endpoints are prefixed with `/api/`

---

### 1. User Registration
**Endpoint:** `POST /api/auth/register/`

**Description:** Register a new user account

**Authentication:** Not required

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "John",  // Optional
    "last_name": "Doe"     // Optional
}
```

**Success Response (201 Created):**
```json
{
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
```

**Error Response (400 Bad Request):**
```json
{
    "password": ["Password fields didn't match."],
    "email": ["A user with this email already exists."]
}
```

---

### 2. User Login
**Endpoint:** `POST /api/auth/login/`

**Description:** Login with username and password

**Authentication:** Not required

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "SecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
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
```

**Error Response (400 Bad Request):**
```json
{
    "non_field_errors": ["Unable to log in with provided credentials."]
}
```

---

### 3. Token Refresh
**Endpoint:** `POST /api/auth/token/refresh/`

**Description:** Get a new access token using refresh token

**Authentication:** Not required (but needs valid refresh token)

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // New refresh token (rotation enabled)
}
```

---

### 4. User Logout
**Endpoint:** `POST /api/auth/logout/`

**Description:** Logout and blacklist the refresh token

**Authentication:** Required (Bearer Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Invalid token or token already blacklisted"
}
```

---

### 5. Get Current User
**Endpoint:** `GET /api/auth/me/`

**Description:** Get current authenticated user's information

**Authentication:** Required (Bearer Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "USER",
    "created_at": "2024-01-01T12:00:00Z"
}
```

---

### 6. Get/Update User Profile
**Endpoint:** 
- `GET /api/auth/profile/` - Get own profile
- `PUT /api/auth/profile/` - Update own profile
- `PATCH /api/auth/profile/` - Partially update own profile
- `GET /api/auth/profile/{id}/` - Get specific user profile (Admin only)
- `PUT /api/auth/profile/{id}/` - Update specific user profile (Admin only)

**Description:** Retrieve or update user profile

**Authentication:** Required (Bearer Token)

**Request Body (for PUT/PATCH):**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "newemail@example.com"
}
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "newemail@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "USER",
    "created_at": "2024-01-01T12:00:00Z"
}
```

---

### 7. Change Password
**Endpoint:** `POST /api/auth/change-password/`

**Description:** Change user password

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
    "old_password": "OldPassword123!",
    "new_password": "NewSecurePassword123!",
    "new_password2": "NewSecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
    "old_password": ["Old password is incorrect."],
    "new_password": ["Password fields didn't match."]
}
```

---

### 8. List Users
**Endpoint:** `GET /api/users/`

**Description:** List all users (Admins see all, regular users see only themselves)

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "USER",
            "created_at": "2024-01-01T12:00:00Z"
        },
        // ... more users
    ]
}
```

---

## Authentication Flow

### Using JWT Tokens

1. **Register or Login** to get access and refresh tokens
2. **Use Access Token** in Authorization header for all protected endpoints:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Access tokens expire after 1 hour**
4. **Refresh tokens expire after 7 days**
5. When access token expires, use refresh token to get a new one via `/api/auth/token/refresh/`
6. When logging out, send the refresh token to `/api/auth/logout/` to blacklist it

### Example: Making an Authenticated Request

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "password": "SecurePassword123!"}'

# Response will include access token
# Use it in subsequent requests:

curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <your_access_token>"
```

---

## Custom Permissions

The system includes several custom permission classes:

### 1. `IsAdminUser`
- Only allows administrators to access
- Used for admin-only endpoints (e.g., user management, book management)

### 2. `IsRegisteredUser`
- Only allows registered users (non-admin authenticated users)
- Used for user-specific actions (e.g., borrowing books)

### 3. `IsOwnerOrAdmin`
- Allows users to access their own resources or admins to access any resource
- Used for profile management

### 4. `ReadOnlyOrAuthenticated`
- Anonymous users can read (browse books)
- Authenticated users can read and write (borrow books)
- Perfect for the library browsing feature

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
Ensure your `.env` file has the correct PostgreSQL credentials:
```env
DB_NAME=library_db
DB_USER=library_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

### 6. Access the API
- API Base URL: `http://localhost:8000/api/`
- Admin Panel: `http://localhost:8000/admin/`

---

## Password Requirements

Django's built-in password validation is enabled:
- Minimum length: 8 characters
- Cannot be too similar to username/email
- Cannot be a commonly used password
- Cannot be entirely numeric

---

## Security Notes

1. **SECRET_KEY**: Keep it secret and never commit it to version control
2. **DEBUG**: Set to `False` in production
3. **HTTPS**: Always use HTTPS in production
4. **Token Storage**: Store tokens securely on the client side (e.g., httpOnly cookies)
5. **Token Rotation**: Refresh tokens are rotated on each use for better security
6. **Token Blacklisting**: Logout properly blacklists tokens to prevent reuse

---

## Next Steps

After setting up authentication, you can:
1. Create Book model for library catalog
2. Create Loan model for tracking borrowed books
3. Implement book search and filtering
4. Add book borrowing/returning functionality
5. Create admin panel for book management

---

## Testing the API

You can test the API using tools like:
- **Postman**: Import the endpoints and test
- **curl**: Command-line testing
- **HTTPie**: User-friendly command-line HTTP client
- **Django REST Framework Browsable API**: Visit endpoints in browser

Example with HTTPie:
```bash
# Register
http POST http://localhost:8000/api/auth/register/ \
  username=johndoe \
  email=john@example.com \
  password=SecurePassword123! \
  password2=SecurePassword123!

# Login
http POST http://localhost:8000/api/auth/login/ \
  username=johndoe \
  password=SecurePassword123!
```

---

## Support

For issues or questions, please refer to the project documentation or contact the development team.

