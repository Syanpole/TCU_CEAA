import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

print("=" * 60)
print("Testing User Authentication")
print("=" * 60)
print()

# List all users
print("All users in database:")
for user in User.objects.all():
    print(f"  - {user.username} ({user.role}) - Active: {user.is_active}")
print()

# Test admin login
print("Testing admin login with password: admin@123")
admin_user = authenticate(username='admin', password='admin@123')
if admin_user:
    print("  ✓ Admin login successful!")
else:
    print("  ✗ Admin login failed!")
print()

# Test if we can check password directly
print("Checking password hashes:")
admin = User.objects.get(username='admin')
print(f"  Admin password hash: {admin.password[:50]}...")
print(f"  Admin check_password('admin@123'): {admin.check_password('admin@123')}")
print()

# Check one of the migrated users
try:
    test_user = User.objects.get(username='kyoti')
    print(f"  kyoti password hash: {test_user.password[:50]}...")
    print(f"  kyoti is_active: {test_user.is_active}")
    print()
    
    # The issue is that we copied the password hash from SQLite
    # Django's authenticate() should still work if the hash is valid
    print("NOTE: Migrated users have their password hashes from SQLite.")
    print("They should be able to login with their original passwords.")
    print()
    print("If login fails, it means:")
    print("1. Password hash format is correct (Django hashes)")
    print("2. But the user needs to know their original password")
    print()
    print("To test a migrated user login, you need to know their original password.")
    print("Or you can reset their password.")
    
except User.DoesNotExist:
    print("  Test user 'kyoti' not found")

print()
print("=" * 60)
print("Recommendation:")
print("=" * 60)
print()
print("If users don't remember their passwords, you have two options:")
print()
print("1. Reset passwords for all users:")
print("   python reset_all_passwords.py")
print()
print("2. Let users reset individually through 'Forgot Password'")
print()
print("For now, test login with:")
print("  Username: admin")
print("  Password: admin@123")
