import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from myapp.coe_verification_service import get_coe_verification_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("EXTRACTING SUBJECTS FROM COEs WITHOUT SUBJECTS")
print("=" * 80)

# Find approved COEs without extracted subjects
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

if not coes_without_subjects.exists():
    print("\n✅ All approved COEs have extracted subjects!")
    exit(0)

print(f"\nFound {coes_without_subjects.count()} COEs without subjects")

# Initialize COE service
coe_service = get_coe_verification_service()

for coe in coes_without_subjects:
    print(f"\n{'='*80}")
    print(f"Processing COE for: {coe.student.username} ({coe.student.get_full_name()})")
    print(f"Submitted: {coe.submitted_at}")
    print(f"Document ID: {coe.id}")
    
    try:
        # Get the file path
        file_path = coe.document_file.path if hasattr(coe.document_file, 'path') else None
        
        if not file_path:
            print("❌ No file path available")
            continue
        
        print(f"File path: {file_path}")
        
        # Extract subjects
        print("🔍 Extracting subjects...")
        subject_result = coe_service.extract_subject_list(file_path)
        
        if subject_result['success'] and subject_result['subjects']:
            print(f"✅ Successfully extracted {subject_result['subject_count']} subjects!")
            print(f"Confidence: {subject_result['confidence']:.2%}")
            
            # Display extracted subjects
            print("\nExtracted subjects:")
            for idx, subject in enumerate(subject_result['subjects'], 1):
                print(f"  {idx}. {subject['subject_code']} - {subject['subject_name']}")
            
            # Save to database
            coe.extracted_subjects = subject_result['subjects']
            coe.subject_count = subject_result['subject_count']
            coe.save()
            
            print("\n💾 Subjects saved to database!")
            
        else:
            print(f"❌ Failed to extract subjects")
            if subject_result.get('errors'):
                print(f"Errors: {', '.join(subject_result['errors'])}")
    
    except Exception as e:
        print(f"❌ Error processing COE: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("EXTRACTION COMPLETE")
print("="*80)
