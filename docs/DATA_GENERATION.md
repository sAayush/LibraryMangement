# 🎲 Fake Data Generation Guide

This guide explains how to generate realistic fake data for testing and demonstration purposes.

## 📋 Prerequisites

Install Faker:
```bash
pip install Faker
```

---

## 🚀 Quick Start

### Generate Everything at Once

```bash
# Generate default data (50 books, 20 users, 2 admins)
python manage.py seed_database

# Custom amounts
python manage.py seed_database --books 100 --users 50 --admins 5

# Clear existing data and reseed
python manage.py seed_database --clear
```

---

## 📚 Generate Books Only

### Basic Usage

```bash
# Generate 50 books (default)
python manage.py generate_books

# Generate specific number
python manage.py generate_books --count 100
```

### Advanced Options

```bash
# Clear existing books and generate new ones
python manage.py generate_books --count 50 --clear

# Assign books to specific admin
python manage.py generate_books --count 50 --admin-username admin
```

### Generated Book Data

Each book includes:
- ✅ **Title**: Realistic business/tech phrases
- ✅ **Author**: Random names
- ✅ **ISBN**: Unique 13-digit numbers
- ✅ **Publisher**: Major publishing houses
- ✅ **Genre**: 30+ genres (Fiction, Sci-Fi, Business, etc.)
- ✅ **Language**: Multiple languages (mostly English)
- ✅ **Description**: Random paragraphs
- ✅ **Page Count**: 100-800 pages
- ✅ **Publication Date**: Last 50 years
- ✅ **Copies**: 1-10 copies per book
- ✅ **Status**: Available, Borrowed, Maintenance, or Lost
- ✅ **Rating**: 2.5-5.0 stars (70% of books)
- ✅ **Cover Image**: Placeholder images

---

## 👥 Generate Users Only

### Basic Usage

```bash
# Generate 20 users and 2 admins (default)
python manage.py generate_users

# Generate specific numbers
python manage.py generate_users --count 50 --admins 5
```

### Advanced Options

```bash
# Clear existing users (keeps superusers)
python manage.py generate_users --count 30 --clear
```

### Generated User Data

Each user includes:
- ✅ **Username**: Unique usernames
- ✅ **Email**: Unique email addresses
- ✅ **Name**: First and last names
- ✅ **Role**: USER or ADMIN
- ✅ **Password**: 
  - Admins: `admin123`
  - Users: `user123`

---

## 📖 Example Workflows

### 1. Fresh Start

```bash
# Clear everything and start fresh
python manage.py seed_database --clear --books 100 --users 50 --admins 5
```

### 2. Add More Books

```bash
# Add 50 more books without clearing
python manage.py generate_books --count 50
```

### 3. Add More Users

```bash
# Add 20 more users and 3 more admins
python manage.py generate_users --count 20 --admins 3
```

### 4. Testing Scenario

```bash
# Small dataset for quick testing
python manage.py seed_database --books 20 --users 10 --admins 1
```

### 5. Demo Scenario

```bash
# Large dataset for impressive demos
python manage.py seed_database --books 200 --users 100 --admins 10
```

---

## 🔍 Verify Generated Data

### Check Database

```bash
# Django shell
python manage.py shell

# Run these commands:
from library.models import Book
from core.models import User

print(f"Total books: {Book.objects.count()}")
print(f"Available books: {Book.objects.filter(status='AVAILABLE').count()}")
print(f"Total users: {User.objects.count()}")
print(f"Admins: {User.objects.filter(role='ADMIN').count()}")
```

### Via API

Visit http://localhost:8000/swagger/ and test these endpoints:
- `GET /api/books/` - List all books
- `GET /api/users/` - List users (requires admin)

### Via Dashboard

Visit http://localhost:8000/ to see:
- Overview statistics
- Book catalog
- User information (if logged in)

---

## 🎨 Customization

### Modify Book Data

Edit `library/management/commands/generate_books.py`:

```python
# Change genres
genres = ['Your', 'Custom', 'Genres']

# Change publishers
publishers = ['Your', 'Publishers']

# Adjust page count range
page_count = random.randint(50, 1000)  # Your custom range

# Adjust rating distribution
rating = round(random.uniform(1.0, 5.0), 2)  # Your custom range
```

### Modify User Data

Edit `library/management/commands/generate_users.py`:

```python
# Change default passwords
password='your_password'

# Change role distribution
role='ADMIN' if random.random() > 0.9 else 'USER'  # 10% admins
```

---

## 📊 Statistics After Seeding

After running `seed_database`, you'll see:

```
==============================================================
  📊 FINAL DATABASE STATISTICS
==============================================================

👥 Users:
  Total: 23
  Superusers: 1
  Admins: 2
  Regular: 20

📚 Books:
  Total: 50
  Available: 45
  Borrowed: 5

🔑 Access Information:
  Dashboard: http://localhost:8000/
  Admin Panel: http://localhost:8000/admin/
  API Docs: http://localhost:8000/swagger/

🔐 Demo Credentials:
  Admins: username: (any admin) | password: admin123
  Users: username: (any user) | password: user123

==============================================================
  ✅ DATABASE SEEDING COMPLETED SUCCESSFULLY
==============================================================
```

---

## 🛠️ Troubleshooting

### Issue: Command not found

**Solution**: Make sure Django can find the management commands:
```bash
# Check if files exist
ls library/management/commands/

# Should show:
# __init__.py
# generate_books.py
# generate_users.py
# seed_database.py
```

### Issue: Faker not installed

**Solution**:
```bash
pip install Faker
```

### Issue: Duplicate ISBN errors

**Solution**: The command automatically handles duplicates. If you still see errors, clear existing books:
```bash
python manage.py generate_books --clear --count 50
```

### Issue: Permission errors

**Solution**: Make sure you have database write permissions and migrations are up to date:
```bash
python manage.py migrate
```

---

## 🎯 Best Practices

1. **Start Small**: Test with a small dataset first
   ```bash
   python manage.py seed_database --books 10 --users 5
   ```

2. **Use Clear Flag Carefully**: `--clear` deletes existing data
   ```bash
   # Be cautious with this!
   python manage.py seed_database --clear
   ```

3. **Backup First**: Before clearing data in production:
   ```bash
   python manage.py dumpdata > backup.json
   ```

4. **Performance**: Generating large datasets takes time:
   - 50 books: ~5 seconds
   - 500 books: ~30 seconds
   - 1000 books: ~1 minute

5. **Demo Accounts**: Remember the default passwords:
   - Admins: `admin123`
   - Users: `user123`

---

## 📝 Examples

### Example 1: Quick Demo Setup

```bash
# Create a superuser first
python manage.py createsuperuser

# Seed with demo data
python manage.py seed_database --books 50 --users 20

# Login with any generated user:
# Username: (check /admin/ to see usernames)
# Password: user123 (for regular users) or admin123 (for admins)
```

### Example 2: Testing Environment

```bash
# Small dataset for unit tests
python manage.py seed_database --clear --books 20 --users 10 --admins 2

# Run your tests
python manage.py test
```

### Example 3: Load Testing

```bash
# Large dataset for performance testing
python manage.py seed_database --clear --books 1000 --users 200 --admins 10
```

---

## 🔄 Reset Database

To completely reset and reseed:

```bash
# Method 1: Using --clear flag
python manage.py seed_database --clear --books 50 --users 20

# Method 2: Drop and recreate database
python manage.py flush  # Warning: Deletes ALL data
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_database
```

---

## 📞 Need Help?

- Check command help: `python manage.py generate_books --help`
- View all management commands: `python manage.py help`
- Report issues: Open an issue on GitHub

---

## 🎉 Have Fun!

These commands make it easy to:
- ✅ Demo your library system
- ✅ Test with realistic data
- ✅ Develop without manual data entry
- ✅ Impress stakeholders with populated databases
- ✅ Train users with sample data

Happy data generation! 🚀

