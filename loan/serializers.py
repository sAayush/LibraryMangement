from rest_framework import serializers
from .models import Loan
from library.serializers import BookListSerializer
from core.serializers import UserSerializer
from django.utils import timezone


class LoanSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Loan model
    """
    user = UserSerializer(read_only=True)
    book = BookListSerializer(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    can_renew = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = (
            'id', 'user', 'book', 'status', 'borrowed_date', 'due_date',
            'returned_date', 'notes', 'renewed_count', 'max_renewals',
            'is_overdue', 'days_until_due', 'days_overdue', 'can_renew',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'borrowed_date', 'returned_date',
            'created_at', 'updated_at'
        )
    
    def get_can_renew(self, obj):
        """Check if loan can be renewed"""
        return obj.can_renew()


class LoanCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new loan (borrowing a book)
    """
    book_id = serializers.IntegerField(write_only=True)
    book = BookListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = ('id', 'book_id', 'book', 'user', 'notes', 'borrowed_date', 'due_date')
        read_only_fields = ('id', 'borrowed_date', 'due_date', 'user', 'book')
    
    def validate_book_id(self, value):
        """Validate that book exists"""
        from library.models import Book
        try:
            book = Book.objects.get(id=value)
            if not book.is_available:
                raise serializers.ValidationError(
                    "This book is not available for borrowing"
                )
            return value
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book not found")
    
    def validate(self, attrs):
        """Check if user already has active loan for this book"""
        from library.models import Book
        
        user = self.context['request'].user
        book = Book.objects.get(id=attrs['book_id'])
        
        # Check for existing active loan
        existing_loan = Loan.objects.filter(
            user=user,
            book=book,
            status=Loan.LoanStatus.ACTIVE
        ).exists()
        
        if existing_loan:
            raise serializers.ValidationError(
                "You already have an active loan for this book"
            )
        
        # Check loan limit (max 5 active loans per user)
        active_loans_count = Loan.objects.filter(
            user=user,
            status=Loan.LoanStatus.ACTIVE
        ).count()
        
        if active_loans_count >= 5:
            raise serializers.ValidationError(
                "You have reached the maximum limit of 5 active loans"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create loan and update book availability"""
        from library.models import Book
        
        book_id = validated_data.pop('book_id')
        book = Book.objects.get(id=book_id)
        user = self.context['request'].user
        
        # Decrease available copies
        if not book.borrow():
            raise serializers.ValidationError(
                "Unable to borrow book - no copies available"
            )
        
        # Create loan
        loan = Loan.objects.create(
            user=user,
            book=book,
            **validated_data
        )
        
        return loan


class LoanListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for loan listings
    """
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Loan
        fields = (
            'id', 'book_title', 'book_author', 'user_username',
            'status', 'borrowed_date', 'due_date', 'is_overdue'
        )


class LoanReturnSerializer(serializers.Serializer):
    """
    Serializer for returning a book
    """
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate that loan can be returned"""
        loan = self.context['loan']
        
        if loan.status == Loan.LoanStatus.RETURNED:
            raise serializers.ValidationError(
                "This book has already been returned"
            )
        
        return attrs


class LoanRenewSerializer(serializers.Serializer):
    """
    Serializer for renewing a loan
    """
    days = serializers.IntegerField(default=14, min_value=1, max_value=30)
    
    def validate(self, attrs):
        """Validate that loan can be renewed"""
        loan = self.context['loan']
        
        if not loan.can_renew():
            if loan.status != Loan.LoanStatus.ACTIVE:
                raise serializers.ValidationError(
                    "Only active loans can be renewed"
                )
            elif loan.renewed_count >= loan.max_renewals:
                raise serializers.ValidationError(
                    f"Maximum renewals ({loan.max_renewals}) reached"
                )
            elif loan.is_overdue:
                raise serializers.ValidationError(
                    "Overdue loans cannot be renewed"
                )
        
        return attrs

