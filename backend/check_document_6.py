import sys
sys.path.insert(0, '.')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
import django
django.setup()

from myapp.models import Document
import json

# Get document 6
doc = Document.objects.get(id=6)

print(f'\n{"="*80}')
print(f'DOCUMENT 6 DETAILS')
print(f'{"="*80}')
print(f'User: {doc.user.username} ({doc.user.first_name} {doc.user.last_name})')
print(f'Student ID: {doc.user.student_id}')
print(f'Document Type: {doc.document_type}')
print(f'Status: {doc.verification_status}')
print(f'Confidence: {doc.ai_confidence_score}')
print(f'Uploaded: {doc.uploaded_at}')
print(f'File: {doc.file.name}')

print(f'\n{"="*80}')
print(f'REJECTION REASON:')
print(f'{"="*80}')
print(doc.rejection_reason)

print(f'\n{"="*80}')
print(f'AI ANALYSIS RESULT:')
print(f'{"="*80}')
if doc.ai_analysis_result:
    try:
        analysis = json.loads(doc.ai_analysis_result)
        print(json.dumps(analysis, indent=2))
    except:
        print(doc.ai_analysis_result)
else:
    print("None")

# Get user application data
print(f'\n{"="*80}')
print(f'USER APPLICATION DATA:')
print(f'{"="*80}')
print(f'First Name: {doc.user.first_name}')
print(f'Middle Name: {doc.user.middle_name}')
print(f'Last Name: {doc.user.last_name}')
print(f'Date of Birth: {doc.user.date_of_birth}')
print(f'Place of Birth: {doc.user.place_of_birth}')
print(f'Father Name: {doc.user.father_name}')
print(f'Mother Name: {doc.user.mother_name}')
