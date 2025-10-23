#!/usr/bin/env python
"""
Test original login credentials to verify authentication system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import authenticate
from myapp.models import CustomUser

def test_original_credentials():
    print("=" * 60)
    print("🔍 TESTING ORIGINAL LOGIN CREDENTIALS")
    print("=" * 60)
    
    # Get all users
    users = CustomUser.objects.all()
    print(f"\n📊 Total users in database: {users.count()}")
    print("\n👥 User list:")
    for user in users:
        print(f"  - {user.username} ({user.role}) - Active: {user.is_active}")
    
    print("\n" + "=" * 60)
    print("🧪 TESTING COMMON PASSWORDS")
    print("=" * 60)
    
    # Test common passwords for salagubang user
    test_user = 'salagubang'
    common_passwords = [
        'salagubang',
        'salagubang123',
        'password',
        'password123',
        '12345678',
        'admin',
        'admin123',
        'student',
        'student123'
    ]
    
    print(f"\n🎯 Testing passwords for user: {test_user}")
    
    user_obj = CustomUser.objects.filter(username=test_user).first()
    if not user_obj:
        print(f"❌ User '{test_user}' not found!")
        return
    
    print(f"✅ User found: {user_obj.username}")
    print(f"   Email: {user_obj.email}")
    print(f"   Role: {user_obj.role}")
    print(f"   Active: {user_obj.is_active}")
    print(f"   Has password hash: {bool(user_obj.password)}")
    
    print(f"\n🔑 Testing passwords...")
    for password in common_passwords:
        result = authenticate(username=test_user, password=password)
        if result:
            print(f"   ✅ PASSWORD FOUND: '{password}' works!")
            print(f"\n🎉 SUCCESS! The working credentials are:")
            print(f"   Username: {test_user}")
            print(f"   Password: {password}")
            return
        else:
            print(f"   ❌ '{password}' - doesn't work")
    
    print(f"\n⚠️ None of the common passwords worked!")
    print(f"\n💡 The password might be:")
    print(f"   1. A custom password set by the user")
    print(f"   2. Need to check what password was used during user creation")
    
    # Check admin user too
    print("\n" + "=" * 60)
    print("🧪 TESTING ADMIN USER")
    print("=" * 60)
    
    admin_user = CustomUser.objects.filter(username='admin').first()
    if admin_user:
        print(f"✅ Admin user found: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Is superuser: {admin_user.is_superuser}")
        print(f"\n🔑 Testing admin passwords...")
        
        admin_passwords = ['admin', 'admin123', 'password', 'password123', '12345678']
        for password in admin_passwords:
            result = authenticate(username='admin', password=password)
            if result:
                print(f"   ✅ ADMIN PASSWORD FOUND: '{password}' works!")
                return
            else:
                print(f"   ❌ '{password}' - doesn't work")

if __name__ == '__main__':
    test_original_credentials()
