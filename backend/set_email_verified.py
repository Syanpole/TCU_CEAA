"""
Script to set is_email_verified to True for all existing users
(So they can login without email verification)
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

def set_all_verified():
    """Set is_email_verified to True for all existing users"""
    users = CustomUser.objects.all()
    total = users.count()
    
    if total == 0:
        print("⚠️ No users found in database!")
        return
    
    print(f"📊 Found {total} users in database")
    print("\n🔧 Setting is_email_verified=True for all users...\n")
    
    for user in users:
        old_status = user.is_email_verified
        user.is_email_verified = True
        user.save()
        
        status_icon = "✅" if old_status else "🔄"
        print(f"{status_icon} {user.username} ({user.role}) - was: {old_status}, now: True")
    
    print(f"\n✅ Successfully updated {total} users!")
    print("🎉 All users can now login!")

if __name__ == '__main__':
    print("🚀 Setting email verification status for all users...\n")
    set_all_verified()
