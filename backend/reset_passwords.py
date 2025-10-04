"""
Reset passwords for all users in the TCU-CEAA system
This will set default passwords for testing
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

print("=" * 80)
print("PASSWORD RESET UTILITY")
print("=" * 80)

# Default password for all users
DEFAULT_PASSWORD = 'password'

print(f"\nResetting all user passwords to: '{DEFAULT_PASSWORD}'")
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
