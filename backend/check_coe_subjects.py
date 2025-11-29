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
print("CHECKING COE SUBJECTS EXTRACTION")
print("=" * 80)

# Get all approved COEs
coes = DocumentSubmission.objects.filter(
    document_type='certificate_of_enrollment',
    status='approved'
).order_by('-submitted_at')

print(f"\nTotal approved COEs: {coes.count()}")

for idx, coe in enumerate(coes[:5], 1):  # Check first 5
    print(f"\n{'='*80}")
    print(f"COE #{idx}")
    print(f"{'='*80}")
    print(f"Student: {coe.student.username} ({coe.student.get_full_name()})")
    print(f"Submitted: {coe.submitted_at}")
    print(f"Status: {coe.status}")
    print(f"Subject count: {coe.subject_count}")
    print(f"Has extracted_subjects: {bool(coe.extracted_subjects)}")
    
    if coe.extracted_subjects:
        print(f"\nExtracted subjects ({len(coe.extracted_subjects)} subjects):")
        print(json.dumps(coe.extracted_subjects, indent=2))
    else:
        print("\n⚠️ WARNING: No extracted subjects!")
        print(f"Document file: {coe.document_file if hasattr(coe, 'document_file') else 'N/A'}")
        
print("\n" + "="*80)

# Check if any COE has missing subjects
coes_without_subjects = DocumentSubmission.objects.filter(
    document_type='certificate_of_enrollment',
    status='approved'
).filter(
    extracted_subjects__isnull=True
) | DocumentSubmission.objects.filter(
    document_type='certificate_of_enrollment',
    status='approved',
    extracted_subjects=[]
)

if coes_without_subjects.exists():
    print(f"\n⚠️ ISSUE FOUND: {coes_without_subjects.count()} approved COEs without extracted subjects!")
    print("\nAffected students:")
    for coe in coes_without_subjects:
        print(f"  - {coe.student.username}: {coe.student.get_full_name()}")
