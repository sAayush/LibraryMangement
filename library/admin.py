from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface for Book model
    """
    list_display = (
        'title', 'author', 'isbn', 'genre', 'status',
        'available_copies', 'total_copies', 'rating', 'created_at'
    )
    list_filter = ('status', 'genre', 'language', 'created_at')
    search_fields = ('title', 'author', 'isbn', 'publisher', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'added_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'publisher', 'published_date')
        }),
        ('Details', {
            'fields': ('page_count', 'language', 'genre', 'description', 'cover_image', 'rating')
        }),
        ('Availability', {
            'fields': ('status', 'total_copies', 'available_copies')
        }),
        ('Metadata', {
            'fields': ('added_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set added_by to current user if creating new book"""
        if not change:  # Creating new book
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
