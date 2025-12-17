from rest_framework import generics, filters, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Book
from .serializers import (
    BookSerializer,
    BookListSerializer,
    BookCreateSerializer
)
from core.permissions import IsAdminUser, ReadOnlyOrAuthenticated


class BookListView(generics.ListAPIView):
    """
    List all books with filtering, search, and pagination.
    Anonymous users can browse, authenticated users can see more details.
    """
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering
    filterset_fields = {
        'status': ['exact'],
        'genre': ['exact', 'icontains'],
        'language': ['exact'],
        'author': ['exact', 'icontains'],
        'published_date': ['gte', 'lte', 'exact'],
        'page_count': ['gte', 'lte'],
        'rating': ['gte', 'lte'],
    }
    
    # Search
    search_fields = ['title', 'author', 'isbn', 'description', 'genre', 'publisher']
    
    # Ordering
    ordering_fields = ['title', 'author', 'published_date', 'rating', 'created_at']
    ordering = ['-created_at']
    
    @swagger_auto_schema(
        operation_summary="List all books",
        operation_description="""
        Browse all books in the library catalog.
        
        **Features:**
        - **Filtering**: Filter by status, genre, language, author, publication date, page count, rating
        - **Search**: Search across title, author, ISBN, description, genre, publisher
        - **Ordering**: Sort by title, author, published_date, rating, created_at
        - **Pagination**: 10 books per page
        
        **Available to**: Everyone (including anonymous users)
        
        **Examples:**
        - Filter available books: `?status=AVAILABLE`
        - Search for books: `?search=python`
        - Filter by genre: `?genre__icontains=science`
        - Filter by author: `?author__icontains=martin`
        - Books with high rating: `?rating__gte=4.0`
        - Sort by rating: `?ordering=-rating`
        - Multiple filters: `?status=AVAILABLE&genre__icontains=fiction&ordering=-rating`
        """,
        responses={200: BookListSerializer(many=True)},
        tags=['Books']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed information about a specific book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Get book details",
        operation_description="""
        Get detailed information about a specific book including:
        - Full book information
        - Availability status
        - Number of borrowed copies
        - Who added the book
        
        **Available to**: Everyone (including anonymous users)
        """,
        responses={
            200: BookSerializer,
            404: "Book not found"
        },
        tags=['Books']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookCreateView(generics.CreateAPIView):
    """
    Create a new book (Admin only).
    """
    queryset = Book.objects.all()
    serializer_class = BookCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @swagger_auto_schema(
        operation_summary="Add new book",
        operation_description="""
        Add a new book to the library catalog.
        
        **Requires**: Administrator privileges
        
        **Security Notes:**
        - ISBN must be unique (13 digits)
        - All required fields must be provided
        - Book is automatically marked as added by the current admin
        """,
        responses={
            201: BookSerializer,
            400: "Validation errors",
            401: "Authentication required",
            403: "Admin privileges required"
        },
        tags=['Books'],
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Set the admin who added the book"""
        serializer.save(added_by=self.request.user)


class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book (Admin only).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @swagger_auto_schema(
        operation_summary="Update book",
        operation_description="""
        Update an existing book's information.
        
        **Requires**: Administrator privileges
        
        Supports both PUT (full update) and PATCH (partial update).
        """,
        responses={
            200: BookSerializer,
            400: "Validation errors",
            401: "Authentication required",
            403: "Admin privileges required",
            404: "Book not found"
        },
        tags=['Books'],
        security=[{'Bearer': []}]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partially update book",
        operation_description="""
        Partially update a book's information.
        
        **Requires**: Administrator privileges
        """,
        responses={
            200: BookSerializer,
            400: "Validation errors",
            401: "Authentication required",
            403: "Admin privileges required",
            404: "Book not found"
        },
        tags=['Books'],
        security=[{'Bearer': []}]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book (Admin only).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @swagger_auto_schema(
        operation_summary="Delete book",
        operation_description="""
        Delete a book from the library catalog.
        
        **Requires**: Administrator privileges
        
        **Warning**: This action cannot be undone. All associated loan records will also be deleted.
        """,
        responses={
            204: "Book deleted successfully",
            401: "Authentication required",
            403: "Admin privileges required",
            404: "Book not found"
        },
        tags=['Books'],
        security=[{'Bearer': []}]
    )
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BookAvailabilityView(APIView):
    """
    Check book availability status.
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Check book availability",
        operation_description="""
        Check if a specific book is available for borrowing.
        
        Returns:
        - Book availability status
        - Number of available copies
        - Number of borrowed copies
        
        **Available to**: Everyone
        """,
        responses={
            200: openapi.Response(
                description="Availability information",
                examples={
                    "application/json": {
                        "book_id": 1,
                        "title": "Clean Code",
                        "is_available": True,
                        "available_copies": 3,
                        "total_copies": 5,
                        "borrowed_copies": 2,
                        "status": "AVAILABLE"
                    }
                }
            ),
            404: "Book not found"
        },
        tags=['Books']
    )
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            return Response({
                'book_id': book.id,
                'title': book.title,
                'is_available': book.is_available,
                'available_copies': book.available_copies,
                'total_copies': book.total_copies,
                'borrowed_copies': book.borrowed_copies,
                'status': book.status
            })
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )
