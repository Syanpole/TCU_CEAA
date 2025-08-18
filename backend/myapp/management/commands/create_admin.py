from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Create the first admin user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Admin username')
        parser.add_argument('--email', type=str, default='admin@tcu.edu', help='Admin email')
        parser.add_argument('--password', type=str, default='admin123', help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            # Check if admin user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Admin user "{username}" already exists.')
                )
                return

            # Create admin user
            admin_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin',
                first_name='System',
                last_name='Administrator',
                is_staff=True,
                is_superuser=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user "{username}" with password "{password}"'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Admin can login at: http://localhost:8000/admin/'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'API login endpoint: http://localhost:8000/api/auth/login/'
                )
            )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
