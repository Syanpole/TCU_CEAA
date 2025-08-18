from django.core.management.base import BaseCommand
from myapp.models import CustomUser

class Command(BaseCommand):
    help = 'Create test users for development'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tcu.edu.ph',
                'role': 'admin',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created or not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.save()
        self.stdout.write(f"Admin user {'created' if created else 'updated'}: {admin_user}")

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
