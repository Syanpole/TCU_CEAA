import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission, FullApplication

print("=" * 80)
print("RECENT DOCUMENT SUBMISSIONS - LAST 20 DOCUMENTS")
print("=" * 80)

docs = DocumentSubmission.objects.all().order_by('-submitted_at')[:20]

for d in docs:
    print(f"\n{'='*80}")
    print(f"📄 Document ID: {d.id}")
    print(f"👤 User: {d.student.username} (User ID: {d.student.id})")
    print(f"📝 Document Type: {d.document_type}")
    print(f"📊 Status: {d.status}")
    print(f"🤖 AI Confidence Score: {d.ai_confidence_score}")
    print(f"📅 Submitted: {d.submitted_at}")
    print(f"✅ Reviewed: {d.reviewed_at or 'Not reviewed'}")
    
    if d.admin_notes:
        print(f"📝 Admin Notes: {d.admin_notes}")
    
    if d.ai_recommendations:
        print(f"\n🔍 AI Recommendations:")
        print(f"   {d.ai_recommendations[:300]}...")
    
    if d.ai_extracted_text:
        print(f"\n📝 AI Extracted Text (first 200 chars):")
        print(f"   {d.ai_extracted_text[:200]}...")
    
    if d.ai_key_information:
        print(f"\n🔑 AI Key Information:")
        print(f"   {d.ai_key_information[:200]}...")
    
    print(f"\n📊 AI Analysis Details:")
    print(f"   Auto-Approved: {d.ai_auto_approved}")
    print(f"   Analysis Completed: {d.ai_analysis_completed}")
    print(f"   Document Type Match: {d.ai_document_type_match}")
    print(f"   Quality Assessment: {d.ai_quality_assessment or 'N/A'}")
    
    print(f"\n📁 File Path: {d.document_file.name if d.document_file else 'No file'}")
    print("-" * 80)

print("\n" + "=" * 80)
print("RECENT APPLICATIONS - LAST 10")
print("=" * 80)

apps = FullApplication.objects.all().order_by('-submitted_at')[:10]

for app in apps:
    print(f"\n{'='*80}")
    print(f"📋 Application ID: {app.id}")
    print(f"👤 User: {app.user.username} (ID: {app.user.id})")
    print(f"📝 Status: {app.application_status}")
    print(f"📅 Submitted: {app.submitted_at}")
    print(f"🔒 Locked: {app.is_locked}")
    
    # Count documents
    from django.db.models import Q
    docs = DocumentSubmission.objects.filter(student__user=app.user, submitted_at__lte=app.submitted_at)
    pending = docs.filter(status='pending').count()
    approved = docs.filter(status='approved').count()
    rejected = docs.filter(status='rejected').count()
    
    print(f"\n📊 Documents Summary:")
    print(f"   Pending: {pending}")
    print(f"   Approved: {approved}")
    print(f"   Rejected: {rejected}")
    print(f"   Total: {docs.count()}")
    
    if rejected > 0:
        print(f"\n❌ Rejected Documents:")
        rejected_docs = docs.filter(status='rejected')
        for rd in rejected_docs:
            print(f"      - {rd.document_type}: {rd.rejection_reason or 'No reason specified'}")
    
    print("-" * 80)

print("\n" + "=" * 80)
print("END OF REPORT")
print("=" * 80)
