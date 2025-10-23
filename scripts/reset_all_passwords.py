import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("Resetting User Passwords")
print("=" * 60)
print()

# Passwords
admin_password = "admin@123"
student_password = "student@123"

print("Setting passwords:")
print(f"  - Admin users: {admin_password}")
print(f"  - Student users: {student_password}")
print()

admins_updated = []
students_updated = []

for user in User.objects.all():
    if user.role == 'admin' or user.is_superuser:
        user.set_password(admin_password)
        user.save()
        admins_updated.append(user.username)
        print(f"✓ Reset ADMIN password for: {user.username}")
    else:
        user.set_password(student_password)
        user.save()
        students_updated.append(user.username)
        print(f"✓ Reset STUDENT password for: {user.username}")

print()
print("=" * 60)
print("Password Reset Complete!")
print("=" * 60)
print()
print(f"ADMIN USERS ({len(admins_updated)}) - Password: {admin_password}")
for username in admins_updated:
    print(f"  - {username}")
print()
print(f"STUDENT USERS ({len(students_updated)}) - Password: {student_password}")
for username in students_updated:
    print(f"  - {username}")
print()
print("✓ All users can now login with their respective passwords!")
print()
print("IMPORTANT: Tell users to change their password after first login!")
