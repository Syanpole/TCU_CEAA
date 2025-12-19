import os
import sys
import django

print("🔒 PASSWORD RESET UTILITY - DEVELOPMENT ONLY")
print("=" * 60)
print("⚠️  WARNING: This script resets passwords to weak defaults")
print("⚠️  ONLY use in development/testing environments")
print("=" * 60)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser
from django.conf import settings

# 🔒 SECURITY: Prevent running in production
if not settings.DEBUG:
    print("\n❌ ERROR: This script can only run in DEBUG mode (development)")
    print("🔒 For production password resets, use:")
    print("  - Django admin panel")
    print("  - Password reset email flow")
    print("  - python manage.py changepassword <username>")
    sys.exit(1)

confirm = input("\nType 'RESET' to confirm password reset: ")
if confirm != 'RESET':
    print("❌ Operation cancelled")
    sys.exit(0)

print("\n" + "=" * 60)
print("Current Users in Database")
print("=" * 60)

users = CustomUser.objects.all()

if not users.exists():
    print("No users found in database!")
else:
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"  Role: {user.role}")
        print(f"  Email: {user.email}")
        print(f"  First Name: {user.first_name}")
        print(f"  Last Name: {user.last_name}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")

print("\n" + "=" * 60)
print("Resetting Passwords")
print("=" * 60)

# ⚠️ WEAK PASSWORDS - FOR TESTING ONLY
TEST_ADMIN_PASSWORD = 'TestAdmin123!'
TEST_STUDENT_PASSWORD = 'TestStudent123!'
TEST_DEFAULT_PASSWORD = 'TestUser123!'

print(f"\n⚠️  Using weak test passwords:")
print(f"   Admin: {TEST_ADMIN_PASSWORD}")
print(f"   Students: {TEST_STUDENT_PASSWORD}")
print(f"   Others: {TEST_DEFAULT_PASSWORD}")

# Reset admin password
try:
    admin_user = CustomUser.objects.get(username='admin')
    admin_user.set_password(TEST_ADMIN_PASSWORD)
    admin_user.save()
    print(f"✓ Admin password reset to: {TEST_ADMIN_PASSWORD}")
except CustomUser.DoesNotExist:
    print("✗ Admin user not found. Creating new admin user...")
    admin_user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@tcu.edu',
        password=TEST_ADMIN_PASSWORD,
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    print(f"✓ Admin user created with password: {TEST_ADMIN_PASSWORD}")

# Reset salagubang password (if exists)
try:
    student = CustomUser.objects.get(username='salagubang')
    student.set_password(TEST_STUDENT_PASSWORD)
    student.save()
    print(f"✓ Student 'salagubang' password reset to: {TEST_STUDENT_PASSWORD}")
except CustomUser.DoesNotExist:
    print("✗ Student 'salagubang' not found. Creating...")
    student = CustomUser.objects.create_user(
        username='salagubang',
        email='salagubang@student.tcu.edu',
        password=TEST_STUDENT_PASSWORD,
        first_name='Juan',
        last_name='Dela Cruz',
        role='student',
        student_id='22-00001'
    )
    print(f"✓ Student 'salagubang' created with password: {TEST_STUDENT_PASSWORD}")

# List all users and set default password for any without proper password
print("\n" + "=" * 60)
print("Setting default passwords for all users")
print("=" * 60)

for user in CustomUser.objects.all():
    if user.username == 'admin':
        user.set_password(TEST_ADMIN_PASSWORD)
    elif user.role == 'student':
        user.set_password(TEST_STUDENT_PASSWORD)
    else:
        user.set_password(TEST_DEFAULT_PASSWORD)
    user.save()
    print(f"✓ {user.username} ({user.role}) - password set")

print("\n" + "=" * 60)
print("CREDENTIALS SUMMARY")
print("=" * 60)
print("\nAdmin Login:")
print("  Username: admin")
print("  Password: admin@123")

print("\nStudent Login:")
print("  Username: salagubang (or any student username)")
print("  Password: 12345678")

print("\nAll users have been reset!")
print("=" * 60)
