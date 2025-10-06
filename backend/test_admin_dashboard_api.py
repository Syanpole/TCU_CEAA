"""
Admin Dashboard API Test - Manual Test Script
This is NOT a Django test case - it's a manual testing script.
Rename to avoid Django test discovery (doesn't start with 'test_' at root level).
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from myapp.views import admin_dashboard_data

User = get_user_model()


def run_manual_test():
    """Manual test function - only runs when script is executed directly"""
    # Get admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Admin user not found. Please create an admin user first.")
        return

    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/dashboard/admin/')
    request.user = admin_user

    # Test the view
    try:
        response = admin_dashboard_data(request)
        print(f"✅ API Response Status: {response.status_code}")
        print(f"✅ Response Data:")
        import json
        print(json.dumps(response.data, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_manual_test()
