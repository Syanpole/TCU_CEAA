"""
Re-process rejected document with new verification system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from myapp.id_verification_service import get_id_verification_service
from myapp.audit_logger import audit_logger
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

print("=" * 80)
print("🔄 RE-PROCESSING REJECTED DOCUMENT")
print("=" * 80)

# Get the rejected document
try:
    document = DocumentSubmission.objects.get(id=5)
    print(f"\n📄 Document Details:")
    print(f"   ID: {document.id}")
    print(f"   Student: {document.student.get_full_name()} ({document.student.student_id})")
    print(f"   Type: {document.get_document_type_display()}")
    print(f"   Current Status: {document.status}")
    print(f"   File: {document.document_file.path}")
except DocumentSubmission.DoesNotExist:
    print("\n❌ Document ID 5 not found")
    exit()

print(f"\n{'=' * 80}")
print("🤖 RUNNING NEW ID VERIFICATION SERVICE")
print("=" * 80)

# Initialize ID verification service
id_service = get_id_verification_service()

# Prepare student data
student_data = {
    'name': f"{document.student.first_name} {document.student.last_name}",
    'student_id': document.student.student_id if hasattr(document.student, 'student_id') else None
}

print(f"\n🔍 Verifying ID document...")
print(f"   Student Name: {student_data['name']}")
print(f"   Student ID: {student_data['student_id']}")

# Run verification
try:
    id_result = id_service.verify_id_card(
        image_path=document.document_file.path,
        document_type=document.document_type,
        user=document.student
    )
    
    print(f"\n✅ VERIFICATION COMPLETED!")
    print(f"\n📊 Results:")
    print(f"   Status: {id_result.get('status', 'UNKNOWN')}")
    print(f"   Confidence: {id_result.get('confidence', 0):.1%}")
    print(f"   Is Valid: {id_result.get('is_valid', False)}")
    print(f"   Checks Passed: {id_result.get('checks_passed', 0)}")
    print(f"   Success: {id_result.get('success', False)}")
    
    if id_result.get('identity_verification'):
        identity = id_result['identity_verification']
        print(f"\n   Identity Verification:")
        print(f"      Match: {identity.get('match', False)}")
        print(f"      Message: {identity.get('message', 'N/A')}")
    
    if id_result.get('errors'):
        print(f"\n   ⚠️ Errors:")
        for error in id_result['errors']:
            print(f"      • {error}")
    
    # Determine new status
    confidence = id_result.get('confidence', 0.0)
    is_valid = id_result.get('is_valid', False)
    checks_passed = id_result.get('checks_passed', 0)
    
    if is_valid and confidence >= 0.70:
        new_status = 'approved'
        status_msg = "AUTO-APPROVED ✅"
    elif confidence >= 0.50 or checks_passed >= 5:
        new_status = 'needs_review'
        status_msg = "NEEDS REVIEW ⚠️"
    else:
        new_status = 'rejected'
        status_msg = "AUTO-REJECTED ❌"
    
    print(f"\n🎯 New Status: {status_msg}")
    print(f"   Reason: Confidence {confidence:.1%}, Checks {checks_passed}, Valid: {is_valid}")
    
    # Update document
    document.status = new_status
    document.ai_auto_approved = (new_status == 'approved')
    document.ai_confidence_score = confidence
    document.ai_analysis_completed = True
    document.reviewed_at = timezone.now()
    
    # Build comprehensive notes
    notes_parts = [
        f"ID Verification ({status_msg})",
        f"Re-processed with new system: {timezone.now()}",
        f"Status: {id_result.get('status', 'UNKNOWN')}",
        f"Confidence: {confidence:.1%}",
        f"Checks Passed: {checks_passed}",
    ]
    
    if id_result.get('identity_verification'):
        identity = id_result['identity_verification']
        notes_parts.append(f"Identity Match: {identity.get('match', False)} - {identity.get('message', '')}")
    
    if id_result.get('extracted_fields'):
        notes_parts.append(f"\nExtracted Fields:")
        for field, value in id_result['extracted_fields'].items():
            if value:
                notes_parts.append(f"  {field}: {value}")
    
    if id_result.get('errors'):
        notes_parts.append(f"\nErrors: {', '.join(id_result['errors'])}")
    
    if id_result.get('recommendations'):
        notes_parts.append(f"\nRecommendations: {', '.join(id_result['recommendations'])}")
    
    document.ai_analysis_notes = "\n".join(notes_parts)
    document.save()
    
    print(f"\n💾 Document updated in database")
    
    # Log the re-analysis
    audit_logger.log_ai_analysis(
        user=document.student,
        target_model='DocumentSubmission',
        target_id=document.id,
        analysis_type='id_verification_reprocess',
        results={
            'confidence_score': confidence,
            'status': new_status,
            'is_valid': is_valid,
            'service_used': 'ID Verification Service (YOLO + Advanced OCR + Identity Matching)',
            'name_match': id_result.get('name_match', False),
            'id_match': id_result.get('id_match', False),
            'reprocessed': True
        },
        request=None
    )
    
    if new_status == 'approved':
        audit_logger.log_document_approved(document.student, document, None, auto_approved=True)
    elif new_status == 'rejected':
        rejection_reason = f"AI confidence too low: {confidence:.1%}, Checks passed: {checks_passed}"
        if id_result.get('errors'):
            rejection_reason += f". Errors: {', '.join(id_result['errors'])}"
        
        audit_logger.log_document_rejected(
            admin_user=document.student,
            document=document,
            reason=rejection_reason,
            request=None,
            auto_rejected=True
        )
    
    print(f"📝 Audit logs created")
    
    if 'detected_elements' in id_result:
        print(f"\n🔍 Detected Elements:")
        for element, conf in id_result['detected_elements'].items():
            print(f"   {element}: {conf:.1%}")
    
    if 'extracted_text' in id_result and id_result['extracted_text']:
        print(f"\n📝 Extracted Text:")
        print(f"   {id_result['extracted_text'][:200]}...")
    
    print(f"\n{'=' * 80}")
    print("✅ RE-PROCESSING COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    print(f"\nFull traceback:")
    print(traceback.format_exc())
