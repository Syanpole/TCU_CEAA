#!/usr/bin/env python
"""
Manually verify a user's email address
Usage: python verify_user_email.py <username_or_email>
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

def verify_user(identifier):
    """Verify a user's email by username or email"""
    try:
        # Try to find user by username or email
        try:
            user = CustomUser.objects.get(username=identifier)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.get(email=identifier)
        
        print(f"\n{'='*60}")
        print(f"USER FOUND")
        print(f"{'='*60}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Email Verified: {user.is_email_verified}")
        
        if user.is_email_verified:
            print(f"\n✅ Email is already verified!")
            return True
        
        # Verify the email
        user.is_email_verified = True
        user.save()
        
        print(f"\n✅ SUCCESS: Email has been verified!")
        print(f"User '{user.username}' can now log in.")
        return True
        
    except CustomUser.DoesNotExist:
        print(f"\n❌ ERROR: User '{identifier}' not found.")
        print(f"Please check the username or email and try again.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\nUsage: python verify_user_email.py <username_or_email>")
        print("Example: python verify_user_email.py kyoti")
        print("Example: python verify_user_email.py ramoslloydkenneth1@gmail.com")
        sys.exit(1)
    
    identifier = sys.argv[1]
    success = verify_user(identifier)
    sys.exit(0 if success else 1)
