from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from library.models import Book
from .models import Loan

User = get_user_model()


class LoanModelTest(TestCase):
    """Test cases for the Loan model"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.book = Book.objects.create(
            title='Clean Code',
            author='Robert C. Martin',
            isbn='9780132350884',
            page_count=464,
            genre='Programming',
            total_copies=5,
            available_copies=5,
            added_by=self.admin
        )
    
    def test_create_loan(self):
        """Test creating a loan"""
        loan = Loan.objects.create(
            user=self.user,
            book=self.book
        )
        self.assertEqual(loan.user, self.user)
        self.assertEqual(loan.book, self.book)
        self.assertEqual(loan.status, Loan.LoanStatus.ACTIVE)
        self.assertIsNotNone(loan.due_date)
    
    def test_loan_str_representation(self):
        """Test the string representation of loan"""
        loan = Loan.objects.create(user=self.user, book=self.book)
        self.assertIn('testuser', str(loan))
        self.assertIn('Clean Code', str(loan))
    
    def test_loan_due_date_auto_calculation(self):
        """Test due date is automatically set to 14 days"""
        loan = Loan.objects.create(user=self.user, book=self.book)
        expected_due_date = loan.borrowed_date + timedelta(days=14)
        # Allow 1 second difference for test execution time
        self.assertLess(abs((loan.due_date - expected_due_date).total_seconds()), 1)
    
    def test_is_overdue_property(self):
        """Test is_overdue property"""
        # Create loan with past due date (borrowed 20 days ago, due 6 days ago)
        past_date = timezone.now() - timedelta(days=20)
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            borrowed_date=past_date,
            due_date=past_date + timedelta(days=14)  # Due 6 days ago
        )
        self.assertTrue(loan.is_overdue)
        
        # Create loan with future due date
        future_loan = Loan.objects.create(user=self.user, book=self.book)
        self.assertFalse(future_loan.is_overdue)
    
    def test_days_until_due(self):
        """Test days_until_due calculation"""
        loan = Loan.objects.create(user=self.user, book=self.book)
        days_until = loan.days_until_due
        self.assertIsNotNone(days_until)
        self.assertGreater(days_until, 0)
    
    def test_days_overdue(self):
        """Test days_overdue calculation"""
        past_date = timezone.now() - timedelta(days=20)
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            borrowed_date=past_date,
            due_date=past_date + timedelta(days=14)
        )
        self.assertGreater(loan.days_overdue, 0)
    
    def test_can_renew(self):
        """Test can_renew logic"""
        loan = Loan.objects.create(user=self.user, book=self.book)
        self.assertTrue(loan.can_renew())
        
        # After max renewals
        loan.renewed_count = 2
        loan.save()
        self.assertFalse(loan.can_renew())
    
    def test_renew_loan(self):
        """Test renewing a loan"""
        loan = Loan.objects.create(user=self.user, book=self.book)
        original_due_date = loan.due_date
        original_renewed_count = loan.renewed_count
        
        loan.renew()
        self.assertGreater(loan.due_date, original_due_date)
        self.assertEqual(loan.renewed_count, original_renewed_count + 1)
    
    def test_cannot_renew_overdue_loan(self):
        """Test cannot renew an overdue loan"""
        past_date = timezone.now() - timedelta(days=20)
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            borrowed_date=past_date,
            due_date=past_date + timedelta(days=14)
        )
        
        with self.assertRaises(Exception):
            loan.renew()
    
    def test_return_book(self):
        """Test returning a book"""
        self.book.borrow()  # Decrease available copies
        loan = Loan.objects.create(user=self.user, book=self.book)
        
        initial_available = self.book.available_copies
        loan.return_book()
        
        self.assertEqual(loan.status, Loan.LoanStatus.RETURNED)
        self.assertIsNotNone(loan.returned_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, initial_available + 1)
    
    def test_cannot_return_already_returned_book(self):
        """Test cannot return a book twice"""
        loan = Loan.objects.create(user=self.user, book=self.book)
        loan.return_book()
        
        with self.assertRaises(Exception):
            loan.return_book()


class LoanAPITest(APITestCase):
    """Test cases for Loan API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        
        # Get tokens
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
        
        # Create test books
        self.book = Book.objects.create(
            title='Clean Code',
            author='Robert C. Martin',
            isbn='9780132350884',
            page_count=464,
            genre='Programming',
            total_copies=5,
            available_copies=5,
            added_by=self.admin
        )
    
    def test_borrow_book(self):
        """Test borrowing a book"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {'book_id': self.book.id}
        response = self.client.post('/api/loans/borrow/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['book']['id'], self.book.id)
        self.assertEqual(response.data['user']['username'], 'testuser')
        
        # Verify book availability decreased
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)
    
    def test_borrow_book_requires_authentication(self):
        """Test borrowing requires authentication"""
        data = {'book_id': self.book.id}
        response = self.client.post('/api/loans/borrow/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_cannot_borrow_unavailable_book(self):
        """Test cannot borrow when no copies available"""
        self.book.available_copies = 0
        self.book.status = Book.BookStatus.BORROWED
        self.book.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {'book_id': self.book.id}
        response = self.client.post('/api/loans/borrow/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cannot_borrow_same_book_twice(self):
        """Test cannot borrow the same book twice simultaneously"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {'book_id': self.book.id}
        
        # First borrow
        response1 = self.client.post('/api/loans/borrow/', data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second borrow (should fail)
        response2 = self.client.post('/api/loans/borrow/', data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_loan_limit(self):
        """Test user cannot have more than 5 active loans"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        
        # Create 5 books and borrow all
        for i in range(5):
            book = Book.objects.create(
                title=f'Book {i}',
                author='Test Author',
                isbn=f'978012345678{i}',
                page_count=300,
                genre='Test',
                total_copies=1,
                available_copies=1,
                added_by=self.admin
            )
            self.client.post('/api/loans/borrow/', {'book_id': book.id})
        
        # Try to borrow 6th book (should fail)
        book6 = Book.objects.create(
            title='Book 6',
            author='Test Author',
            isbn='9780123456786',
            page_count=300,
            genre='Test',
            total_copies=1,
            available_copies=1,
            added_by=self.admin
        )
        response = self.client.post('/api/loans/borrow/', {'book_id': book6.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_return_book(self):
        """Test returning a borrowed book"""
        # Borrow first
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        borrow_response = self.client.post('/api/loans/borrow/', {'book_id': self.book.id})
        loan_id = borrow_response.data['id']
        
        initial_available = Book.objects.get(id=self.book.id).available_copies
        
        # Return
        response = self.client.post(f'/api/loans/{loan_id}/return/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify book availability increased
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, initial_available + 1)
    
    def test_renew_loan(self):
        """Test renewing a loan"""
        # Borrow first
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        borrow_response = self.client.post('/api/loans/borrow/', {'book_id': self.book.id})
        loan_id = borrow_response.data['id']
        
        # Get original due date
        loan = Loan.objects.get(id=loan_id)
        original_due_date = loan.due_date
        
        # Renew
        response = self.client.post(f'/api/loans/{loan_id}/renew/', {'days': 14})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify due date extended
        loan.refresh_from_db()
        self.assertGreater(loan.due_date, original_due_date)
        self.assertEqual(loan.renewed_count, 1)
    
    def test_cannot_renew_others_loan(self):
        """Test user cannot renew another user's loan"""
        # Create another user
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='TestPass123!'
        )
        user2_token = str(RefreshToken.for_user(user2).access_token)
        
        # User1 borrows
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        borrow_response = self.client.post('/api/loans/borrow/', {'book_id': self.book.id})
        loan_id = borrow_response.data['id']
        
        # User2 tries to renew user1's loan
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user2_token}')
        response = self.client.post(f'/api/loans/{loan_id}/renew/', {'days': 14})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_my_loans(self):
        """Test getting current user's loans"""
        # Create a loan
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.client.post('/api/loans/borrow/', {'book_id': self.book.id})
        
        # List loans
        response = self.client.get('/api/loans/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_admin_can_see_all_loans(self):
        """Test admin can see all loans"""
        # User borrows a book
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.client.post('/api/loans/borrow/', {'book_id': self.book.id})
        
        # Admin lists all loans
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get('/api/loans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_user_sees_only_own_loans(self):
        """Test regular user sees only their own loans"""
        # Create another user and loan
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='TestPass123!'
        )
        book2 = Book.objects.create(
            title='Another Book',
            author='Author',
            isbn='9780123456789',
            page_count=300,
            genre='Test',
            total_copies=1,
            available_copies=1,
            added_by=self.admin
        )
        Loan.objects.create(user=user2, book=book2)
        
        # User1 borrows
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.client.post('/api/loans/borrow/', {'book_id': self.book.id})
        
        # User1 lists loans (should see only their own)
        response = self.client.get('/api/loans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user_username'], 'testuser')
    
    def test_admin_view_overdue_loans(self):
        """Test admin can view overdue loans"""
        # Create overdue loan
        past_date = timezone.now() - timedelta(days=20)
        Loan.objects.create(
            user=self.user,
            book=self.book,
            borrowed_date=past_date,
            due_date=past_date + timedelta(days=14),
            status=Loan.LoanStatus.OVERDUE
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get('/api/loans/overdue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_regular_user_cannot_view_all_overdue_loans(self):
        """Test regular user cannot view overdue loans endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get('/api/loans/overdue/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
