import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, r'C:\xampp\htdocs\TCU_CEAA\django-react-app\backend')
os.chdir(r'C:\xampp\htdocs\TCU_CEAA\django-react-app\backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

# Setup Django
import django
django.setup()

# Test admin user
from myapp.models import CustomUser
from django.contrib.auth import authenticate

print("=== Testing Admin User ===")

# Check if admin exists
admin = CustomUser.objects.filter(username='admin').first()
print(f"Admin exists: {admin is not None}")

if admin:
    print(f"Admin role: {admin.role}")
    print(f"Is superuser: {admin.is_superuser}")
    print(f"Is staff: {admin.is_staff}")
    print(f"Is active: {admin.is_active}")
    print(f"Check password 'admin123': {admin.check_password('admin123')}")
    
    # Test authentication
    auth_user = authenticate(username='admin', password='admin123')
    print(f"Authentication successful: {auth_user is not None}")
    
    if not auth_user:
        print("Authentication failed!")
        
        # Try to create a new admin user
        print("\nCreating new admin user...")
        try:
            new_admin = CustomUser.objects.create_user(
                username='admin',
                password='admin123',
                email='admin@tcu.edu',
                role='admin',
                is_staff=True,
                is_superuser=True,
                first_name='Admin',
                last_name='User'
            )
            print("New admin user created successfully!")
        except Exception as e:
            print(f"Error creating admin: {e}")
            # Admin might already exist, let's reset password
            admin.set_password('admin123')
            admin.save()
            print("Admin password reset!")
            
            # Test again
            auth_user = authenticate(username='admin', password='admin123')
            print(f"Authentication after reset: {auth_user is not None}")
else:
    print("No admin user found. Creating one...")
    try:
        admin = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@tcu.edu',
            role='admin',
            is_staff=True,
            is_superuser=True,
            first_name='Admin',
            last_name='User'
        )
        print("Admin user created successfully!")
        
        # Test authentication
        auth_user = authenticate(username='admin', password='admin123')
        print(f"Authentication successful: {auth_user is not None}")
    except Exception as e:
        print(f"Error creating admin: {e}")

print("\n=== All Users ===")
users = CustomUser.objects.all()
for user in users:
    print(f"Username: {user.username}, Role: {user.role}, Active: {user.is_active}")
