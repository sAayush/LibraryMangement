from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class Loan(models.Model):
    """
    Loan model to track book borrowing.
    Tracks which user borrowed which book and when.
    """
    
    class LoanStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        RETURNED = 'RETURNED', 'Returned'
        OVERDUE = 'OVERDUE', 'Overdue'
        LOST = 'LOST', 'Lost/Damaged'
    
    # Relationships
    user = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='loans',
        help_text='User who borrowed the book'
    )
    book = models.ForeignKey(
        'library.Book',
        on_delete=models.CASCADE,
        related_name='loans',
        help_text='Book that was borrowed'
    )
    
    # Loan Details
    status = models.CharField(
        max_length=20,
        choices=LoanStatus.choices,
        default=LoanStatus.ACTIVE,
        help_text='Current status of the loan'
    )
    
    # Dates
    borrowed_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time when book was borrowed'
    )
    due_date = models.DateTimeField(
        help_text='Date and time when book should be returned'
    )
    returned_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date and time when book was actually returned'
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the loan'
    )
    renewed_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of times loan has been renewed'
    )
    max_renewals = models.PositiveIntegerField(
        default=2,
        help_text='Maximum number of renewals allowed'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loans'
        ordering = ['-borrowed_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(renewed_count__lte=models.F('max_renewals')),
                name='renewed_count_within_limit'
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Set due_date if not provided (14 days from borrowed_date)"""
        if not self.due_date:
            self.due_date = self.borrowed_date + timedelta(days=14)
        
        # Update status based on dates
        if self.status == self.LoanStatus.ACTIVE:
            if timezone.now() > self.due_date:
                self.status = self.LoanStatus.OVERDUE
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if loan is overdue"""
        if self.status in [self.LoanStatus.ACTIVE, self.LoanStatus.OVERDUE]:
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.status in [self.LoanStatus.ACTIVE, self.LoanStatus.OVERDUE]:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            delta = timezone.now() - self.due_date
            return delta.days
        return 0
    
    def can_renew(self):
        """Check if loan can be renewed"""
        return (
            self.status == self.LoanStatus.ACTIVE and
            self.renewed_count < self.max_renewals and
            not self.is_overdue
        )
    
    def renew(self, days=14):
        """Renew the loan by extending due date"""
        if not self.can_renew():
            raise ValidationError("This loan cannot be renewed")
        
        self.due_date = timezone.now() + timedelta(days=days)
        self.renewed_count += 1
        self.save()
        return True
    
    def return_book(self):
        """Mark book as returned"""
        if self.status == self.LoanStatus.RETURNED:
            raise ValidationError("Book has already been returned")
        
        self.status = self.LoanStatus.RETURNED
        self.returned_date = timezone.now()
        self.save()
        
        # Update book availability
        self.book.return_book()
        return True
    
    def clean(self):
        """Validate loan data"""
        # Check if user already has an active loan for this book
        if not self.pk:  # Only for new loans
            existing_loan = Loan.objects.filter(
                user=self.user,
                book=self.book,
                status=self.LoanStatus.ACTIVE
            ).exists()
            
            if existing_loan:
                raise ValidationError(
                    'You already have an active loan for this book'
                )
        
        # Validate dates
        if self.returned_date and self.returned_date < self.borrowed_date:
            raise ValidationError(
                'Return date cannot be before borrow date'
            )
