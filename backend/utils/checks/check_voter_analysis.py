import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.models import DocumentSubmission
import json

def main():
    print("="*80)
    print("CHECKING VOTER CERTIFICATE DOCUMENT ANALYSIS")
    print("="*80)
    
    # Get the voter certificate document
    doc = DocumentSubmission.objects.get(id=7)
    
    print(f"\n📄 Document Details:")
    print(f"   ID: {doc.id}")
    print(f"   Student: {doc.student.username} (ID: {doc.student.id})")
    print(f"   Type: {doc.document_type}")
    print(f"   Status: {doc.status}")
    print(f"   Confidence: {doc.ai_confidence_score*100:.1f}%")
    print(f"   Auto-Approved: {doc.ai_auto_approved}")
    
    print(f"\n📋 Extracted Key Information:")
    if doc.ai_key_information:
        for key, value in doc.ai_key_information.items():
            if value:
                print(f"   • {key.replace('_', ' ').title()}: {value}")
    else:
        print("   No key information extracted")
    
    print(f"\n🔍 Quality Assessment:")
    if doc.ai_quality_assessment:
        print(json.dumps(doc.ai_quality_assessment, indent=2))
        
        # Check if field_matches exists
        if 'field_matches' in doc.ai_quality_assessment:
            print(f"\n✅ Field Matches Found!")
            field_matches = doc.ai_quality_assessment['field_matches']
            if field_matches:
                print(f"\n📊 Field Comparison Results:")
                for field_name, match_info in field_matches.items():
                    match_icon = "✅" if match_info.get('match') else "❌"
                    score = match_info.get('score', 0.0) * 100
                    print(f"   {match_icon} {field_name.replace('_', ' ').title()}: {score:.1f}% match")
                    print(f"      Extracted:   {match_info.get('extracted', 'N/A')}")
                    print(f"      Application: {match_info.get('application', 'N/A')}")
            else:
                print("   No field matches data")
        else:
            print(f"\n❌ NO Field Matches - Document was processed BEFORE comparison feature was added")
    
    print(f"\n📝 Analysis Notes:")
    if doc.ai_analysis_notes:
        print(doc.ai_analysis_notes)
    else:
        print("   No analysis notes")
    
    print(f"\n💡 Recommendations:")
    if doc.ai_recommendations:
        for rec in doc.ai_recommendations:
            print(f"   {rec}")
    else:
        print("   No recommendations")

if __name__ == "__main__":
    main()
