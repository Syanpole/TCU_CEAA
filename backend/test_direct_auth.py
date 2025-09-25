#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import authenticate
from myapp.models import CustomUser
from myapp.serializers import LoginSerializer
from rest_framework.authtoken.models import Token
import json

def test_authentication():
    print("🔐 Testing Django Authentication System")
    print("=" * 50)
    
    # Test 1: Check if admin user exists
    print("\n1. Checking admin user...")
    try:
        admin_user = CustomUser.objects.get(username='admin')
        print(f"✅ Admin user found: {admin_user.username}")
        print(f"   - Role: {admin_user.role}")
        print(f"   - Active: {admin_user.is_active}")
        print(f"   - Email: {admin_user.email}")
    except CustomUser.DoesNotExist:
        print("❌ Admin user not found!")
        return
    
    # Test 2: Test direct Django authentication
    print("\n2. Testing direct Django authentication...")
    auth_user = authenticate(username='admin', password='admin123')
    if auth_user:
        print(f"✅ Django authentication successful: {auth_user.username}")
    else:
        print("❌ Django authentication failed!")
        return
    
    # Test 3: Test LoginSerializer
    print("\n3. Testing LoginSerializer...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    serializer = LoginSerializer(data=login_data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        print(f"✅ LoginSerializer validation successful: {user.username}")
        
        # Test 4: Test token generation
        print("\n4. Testing token generation...")
        token, created = Token.objects.get_or_create(user=user)
        print(f"✅ Token generated: {token.key[:10]}...")
        print(f"   - Token created: {created}")
        
    else:
        print("❌ LoginSerializer validation failed!")
        print(f"   Errors: {serializer.errors}")
        return
    
    # Test 5: Test regular user authentication
    print("\n5. Testing regular user authentication...")
    try:
        # Check if there are any regular users
        regular_users = CustomUser.objects.filter(role='student')
        if regular_users.exists():
            test_user = regular_users.first()
            print(f"   Found student user: {test_user.username}")
            
            # For testing, let's check if we can authenticate with known password
            # Note: We can't test password directly since it's hashed
            auth_test = authenticate(username=test_user.username, password='password123')
            if auth_test:
                print(f"✅ Student authentication test successful")
            else:
                print(f"ℹ️ Student authentication test failed (password may be different)")
        else:
            print("ℹ️ No student users found for testing")
    except Exception as e:
        print(f"❌ Error testing regular user: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("✅ Admin user exists and is properly configured")
    print("✅ Django authentication is working correctly")
    print("✅ LoginSerializer is working correctly")
    print("✅ Token generation is working")
    print("\n💡 The authentication system appears to be working correctly.")
    print("   The issue might be with:")
    print("   - Django server startup")
    print("   - URL routing")
    print("   - CORS configuration")
    print("   - Network connectivity")

if __name__ == "__main__":
    test_authentication()