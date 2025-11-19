import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission, CustomUser

# Get user
user = CustomUser.objects.get(username='4peytonly')
print(f'User: {user.username} (ID: {user.id}, Student ID: {user.student_id})')

# Check approved documents
print('\n=== Approved Documents ===')
docs = DocumentSubmission.objects.filter(student=user, status='approved')
for doc in docs:
    subjects_count = len(doc.extracted_subjects) if doc.extracted_subjects else 0
    print(f'- {doc.document_type}: Status={doc.status}, Subject_Count={doc.subject_count}, Extracted_Length={subjects_count}')

# COE Details
print('\n=== COE Document Details ===')
coe = docs.filter(document_type='certificate_of_enrollment').first()
if coe:
    print(f'COE ID: {coe.id}')
    print(f'Status: {coe.status}')
    print(f'Subject Count Field: {coe.subject_count}')
    print(f'Extracted Subjects: {coe.extracted_subjects}')
    
    # Check if eligible
    has_coe = docs.filter(document_type='certificate_of_enrollment').exists()
    has_id = docs.filter(document_type__in=['student_id', 'government_id', 'school_id', 'birth_certificate', 'voters_id']).exists()
    
    print(f'\n=== Eligibility Check ===')
    print(f'Has approved COE: {has_coe}')
    print(f'Has approved ID document: {has_id}')
    print(f'Can submit grades: {has_coe and has_id}')
else:
    print('No approved COE found!')
