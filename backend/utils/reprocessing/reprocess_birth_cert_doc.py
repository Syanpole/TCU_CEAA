import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.models import DocumentSubmission, CustomUser
from myapp.ai_service import AIDocumentAnalyzer

def main():
    print("="*80)
    print("REPROCESSING BIRTH CERTIFICATE WITH NEW VERIFICATION SERVICE")
    print("="*80)
    
    # Find the rejected birth certificate document
    # Looking for user 4peytonly (ID: 25) with rejected birth certificate
    try:
        doc = DocumentSubmission.objects.filter(
            document_type='birth_certificate',
            status='rejected'
        ).order_by('-submitted_at').first()
        
        if not doc:
            print("\n❌ No rejected birth certificate found!")
            return
        
        print(f"\n📄 Found Document:")
        print(f"   ID: {doc.id}")
        print(f"   Student: {doc.student.username} (ID: {doc.student.id})")
        print(f"   Type: {doc.document_type}")
        print(f"   Status: {doc.status}")
        print(f"   Current Confidence: {doc.ai_confidence_score*100:.1f}%")
        print(f"   File: {doc.document_file.name}")
        print(f"   Submitted: {doc.submitted_at}")
        
        if doc.ai_analysis_notes:
            print(f"\n📋 Previous Analysis Notes:")
            print(f"   {doc.ai_analysis_notes[:200]}...")
        
        # Confirm reprocessing
        print(f"\n{'='*80}")
        print("RUNNING AI ANALYSIS WITH NEW VERIFICATION SERVICE")
        print("="*80)
        
        # Initialize AI service
        ai_service = AIDocumentAnalyzer()
        
        # Run analysis (will automatically use birth certificate service and compare with user's application)
        analysis_result = ai_service.analyze_document(doc)
        
        # Update document with new analysis
        doc.ai_analysis_completed = True
        doc.ai_confidence_score = analysis_result.get('confidence_score', 0.0)
        doc.ai_document_type_match = analysis_result.get('document_type_match', False)
        doc.ai_extracted_text = analysis_result.get('extracted_text', '')[:5000]  # Limit to 5000 chars
        doc.ai_key_information = analysis_result.get('key_information', {})
        doc.ai_quality_assessment = analysis_result.get('quality_assessment', {})
        doc.ai_recommendations = analysis_result.get('recommendations', [])
        doc.ai_auto_approved = analysis_result.get('auto_approve', False)
        
        # Build analysis notes
        analysis_notes = '\n'.join(analysis_result.get('analysis_notes', []))
        doc.ai_analysis_notes = analysis_notes
        
        # Update status based on auto-approval
        old_status = doc.status
        if doc.ai_auto_approved:
            doc.status = 'approved'
            doc.reviewed_at = datetime.now()
            print(f"\n✅ Document AUTO-APPROVED!")
        else:
            doc.status = 'pending'
            print(f"\n⚠️ Document set to PENDING (needs manual review)")
        
        # Save changes
        doc.save()
        
        print(f"\n{'='*80}")
        print("REPROCESSING COMPLETE")
        print("="*80)
        print(f"\n📊 Results:")
        print(f"   Old Status: {old_status}")
        print(f"   New Status: {doc.status}")
        print(f"   Confidence: {doc.ai_confidence_score*100:.1f}%")
        print(f"   Document Type Match: {doc.ai_document_type_match}")
        print(f"   Auto-Approved: {doc.ai_auto_approved}")
        
        print(f"\n📋 Key Information Extracted:")
        for key, value in doc.ai_key_information.items():
            if value:
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n💡 Recommendations:")
        for rec in doc.ai_recommendations:
            print(f"   {rec}")
        
        print(f"\n📝 Analysis Notes:")
        print(analysis_notes)
        
        print(f"\n{'='*80}")
        print(f"✅ Document #{doc.id} successfully reprocessed!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
