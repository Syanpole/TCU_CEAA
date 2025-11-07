"""
Test the API response format for full applications
"""
import os
import django
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.serializers import FullApplicationSerializer
from myapp.models import FullApplication
from django.test import RequestFactory

# Create a mock request
factory = RequestFactory()
request = factory.get('/api/full-application/')

# Get all applications
applications = FullApplication.objects.all().select_related('user')

print(f"📊 Found {applications.count()} full applications\n")

# Serialize the data
serializer = FullApplicationSerializer(applications, many=True, context={'request': request})
data = serializer.data

print("📤 API Response Format:")
print(json.dumps(data, indent=2, default=str))

print("\n✅ Sample application structure:")
if data:
    print(f"   - ID: {data[0]['id']}")
    print(f"   - User: {data[0]['user']}")
    print(f"   - School Year: {data[0]['school_year']}")
    print(f"   - Semester: {data[0]['semester']}")
    print(f"   - Email: {data[0]['email']}")
    print(f"   - Submitted: {data[0]['is_submitted']}")
    print(f"   - Locked: {data[0]['is_locked']}")
