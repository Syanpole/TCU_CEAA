import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

# Delete existing admin user if it exists
try:
    existing_admin = CustomUser.objects.get(username='admin')
    existing_admin.delete()
    print("Deleted existing admin user")
except CustomUser.DoesNotExist:
    print("No existing admin user found")

# Create new admin user
admin_user = CustomUser.objects.create_user(
    username='admin',
    password='admin123',
    email='admin@example.com',
    role='admin',
    first_name='Admin',
    last_name='User',
    is_staff=True,
    is_superuser=True
)

print(f"Created admin user: {admin_user.username}")
print(f"Role: {admin_user.role}")
print(f"Is active: {admin_user.is_active}")
print(f"Is staff: {admin_user.is_staff}")
print(f"Is superuser: {admin_user.is_superuser}")
