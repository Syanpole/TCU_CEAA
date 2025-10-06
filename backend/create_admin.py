import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin user already exists
if User.objects.filter(username='admin').exists():
    print("Admin user already exists!")
    user = User.objects.get(username='admin')
    user.set_password('admin@123')
    user.role = 'admin'  # Ensure role is set to admin
    user.save()
    print("Password updated to: admin@123")
    print("Role updated to: admin")
else:
    # Create new admin user
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin@123',
        first_name='Admin',
        last_name='User'
    )
    # Set the role to admin
    user.role = 'admin'
    user.save()
    print("Superuser created successfully!")
    print("Username: admin")
    print("Password: admin@123")
    print("Email: admin@example.com")
    print("Role: admin")

print("\nYou can now login at: http://localhost:8000/admin")
