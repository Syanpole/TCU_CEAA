"""
User Authentication Test - Manual Test Script
This is NOT a Django test case - it's a manual testing script.
Use myapp/tests.py for proper Django test cases.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


def run_manual_test():
    """Manual test function - only runs when script is executed directly"""
    print("=" * 60)
    print("Testing User Authentication")
    print("=" * 60)
    print()

    # List all users
    print("All users in database:")
    users = User.objects.all()
    if users.exists():
        for user in users:
            print(f"  - {user.username} ({user.role}) - Active: {user.is_active}")
    else:
        print("  No users found in database")
    print()

    # Test admin login if admin exists
    try:
        admin = User.objects.get(username='admin')
        print("Testing admin login with password: admin@123")
        admin_user = authenticate(username='admin', password='admin@123')
        if admin_user:
            print("  ✓ Admin login successful!")
        else:
            print("  ✗ Admin login failed!")
        print()

        # Check password directly
        print("Checking password hashes:")
        print(f"  Admin password hash: {admin.password[:50]}...")
        print(f"  Admin check_password('admin@123'): {admin.check_password('admin@123')}")
        print()
    except User.DoesNotExist:
        print("⚠️  Admin user does not exist. Skipping admin tests.")
        print()

    # Check one of the migrated users if exists
    try:
        test_user = User.objects.get(username='kyoti')
        print(f"  kyoti password hash: {test_user.password[:50]}...")
        print(f"  kyoti is_active: {test_user.is_active}")
        print()
        
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
