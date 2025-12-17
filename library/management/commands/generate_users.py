"""
Management command to generate fake users using Faker.

Usage:
    python manage.py generate_users --count 20
    python manage.py generate_users --count 50 --admins 5
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate fake users for testing and demonstration purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of users to generate (default: 20)'
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
            help='Clear existing users before generating new ones (keeps superusers)'
        )

    def handle(self, *args, **options):
        count = options['count']
        admin_count = options['admins']
        clear = options['clear']

        fake = Faker()

        # Clear existing users if requested (keep superusers)
        if clear:
            deleted_count = User.objects.filter(is_superuser=False).count()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing users (kept superusers)')
            )

        users_created = 0
        users_failed = 0

        # Generate admin users
        self.stdout.write(f'Generating {admin_count} admin users...')
        for i in range(admin_count):
            try:
                username = fake.user_name()
                while User.objects.filter(username=username).exists():
                    username = fake.user_name()

                email = fake.email()
                while User.objects.filter(email=email).exists():
                    email = fake.email()

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='admin123',  # Default password for demo
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role='ADMIN',
                    is_staff=True
                )
                users_created += 1
                self.stdout.write(f'  Created admin: {username}')

            except Exception as e:
                users_failed += 1
                self.stdout.write(
                    self.style.WARNING(f'Failed to create admin {i + 1}: {str(e)}')
                )

        # Generate regular users
        self.stdout.write(f'\nGenerating {count} regular users...')
        for i in range(count):
            try:
                username = fake.user_name()
                while User.objects.filter(username=username).exists():
                    username = fake.user_name()

                email = fake.email()
                while User.objects.filter(email=email).exists():
                    email = fake.email()

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='user123',  # Default password for demo
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role='USER'
                )
                users_created += 1

                if (i + 1) % 10 == 0:
                    self.stdout.write(f'  Created {i + 1}/{count} users...')

            except Exception as e:
                users_failed += 1
                self.stdout.write(
                    self.style.WARNING(f'Failed to create user {i + 1}: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Successfully created {users_created} users')
        )
        if users_failed > 0:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to create {users_failed} users')
            )

        # Statistics
        total_users = User.objects.count()
        admin_users = User.objects.filter(role='ADMIN').count()
        regular_users = User.objects.filter(role='USER').count()

        self.stdout.write('\n' + 'Database Statistics:')
        self.stdout.write(f'  Total users: {total_users}')
        self.stdout.write(f'  Admins: {admin_users}')
        self.stdout.write(f'  Regular users: {regular_users}')
        self.stdout.write('\n' + 'Default Passwords:')
        self.stdout.write('  Admins: admin123')
        self.stdout.write('  Users: user123')
        self.stdout.write('=' * 50)

