import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TESTING COE SUBJECTS API ENDPOINT SIMULATION")
print("=" * 80)

# Get the user (4peytonly)
user = User.objects.get(username='4peytonly')
print(f"\nUser: {user.username} ({user.get_full_name()})")
print(f"Student ID: {user.student_id}")

# Simulate the get_coe_subjects API call
coe_document = DocumentSubmission.objects.filter(
    student=user,
    document_type='certificate_of_enrollment',
    status='approved'
).order_by('-submitted_at').first()

if not coe_document:
    print("\n❌ ERROR: No approved Certificate of Enrollment found")
    exit(1)

print(f"\n✅ Found COE document (ID: {coe_document.id})")
print(f"Submitted: {coe_document.submitted_at}")

# Check if subjects have been extracted
if not coe_document.extracted_subjects or coe_document.subject_count == 0:
    print("\n❌ ERROR: No subjects found in COE")
    print("This would cause the grade submission form to fail!")
    exit(1)

print(f"\n✅ Subjects extracted: {coe_document.subject_count} subjects")
print("\nAPI Response would return:")
print(json.dumps({
    'subjects': coe_document.extracted_subjects,
    'subject_count': coe_document.subject_count,
    'coe_document_id': coe_document.id,
    'coe_submitted_at': str(coe_document.submitted_at)
}, indent=2))

print("\n" + "=" * 80)
print("✅ GRADE SUBMISSION FORM WILL WORK!")
print("=" * 80)
print("\nThe form will display these subjects for grade submission:")
for idx, subject in enumerate(coe_document.extracted_subjects, 1):
    print(f"  {idx}. {subject['subject_code']} - {subject['subject_name']}")
