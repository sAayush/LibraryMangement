from rest_framework import serializers
from .models import Book
from core.serializers import UserSerializer


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model with all fields
    """
    added_by = UserSerializer(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    borrowed_copies = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'isbn', 'publisher', 'published_date',
            'page_count', 'language', 'genre', 'description', 'status',
            'total_copies', 'available_copies', 'cover_image', 'rating',
            'is_available', 'borrowed_copies', 'added_by', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'added_by')
    
    def validate_isbn(self, value):
        """Validate ISBN format (13 digits)"""
        if not value.isdigit():
            raise serializers.ValidationError("ISBN must contain only digits")
        if len(value) != 13:
            raise serializers.ValidationError("ISBN must be exactly 13 digits")
        return value
    
    def validate(self, attrs):
        """Validate that available_copies <= total_copies"""
        total_copies = attrs.get('total_copies', getattr(self.instance, 'total_copies', None))
        available_copies = attrs.get('available_copies', getattr(self.instance, 'available_copies', None))
        
        if available_copies and total_copies and available_copies > total_copies:
            raise serializers.ValidationError({
                'available_copies': 'Available copies cannot exceed total copies'
            })
        return attrs


class BookListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for book listings (lighter payload)
    """
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'isbn', 'genre', 'status',
            'available_copies', 'total_copies', 'is_available',
            'cover_image', 'rating'
        )


class BookCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new books (admin only)
    """
    class Meta:
        model = Book
        fields = (
            'title', 'author', 'isbn', 'publisher', 'published_date',
            'page_count', 'language', 'genre', 'description',
            'total_copies', 'available_copies', 'cover_image', 'rating'
        )
    
    def validate_isbn(self, value):
        """Validate ISBN format and uniqueness"""
        if not value.isdigit():
            raise serializers.ValidationError("ISBN must contain only digits")
        if len(value) != 13:
            raise serializers.ValidationError("ISBN must be exactly 13 digits")
        return value

