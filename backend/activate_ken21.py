#!/usr/bin/env python
"""
Quick fix to activate user ken21
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

print("=" * 70)
print("🔧 ACTIVATING USER: ken21")
print("=" * 70)

try:
    user = CustomUser.objects.get(username='ken21')
    
    print(f"\n✅ User found: {user.username}")
    print(f"\nBEFORE:")
    print(f"  - is_active: {user.is_active}")
    print(f"  - is_email_verified: {user.is_email_verified}")
    
    # Fix the account
    user.is_active = True
    user.is_email_verified = True
    user.save()
    
    print(f"\nAFTER:")
    print(f"  - is_active: {user.is_active}")
    print(f"  - is_email_verified: {user.is_email_verified}")
    
    print(f"\n✅ ACCOUNT ACTIVATED SUCCESSFULLY!")
    print(f"\n🎯 You can now login with:")
    print(f"   Username: {user.username}")
    print(f"   Password: (the password you set during registration)")
    
except CustomUser.DoesNotExist:
    print(f"\n❌ User 'ken21' not found")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
