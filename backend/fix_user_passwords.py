import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

print("=" * 60)
print("Current Users in Database")
print("=" * 60)

users = CustomUser.objects.all()

if not users.exists():
    print("No users found in database!")
else:
    for user in users:
        print(f"\nUsername: {user.username}")
        print(f"  Role: {user.role}")
        print(f"  Email: {user.email}")
        print(f"  First Name: {user.first_name}")
        print(f"  Last Name: {user.last_name}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")

print("\n" + "=" * 60)
print("Resetting Passwords")
print("=" * 60)

# Reset admin password
try:
    admin_user = CustomUser.objects.get(username='admin')
    admin_user.set_password('admin@123')
    admin_user.save()
    print("✓ Admin password reset to: admin@123")
except CustomUser.DoesNotExist:
    print("✗ Admin user not found. Creating new admin user...")
    admin_user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@tcu.edu',
        password='admin@123',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    print("✓ Admin user created with password: admin@123")

# Reset salagubang password (if exists)
try:
    student = CustomUser.objects.get(username='salagubang')
    student.set_password('12345678')
    student.save()
    print("✓ Student 'salagubang' password reset to: 12345678")
except CustomUser.DoesNotExist:
    print("✗ Student 'salagubang' not found. Creating...")
    student = CustomUser.objects.create_user(
        username='salagubang',
        email='salagubang@student.tcu.edu',
        password='12345678',
        first_name='Juan',
        last_name='Dela Cruz',
        role='student',
        student_id='22-00001'
    )
    print("✓ Student 'salagubang' created with password: 12345678")

# List all users and set default password for any without proper password
print("\n" + "=" * 60)
print("Setting default passwords for all users")
print("=" * 60)

for user in CustomUser.objects.all():
    if user.username == 'admin':
        user.set_password('admin@123')
    elif user.role == 'student':
        user.set_password('12345678')  # Default password for all students
    else:
        user.set_password('password123')  # Default for other users
    user.save()
    print(f"✓ {user.username} ({user.role}) - password set")

print("\n" + "=" * 60)
print("CREDENTIALS SUMMARY")
print("=" * 60)
print("\nAdmin Login:")
print("  Username: admin")
print("  Password: admin@123")

print("\nStudent Login:")
print("  Username: salagubang (or any student username)")
print("  Password: 12345678")

print("\nAll users have been reset!")
print("=" * 60)
