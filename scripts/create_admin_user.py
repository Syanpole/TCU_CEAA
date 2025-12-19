import os
import sys
import django
import getpass
import secrets

print("🔒 ADMIN USER CREATION UTILITY")
print("=" * 50)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser
from django.conf import settings

# 🔒 SECURITY: Check if running in production
if not settings.DEBUG:
    print("⚠️  WARNING: Running in PRODUCTION mode")
    confirm = input("Continue? (yes/NO): ").lower()
    if confirm != 'yes':
        print("❌ Operation cancelled")
        sys.exit(0)

# Delete existing admin user if it exists
try:
    existing_admin = CustomUser.objects.get(username='admin')
    print(f"Found existing admin user: {existing_admin.username}")
    delete = input("Delete and recreate? (y/N): ").lower()
    if delete == 'y':
        existing_admin.delete()
        print("✓ Deleted existing admin user")
    else:
        print("❌ Keeping existing admin user")
        sys.exit(0)
except CustomUser.DoesNotExist:
    print("No existing admin user found")

# 🔒 SECURITY: Secure password handling
if settings.DEBUG:
    print("\n⚠️  Running in DEBUG mode")
    password = getpass.getpass("Enter admin password (or press Enter to generate): ")
    if not password:
        password = secrets.token_urlsafe(16)
        print(f"✅ Generated secure password: {password}")
        print("⚠️  SAVE THIS PASSWORD - it won't be shown again!")
else:
    print("\n🔒 Production mode - strong password required")
    password = getpass.getpass("Enter admin password (min 12 chars): ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("❌ Passwords do not match!")
        sys.exit(1)
    if len(password) < 12:
        print("❌ Password must be at least 12 characters!")
        sys.exit(1)

# Create new admin user
admin_user = CustomUser.objects.create_user(
    username='admin',
    password=password,
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
