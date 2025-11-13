import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission

print("=" * 80)
print("REJECTED DOCUMENTS ANALYSIS")
print("=" * 80)

rejected_docs = DocumentSubmission.objects.filter(status='rejected').order_by('-submitted_at')[:10]

print(f"\nFound {rejected_docs.count()} rejected documents")

for d in rejected_docs:
    print(f"\n{'='*80}")
    print(f"📄 Document ID: {d.id}")
    print(f"👤 User: {d.student.username} (ID: {d.student.id})")
    print(f"📝 Document Type: {d.document_type}")
    print(f"📊 Status: {d.status}")
    print(f"📅 Submitted: {d.submitted_at}")
    print(f"✅ Reviewed: {d.reviewed_at}")
    print(f"👨‍💼 Reviewed By: {d.reviewed_by.username if d.reviewed_by else 'Auto-rejected by AI'}")
    
    print(f"\n🤖 AI Analysis:")
    print(f"   Confidence Score: {d.ai_confidence_score}")
    print(f"   Auto-Approved: {d.ai_auto_approved}")
    print(f"   Analysis Completed: {d.ai_analysis_completed}")
    print(f"   Document Type Match: {d.ai_document_type_match}")
    
    if d.admin_notes:
        print(f"\n📝 Admin Notes/Rejection Reason:")
        print(f"   {d.admin_notes}")
    
    if d.ai_recommendations:
        print(f"\n🔍 AI Recommendations:")
        if isinstance(d.ai_recommendations, list):
            for rec in d.ai_recommendations[:5]:
                print(f"   - {rec}")
        else:
            print(f"   {d.ai_recommendations}")
    
    if d.ai_analysis_notes:
        print(f"\n📋 AI Analysis Notes:")
        print(f"   {d.ai_analysis_notes[:300]}...")
    
    if d.ai_extracted_text:
        print(f"\n📝 Extracted Text (first 300 chars):")
        print(f"   {d.ai_extracted_text[:300]}...")
    
    if d.ai_key_information:
        print(f"\n🔑 Key Information Extracted:")
        if isinstance(d.ai_key_information, dict):
            for key, value in list(d.ai_key_information.items())[:5]:
                print(f"   {key}: {value}")
        else:
            print(f"   {d.ai_key_information}")
    
    print(f"\n📁 File: {d.document_file.name}")
    print("-" * 80)

print("\n" + "=" * 80)
print("SUMMARY OF REJECTION REASONS")
print("=" * 80)

for d in rejected_docs:
    print(f"\nDoc #{d.id} ({d.document_type}):")
    if d.admin_notes:
        print(f"  Reason: {d.admin_notes[:200]}")
    elif not d.ai_document_type_match:
        print(f"  Reason: Document type mismatch (AI Confidence: {d.ai_confidence_score})")
    elif d.ai_confidence_score < 0.7:
        print(f"  Reason: Low AI confidence score ({d.ai_confidence_score})")
    else:
        print(f"  Reason: Unknown (AI Confidence: {d.ai_confidence_score})")
