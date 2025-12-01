import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from myapp.ai_service import AIDocumentAnalyzer

print("=" * 80)
print("RE-PROCESSING REJECTED VOTER CERTIFICATE DOCUMENT")
print("=" * 80)

# Get the rejected voter document
doc = DocumentSubmission.objects.get(id=7)

print(f"\n📄 Document ID: {doc.id}")
print(f"👤 User: {doc.student.username}")
print(f"📝 Document Type: {doc.document_type}")
print(f"📊 Current Status: {doc.status}")
print(f"🤖 Current AI Score: {doc.ai_confidence_score}")

print("\n" + "=" * 80)
print("RUNNING NEW AI ANALYSIS")
print("=" * 80)

# Initialize AI service
ai_service = AIDocumentAnalyzer()

# Run analysis
result = ai_service.analyze_document(doc)

print(f"\n✅ Analysis Complete!")
print(f"📊 New Confidence Score: {result.get('confidence_score', 0)*100:.2f}%")
print(f"✅ Document Type Match: {result.get('document_type_match', False)}")
print(f"🤖 Should Auto-Approve: {result.get('auto_approve', False)}")

print("\n" + "=" * 80)
print("UPDATING DOCUMENT STATUS")
print("=" * 80)

# Update document with new analysis results
doc.ai_confidence_score = result.get('confidence_score', 0.0)
doc.ai_document_type_match = result.get('document_type_match', False)
doc.ai_analysis_completed = True
doc.ai_extracted_text = result.get('extracted_text', '')
doc.ai_key_information = result.get('key_information', {})
doc.ai_quality_assessment = result.get('quality_assessment', {})
doc.ai_recommendations = result.get('recommendations', [])

# Update status based on auto-approve decision
if result.get('auto_approve', False):
    doc.status = 'approved'
    doc.ai_auto_approved = True
    doc.reviewed_at = datetime.now()
    doc.admin_notes = "Auto-approved by Voter Certificate Verification Service with Advanced OCR"
    print("✅ Status changed to: APPROVED")
    print("🤖 Auto-approved: YES")
else:
    doc.status = 'pending'
    doc.ai_auto_approved = False
    doc.admin_notes = "Re-analyzed with Voter Certificate Verification Service - Requires manual review"
    print("⚠️ Status changed to: PENDING (Manual Review Required)")
    print("🤖 Auto-approved: NO")

# Build detailed analysis notes
analysis_notes = "\n".join([
    "🤖 AI VOTER CERTIFICATE VERIFICATION",
    "=" * 50,
    f"📅 Re-processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"⚡ Service: Voter Certificate Verification (YOLO + Advanced OCR)",
    f"🎯 AI Decision: {'✅ AUTO-APPROVED' if result.get('auto_approve') else '⚠️ NEEDS REVIEW'}",
    f"📊 Confidence Score: {result.get('confidence_score', 0)*100:.1f}%",
    "",
    "🔍 YOLO Detection Results:",
])

detected_elements = result.get('quality_assessment', {}).get('detected_elements', {})
for element_name, element_data in detected_elements.items():
    if element_data.get('present'):
        analysis_notes += f"\n   ✅ {element_name.replace('_', ' ').title()}: {element_data.get('confidence', 0)*100:.1f}%"

extracted_fields = result.get('key_information', {})
if extracted_fields and any(extracted_fields.values()):
    analysis_notes += "\n\n📋 Extracted Information:"
    for field_name, field_value in extracted_fields.items():
        if field_value:
            analysis_notes += f"\n   • {field_name.replace('_', ' ').title()}: {field_value}"

recommendations = result.get('recommendations', [])
if recommendations:
    analysis_notes += "\n\n💡 Recommendations:"
    for rec in recommendations:
        analysis_notes += f"\n   - {rec}"

doc.ai_analysis_notes = analysis_notes

# Save changes
doc.save()

print(f"\n✅ Document updated successfully!")
print(f"📊 AI Confidence Score: {doc.ai_confidence_score*100:.1f}%")
print(f"📊 Status: {doc.status.upper()}")
print(f"📝 Auto-Approved: {doc.ai_auto_approved}")

print("\n" + "=" * 80)
print("UPDATED DOCUMENT DETAILS")
print("=" * 80)

print(f"\n📄 Document ID: {doc.id}")
print(f"👤 User: {doc.student.username}")
print(f"📝 Document Type: {doc.document_type}")
print(f"📊 Status: {doc.status}")
print(f"🤖 AI Confidence: {doc.ai_confidence_score*100:.1f}%")
print(f"✅ Type Match: {doc.ai_document_type_match}")
print(f"🤖 Auto-Approved: {doc.ai_auto_approved}")
print(f"📅 Reviewed: {doc.reviewed_at}")

print("\n📋 Analysis Notes:")
print(doc.ai_analysis_notes)

print("\n" + "=" * 80)
print("RE-PROCESSING COMPLETE")
print("=" * 80)
