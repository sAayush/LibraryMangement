# 🚀 Deployment Guide - Library Management System

This guide covers deploying the Library Management System to various platforms including Docker, Heroku, and manual server deployment.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Heroku Deployment](#heroku-deployment)
6. [Production Server Deployment](#production-server-deployment)
7. [Post-Deployment Tasks](#post-deployment-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.13+
- PostgreSQL 15+
- Docker & Docker Compose (for containerized deployment)
- Git
- Heroku CLI (for Heroku deployment)

### Required Accounts
- Heroku account (for Heroku deployment)
- PostgreSQL database (local or cloud-hosted)

---

## Environment Configuration

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
# Security
SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DB_NAME=library_db
DB_USER=library_user
DB_PASSWORD=your-secure-password-here
DB_HOST=localhost
DB_PORT=5432

# Optional: CORS Configuration
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
DJANGO_LOG_LEVEL=INFO
```

### 2. Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Local Development

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb library_db

# Or using psql
psql -U postgres
CREATE DATABASE library_db;
CREATE USER library_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
\q
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit:
- **Dashboard**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/swagger/
- **Admin Panel**: http://localhost:8000/admin/

---

## Docker Deployment

### 1. Build and Run with Docker Compose

```bash
# Navigate to docker directory
cd docker

# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Access the Application

- **Application**: http://localhost
- **API**: http://localhost/api/
- **Admin**: http://localhost/admin/

### 3. Run Management Commands in Docker

```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Run tests
docker-compose exec web python manage.py test
```

### 4. Docker Environment Variables

The `docker-compose.yml` file is pre-configured with environment variables. Update them as needed:

```yaml
environment:
  - SECRET_KEY=your-secret-key
  - DEBUG=False
  - DB_HOST=db
  - DB_PORT=5432
  - DB_NAME=library_db
  - DB_USER=library_user
  - DB_PASSWORD=library_password
```

### 5. Production Docker Build

For production, use the optimized Dockerfile:

```bash
# Build production image
docker build -f docker/Dockerfile -t library-management:latest .

# Run production container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name library-app \
  library-management:latest
```

---

## Heroku Deployment

### 1. Install Heroku CLI

```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
# Or use package manager:
# Windows (Chocolatey)
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku

# Linux (Ubuntu/Debian)
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Login to Heroku

```bash
heroku login
```

### 3. Create Heroku App

```bash
# Create new app
heroku create your-app-name

# Or use existing app
heroku git:remote -a your-app-name
```

### 4. Add PostgreSQL Database

```bash
# Add Heroku Postgres addon
heroku addons:create heroku-postgresql:essential-0

# Check database credentials
heroku config:get DATABASE_URL
```

### 5. Set Environment Variables

```bash
# Set secret key
heroku config:set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Set debug mode
heroku config:set DEBUG=False

# Set allowed hosts
heroku config:set ALLOWED_HOSTS=.herokuapp.com

# View all config
heroku config
```

### 6. Deploy to Heroku

```bash
# Add all files
git add .

# Commit changes
git commit -m "Ready for Heroku deployment"

# Push to Heroku
git push heroku main

# Or if using master branch
git push heroku master
```

### 7. Run Migrations on Heroku

```bash
# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Collect static files (done automatically via Procfile)
heroku run python manage.py collectstatic --noinput
```

### 8. Open Application

```bash
heroku open
```

### 9. View Logs

```bash
# View live logs
heroku logs --tail

# View recent logs
heroku logs --num=100
```

### 10. Scale Dynos

```bash
# Check current dynos
heroku ps

# Scale web dynos
heroku ps:scale web=1

# For production, upgrade to better dynos
heroku ps:type web=standard-1x
```

---

## Production Server Deployment

### Manual Deployment on Linux Server (Ubuntu/Debian)

#### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Install Dependencies

```bash
# Install Python, PostgreSQL, and Nginx
sudo apt install -y python3.13 python3.13-venv python3-pip postgresql postgresql-contrib nginx git

# Install system dependencies
sudo apt install -y libpq-dev python3-dev build-essential
```

#### 3. Setup PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE library_db;
CREATE USER library_user WITH PASSWORD 'your_secure_password';
ALTER ROLE library_user SET client_encoding TO 'utf8';
ALTER ROLE library_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE library_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
\q
```

#### 4. Clone and Setup Project

```bash
# Create project directory
sudo mkdir -p /var/www/library
sudo chown $USER:$USER /var/www/library
cd /var/www/library

# Clone repository
git clone https://github.com/yourusername/library-management.git .

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 5. Configure Environment

```bash
# Create .env file
nano .env

# Add your environment variables (see Environment Configuration section)
```

#### 6. Run Django Setup

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 7. Setup Gunicorn

```bash
# Test Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Create Gunicorn systemd service
sudo nano /etc/systemd/system/library.service
```

Add the following content:

```ini
[Unit]
Description=Library Management System Gunicorn daemon
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/var/www/library
ExecStart=/var/www/library/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/library/library.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable service
sudo systemctl start library
sudo systemctl enable library
sudo systemctl status library
```

#### 8. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/library
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/library/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/library/mediafiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/library/library.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/library /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### 9. Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

---

## Post-Deployment Tasks

### 1. Create Admin User

```bash
python manage.py createsuperuser
```

### 2. Test API Endpoints

Visit `/swagger/` to test all API endpoints.

### 3. Configure CORS (if needed for frontend)

Update `.env`:
```
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### 4. Setup Monitoring

Consider setting up monitoring tools:
- **Sentry** for error tracking
- **New Relic** for performance monitoring
- **Datadog** for infrastructure monitoring

### 5. Setup Backups

```bash
# Backup PostgreSQL database
pg_dump -U library_user library_db > backup_$(date +%Y%m%d).sql

# Restore database
psql -U library_user library_db < backup_20231218.sql

# Automate backups with cron
crontab -e
# Add: 0 2 * * * pg_dump -U library_user library_db > /backups/library_$(date +\%Y\%m\%d).sql
```

### 6. Performance Optimization

```bash
# Enable database connection pooling in settings.py
# Configure caching (Redis or Memcached)
# Setup CDN for static files
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error**: `could not connect to server: Connection refused`

**Solution**:
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database credentials in `.env`
- Check `pg_hba.conf` for connection permissions

#### 2. Static Files Not Loading

**Solution**:
```bash
python manage.py collectstatic --noinput
# Check STATIC_ROOT and STATIC_URL in settings.py
# Verify Nginx configuration for /static/ location
```

#### 3. Permission Denied Errors

**Solution**:
```bash
# Fix permissions
sudo chown -R $USER:www-data /var/www/library
sudo chmod -R 755 /var/www/library
```

#### 4. Gunicorn Not Starting

**Solution**:
```bash
# Check service logs
sudo journalctl -u library -f

# Test Gunicorn manually
cd /var/www/library
source venv/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

#### 5. 502 Bad Gateway (Nginx)

**Solution**:
- Check if Gunicorn is running: `sudo systemctl status library`
- Verify socket file exists: `ls -la /var/www/library/library.sock`
- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

#### 6. Environment Variables Not Loading

**Solution**:
- Ensure `.env` file exists in project root
- Check file permissions: `chmod 600 .env`
- Verify `python-dotenv` is installed
- Restart application after changes

---

## Security Checklist

Before going to production:

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable HTTPS/SSL
- [ ] Setup database backups
- [ ] Configure firewall rules
- [ ] Use environment variables for sensitive data
- [ ] Enable CSRF protection (enabled by default)
- [ ] Setup rate limiting
- [ ] Regular security updates
- [ ] Monitor application logs
- [ ] Setup error tracking (Sentry)

---

## Maintenance Commands

```bash
# Update code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run new migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart library

# View logs
sudo journalctl -u library -f

# Run tests
python manage.py test
```

---

## Support

For issues and questions:
- **Documentation**: https://github.com/yourusername/library-management/wiki
- **Issues**: https://github.com/yourusername/library-management/issues
- **Email**: support@yourlibrary.com

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

