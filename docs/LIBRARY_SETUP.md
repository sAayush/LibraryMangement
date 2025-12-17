# Library System Setup Guide

## 🚀 Quick Setup

### 1. Run Migrations
```bash
# Create migration files for the new apps
python manage.py makemigrations library loan

# Apply all migrations
python manage.py migrate
```

Expected output:
```
Migrations for 'library':
  library\migrations\0001_initial.py
    - Create model Book
Migrations for 'loan':
  loan\migrations\0001_initial.py
    - Create model Loan

Running migrations:
  Applying library.0001_initial... OK
  Applying loan.0001_initial... OK
```

### 2. Create Admin User
```bash
python manage.py createsuperuser
```

Follow the prompts to create an administrator account.

### 3. Start the Server
```bash
python manage.py runserver
```

### 4. Access the Application
- **API Root**: http://localhost:8000/api/
- **Swagger Docs**: http://localhost:8000/swagger/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📚 Adding Sample Books

### Via Django Admin
1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Click on "Books"
4. Click "Add Book"
5. Fill in the details and save

### Via API (Admin Token Required)
```bash
# First, login as admin and get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Add a book
curl -X POST http://localhost:8000/api/books/create/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "publisher": "Prentice Hall",
    "published_date": "2008-08-01",
    "page_count": 464,
    "language": "English",
    "genre": "Programming",
    "description": "Even bad code can function. But if code isnt clean, it can bring a development organization to its knees.",
    "total_copies": 5,
    "available_copies": 5,
    "rating": 4.7
  }'
```

### Via Django Shell
```bash
python manage.py shell
```

```python
from library.models import Book
from core.models import User

# Get admin user
admin = User.objects.filter(is_superuser=True).first()

# Create some sample books
books = [
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "page_count": 464,
        "genre": "Programming",
        "total_copies": 5,
        "available_copies": 5,
        "added_by": admin
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt, David Thomas",
        "isbn": "9780135957059",
        "page_count": 352,
        "genre": "Programming",
        "total_copies": 3,
        "available_copies": 3,
        "added_by": admin
    },
    {
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "isbn": "9780201633610",
        "page_count": 395,
        "genre": "Programming",
        "total_copies": 4,
        "available_copies": 4,
        "added_by": admin
    }
]

for book_data in books:
    Book.objects.create(**book_data)

print("Sample books created successfully!")
```

---

## 🧪 Testing the System

### 1. Test Anonymous Access (Browse Books)
```bash
# No authentication required
curl http://localhost:8000/api/books/

# Search for books
curl "http://localhost:8000/api/books/?search=clean"

# Filter available books
curl "http://localhost:8000/api/books/?status=AVAILABLE"
```

### 2. Test User Registration and Borrowing
```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_reader",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Reader"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_reader", "password": "SecurePass123!"}'

# Borrow a book (use the access token from login)
curl -X POST http://localhost:8000/api/loans/borrow/ \
  -H "Authorization: Bearer <user_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "notes": "Looking forward to reading this!"}'

# Check my loans
curl http://localhost:8000/api/loans/my/ \
  -H "Authorization: Bearer <user_access_token>"
```

### 3. Test Loan Return
```bash
# Return a borrowed book
curl -X POST http://localhost:8000/api/loans/1/return/ \
  -H "Authorization: Bearer <user_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Great book, highly recommended!"}'
```

### 4. Test Loan Renewal
```bash
# Renew a loan (extends due date by 14 days)
curl -X POST http://localhost:8000/api/loans/1/renew/ \
  -H "Authorization: Bearer <user_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"days": 14}'
```

---

## 🔍 Common Queries

### Find Available Books
```bash
curl "http://localhost:8000/api/books/?status=AVAILABLE"
```

### Search by Genre
```bash
curl "http://localhost:8000/api/books/?genre__icontains=fiction"
```

### Find Books by Author
```bash
curl "http://localhost:8000/api/books/?author__icontains=martin"
```

### Get High-Rated Books
```bash
curl "http://localhost:8000/api/books/?rating__gte=4.5&ordering=-rating"
```

### Find Recently Added Books
```bash
curl "http://localhost:8000/api/books/?ordering=-created_at"
```

### Check Book Availability
```bash
curl "http://localhost:8000/api/books/1/availability/"
```

---

## 👨‍💼 Admin Operations

### View All Loans (Admin Only)
```bash
curl http://localhost:8000/api/loans/ \
  -H "Authorization: Bearer <admin_access_token>"
```

### View Overdue Loans (Admin Only)
```bash
curl http://localhost:8000/api/loans/overdue/ \
  -H "Authorization: Bearer <admin_access_token>"
```

### Update Book Details (Admin Only)
```bash
curl -X PATCH http://localhost:8000/api/books/1/update/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"available_copies": 3, "rating": 4.8}'
```

### Delete a Book (Admin Only)
```bash
curl -X DELETE http://localhost:8000/api/books/1/delete/ \
  -H "Authorization: Bearer <admin_access_token>"
```

---

## 🐛 Troubleshooting

### Issue: "Book not available for borrowing"
**Solution**: Check book availability:
```bash
curl "http://localhost:8000/api/books/1/availability/"
```

### Issue: "Maximum loan limit reached"
**Reason**: Users can have max 5 active loans
**Solution**: Return some books before borrowing new ones

### Issue: "Cannot renew loan"
**Possible Reasons**:
1. Loan is overdue
2. Maximum renewals (2) reached
3. Loan is not active

**Solution**: Check loan details:
```bash
curl http://localhost:8000/api/loans/1/ \
  -H "Authorization: Bearer <your_access_token>"
```

### Issue: "Already have active loan for this book"
**Reason**: Cannot borrow the same book twice simultaneously
**Solution**: Return the first loan before borrowing again

---

## 📊 Monitoring

### Check Overdue Loans
Admin can monitor overdue loans via:
- API: `/api/loans/overdue/`
- Admin Panel: Filter loans by status = "OVERDUE"

### View Borrowing Statistics
Currently available via Django admin:
1. Go to http://localhost:8000/admin/
2. Navigate to "Loans"
3. Use filters and date hierarchy

---

## 🔄 Updating the System

### Adding New Book Fields
1. Update `library/models.py`
2. Run migrations:
```bash
python manage.py makemigrations library
python manage.py migrate
```

### Changing Loan Rules
Update `loan/models.py`:
- Modify `due_date` calculation in `save()` method
- Adjust `max_renewals` default value
- Change `MAX_ACTIVE_LOANS` in loan creation validation

---

## 📝 Best Practices

### For Users
1. Return books on time to avoid overdue status
2. Renew loans before they're overdue
3. Check book availability before visiting library
4. Use search and filters to find books quickly

### For Admins
1. Regularly monitor overdue loans
2. Keep book information up to date
3. Update availability when receiving new copies
4. Use bulk actions in admin panel for efficiency

---

## 🆘 Getting Help

1. **Swagger Documentation**: http://localhost:8000/swagger/
2. **Admin Panel**: http://localhost:8000/admin/
3. **Django Shell**: `python manage.py shell`
4. **Check Logs**: Console output when running server

---

## ✅ Setup Verification Checklist

- [ ] Migrations applied successfully
- [ ] Superuser created
- [ ] Can access admin panel
- [ ] Can access Swagger UI
- [ ] Sample books added
- [ ] Can register new user
- [ ] Can login and get JWT tokens
- [ ] Can browse books anonymously
- [ ] User can borrow a book
- [ ] User can view their loans
- [ ] User can return a book
- [ ] User can renew a loan
- [ ] Admin can view all loans
- [ ] Admin can view overdue loans

---

**🎉 Your library system is ready to use!**

For more details, see:
- `README.md` - General overview
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `http://localhost:8000/swagger/` - Interactive API docs

