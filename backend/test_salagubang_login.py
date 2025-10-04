import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import authenticate

# Test salagubang login
user = authenticate(username='salagubang', password='student@123')
print(f"Testing login for: salagubang")
print(f"Result: {'SUCCESS - User found and password correct!' if user else 'FAILED - Invalid credentials'}")
if user:
    print(f"User ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")
    print(f"Is Active: {user.is_active}")
