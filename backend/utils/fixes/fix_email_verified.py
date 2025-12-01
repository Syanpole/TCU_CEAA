#!/usr/bin/env python
"""
Fix email verification field for existing users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

# Update all existing users to have is_email_verified = True (for backward compatibility)
# New users will need to verify their email
updated_count = CustomUser.objects.filter(is_email_verified=False).update(is_email_verified=True)

print(f"✅ Updated {updated_count} existing users to have email verified status.")
print("📧 New users will need to verify their email during registration.")

# Show current status
total_users = CustomUser.objects.count()
verified_users = CustomUser.objects.filter(is_email_verified=True).count()
unverified_users = CustomUser.objects.filter(is_email_verified=False).count()

print(f"\n📊 Current Status:")
print(f"   Total users: {total_users}")
print(f"   Verified: {verified_users}")
print(f"   Unverified: {unverified_users}")
