"""
Extract subjects from approved COE documents
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from myapp.coe_verification_service import get_coe_verification_service

print("=" * 80)
print("EXTRACTING SUBJECTS FROM COE DOCUMENTS")
print("=" * 80)

# Get all approved COEs
coes = DocumentSubmission.objects.filter(
    document_type='certificate_of_enrollment',
    status='approved'
).order_by('-submitted_at')

print(f"\nFound {coes.count()} approved COE documents\n")

coe_service = get_coe_verification_service()

for coe in coes:
    print(f"\n{'='*80}")
    print(f"COE ID: {coe.id}")
    print(f"Student: {coe.student.username} ({coe.student.get_full_name()})")
    print(f"Current subject count: {coe.subject_count}")
    print(f"Current subjects: {coe.extracted_subjects}")
    
    # Get file path
    try:
        from myapp.s3_utils import get_file_path_for_processing, cleanup_temp_file
        
        file_path, is_temp = get_file_path_for_processing(coe.document_file)
        print(f"File: {file_path}")
        
        # Extract subjects
        print("\n🔍 Extracting subjects...")
        subject_result = coe_service.extract_subject_list(file_path)
        
        if subject_result['success'] and subject_result['subjects']:
            print(f"✅ Extracted {subject_result['subject_count']} subjects!")
            
            for i, subj in enumerate(subject_result['subjects'], 1):
                print(f"  {i}. {subj['subject_code']} - {subj['subject_name']}")
            
            # Update database
            coe.extracted_subjects = subject_result['subjects']
            coe.subject_count = subject_result['subject_count']
            coe.save()
            print(f"\n💾 Updated database with {coe.subject_count} subjects")
        else:
            print(f"❌ Failed to extract subjects")
            if subject_result.get('errors'):
                print(f"Errors: {subject_result['errors']}")
        
        # Cleanup temp file
        if is_temp:
            cleanup_temp_file(file_path)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("EXTRACTION COMPLETE")
print("=" * 80)
