from rest_framework import generics, filters, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Loan
from .serializers import (
    LoanSerializer,
    LoanListSerializer,
    LoanCreateSerializer,
    LoanReturnSerializer,
    LoanRenewSerializer
)
from core.permissions import IsAdminUser


class LoanCreateView(generics.CreateAPIView):
    """
    Borrow a book (Registered users only).
    """
    queryset = Loan.objects.all()
    serializer_class = LoanCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Borrow a book",
        operation_description="""
        Borrow an available book from the library.
        
        **Requirements:**
        - Must be a registered user (authenticated)
        - Book must be available
        - User cannot have more than 5 active loans
        - User cannot borrow the same book twice simultaneously
        
        **Loan Details:**
        - Loan duration: 14 days
        - Maximum renewals: 2 times
        - Book availability is automatically updated
        
        **Requires**: Authentication
        """,
        request_body=LoanCreateSerializer,
        responses={
            201: LoanSerializer,
            400: "Validation errors (book not available, loan limit reached, etc.)",
            401: "Authentication required"
        },
        tags=['Loans'],
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LoanListView(generics.ListAPIView):
    """
    List loans with filtering.
    - Regular users: See only their own loans
    - Admins: See all loans
    """
    serializer_class = LoanListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering
    filterset_fields = {
        'status': ['exact'],
        'borrowed_date': ['gte', 'lte'],
        'due_date': ['gte', 'lte'],
    }
    
    # Search
    search_fields = ['book__title', 'book__author', 'user__username']
    
    # Ordering
    ordering_fields = ['borrowed_date', 'due_date', 'status']
    ordering = ['-borrowed_date']
    
    @swagger_auto_schema(
        operation_summary="List loans",
        operation_description="""
        List all loans with filtering and search capabilities.
        
        **Access:**
        - Regular users: See only their own loans
        - Administrators: See all loans in the system
        
        **Features:**
        - Filter by status, borrowed date, due date
        - Search by book title, author, or username
        - Sort by date, status
        - Pagination (10 loans per page)
        
        **Examples:**
        - Active loans: `?status=ACTIVE`
        - Overdue loans: `?status=OVERDUE`
        - Loans due soon: `?due_date__lte=2024-12-31`
        - Search by book: `?search=python`
        
        **Requires**: Authentication
        """,
        responses={
            200: LoanListSerializer(many=True),
            401: "Authentication required"
        },
        tags=['Loans'],
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter loans based on user role"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Loan.objects.none()
        
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'is_admin') and user.is_admin:
            return Loan.objects.all()
        return Loan.objects.filter(user=user)


class LoanDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific loan.
    """
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get loan details",
        operation_description="""
        Get detailed information about a specific loan including:
        - Loan status and dates
        - Book information
        - User information
        - Renewal information
        - Overdue status
        
        **Access:**
        - Users can view their own loans
        - Admins can view any loan
        
        **Requires**: Authentication
        """,
        responses={
            200: LoanSerializer,
            401: "Authentication required",
            403: "Not authorized to view this loan",
            404: "Loan not found"
        },
        tags=['Loans'],
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter loans based on user role"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Loan.objects.none()
        
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'is_admin') and user.is_admin:
            return Loan.objects.all()
        return Loan.objects.filter(user=user)


class LoanReturnView(APIView):
    """
    Return a borrowed book.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Return a book",
        operation_description="""
        Return a borrowed book to the library.
        
        **Actions performed:**
        - Marks loan as returned
        - Records return date
        - Updates book availability (increases available copies)
        
        **Access:**
        - Users can return their own borrowed books
        - Admins can return any borrowed book
        
        **Requires**: Authentication
        """,
        request_body=LoanReturnSerializer,
        responses={
            200: openapi.Response(
                description="Book returned successfully",
                examples={
                    "application/json": {
                        "message": "Book returned successfully",
                        "loan": {
                            "id": 1,
                            "status": "RETURNED",
                            "returned_date": "2024-12-17T10:30:00Z"
                        }
                    }
                }
            ),
            400: "Book already returned",
            401: "Authentication required",
            403: "Not authorized to return this loan",
            404: "Loan not found"
        },
        tags=['Loans'],
        security=[{'Bearer': []}]
    )
    def post(self, request, pk):
        try:
            loan = Loan.objects.get(pk=pk)
            
            # Check permission
            if not request.user.is_admin and loan.user != request.user:
                return Response(
                    {'error': 'You are not authorized to return this loan'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate and return
            serializer = LoanReturnSerializer(
                data=request.data,
                context={'loan': loan}
            )
            serializer.is_valid(raise_exception=True)
            
            # Add notes if provided
            if 'notes' in serializer.validated_data:
                loan.notes = serializer.validated_data['notes']
            
            loan.return_book()
            
            return Response({
                'message': 'Book returned successfully',
                'loan': LoanSerializer(loan).data
            })
            
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Loan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoanRenewView(APIView):
    """
    Renew a loan (extend due date).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Renew a loan",
        operation_description="""
        Renew a loan to extend the due date.
        
        **Requirements:**
        - Loan must be active (not returned)
        - Cannot be overdue
        - Maximum 2 renewals per loan
        
        **Default renewal period**: 14 days
        
        **Access:**
        - Users can renew their own loans
        - Admins can renew any loan
        
        **Requires**: Authentication
        """,
        request_body=LoanRenewSerializer,
        responses={
            200: openapi.Response(
                description="Loan renewed successfully",
                examples={
                    "application/json": {
                        "message": "Loan renewed successfully",
                        "loan": {
                            "id": 1,
                            "due_date": "2025-01-15T10:30:00Z",
                            "renewed_count": 1
                        }
                    }
                }
            ),
            400: "Cannot renew (overdue, max renewals reached, or already returned)",
            401: "Authentication required",
            403: "Not authorized to renew this loan",
            404: "Loan not found"
        },
        tags=['Loans'],
        security=[{'Bearer': []}]
    )
    def post(self, request, pk):
        try:
            loan = Loan.objects.get(pk=pk)
            
            # Check permission
            if not request.user.is_admin and loan.user != request.user:
                return Response(
                    {'error': 'You are not authorized to renew this loan'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate and renew
            serializer = LoanRenewSerializer(
                data=request.data,
                context={'loan': loan}
            )
            serializer.is_valid(raise_exception=True)
            
            days = serializer.validated_data.get('days', 14)
            loan.renew(days=days)
            
            return Response({
                'message': 'Loan renewed successfully',
                'loan': LoanSerializer(loan).data
            })
            
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Loan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MyLoansView(generics.ListAPIView):
    """
    Get current user's loans.
    """
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = ['status']
    ordering_fields = ['borrowed_date', 'due_date']
    ordering = ['-borrowed_date']
    
    @swagger_auto_schema(
        operation_summary="Get my loans",
        operation_description="""
        Get all loans for the currently authenticated user.
        
        **Features:**
        - Filter by status: `?status=ACTIVE`
        - Sort by date: `?ordering=-due_date`
        - Shows detailed loan information including overdue status
        
        **Requires**: Authentication
        """,
        responses={
            200: LoanSerializer(many=True),
            401: "Authentication required"
        },
        tags=['Loans'],
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Get current user's loans"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Loan.objects.none()
        
        return Loan.objects.filter(user=self.request.user)


class OverdueLoansView(generics.ListAPIView):
    """
    List all overdue loans (Admin only).
    """
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    ordering_fields = ['due_date', 'borrowed_date']
    ordering = ['due_date']
    
    @swagger_auto_schema(
        operation_summary="List overdue loans",
        operation_description="""
        Get all overdue loans in the system.
        
        Useful for administrators to track and manage overdue books.
        
        **Requires**: Administrator privileges
        """,
        responses={
            200: LoanSerializer(many=True),
            401: "Authentication required",
            403: "Admin privileges required"
        },
        tags=['Loans'],
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Get all overdue loans"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Loan.objects.none()
        
        return Loan.objects.filter(status=Loan.LoanStatus.OVERDUE)
