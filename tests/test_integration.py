"""
Integration tests for the Library Management System.
Tests complete user workflows from start to finish.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from library.models import Book
from loan.models import Loan

User = get_user_model()


class LibraryWorkflowIntegrationTest(APITestCase):
    """
    Integration tests for complete library workflows
    """
    
    def setUp(self):
        self.client = APIClient()
    
    def test_complete_user_registration_and_borrowing_workflow(self):
        """
        Test complete workflow: Register -> Login -> Browse Books -> Borrow -> Return
        """
        # Step 1: Register a new user
        register_data = {
            'username': 'newreader',
            'email': 'reader@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        register_response = self.client.post('/api/auth/register/', register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', register_response.data)
        
        access_token = register_response.data['tokens']['access']
        
        # Step 2: Create admin and add a book
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        book = Book.objects.create(
            title='Clean Code',
            author='Robert C. Martin',
            isbn='9780132350884',
            page_count=464,
            genre='Programming',
            total_copies=5,
            available_copies=5,
            added_by=admin
        )
        
        # Step 3: Browse books (as anonymous)
        self.client.credentials()  # Remove authentication
        browse_response = self.client.get('/api/books/')
        self.assertEqual(browse_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(browse_response.data['results']), 1)
        
        # Step 4: Search for a book
        search_response = self.client.get('/api/books/?search=Clean')
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(search_response.data['results']), 0)
        
        # Step 5: Check book availability
        availability_response = self.client.get(f'/api/books/{book.id}/availability/')
        self.assertEqual(availability_response.status_code, status.HTTP_200_OK)
        self.assertTrue(availability_response.data['is_available'])
        
        # Step 6: Borrow the book (requires authentication)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        borrow_data = {'book_id': book.id, 'notes': 'Excited to read this!'}
        borrow_response = self.client.post('/api/loans/borrow/', borrow_data)
        self.assertEqual(borrow_response.status_code, status.HTTP_201_CREATED)
        loan_id = borrow_response.data['id']
        
        # Step 7: Verify book availability decreased
        book.refresh_from_db()
        self.assertEqual(book.available_copies, 4)
        
        # Step 8: View my loans
        my_loans_response = self.client.get('/api/loans/my/')
        self.assertEqual(my_loans_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(my_loans_response.data['results']), 1)
        
        # Step 9: Renew the loan
        renew_response = self.client.post(f'/api/loans/{loan_id}/renew/', {'days': 14})
        self.assertEqual(renew_response.status_code, status.HTTP_200_OK)
        self.assertEqual(renew_response.data['loan']['renewed_count'], 1)
        
        # Step 10: Return the book
        return_response = self.client.post(
            f'/api/loans/{loan_id}/return/',
            {'notes': 'Great book!'}
        )
        self.assertEqual(return_response.status_code, status.HTTP_200_OK)
        
        # Step 11: Verify book availability increased
        book.refresh_from_db()
        self.assertEqual(book.available_copies, 5)
        self.assertEqual(book.status, Book.BookStatus.AVAILABLE)
        
        # Step 12: Verify loan is marked as returned
        loan = Loan.objects.get(id=loan_id)
        self.assertEqual(loan.status, Loan.LoanStatus.RETURNED)
        self.assertIsNotNone(loan.returned_date)
    
    def test_complete_admin_workflow(self):
        """
        Test complete admin workflow: Create Admin -> Add Books -> Manage Loans
        """
        # Step 1: Create super admin
        super_admin = User.objects.create_superuser(
            username='superadmin',
            email='super@example.com',
            password='SuperPass123!'
        )
        super_admin.role = User.UserRole.ADMIN
        super_admin.save()
        
        # Step 2: Login as admin
        login_response = self.client.post('/api/auth/login/', {
            'username': 'superadmin',
            'password': 'SuperPass123!'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        admin_token = login_response.data['tokens']['access']
        
        # Step 3: Create a new admin user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        new_admin_data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'AdminPass123!',
            'password2': 'AdminPass123!'
        }
        create_admin_response = self.client.post('/api/admin/create-admin/', new_admin_data)
        self.assertEqual(create_admin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_admin_response.data['user']['role'], 'ADMIN')
        
        # Step 4: Add books to the library
        books_to_add = [
            {
                'title': 'Clean Code',
                'author': 'Robert C. Martin',
                'isbn': '9780132350884',
                'page_count': 464,
                'genre': 'Programming',
                'total_copies': 5,
                'available_copies': 5
            },
            {
                'title': 'The Pragmatic Programmer',
                'author': 'Andrew Hunt',
                'isbn': '9780135957059',
                'page_count': 352,
                'genre': 'Programming',
                'total_copies': 3,
                'available_copies': 3
            }
        ]
        
        for book_data in books_to_add:
            response = self.client.post('/api/books/create/', book_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 5: Create a regular user and have them borrow a book
        user = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='UserPass123!'
        )
        book = Book.objects.get(isbn='9780132350884')
        loan = Loan.objects.create(user=user, book=book)
        book.borrow()
        
        # Step 6: Admin views all loans
        all_loans_response = self.client.get('/api/loans/')
        self.assertEqual(all_loans_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(all_loans_response.data['results']), 1)
        
        # Step 7: Update book information
        update_response = self.client.patch(
            f'/api/books/{book.id}/update/',
            {'rating': 4.8, 'description': 'A must-read for programmers'}
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(update_response.data['rating']), 4.8)
    
    def test_anonymous_to_authenticated_workflow(self):
        """
        Test workflow where anonymous user browses, then registers to borrow
        """
        # Step 1: Create admin and book
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        book = Book.objects.create(
            title='Design Patterns',
            author='Erich Gamma',
            isbn='9780201633610',
            page_count=395,
            genre='Programming',
            total_copies=4,
            available_copies=4,
            added_by=admin
        )
        
        # Step 2: Browse as anonymous user
        browse_response = self.client.get('/api/books/')
        self.assertEqual(browse_response.status_code, status.HTTP_200_OK)
        
        # Step 3: Try to borrow without authentication (should fail)
        borrow_response = self.client.post('/api/loans/borrow/', {'book_id': book.id})
        self.assertEqual(borrow_response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Step 4: Register
        register_response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'UserPass123!',
            'password2': 'UserPass123!'
        })
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        token = register_response.data['tokens']['access']
        
        # Step 5: Now borrow with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        borrow_response = self.client.post('/api/loans/borrow/', {'book_id': book.id})
        self.assertEqual(borrow_response.status_code, status.HTTP_201_CREATED)
    
    def test_multiple_users_borrowing_same_book(self):
        """
        Test multiple users borrowing copies of the same book
        """
        # Setup: Create admin and book with multiple copies
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        book = Book.objects.create(
            title='Popular Book',
            author='Famous Author',
            isbn='9780123456789',
            page_count=400,
            genre='Fiction',
            total_copies=3,
            available_copies=3,
            added_by=admin
        )
        
        # Create 3 users
        users = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='UserPass123!'
            )
            users.append(user)
        
        # Each user borrows the book
        for i, user in enumerate(users):
            login_response = self.client.post('/api/auth/login/', {
                'username': f'user{i}',
                'password': 'UserPass123!'
            })
            token = login_response.data['tokens']['access']
            
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            borrow_response = self.client.post('/api/loans/borrow/', {'book_id': book.id})
            self.assertEqual(borrow_response.status_code, status.HTTP_201_CREATED)
        
        # Verify book status
        book.refresh_from_db()
        self.assertEqual(book.available_copies, 0)
        self.assertEqual(book.status, Book.BookStatus.BORROWED)
        
        # 4th user tries to borrow (should fail)
        user4 = User.objects.create_user(
            username='user4',
            email='user4@example.com',
            password='UserPass123!'
        )
        login_response = self.client.post('/api/auth/login/', {
            'username': 'user4',
            'password': 'UserPass123!'
        })
        token = login_response.data['tokens']['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        borrow_response = self.client.post('/api/loans/borrow/', {'book_id': book.id})
        self.assertEqual(borrow_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # First user returns the book
        loan = Loan.objects.filter(user=users[0], book=book).first()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')  # Use any authenticated user
        login_response = self.client.post('/api/auth/login/', {
            'username': 'user0',
            'password': 'UserPass123!'
        })
        user0_token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user0_token}')
        
        return_response = self.client.post(f'/api/loans/{loan.id}/return/', {})
        self.assertEqual(return_response.status_code, status.HTTP_200_OK)
        
        # Now book should be available again
        book.refresh_from_db()
        self.assertEqual(book.available_copies, 1)
        self.assertEqual(book.status, Book.BookStatus.AVAILABLE)
    
    def test_security_unauthorized_access_attempts(self):
        """
        Test that unauthorized users cannot access protected endpoints
        """
        # Create admin and regular user
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='UserPass123!'
        )
        
        # Get user token
        login_response = self.client.post('/api/auth/login/', {
            'username': 'user',
            'password': 'UserPass123!'
        })
        user_token = login_response.data['tokens']['access']
        
        # Test 1: Regular user tries to create a book
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        create_book_response = self.client.post('/api/books/create/', {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '9780123456789',
            'page_count': 300,
            'genre': 'Test',
            'total_copies': 1,
            'available_copies': 1
        })
        self.assertEqual(create_book_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test 2: Regular user tries to create an admin
        create_admin_response = self.client.post('/api/admin/create-admin/', {
            'username': 'badactor',
            'email': 'badactor@example.com',
            'password': 'BadPass123!',
            'password2': 'BadPass123!'
        })
        self.assertEqual(create_admin_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test 3: Regular user tries to view overdue loans
        overdue_response = self.client.get('/api/loans/overdue/')
        self.assertEqual(overdue_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test 4: Unauthenticated user tries to borrow
        self.client.credentials()  # Remove authentication
        book = Book.objects.create(
            title='Test Book',
            author='Author',
            isbn='9780987654321',
            page_count=300,
            genre='Test',
            total_copies=1,
            available_copies=1,
            added_by=admin
        )
        borrow_response = self.client.post('/api/loans/borrow/', {'book_id': book.id})
        self.assertEqual(borrow_response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIPerformanceTest(APITestCase):
    """
    Test API performance with pagination and filtering
    """
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        
        # Create 25 books for pagination testing
        for i in range(25):
            Book.objects.create(
                title=f'Book {i}',
                author=f'Author {i % 5}',  # 5 different authors
                isbn=f'978012345{i:04d}',
                page_count=300 + i,
                genre='Fiction' if i % 2 == 0 else 'Non-Fiction',
                total_copies=1 + (i % 3),
                available_copies=1 + (i % 3),
                added_by=self.admin
            )
    
    def test_pagination(self):
        """Test that pagination works correctly"""
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Default page size
        self.assertIn('next', response.data)
        self.assertIsNotNone(response.data['next'])
    
    def test_filtering_performance(self):
        """Test that filtering returns correct results"""
        # Filter by genre
        response = self.client.get('/api/books/?genre=Fiction')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data['results']:
            self.assertEqual(book['genre'], 'Fiction')
        
        # Filter by status
        response = self.client.get('/api/books/?status=AVAILABLE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data['results']:
            self.assertEqual(book['status'], 'AVAILABLE')
    
    def test_search_functionality(self):
        """Test that search works across multiple fields"""
        # Search by title
        response = self.client.get('/api/books/?search=Book 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # Search by author
        response = self.client.get('/api/books/?search=Author 0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_ordering(self):
        """Test that ordering works correctly"""
        response = self.client.get('/api/books/?ordering=title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles))

