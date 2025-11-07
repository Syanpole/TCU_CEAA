import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, FullApplication
from myapp.serializers import FullApplicationSerializer
from django.test import RequestFactory
from rest_framework.test import force_authenticate

# Create a test user
try:
    user = CustomUser.objects.get(username='testuser')
except CustomUser.DoesNotExist:
    user = CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass',
        role='student',
        student_id='21-12345',
        first_name='Test',
        last_name='User'
    )

print(f"✅ User created/found: {user.username}")

# Create test application data (similar to frontend submission)
test_data = {
    'facebook_link': '',
    'application_type': 'new',
    'scholarship_type': 'TCU-CEAA',
    'school_year': '2024-2025',
    'semester': '1st',
    'applying_for_merit': '',
    
    # Personal Information
    'first_name': 'QWEQWE',
    'middle_name': '',
    'last_name': 'QWEQWE',
    'house_no': 'QWEQWE',
    'street': 'QWEQWE',
    'zip_code': '123456',
    'barangay': 'QWEQWE',
    'district': '',
    'mobile_no': '09234545678',
    'other_contact': '',
    'email': 'test@example.com',
    'date_of_birth': '2000-01-01',
    'age': 24,
    'citizenship': 'Filipino',
    'sex': 'Male',
    'marital_status': 'Single',
    'religion': 'Catholic',
    'place_of_birth': 'Taguig City',
    'years_of_residency': '24',
    
    # School Information
    'course_name': 'QWEQWE',
    'ladderized': 'NO',
    'year_level': '4th Year',
    'swa_input': '',
    'units_enrolled': '21',
    'course_duration': '4 years',
    'school_name': 'TAGUIG CITY UNIVERSITY (TCU)',
    'school_address': 'Gen. Santos Ave., Central Bicutan, Taguig City',
    'graduating_this_term': 'Yes',
    'semesters_to_graduate': '',
    'with_honors': '',
    'transferee': 'NO',
    'shiftee': 'NO',
    'status': 'Living',
    
    # Educational Background
    'shs_attended': '',
    'shs_type': '',
    'shs_address': '',
    'shs_years': '',
    'shs_honors': '',
    'jhs_attended': '',
    'jhs_type': '',
    'jhs_address': '',
    'jhs_years': '',
    'jhs_honors': '',
    'elem_attended': '',
    'elem_type': '',
    'elem_address': '',
    'elem_years': '',
    'elem_honors': '',
    
    # Parents Information
    'father_name': 'QWEQWEQWE',
    'father_address': 'QWEQWEQWE',
    'father_contact': '09234545678',
    'father_occupation': 'QWEQWEQWE',
    'father_place_of_work': 'QWEQWEQW',
    'father_education': 'College Graduate',
    'father_deceased': False,
    'mother_name': 'QWEQWEQWE',
    'mother_address': 'QWEQWEQWE',
    'mother_contact': '09234545678',
    'mother_occupation': 'QWEQWEQWE',
    'mother_place_of_work': 'QWEQWEQW',
    'mother_education': 'College Graduate',
    'mother_deceased': False,
    
    # Status
    'is_submitted': True,
    'is_locked': True
}

print("\n📤 Testing full application submission...")

# Create a fake request
factory = RequestFactory()
request = factory.post('/api/full-application/')
request.user = user

# Create serializer with request context
serializer = FullApplicationSerializer(data=test_data, context={'request': request})

if serializer.is_valid():
    print("✅ Validation passed!")
    application = serializer.save()
    print(f"✅ Application created successfully with ID: {application.id}")
    print(f"   School Year: {application.school_year}")
    print(f"   Semester: {application.semester}")
    print(f"   Submitted: {application.is_submitted}")
    print(f"   Locked: {application.is_locked}")
else:
    print("❌ Validation failed!")
    print("\nErrors:")
    for field, errors in serializer.errors.items():
        print(f"  {field}: {errors}")
    
    print("\n🔍 Error details:")
    import json
    print(json.dumps(dict(serializer.errors), indent=2, default=str))
