from django.core.management.base import BaseCommand
from myapp.models import CustomUser
from django.conf import settings

class Command(BaseCommand):
    help = 'Create test users for development (⚠️  DEVELOPMENT ONLY)'

    def handle(self, *args, **options):
        # 🔒 SECURITY: Only allow in development
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("❌ Cannot create test users in production mode"))
            self.stdout.write("🔒 Use proper user registration or admin panel")
            return
        
        self.stdout.write(self.style.WARNING("⚠️  Creating test users with weak passwords - DEVELOPMENT ONLY"))
        
        TEST_PASSWORD = 'TestPass123!'  # Weak password for testing only
        
        # Create admin user
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tcu.edu.ph',
                'role': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created or not admin_user.check_password(TEST_PASSWORD):
            admin_user.set_password(TEST_PASSWORD)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"✓ Admin user {'created' if created else 'updated'}: {admin_user.username} (password: {TEST_PASSWORD})"))

        # Create a test student
        student_user, created = CustomUser.objects.get_or_create(
            username='student1',
            defaults={
                'email': 'john.doe@student.tcu.edu.ph',
                'role': 'student',
                'first_name': 'John',
                'last_name': 'Doe',
                'student_id': '22-00001'
            }
        )
        if created or not student_user.check_password('student123'):
            student_user.set_password('student123')
            student_user.save()
        self.stdout.write(f"Student user {'created' if created else 'updated'}: {student_user}")

        self.stdout.write(
            self.style.SUCCESS('Successfully created test users')
        )
