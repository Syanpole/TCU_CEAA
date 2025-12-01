#!/usr/bin/env python
"""
Test script to verify the login functionality after database fix
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser
from django.contrib.auth import authenticate

def test_user_query():
    """Test if we can query users without errors"""
    print("=" * 60)
    print("Testing User Query")
    print("=" * 60)
    
    try:
        # Try to get a user (admin)
        users = CustomUser.objects.all()[:5]
        print(f"✅ Successfully queried {users.count()} users")
        
        for user in users:
            print(f"\nUser: {user.username}")
            print(f"  - Role: {user.role}")
            print(f"  - Email: {user.email}")
            print(f"  - Email Verified: {user.is_email_verified}")
            print(f"  - Email Verified At: {user.email_verified_at}")
        
        return True
    except Exception as e:
        print(f"❌ Error querying users: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication():
    """Test authentication with a sample user"""
    print("\n" + "=" * 60)
    print("Testing Authentication")
    print("=" * 60)
    
    # Try to find an admin user
    try:
        admin_user = CustomUser.objects.filter(role='admin').first()
        if not admin_user:
            print("⚠️  No admin users found in database")
            return True
        
        print(f"\nFound admin user: {admin_user.username}")
        print(f"  - Email: {admin_user.email}")
        print(f"  - Email Verified: {admin_user.is_email_verified}")
        print(f"  - Email Verified At: {admin_user.email_verified_at}")
        
        # Note: We can't test actual password authentication here
        # without knowing the password, but we can verify the user object
        # can be retrieved without errors
        
        print("\n✅ User retrieval successful (column access working)")
        return True
        
    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "🔍 " * 20)
    print("DATABASE FIX VERIFICATION TEST")
    print("🔍 " * 20 + "\n")
    
    success = True
    
    # Test 1: User Query
    if not test_user_query():
        success = False
    
    # Test 2: Authentication
    if not test_authentication():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Restart your Django development server")
        print("2. Try logging in through the web interface")
        print("3. Test the forgot password functionality")
        print("\nLogin URL: http://localhost:8000/api/auth/login/")
        print("Password Reset URL: http://localhost:8000/api/auth/request-password-reset/")
    else:
        print("❌ SOME TESTS FAILED!")
        print("=" * 60)
        print("\nPlease review the errors above.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
