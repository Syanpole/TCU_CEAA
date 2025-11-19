"""
Test the new check_grade_submission_eligibility endpoint
"""
import os
import django

os.chdir('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.test import RequestFactory
from myapp.views import check_grade_submission_eligibility
from myapp.models import CustomUser

# Get 4peytonly user
user = CustomUser.objects.get(username='4peytonly')

# Create a mock request
factory = RequestFactory()
request = factory.get('/api/grades/check-eligibility/')
request.user = user

# Call the endpoint
response = check_grade_submission_eligibility(request)

print(f"Status Code: {response.status_code}")
print(f"Response Data:")
print(response.data)
