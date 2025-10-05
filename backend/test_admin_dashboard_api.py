import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from myapp.views import admin_dashboard_data

User = get_user_model()

# Get admin user
admin_user = User.objects.get(username='admin')

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
