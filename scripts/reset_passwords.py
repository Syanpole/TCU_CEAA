"""
Reset passwords for all users in the TCU-CEAA system
⚠️  WARNING: FOR DEVELOPMENT/TESTING ONLY
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser
from django.conf import settings

print("=" * 80)
print("🔒 MASS PASSWORD RESET UTILITY - DEVELOPMENT ONLY")
print("=" * 80)
print("⚠️  WARNING: This will reset ALL user passwords to a weak default")
print("⚠️  This script should ONLY be used in development/testing")
print("=" * 80)

# 🔒 SECURITY: Prevent running in production
if not settings.DEBUG:
    print("\n❌ ERROR: This script can only run in DEBUG mode (development)")
    print("🔒 For production password resets:")
    print("  - Use individual password reset flows")
    print("  - Use Django admin: python manage.py changepassword <username>")
    print("  - Use password reset email functionality")
    sys.exit(1)

confirm = input("\nType 'RESET' to confirm mass password reset: ")
if confirm != 'RESET':
    print("❌ Operation cancelled")
    sys.exit(0)

# Default password for all users - TESTING ONLY
DEFAULT_PASSWORD = 'DevPassword123!'

print(f"\n⚠️  Resetting all user passwords to: '{DEFAULT_PASSWORD}'")
print("\nProcessing users...")

try:
    users = CustomUser.objects.all()
    reset_count = 0
    
    for user in users:
        user.set_password(DEFAULT_PASSWORD)
        user.save()
        reset_count += 1
        print(f"  ✓ Reset password for: {user.username} ({user.role})")
    
    print(f"\n✅ Successfully reset passwords for {reset_count} users")
    print("\n" + "=" * 80)
    print("TEST CREDENTIALS:")
    print("=" * 80)
    print(f"\nUsername: salagubang")
    print(f"Password: {DEFAULT_PASSWORD}")
    print(f"\nUsername: admin")
    print(f"Password: {DEFAULT_PASSWORD}")
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
