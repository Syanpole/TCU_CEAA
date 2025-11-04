#!/usr/bin/env python
"""
Auto-verify all old user accounts that were created before email verification was implemented
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

def verify_all_old_accounts():
    """Verify all users who don't have email verification"""
    
    # Find all unverified users
    unverified_users = CustomUser.objects.filter(is_email_verified=False)
    
    count = unverified_users.count()
    
    if count == 0:
        print("\n✅ All users are already verified!")
        return
    
    print(f"\n{'='*60}")
    print(f"FOUND {count} UNVERIFIED USERS")
    print(f"{'='*60}\n")
    
    for user in unverified_users:
        print(f"  • {user.username} ({user.email}) - {user.role}")
    
    print(f"\n{'='*60}")
    response = input(f"Do you want to verify all {count} users? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled.")
        return
    
    # Verify all users
    verified_count = 0
    for user in unverified_users:
        user.is_email_verified = True
        user.save()
        verified_count += 1
        print(f"  ✅ Verified: {user.username}")
    
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS: {verified_count} users verified!")
    print(f"All old accounts can now log in.")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    verify_all_old_accounts()
