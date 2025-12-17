"""
Management command to generate fake books using Faker.

Usage:
    python manage.py generate_books --count 50
    python manage.py generate_books --count 100 --admin-username admin
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from library.models import Book
from faker import Faker
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate fake books for testing and demonstration purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of books to generate (default: 50)'
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default=None,
            help='Username of admin who added the books (optional)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing books before generating new ones'
        )

    def handle(self, *args, **options):
        count = options['count']
        admin_username = options['admin_username']
        clear = options['clear']

        fake = Faker()
        
        # Get admin user if provided
        added_by = None
        if admin_username:
            try:
                added_by = User.objects.get(username=admin_username, role='ADMIN')
                self.stdout.write(f'Books will be added by: {added_by.username}')
            except User.DoesNotExist:
                raise CommandError(f'Admin user "{admin_username}" not found')

        # Clear existing books if requested
        if clear:
            deleted_count = Book.objects.count()
            Book.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing books')
            )

        # Book genres
        genres = [
            'Fiction', 'Science Fiction', 'Fantasy', 'Mystery', 'Thriller',
            'Romance', 'Horror', 'Historical Fiction', 'Biography', 'Autobiography',
            'Self-Help', 'Business', 'History', 'Science', 'Philosophy',
            'Psychology', 'Technology', 'Travel', 'Cooking', 'Art', 'Poetry',
            'Drama', 'Adventure', 'Children', 'Young Adult', 'Graphic Novel',
            'Crime', 'Comedy', 'Non-Fiction', 'Religion'
        ]

        # Languages
        languages = ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese']

        # Publishers
        publishers = [
            'Penguin Random House', 'HarperCollins', 'Simon & Schuster',
            'Hachette Book Group', 'Macmillan Publishers', 'Scholastic',
            'Pearson Education', 'Oxford University Press', 'Cambridge University Press',
            'Wiley', "O'Reilly Media", 'MIT Press', 'Princeton University Press'
        ]

        self.stdout.write(f'Generating {count} fake books...')
        
        books_created = 0
        books_failed = 0

        for i in range(count):
            try:
                # Generate ISBN-13 (without dashes)
                isbn = ''.join([str(random.randint(0, 9)) for _ in range(13)])
                
                # Ensure unique ISBN
                while Book.objects.filter(isbn=isbn).exists():
                    isbn = ''.join([str(random.randint(0, 9)) for _ in range(13)])

                # Generate book data
                title = fake.catch_phrase().title() if random.choice([True, False]) else fake.bs().title()
                author = fake.name()
                publisher = random.choice(publishers)
                genre = random.choice(genres)
                language = random.choice(languages) if random.random() > 0.7 else 'English'
                
                # Generate description
                description = fake.paragraph(nb_sentences=random.randint(3, 7))
                
                # Generate page count (realistic range)
                page_count = random.randint(100, 800)
                
                # Generate publication date (last 50 years)
                published_date = fake.date_between(start_date='-50y', end_date='today')
                
                # Generate copies (most books have 1-5 copies)
                total_copies = random.choices(
                    [1, 2, 3, 4, 5, 10],
                    weights=[30, 25, 20, 15, 7, 3]
                )[0]
                
                # Some books are borrowed
                borrowed_count = random.randint(0, min(total_copies, 2))
                available_copies = total_copies - borrowed_count
                
                # Determine status
                if available_copies == 0:
                    status = Book.BookStatus.BORROWED
                elif random.random() < 0.05:  # 5% chance
                    status = random.choice([Book.BookStatus.MAINTENANCE, Book.BookStatus.LOST])
                else:
                    status = Book.BookStatus.AVAILABLE
                
                # Generate rating (70% of books have ratings)
                rating = round(random.uniform(2.5, 5.0), 2) if random.random() > 0.3 else None
                
                # Generate cover image URL (placeholder)
                cover_image = f'https://picsum.photos/seed/{isbn}/400/600' if random.random() > 0.2 else None

                # Create book
                book = Book.objects.create(
                    title=title,
                    author=author,
                    isbn=isbn,
                    publisher=publisher,
                    published_date=published_date,
                    page_count=page_count,
                    language=language,
                    genre=genre,
                    description=description,
                    status=status,
                    total_copies=total_copies,
                    available_copies=available_copies,
                    cover_image=cover_image,
                    rating=rating,
                    added_by=added_by
                )

                books_created += 1
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'  Created {i + 1}/{count} books...')

            except Exception as e:
                books_failed += 1
                self.stdout.write(
                    self.style.WARNING(f'Failed to create book {i + 1}: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Successfully created {books_created} books')
        )
        if books_failed > 0:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to create {books_failed} books')
            )
        
        # Statistics
        total_books = Book.objects.count()
        available_books = Book.objects.filter(status=Book.BookStatus.AVAILABLE).count()
        borrowed_books = Book.objects.filter(status=Book.BookStatus.BORROWED).count()
        
        self.stdout.write('\n' + 'Database Statistics:')
        self.stdout.write(f'  Total books: {total_books}')
        self.stdout.write(f'  Available: {available_books}')
        self.stdout.write(f'  Borrowed: {borrowed_books}')
        self.stdout.write('=' * 50)

