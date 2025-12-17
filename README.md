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
  
- **Book Catalog Management**
  - Complete CRUD operations for books
  - ISBN validation and uniqueness
  - Book availability tracking
  - Cover images and ratings
  - Status management (Available, Borrowed, Maintenance, Lost)
  
- **Advanced Search & Filtering**
  - Full-text search across title, author, ISBN, description
  - Filter by status, genre, language, author, publication date, rating
  - Sort by title, author, date, rating
  - Pagination (10 items per page)
  
- **Loan Management System**
  - Borrow books (14-day loan period)
  - Return books with automatic availability updates
  - Renew loans (up to 2 renewals)
  - Overdue tracking and management
  - Loan limit (max 5 active loans per user)
  
- **Security Features**
  - CSRF protection (built-in Django middleware)
  - XSS protection (Django template escaping)
  - SQL injection protection (Django ORM)
  - JWT token authentication
  - Permission-based access control
  
- **User Roles**
  - **Anonymous Users**: Browse and search books (read-only)
  - **Registered Users**: Browse, search, and borrow books
  - **Administrators**: Full access to manage books, users, and loans

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

The **Swagger documentation** will be available at `http://localhost:8000/swagger/`

## API Endpoints

### 🔐 Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout and blacklist token
- `POST /api/auth/token/refresh/` - Refresh access token

### 👤 User Management
- `GET /api/users/me/` - Get current user info
- `GET /api/users/profile/` - Get/Update own profile
- `GET /api/users/profile/{id}/` - Get/Update specific user (Admin)
- `POST /api/users/change-password/` - Change password
- `GET /api/users/` - List users (role-based access)

### 🔑 Admin Operations
- `POST /api/admin/create-admin/` - Create a new admin user (Admin only)
- `POST /api/admin/promote/` - Promote user to admin (Admin only)

### 📚 Book Management
- `GET /api/books/` - List all books (with filtering & search)
- `GET /api/books/{id}/` - Get book details
- `POST /api/books/create/` - Add new book (Admin only)
- `PUT /api/books/{id}/update/` - Update book (Admin only)
- `DELETE /api/books/{id}/delete/` - Delete book (Admin only)
- `GET /api/books/{id}/availability/` - Check book availability

### 📖 Loan Management
- `GET /api/loans/` - List loans (filtered by user role)
- `GET /api/loans/my/` - Get current user's loans
- `GET /api/loans/overdue/` - List overdue loans (Admin only)
- `GET /api/loans/{id}/` - Get loan details
- `POST /api/loans/borrow/` - Borrow a book
- `POST /api/loans/{id}/return/` - Return a borrowed book
- `POST /api/loans/{id}/renew/` - Renew a loan

### 📋 Interactive Documentation
- **Swagger UI**: `http://localhost:8000/swagger/` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc/` - Alternative documentation view
- **OpenAPI Schema**: `http://localhost:8000/swagger.json` - Raw OpenAPI spec

## Quick Start - Testing the Library System

### 1. Register & Login
```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'

# Login and get access token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### 2. Browse Books (No Authentication Required)
```bash
# List all books
curl http://localhost:8000/api/books/

# Search for books
curl "http://localhost:8000/api/books/?search=python"

# Filter available books
curl "http://localhost:8000/api/books/?status=AVAILABLE"

# Filter by genre
curl "http://localhost:8000/api/books/?genre__icontains=fiction"

# Get book details
curl http://localhost:8000/api/books/1/
```

### 3. Borrow a Book (Requires Authentication)
```bash
# Borrow book with ID 1
curl -X POST http://localhost:8000/api/loans/borrow/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "notes": "First book borrowed"}'

# View my loans
curl -X GET http://localhost:8000/api/loans/my/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 4. Manage Books (Admin Only)
```bash
# Add a new book (Admin only)
curl -X POST http://localhost:8000/api/books/create/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "page_count": 464,
    "genre": "Programming",
    "total_copies": 5,
    "available_copies": 5
  }'
```

### 5. Use Swagger UI (Recommended)
Visit `http://localhost:8000/swagger/` for interactive API documentation and testing!

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
- [x] Book model and management
- [x] Loan tracking system
- [x] Advanced search and filtering
- [x] Book availability management
- [x] API documentation with Swagger/OpenAPI
- [x] Security implementation (CSRF, XSS, SQL Injection protection)
- [ ] Email notifications for overdue books
- [ ] Book reservations
- [ ] Fine calculation for overdue returns
- [ ] Unit and integration tests
- [ ] Book cover image upload
- [ ] Export reports (PDF/Excel)
- [ ] Docker deployment
- [ ] CI/CD pipeline

## License

This project is licensed under the MIT License.

## Support

For questions or support, please open an issue on the GitHub repository.

---

**Note**: This project is currently in development. The authentication system is complete, and book/loan management features are coming soon.