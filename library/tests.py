from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Book

User = get_user_model()


class BookModelTest(TestCase):
    """Test cases for the Book model"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            role=User.UserRole.ADMIN
        )
        
        self.book_data = {
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'page_count': 464,
            'genre': 'Programming',
            'total_copies': 5,
            'available_copies': 5,
            'added_by': self.admin
        }
    
    def test_create_book(self):
        """Test creating a book"""
        book = Book.objects.create(**self.book_data)
        self.assertEqual(book.title, 'Clean Code')
        self.assertEqual(book.author, 'Robert C. Martin')
        self.assertEqual(book.isbn, '9780132350884')
        self.assertEqual(book.status, Book.BookStatus.AVAILABLE)
    
    def test_book_str_representation(self):
        """Test the string representation of book"""
        book = Book.objects.create(**self.book_data)
        self.assertEqual(str(book), 'Clean Code by Robert C. Martin')
    
    def test_is_available_property(self):
        """Test is_available property"""
        book = Book.objects.create(**self.book_data)
        self.assertTrue(book.is_available)
        
        # Make all copies borrowed
        book.available_copies = 0
        book.status = Book.BookStatus.BORROWED
        book.save()
        self.assertFalse(book.is_available)
    
    def test_borrow_book(self):
        """Test borrowing a book decreases available copies"""
        book = Book.objects.create(**self.book_data)
        initial_available = book.available_copies
        
        result = book.borrow()
        self.assertTrue(result)
        self.assertEqual(book.available_copies, initial_available - 1)
    
    def test_borrow_last_copy_changes_status(self):
        """Test borrowing last copy changes status to BORROWED"""
        book_data = self.book_data.copy()
        book_data['total_copies'] = 1
        book_data['available_copies'] = 1
        book = Book.objects.create(**book_data)
        
        book.borrow()
        self.assertEqual(book.status, Book.BookStatus.BORROWED)
        self.assertEqual(book.available_copies, 0)
    
    def test_cannot_borrow_unavailable_book(self):
        """Test cannot borrow when no copies available"""
        book_data = self.book_data.copy()
        book_data['available_copies'] = 0
        book = Book.objects.create(**book_data)
        
        result = book.borrow()
        self.assertFalse(result)
    
    def test_return_book(self):
        """Test returning a book increases available copies"""
        book = Book.objects.create(**self.book_data)
        book.borrow()  # Borrow first
        initial_available = book.available_copies
        
        result = book.return_book()
        self.assertTrue(result)
        self.assertEqual(book.available_copies, initial_available + 1)
    
    def test_return_book_changes_status_to_available(self):
        """Test returning a book changes status back to AVAILABLE"""
        book_data = self.book_data.copy()
        book_data['total_copies'] = 1
        book_data['available_copies'] = 0
        book_data['status'] = Book.BookStatus.BORROWED
        book = Book.objects.create(**book_data)
        
        book.return_book()
        self.assertEqual(book.status, Book.BookStatus.AVAILABLE)
        self.assertEqual(book.available_copies, 1)
    
    def test_borrowed_copies_property(self):
        """Test borrowed_copies property"""
        book = Book.objects.create(**self.book_data)
        self.assertEqual(book.borrowed_copies, 0)
        
        book.borrow()
        self.assertEqual(book.borrowed_copies, 1)


class BookAPITest(APITestCase):
    """Test cases for Book API endpoints"""
    
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
        self.book1 = Book.objects.create(
            title='Clean Code',
            author='Robert C. Martin',
            isbn='9780132350884',
            page_count=464,
            genre='Programming',
            total_copies=5,
            available_copies=5,
            added_by=self.admin
        )
        self.book2 = Book.objects.create(
            title='The Pragmatic Programmer',
            author='Andrew Hunt',
            isbn='9780135957059',
            page_count=352,
            genre='Programming',
            total_copies=3,
            available_copies=0,
            status=Book.BookStatus.BORROWED,
            added_by=self.admin
        )
    
    def test_list_books_anonymous(self):
        """Test anonymous users can list books"""
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_search_books(self):
        """Test searching for books"""
        response = self.client.get('/api/books/?search=Clean')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertIn('Clean', response.data['results'][0]['title'])
    
    def test_filter_available_books(self):
        """Test filtering for available books"""
        response = self.client.get('/api/books/?status=AVAILABLE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data['results']:
            self.assertEqual(book['status'], 'AVAILABLE')
    
    def test_filter_by_genre(self):
        """Test filtering books by genre"""
        response = self.client.get('/api/books/?genre__icontains=programming')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_get_book_detail_anonymous(self):
        """Test anonymous users can view book details"""
        response = self.client.get(f'/api/books/{self.book1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Clean Code')
    
    def test_check_book_availability(self):
        """Test checking book availability"""
        response = self.client.get(f'/api/books/{self.book1.id}/availability/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_available'])
        self.assertEqual(response.data['available_copies'], 5)
    
    def test_create_book_as_admin(self):
        """Test admin can create a book"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        data = {
            'title': 'Design Patterns',
            'author': 'Erich Gamma',
            'isbn': '9780201633610',
            'page_count': 395,
            'genre': 'Programming',
            'total_copies': 4,
            'available_copies': 4
        }
        response = self.client.post('/api/books/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Design Patterns')
    
    def test_create_book_as_regular_user(self):
        """Test regular user cannot create a book"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {
            'title': 'Design Patterns',
            'author': 'Erich Gamma',
            'isbn': '9780201633610',
            'page_count': 395,
            'genre': 'Programming',
            'total_copies': 4,
            'available_copies': 4
        }
        response = self.client.post('/api/books/create/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_book_duplicate_isbn(self):
        """Test cannot create book with duplicate ISBN"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        data = {
            'title': 'Another Book',
            'author': 'Some Author',
            'isbn': '9780132350884',  # Same as book1
            'page_count': 300,
            'genre': 'Programming',
            'total_copies': 2,
            'available_copies': 2
        }
        response = self.client.post('/api/books/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_book_as_admin(self):
        """Test admin can update a book"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        data = {'rating': 4.8}
        response = self.client.patch(f'/api/books/{self.book1.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['rating']), 4.8)
    
    def test_update_book_as_regular_user(self):
        """Test regular user cannot update a book"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {'rating': 4.8}
        response = self.client.patch(f'/api/books/{self.book1.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_book_as_admin(self):
        """Test admin can delete a book"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.delete(f'/api/books/{self.book1.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())
    
    def test_delete_book_as_regular_user(self):
        """Test regular user cannot delete a book"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.delete(f'/api/books/{self.book1.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
