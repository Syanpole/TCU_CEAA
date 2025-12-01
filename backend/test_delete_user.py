"""
Test script to verify user deletion endpoint
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

def test_delete_user():
    # Get an admin user
    admin = CustomUser.objects.filter(role='admin').first()
    if not admin:
        print("❌ No admin user found. Please create an admin user first.")
        return
    
    print(f"✅ Found admin user: {admin.username} ({admin.email})")
    
    # Get or create token for admin
    token, created = Token.objects.get_or_create(user=admin)
    print(f"✅ Admin token: {token.key}")
    
    # Find a test student to delete
    test_student = CustomUser.objects.filter(role='student').first()
    if not test_student:
        print("❌ No student users found to test deletion.")
        return
    
    print(f"✅ Found test student: {test_student.username} (ID: {test_student.id})")
    
    # Create API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    # Try to delete the user
    response = client.delete(f'/api/users/{test_student.id}/')
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Data: {response.data if hasattr(response, 'data') else response.content}")
    
    if response.status_code == 204:
        print("✅ User deletion successful!")
        # Check if user was actually deleted
        if not CustomUser.objects.filter(id=test_student.id).exists():
            print("✅ User confirmed deleted from database")
        else:
            print("❌ User still exists in database")
    else:
        print(f"❌ User deletion failed with status {response.status_code}")

if __name__ == '__main__':
    test_delete_user()
