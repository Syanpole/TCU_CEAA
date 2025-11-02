"""
Test script to diagnose login issues
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import authenticate
from myapp.models import CustomUser

print("=" * 80)
print("LOGIN DIAGNOSTIC TEST")
print("=" * 80)

# Test 1: Check if users exist
print("\n1. Checking users in database...")
try:
    total_users = CustomUser.objects.count()
    print(f"   Total users in database: {total_users}")
    
    # List all users
    users = CustomUser.objects.all()
    for user in users:
        print(f"   - {user.username} (Active: {user.is_active}, Has password: {bool(user.password)})")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Check specific user
print("\n2. Checking 'salagubang' user...")
try:
    user = CustomUser.objects.filter(username='salagubang').first()
    if user:
        print(f"   ✓ User exists: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Active: {user.is_active}")
        print(f"   - Has password: {bool(user.password)}")
        print(f"   - Password hash: {user.password[:20]}...")
        print(f"   - Role: {user.role}")
    else:
        print("   ✗ User 'salagubang' NOT FOUND")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Test authentication
print("\n3. Testing authentication...")
try:
    # Try to authenticate
    test_user = authenticate(username='salagubang', password='password')
    if test_user:
        print(f"   ✓ Authentication SUCCESS for salagubang")
        print(f"   - User: {test_user.username}")
        print(f"   - Active: {test_user.is_active}")
    else:
        print("   ✗ Authentication FAILED")
        print("   Checking possible reasons:")
        
        # Check if user exists
        user = CustomUser.objects.filter(username='salagubang').first()
        if not user:
            print("   - User does not exist")
        else:
            print(f"   - User exists: {user.username}")
            print(f"   - Is active: {user.is_active}")
            
            # Test password check
            if user.check_password('password'):
                print("   - Password matches (but authenticate() failed)")
            else:
                print("   - Password does NOT match")
                print("   - Trying to check what password would work...")
                
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check authentication backends
print("\n4. Checking authentication backends...")
try:
    from django.conf import settings
    backends = settings.AUTHENTICATION_BACKENDS
    print(f"   Configured backends: {backends}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Try to manually verify password
print("\n5. Manual password verification...")
try:
    user = CustomUser.objects.filter(username='salagubang').first()
    if user:
        # Test common passwords
        test_passwords = ['password', 'Password123', 'admin', 'salagubang']
        for pwd in test_passwords:
            if user.check_password(pwd):
                print(f"   ✓ Password '{pwd}' works!")
                break
        else:
            print("   ✗ None of the test passwords work")
            print("   The password might have been changed or reset")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
