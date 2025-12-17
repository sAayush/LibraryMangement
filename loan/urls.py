from django.urls import path
from .views import (
    LoanCreateView,
    LoanListView,
    LoanDetailView,
    LoanReturnView,
    LoanRenewView,
    MyLoansView,
    OverdueLoansView,
)

app_name = 'loan'

urlpatterns = [
    # Loan operations
    path('loans/', LoanListView.as_view(), name='loan-list'),
    path('loans/my/', MyLoansView.as_view(), name='my-loans'),
    path('loans/overdue/', OverdueLoansView.as_view(), name='overdue-loans'),
    path('loans/<int:pk>/', LoanDetailView.as_view(), name='loan-detail'),
    path('loans/borrow/', LoanCreateView.as_view(), name='loan-create'),
    path('loans/<int:pk>/return/', LoanReturnView.as_view(), name='loan-return'),
    path('loans/<int:pk>/renew/', LoanRenewView.as_view(), name='loan-renew'),
]

