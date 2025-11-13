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
    print("REPROCESSING VOTER CERTIFICATE WITH FIELD COMPARISON")
    print("="*80)
    
    # Get the voter certificate document
    try:
        doc = DocumentSubmission.objects.get(id=7)
        
        print(f"\n📄 Found Document:")
        print(f"   ID: {doc.id}")
        print(f"   Student: {doc.student.username} (ID: {doc.student.id})")
        print(f"   Type: {doc.document_type}")
        print(f"   Status: {doc.status}")
        print(f"   Current Confidence: {doc.ai_confidence_score*100:.1f}%")
        print(f"   File: {doc.document_file.name}")
        print(f"   Submitted: {doc.submitted_at}")
        
        # Get user's full application for comparison
        from myapp.models import FullApplication
        full_app = FullApplication.objects.filter(user=doc.student).order_by('-id').first()
        
        if full_app:
            print(f"\n📋 User's Application Data:")
            print(f"   Name: {full_app.first_name} {full_app.middle_name} {full_app.last_name}")
            print(f"   Address: {full_app.house_no} {full_app.street}, {full_app.barangay}")
            print(f"   District: {full_app.district}")
        
        # Confirm reprocessing
        print(f"\n{'='*80}")
        print("RUNNING AI ANALYSIS WITH FIELD COMPARISON")
        print("="*80)
        
        # Initialize AI service
        ai_service = AIDocumentAnalyzer()
        
        # Run analysis (will automatically use voter certificate service and compare with user's application)
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
        old_confidence = doc.ai_confidence_score
        
        if doc.ai_auto_approved and doc.status != 'approved':
            doc.status = 'approved'
            doc.reviewed_at = datetime.now()
        
        # Save changes
        doc.save()
        
        print(f"\n{'='*80}")
        print("REPROCESSING COMPLETE")
        print("="*80)
        print(f"\n📊 Results:")
        print(f"   Status: {old_status} → {doc.status}")
        print(f"   Confidence: {old_confidence*100:.1f}% → {doc.ai_confidence_score*100:.1f}%")
        print(f"   Document Type Match: {doc.ai_document_type_match}")
        print(f"   Auto-Approved: {doc.ai_auto_approved}")
        
        # Check for field matches
        field_matches = doc.ai_quality_assessment.get('field_matches', {})
        if field_matches:
            print(f"\n🔍 Field Comparison Results:")
            for field_name, match_info in field_matches.items():
                match_icon = "✅" if match_info.get('match') else "❌"
                score = match_info.get('score', 0.0) * 100
                print(f"   {match_icon} {field_name.replace('_', ' ').title()}: {score:.1f}% match")
                print(f"      Extracted:   {match_info.get('extracted', 'N/A')}")
                print(f"      Application: {match_info.get('application', 'N/A')}")
        else:
            print(f"\n⚠️ No field comparison performed")
        
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
        print(f"✅ Document #{doc.id} successfully reprocessed with field comparison!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
