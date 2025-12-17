# Library Management System - Setup Guide

This guide will walk you through setting up the Library Management System from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Step-by-Step Setup

### Step 1: Project Setup

1. **Clone or navigate to the project directory**
```bash
cd E:\LibraryMangement
```

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the virtual environment**
- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Step 2: PostgreSQL Database Setup

1. **Start PostgreSQL** and connect to it:
```bash
psql -U postgres
```

2. **Create the database and user**:
```sql
-- Create database
CREATE DATABASE library_db;

-- Create user
CREATE USER library_user WITH PASSWORD 'your_secure_password';

-- Grant encoding and timezone settings
ALTER ROLE library_user SET client_encoding TO 'utf8';
ALTER ROLE library_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE library_user SET timezone TO 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;

-- For PostgreSQL 15+, you may also need:
\c library_db
GRANT ALL ON SCHEMA public TO library_user;

-- Exit psql
\q
```

### Step 3: Environment Variables Configuration

1. **Create a .env file** in the project root directory (E:\LibraryMangement\.env)

2. **Add the following content** (replace values with your actual credentials):

```env
# Database Configuration
DB_NAME=library_db
DB_USER=library_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=django-insecure-%dv42pza#j!90z+!lc!_097)=b+5qyey_+pa9c#(kv9m+-lo=)
DEBUG=True
```

**Important Notes:**
- Replace `your_secure_password` with the password you set for the PostgreSQL user
- For production, generate a new SECRET_KEY using:
  ```python
  from django.core.management.utils import get_random_secret_key
  print(get_random_secret_key())
  ```
- Never commit the .env file to version control (it's already in .gitignore)

### Step 4: Database Migrations

1. **Create migrations for all apps**:
```bash
python manage.py makemigrations
```

Expected output:
```
Migrations for 'core':
  core\migrations\0001_initial.py
    - Create model User
```

2. **Apply migrations**:
```bash
python manage.py migrate
```

This will create all necessary database tables including:
- User tables
- JWT token blacklist tables
- Django admin tables
- Session tables

### Step 5: Create Admin User

Create a superuser account to access the admin panel:

```bash
python manage.py createsuperuser
```

You'll be prompted for:
- Username: `admin` (or your choice)
- Email: `admin@example.com` (or your email)
- Password: (enter a secure password)
- Password confirmation: (re-enter the password)

**Note:** The superuser will have ADMIN role automatically in the system.

### Step 6: Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The server will start at: `http://127.0.0.1:8000/`

You should see:
```
Django version 6.0, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## Verification Steps

### 1. Test the Admin Panel

1. Open your browser and navigate to: `http://localhost:8000/admin/`
2. Login with the superuser credentials you created
3. You should see the Django administration interface with Users listed

### 2. Test User Registration API

Open a new terminal (keep the server running) and test the registration endpoint:

```bash
curl -X POST http://localhost:8000/api/auth/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser\", \"email\": \"test@example.com\", \"password\": \"TestPass123!\", \"password2\": \"TestPass123!\"}"
```

**Expected Response:**
```json
{
    "user": {
        "id": 2,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "",
        "last_name": "",
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

### 3. Test User Login API

```bash
curl -X POST http://localhost:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"testuser\", \"password\": \"TestPass123!\"}"
```

### 4. Test Authenticated Endpoint

Copy the access token from the login response and use it:

```bash
curl -X GET http://localhost:8000/api/auth/me/ ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Common Issues and Solutions

### Issue 1: Database Connection Error
**Error:** `django.db.utils.OperationalError: FATAL: database "library_db" does not exist`

**Solution:**
- Ensure PostgreSQL is running
- Verify database credentials in .env file
- Check if the database was created successfully:
  ```bash
  psql -U postgres -c "\l"
  ```

### Issue 2: Import Error for psycopg2
**Error:** `Error loading psycopg2 module`

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue 3: Migration Error
**Error:** `No changes detected`

**Solution:**
- Ensure all models are properly defined in core/models.py
- Try running: `python manage.py makemigrations core`

### Issue 4: JWT Token Error
**Error:** `Token is invalid or expired`

**Solution:**
- Access tokens expire after 1 hour
- Use the refresh token to get a new access token:
  ```bash
  curl -X POST http://localhost:8000/api/auth/token/refresh/ ^
    -H "Content-Type: application/json" ^
    -d "{\"refresh\": \"YOUR_REFRESH_TOKEN\"}"
  ```

### Issue 5: Permission Denied for Schema
**Error:** `permission denied for schema public`

**Solution (PostgreSQL 15+):**
```sql
-- Connect to the database
\c library_db

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO library_user;
GRANT CREATE ON SCHEMA public TO library_user;
```

## Project Structure Overview

```
LibraryMangement/
├── config/                      # Project settings
│   ├── settings.py             # Main Django settings (✓ Configured)
│   ├── urls.py                 # Root URL configuration (✓ Configured)
│   ├── wsgi.py                 # WSGI config
│   └── asgi.py                 # ASGI config
│
├── core/                        # Main application
│   ├── models.py               # User model (✓ Created)
│   ├── serializers.py          # API serializers (✓ Created)
│   ├── views.py                # API views (✓ Created)
│   ├── permissions.py          # Custom permissions (✓ Created)
│   ├── urls.py                 # App URLs (✓ Created)
│   ├── admin.py                # Admin configuration (✓ Configured)
│   ├── apps.py                 # App configuration
│   └── migrations/             # Database migrations
│
├── .env                         # Environment variables (You need to create)
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies (✓ Available)
├── manage.py                   # Django management script
├── README.md                   # Project overview
├── API_AUTHENTICATION.md       # API documentation
└── SETUP_GUIDE.md             # This file
```

## What's Next?

Now that your authentication system is set up, you can:

1. **Test all authentication endpoints** using the API documentation
2. **Create additional users** through the API or admin panel
3. **Explore the admin panel** to manage users
4. **Start building the Book model** for the library catalog
5. **Implement the Loan model** for tracking borrowed books

## Additional Commands

### Create Test Data
```bash
python manage.py shell
```

Then in the Python shell:
```python
from core.models import User

# Create a test admin user
admin = User.objects.create_user(
    username='admin2',
    email='admin2@example.com',
    password='AdminPass123!',
    role=User.UserRole.ADMIN
)

# Create a test regular user
user = User.objects.create_user(
    username='user2',
    email='user2@example.com',
    password='UserPass123!',
    role=User.UserRole.USER
)

exit()
```

### Reset Database (Careful!)
```bash
# Delete migrations
# Windows
del /s /q core\migrations\0*.py

# Mac/Linux
# rm core/migrations/0*.py

# Drop and recreate database
psql -U postgres -c "DROP DATABASE library_db;"
psql -U postgres -c "CREATE DATABASE library_db;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;"

# Run migrations again
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Backup Database
```bash
pg_dump -U library_user -h localhost library_db > backup.sql
```

### Restore Database
```bash
psql -U library_user -h localhost library_db < backup.sql
```

## API Testing Tools

### Option 1: cURL (Command Line)
Already shown in examples above.

### Option 2: Postman
1. Download and install Postman
2. Create a new collection "Library Management"
3. Add requests for each endpoint
4. Use environment variables for tokens

### Option 3: HTTPie (More user-friendly CLI)
Install:
```bash
pip install httpie
```

Usage:
```bash
# Register
http POST http://localhost:8000/api/auth/register/ \
  username=testuser email=test@example.com \
  password=TestPass123! password2=TestPass123!

# Login
http POST http://localhost:8000/api/auth/login/ \
  username=testuser password=TestPass123!

# Get current user (with token)
http GET http://localhost:8000/api/auth/me/ \
  "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Option 4: Django REST Framework Browsable API
Simply visit the API endpoints in your browser:
- http://localhost:8000/api/auth/register/
- http://localhost:8000/api/auth/login/
- http://localhost:8000/api/users/

## Development Tips

1. **Keep the server running** in one terminal
2. **Use another terminal** for running commands
3. **Check logs** in the server terminal for debugging
4. **Use the browsable API** for quick testing
5. **Keep .env file secure** and never commit it

## Getting Help

- Check `API_AUTHENTICATION.md` for detailed API documentation
- Review `README.md` for project overview
- Check Django documentation: https://docs.djangoproject.com/
- Check DRF documentation: https://www.django-rest-framework.org/

## Success Checklist

- [ ] PostgreSQL installed and running
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] .env file created with correct credentials
- [ ] Database created in PostgreSQL
- [ ] Migrations created and applied
- [ ] Superuser created
- [ ] Development server running successfully
- [ ] Registration API tested successfully
- [ ] Login API tested successfully
- [ ] JWT tokens working correctly
- [ ] Admin panel accessible

Once all items are checked, you're ready to start using the system! 🎉

---

**Last Updated:** December 17, 2024

