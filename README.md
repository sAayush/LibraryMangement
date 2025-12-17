# Library Management System

A comprehensive library management system built with Django and Django REST Framework, featuring JWT authentication, role-based access control, and a RESTful API.

## Features

### ✅ Implemented
- **User Authentication & Authorization**
  - User registration and login with JWT tokens
  - Role-based access control (Admin, Registered User, Anonymous)
  - Secure password management
  - Token refresh and blacklisting
  - User profile management
  
- **User Roles**
  - **Anonymous Users**: Can browse books (read-only access)
  - **Registered Users**: Can browse and borrow books
  - **Administrators**: Full access to manage books and users

### 🚧 Coming Soon
- Book catalog management (CRUD operations)
- Book search and filtering
- Loan management system (borrowing/returning books)
- Advanced admin panel for library operations
- Book availability tracking

## Tech Stack

- **Backend**: Django 6.0
- **API**: Django REST Framework 3.16
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL
- **Environment Management**: python-dotenv

## Prerequisites

- Python 3.10+
- PostgreSQL
- pip

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd LibraryMangement
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# Database Configuration
DB_NAME=library_db
DB_USER=library_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Setup PostgreSQL Database
```bash
# Login to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE library_db;
CREATE USER library_user WITH PASSWORD 'your_secure_password';
ALTER ROLE library_user SET client_encoding TO 'utf8';
ALTER ROLE library_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE library_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
\q
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an administrator account.

### 8. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout and blacklist token
- `POST /api/auth/token/refresh/` - Refresh access token

### User Management
- `GET /api/auth/me/` - Get current user info
- `GET /api/auth/profile/` - Get/Update own profile
- `POST /api/auth/change-password/` - Change password
- `GET /api/users/` - List users (role-based access)

For detailed API documentation, see [API_AUTHENTICATION.md](API_AUTHENTICATION.md)

## Quick Start - Testing Authentication

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### 3. Use Access Token
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer <your_access_token>"
```

## Project Structure

```
LibraryMangement/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings with JWT config
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py
├── core/                   # Main application
│   ├── models.py          # User model with roles
│   ├── serializers.py     # API serializers
│   ├── views.py           # API views
│   ├── permissions.py     # Custom permissions
│   ├── urls.py            # App URLs
│   └── admin.py           # Admin configuration
├── docker/                 # Docker configuration
├── .env                    # Environment variables (not in git)
├── .gitignore
├── requirements.txt        # Python dependencies
├── API_AUTHENTICATION.md   # Detailed API documentation
└── README.md              # This file
```

## User Roles & Permissions

### Anonymous Users
- Browse books (read-only)
- View book details
- Search for books

### Registered Users (USER)
- All anonymous user permissions
- Borrow books
- View borrowing history
- Manage own profile

### Administrators (ADMIN)
- All registered user permissions
- Add/remove books
- Manage all users
- View all loans
- Access admin panel

## Development

### Creating Migrations
```bash
python manage.py makemigrations
```

### Applying Migrations
```bash
python manage.py migrate
```

### Running Tests
```bash
python manage.py test
```

### Accessing Admin Panel
1. Create a superuser (if not already done)
2. Navigate to `http://localhost:8000/admin/`
3. Login with superuser credentials

## Security Features

- JWT token authentication
- Token rotation and blacklisting
- Password hashing with Django's built-in validators
- Role-based access control
- Secure environment variable management
- CSRF protection
- SQL injection protection (Django ORM)

## Environment Variables

Required environment variables in `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_NAME` | PostgreSQL database name | `library_db` |
| `DB_USER` | PostgreSQL username | `library_user` |
| `DB_PASSWORD` | PostgreSQL password | `your_password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `SECRET_KEY` | Django secret key | `random-secret-key` |
| `DEBUG` | Debug mode | `True` or `False` |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Roadmap

- [x] User authentication system
- [x] JWT token management
- [x] Role-based access control
- [ ] Book model and management
- [ ] Loan tracking system
- [ ] Advanced search and filtering
- [ ] Book availability management
- [ ] Email notifications
- [ ] API documentation with Swagger/OpenAPI
- [ ] Unit tests
- [ ] Docker deployment
- [ ] CI/CD pipeline

## License

This project is licensed under the MIT License.

## Support

For questions or support, please open an issue on the GitHub repository.

---

**Note**: This project is currently in development. The authentication system is complete, and book/loan management features are coming soon.