import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.test import RequestFactory
from myapp.views import send_verification_code
import json

# Create a test request
factory = RequestFactory()

# Test with a valid email
email = "testuser@gmail.com"
request = factory.post('/api/auth/send-verification-code/', 
                       data=json.dumps({'email': email}),
                       content_type='application/json')

# Call the view
response = send_verification_code(request)

print(f"Status Code: {response.status_code}")
print(f"Response Data: {response.data}")
print(f"\nSuccess: {'success' in response.data}")
if 'success' in response.data:
    print(f"Success Value: {response.data['success']}")
if 'error' in response.data:
    print(f"Error: {response.data['error']}")
if 'message' in response.data:
    print(f"Message: {response.data['message']}")
