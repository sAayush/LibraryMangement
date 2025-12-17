from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Book(models.Model):
    """
    Book model for library catalog.
    Contains information about books available in the library.
    """
    
    class BookStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        BORROWED = 'BORROWED', 'Borrowed'
        MAINTENANCE = 'MAINTENANCE', 'Under Maintenance'
        LOST = 'LOST', 'Lost'
    
    # Basic Information
    title = models.CharField(
        max_length=255,
        help_text='Title of the book'
    )
    author = models.CharField(
        max_length=255,
        help_text='Author of the book'
    )
    isbn = models.CharField(
        max_length=13,
        unique=True,
        help_text='ISBN-13 number (13 digits)'
    )
    
    # Additional Details
    publisher = models.CharField(
        max_length=255,
        blank=True,
        help_text='Publisher name'
    )
    published_date = models.DateField(
        null=True,
        blank=True,
        help_text='Publication date'
    )
    page_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Number of pages'
    )
    language = models.CharField(
        max_length=50,
        default='English',
        help_text='Language of the book'
    )
    
    # Categories and Classification
    genre = models.CharField(
        max_length=100,
        blank=True,
        help_text='Genre/Category (e.g., Fiction, Science, History)'
    )
    description = models.TextField(
        blank=True,
        help_text='Brief description of the book'
    )
    
    # Availability and Status
    status = models.CharField(
        max_length=20,
        choices=BookStatus.choices,
        default=BookStatus.AVAILABLE,
        help_text='Current status of the book'
    )
    total_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Total number of copies in library'
    )
    available_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text='Number of copies currently available'
    )
    
    # Additional Information
    cover_image = models.URLField(
        blank=True,
        null=True,
        help_text='URL to book cover image'
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))],
        help_text='Average rating (0-5)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='books_added',
        help_text='Admin who added this book'
    )
    
    class Meta:
        db_table = 'books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.status == self.BookStatus.AVAILABLE and self.available_copies > 0
    
    @property
    def borrowed_copies(self):
        """Calculate number of borrowed copies"""
        return self.total_copies - self.available_copies
    
    def borrow(self):
        """Decrease available copies when book is borrowed"""
        if self.available_copies > 0:
            self.available_copies -= 1
            if self.available_copies == 0:
                self.status = self.BookStatus.BORROWED
            self.save()
            return True
        return False
    
    def return_book(self):
        """Increase available copies when book is returned"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            if self.status == self.BookStatus.BORROWED:
                self.status = self.BookStatus.AVAILABLE
            self.save()
            return True
        return False
    
    def clean(self):
        """Validate that available_copies <= total_copies"""
        from django.core.exceptions import ValidationError
        if self.available_copies > self.total_copies:
            raise ValidationError(
                'Available copies cannot exceed total copies'
            )
