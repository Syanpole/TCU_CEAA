import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

# Check admin user
try:
    admin_user = CustomUser.objects.get(username='admin')
    print(f"✅ Admin user found!")
    print(f"   Username: {admin_user.username}")
    print(f"   Email: {admin_user.email}")
    print(f"   Role: {admin_user.role}")
    print(f"   Is Superuser: {admin_user.is_superuser}")
    print(f"   Is Staff: {admin_user.is_staff}")
    print(f"   Is Active: {admin_user.is_active}")
    print(f"   is_admin() method: {admin_user.is_admin()}")
    
    if admin_user.role != 'admin':
        print(f"\n⚠ WARNING: User role is '{admin_user.role}' but should be 'admin'")
        print("Fixing role...")
        admin_user.role = 'admin'
        admin_user.save()
        print("✅ Role updated to 'admin'")
    else:
        print("\n✅ Admin user is correctly configured!")
        
except CustomUser.DoesNotExist:
    print("❌ Admin user not found!")
