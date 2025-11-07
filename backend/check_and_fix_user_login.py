#!/usr/bin/env python
"""
Check and fix user login issues
Run this to diagnose why a user cannot log in
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser
from django.contrib.auth import authenticate

def check_user_login(username):
    """
    Check why a user might not be able to log in
    """
    print("=" * 70)
    print(f"🔍 CHECKING LOGIN ISSUE FOR: {username}")
    print("=" * 70)
    
    # Check if user exists
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        print(f"\n❌ USER NOT FOUND: '{username}'")
        print("\n💡 Possible reasons:")
        print("   - Username is incorrect")
        print("   - User was never created")
        print("\n📋 Available users:")
        users = CustomUser.objects.all()
        for u in users:
            print(f"   - {u.username} ({u.role})")
        return
    
    print(f"\n✅ User found: {user.username}")
    print(f"\n📊 User Details:")
    print(f"   - ID: {user.id}")
    print(f"   - Username: {user.username}")
    print(f"   - Email: {user.email}")
    print(f"   - Role: {user.role}")
    print(f"   - Student ID: {user.student_id}")
    print(f"   - First Name: {user.first_name}")
    print(f"   - Last Name: {user.last_name}")
    
    # Check account status
    print(f"\n🔐 Account Status:")
    print(f"   - is_active: {user.is_active} {'✅' if user.is_active else '❌'}")
    print(f"   - is_email_verified: {user.is_email_verified} {'✅' if user.is_email_verified else '❌'}")
    print(f"   - is_superuser: {user.is_superuser}")
    print(f"   - is_staff: {user.is_staff}")
    
    # Check password
    has_password = bool(user.password)
    print(f"\n🔑 Password:")
    print(f"   - Has password hash: {has_password} {'✅' if has_password else '❌'}")
    if has_password:
        print(f"   - Password hash (first 30 chars): {user.password[:30]}...")
    
    # Diagnose issues
    print(f"\n🔍 DIAGNOSIS:")
    issues = []
    
    if not user.is_active:
        issues.append("❌ Account is NOT ACTIVE (is_active=False)")
        print(f"   {issues[-1]}")
        print(f"      → Account was created but not yet activated")
        print(f"      → This happens when email verification is not completed")
    
    if user.role == 'student' and not user.is_email_verified:
        issues.append("❌ Email is NOT VERIFIED (is_email_verified=False)")
        print(f"   {issues[-1]}")
        print(f"      → Students must verify their email before logging in")
    
    if not has_password:
        issues.append("❌ No password set")
        print(f"   {issues[-1]}")
    
    if not issues:
        print("   ✅ No obvious issues detected")
        print("   💡 The problem might be:")
        print("      - Incorrect password")
        print("      - Authentication backend issue")
    
    # Test authentication with common passwords
    if has_password:
        print(f"\n🧪 Testing Common Passwords:")
        test_passwords = [
            'password', 'password123', '12345678', 
            username, f'{username}123',
            'admin', 'admin123',
            'student', 'student123'
        ]
        
        for pwd in test_passwords:
            result = authenticate(username=username, password=pwd)
            if result:
                print(f"   ✅ FOUND WORKING PASSWORD: '{pwd}'")
                break
        else:
            print(f"   ❌ None of the common passwords worked")
            print(f"   💡 You need to remember/reset the password")
    
    # Provide fix options
    print(f"\n🛠️  FIX OPTIONS:")
    print(f"\n1️⃣  Activate Account (if is_active=False):")
    print(f"   Run: python manage.py shell")
    print(f"   Then: user = CustomUser.objects.get(username='{username}')")
    print(f"         user.is_active = True")
    print(f"         user.save()")
    
    print(f"\n2️⃣  Verify Email (if is_email_verified=False):")
    print(f"   Run: python manage.py shell")
    print(f"   Then: user = CustomUser.objects.get(username='{username}')")
    print(f"         user.is_email_verified = True")
    print(f"         user.save()")
    
    print(f"\n3️⃣  Reset Password:")
    print(f"   Run: python manage.py shell")
    print(f"   Then: user = CustomUser.objects.get(username='{username}')")
    print(f"         user.set_password('newpassword123')")
    print(f"         user.save()")
    
    print(f"\n4️⃣  Quick Fix All (Activate + Verify + Set Password):")
    print(f"   Run this script with --fix flag")
    
    return user, issues

def quick_fix_user(username, password='password123'):
    """
    Quick fix to activate and enable login for a user
    """
    print("=" * 70)
    print(f"🔧 QUICK FIX FOR: {username}")
    print("=" * 70)
    
    try:
        user = CustomUser.objects.get(username=username)
        print(f"\n✅ User found: {user.username}")
        
        # Fix is_active
        if not user.is_active:
            user.is_active = True
            print(f"   ✅ Activated account (is_active=True)")
        
        # Fix is_email_verified
        if user.role == 'student' and not user.is_email_verified:
            user.is_email_verified = True
            print(f"   ✅ Verified email (is_email_verified=True)")
        
        # Set password
        user.set_password(password)
        print(f"   ✅ Set password to: '{password}'")
        
        user.save()
        
        print(f"\n✅ USER FIXED SUCCESSFULLY!")
        print(f"\n🎯 You can now login with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
        # Test authentication
        print(f"\n🧪 Testing authentication...")
        test_user = authenticate(username=username, password=password)
        if test_user:
            print(f"   ✅ Authentication successful!")
        else:
            print(f"   ❌ Authentication failed (unexpected)")
        
    except CustomUser.DoesNotExist:
        print(f"\n❌ User not found: {username}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Check user: python check_and_fix_user_login.py <username>")
        print("  Quick fix:  python check_and_fix_user_login.py <username> --fix")
        print("\nExample:")
        print("  python check_and_fix_user_login.py ken21")
        print("  python check_and_fix_user_login.py ken21 --fix")
        sys.exit(1)
    
    username = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == '--fix':
        # Quick fix mode
        password = input(f"\nEnter new password for '{username}' (default: password123): ").strip()
        if not password:
            password = 'password123'
        quick_fix_user(username, password)
    else:
        # Check mode
        check_user_login(username)
        
        print("\n" + "=" * 70)
        print("🔍 SUMMARY")
        print("=" * 70)
        print("\nTo fix the issue, run:")
        print(f"  python check_and_fix_user_login.py {username} --fix")
