"""
Check Document Processing Details
Show which AI services were used and why
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

import django
django.setup()

from myapp.models import DocumentSubmission
from django.contrib.auth import get_user_model

User = get_user_model()

def check_document_processing():
    """Check how documents were processed."""
    
    print("=" * 80)
    print("DOCUMENT PROCESSING ANALYSIS")
    print("=" * 80)
    
    # Get recent documents
    docs = DocumentSubmission.objects.all().order_by('-submitted_at')[:10]
    
    print(f"\nFound {docs.count()} recent documents\n")
    
    for doc in docs:
        print(f"\n{'=' * 80}")
        print(f"Document ID: {doc.id}")
        print(f"Type: {doc.get_document_type_display()}")
        print(f"Status: {doc.status}")
        print(f"Confidence: {doc.ai_confidence_score * 100:.1f}%")
        print(f"Auto-approved: {doc.ai_auto_approved}")
        print(f"AI Analysis Completed: {doc.ai_analysis_completed}")
        print(f"Submitted: {doc.submitted_at}")
        print(f"Reviewed: {doc.reviewed_at}")
        
        if doc.ai_analysis_notes:
            print(f"\n📝 AI Analysis Notes:")
            print("-" * 80)
            # Show first 500 chars
            notes = doc.ai_analysis_notes[:500]
            if len(doc.ai_analysis_notes) > 500:
                notes += "..."
            print(notes)
    
    # Check AI service status
    print(f"\n\n{'=' * 80}")
    print("AI SERVICE STATUS")
    print("=" * 80)
    
    from myapp.advanced_ocr_service import get_advanced_ocr_service
    from myapp.coe_verification_service import get_coe_verification_service
    
    ocr_service = get_advanced_ocr_service()
    print(f"\n✅ Advanced OCR (AWS Textract):")
    print(f"   - Enabled: {ocr_service.is_enabled()}")
    print(f"   - Region: {ocr_service.region}")
    
    coe_service = get_coe_verification_service()
    coe_status = coe_service.get_verification_status()
    print(f"\n📋 COE Verification Service:")
    print(f"   - YOLO Detection: {coe_status.get('coe_detection')}")
    print(f"   - OCR Available: {coe_status.get('ocr_available')}")
    print(f"   - Advanced OCR: {coe_status.get('advanced_ocr_enabled')}")
    print(f"   - OCR Method: {coe_status.get('ocr_method')}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    check_document_processing()
