from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """
    Admin interface for Loan model
    """
    list_display = (
        'id', 'user', 'book', 'status', 'borrowed_date',
        'due_date', 'returned_date', 'is_overdue', 'renewed_count'
    )
    list_filter = ('status', 'borrowed_date', 'due_date', 'returned_date')
    search_fields = ('user__username', 'user__email', 'book__title', 'book__author', 'book__isbn')
    ordering = ('-borrowed_date',)
    readonly_fields = ('created_at', 'updated_at', 'is_overdue', 'days_until_due', 'days_overdue')
    date_hierarchy = 'borrowed_date'
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('borrowed_date', 'due_date', 'returned_date', 'is_overdue', 'days_until_due', 'days_overdue')
        }),
        ('Renewal Information', {
            'fields': ('renewed_count', 'max_renewals')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_returned', 'mark_as_overdue']
    
    def mark_as_returned(self, request, queryset):
        """Action to mark selected loans as returned"""
        count = 0
        for loan in queryset:
            if loan.status != Loan.LoanStatus.RETURNED:
                try:
                    loan.return_book()
                    count += 1
                except Exception:
                    pass
        self.message_user(request, f"{count} loan(s) marked as returned")
    mark_as_returned.short_description = "Mark selected loans as returned"
    
    def mark_as_overdue(self, request, queryset):
        """Action to mark selected loans as overdue"""
        count = queryset.filter(
            status=Loan.LoanStatus.ACTIVE
        ).update(status=Loan.LoanStatus.OVERDUE)
        self.message_user(request, f"{count} loan(s) marked as overdue")
    mark_as_overdue.short_description = "Mark selected loans as overdue"
