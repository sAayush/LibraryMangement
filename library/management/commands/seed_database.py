"""
Master command to seed the entire database with fake data.

Usage:
    python manage.py seed_database
    python manage.py seed_database --books 100 --users 50 --loans 30
    python manage.py seed_database --clear
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from library.models import Book
from loan.models import Loan

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with fake data (users, books, and loans)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--books',
            type=int,
            default=50,
            help='Number of books to generate (default: 50)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of regular users to generate (default: 20)'
        )
        parser.add_argument(
            '--admins',
            type=int,
            default=2,
            help='Number of admin users to generate (default: 2)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        books_count = options['books']
        users_count = options['users']
        admins_count = options['admins']
        clear = options['clear']

        self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 60))
        self.stdout.write(self.style.HTTP_INFO('  🌱 DATABASE SEEDING STARTED'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60 + '\n'))

        if clear:
            self.stdout.write(self.style.WARNING('⚠️  Clearing existing data...'))
            
            # Clear loans first (foreign key constraints)
            loans_deleted = Loan.objects.count()
            Loan.objects.all().delete()
            self.stdout.write(f'  Deleted {loans_deleted} loans')
            
            # Clear books
            books_deleted = Book.objects.count()
            Book.objects.all().delete()
            self.stdout.write(f'  Deleted {books_deleted} books')
            
            # Clear users (except superusers)
            users_deleted = User.objects.filter(is_superuser=False).count()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(f'  Deleted {users_deleted} users (kept superusers)\n')

        try:
            # Step 1: Generate Users
            self.stdout.write(self.style.HTTP_INFO('\n📝 Step 1: Generating Users'))
            self.stdout.write('-' * 60)
            call_command('generate_users', count=users_count, admins=admins_count)

            # Step 2: Generate Books
            self.stdout.write(self.style.HTTP_INFO('\n📚 Step 2: Generating Books'))
            self.stdout.write('-' * 60)
            
            # Get first admin to assign as book creator
            admin = User.objects.filter(role='ADMIN').first()
            if admin:
                call_command('generate_books', count=books_count, admin_username=admin.username)
            else:
                call_command('generate_books', count=books_count)

            # Final Summary
            self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 60))
            self.stdout.write(self.style.HTTP_INFO('  📊 FINAL DATABASE STATISTICS'))
            self.stdout.write(self.style.HTTP_INFO('=' * 60))
            
            total_users = User.objects.count()
            admin_users = User.objects.filter(role='ADMIN').count()
            regular_users = User.objects.filter(role='USER').count()
            superusers = User.objects.filter(is_superuser=True).count()
            
            total_books = Book.objects.count()
            available_books = Book.objects.filter(status=Book.BookStatus.AVAILABLE).count()
            borrowed_books = Book.objects.filter(status=Book.BookStatus.BORROWED).count()
            
            total_loans = Loan.objects.count()
            active_loans = Loan.objects.filter(status='ACTIVE').count()
            returned_loans = Loan.objects.filter(status='RETURNED').count()
            
            self.stdout.write('\n👥 Users:')
            self.stdout.write(f'  Total: {total_users}')
            self.stdout.write(f'  Superusers: {superusers}')
            self.stdout.write(f'  Admins: {admin_users}')
            self.stdout.write(f'  Regular: {regular_users}')
            
            self.stdout.write('\n📚 Books:')
            self.stdout.write(f'  Total: {total_books}')
            self.stdout.write(f'  Available: {available_books}')
            self.stdout.write(f'  Borrowed: {borrowed_books}')
            
            self.stdout.write('\n📖 Loans:')
            self.stdout.write(f'  Total: {total_loans}')
            self.stdout.write(f'  Active: {active_loans}')
            self.stdout.write(f'  Returned: {returned_loans}')
            
            self.stdout.write('\n🔑 Access Information:')
            self.stdout.write('  Dashboard: http://localhost:8000/')
            self.stdout.write('  Admin Panel: http://localhost:8000/admin/')
            self.stdout.write('  API Docs: http://localhost:8000/swagger/')
            self.stdout.write('\n🔐 Demo Credentials:')
            self.stdout.write('  Admins: username: (any admin) | password: admin123')
            self.stdout.write('  Users: username: (any user) | password: user123')
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('  ✅ DATABASE SEEDING COMPLETED SUCCESSFULLY'))
            self.stdout.write(self.style.HTTP_INFO('=' * 60 + '\n'))

        except Exception as e:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.ERROR(f'  ❌ SEEDING FAILED: {str(e)}'))
            self.stdout.write(self.style.HTTP_INFO('=' * 60 + '\n'))
            raise

