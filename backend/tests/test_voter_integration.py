import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from myapp.ai_service import AIDocumentAnalyzer

print("=" * 80)
print("TESTING VOTER CERTIFICATE INTEGRATION IN AI SERVICE")
print("=" * 80)

# Get the rejected voter document
doc = DocumentSubmission.objects.get(id=7)

print(f"\n📄 Document ID: {doc.id}")
print(f"👤 User: {doc.student.username}")
print(f"📝 Document Type: {doc.document_type}")
print(f"📊 Current Status: {doc.status}")
print(f"📁 File: {doc.document_file.name}")

print("\n" + "=" * 80)
print("RUNNING AI ANALYSIS WITH VOTER CERTIFICATE SERVICE")
print("=" * 80)

# Initialize AI service
ai_service = AIDocumentAnalyzer()

# Run analysis
print("\n🔍 Analyzing document with integrated voter certificate service...\n")
result = ai_service.analyze_document(doc)

print("\n" + "=" * 80)
print("ANALYSIS RESULTS")
print("=" * 80)

print(f"\n📊 Confidence Score: {result.get('confidence_score', 0)*100:.2f}%")
print(f"✅ Document Type Match: {result.get('document_type_match', False)}")
print(f"🤖 Auto-Approve: {result.get('auto_approve', False)}")

print(f"\n📋 Analysis Notes:")
for note in result.get('analysis_notes', []):
    print(f"   {note}")

print(f"\n🔑 Key Information Extracted:")
key_info = result.get('key_information', {})
if key_info:
    for key, value in key_info.items():
        print(f"   {key}: {value}")
else:
    print("   (No key information extracted)")

print(f"\n💡 Recommendations:")
recommendations = result.get('recommendations', [])
if recommendations:
    for rec in recommendations:
        print(f"   - {rec}")
else:
    print("   (No recommendations)")

print(f"\n📝 Extracted Text (first 300 chars):")
extracted_text = result.get('extracted_text', '')
if extracted_text:
    print(f"   {extracted_text[:300]}...")
else:
    print("   (No text extracted)")

print("\n" + "=" * 80)
print("RECOMMENDED ACTION")
print("=" * 80)

if result.get('auto_approve'):
    print("\n✅ DOCUMENT SHOULD BE AUTO-APPROVED")
    print(f"   Confidence: {result.get('confidence_score', 0)*100:.1f}%")
    print(f"   Status: Document meets all criteria for automatic approval")
elif result.get('document_type_match'):
    print("\n⚠️ DOCUMENT NEEDS MANUAL REVIEW")
    print(f"   Confidence: {result.get('confidence_score', 0)*100:.1f}%")
    print(f"   Status: Document type matches but requires human verification")
else:
    print("\n❌ DOCUMENT SHOULD BE REJECTED")
    print(f"   Confidence: {result.get('confidence_score', 0)*100:.1f}%")
    print(f"   Status: Document does not match expected type")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
