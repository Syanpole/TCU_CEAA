"""
Check recent document submissions and rejection reasons
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("📄 RECENT DOCUMENT SUBMISSIONS")
print("=" * 80)

# Get submissions from the last 7 days
recent_submissions = DocumentSubmission.objects.filter(
    submitted_at__gte=timezone.now() - timedelta(days=7)
).order_by('-submitted_at')

if not recent_submissions.exists():
    print("\n❌ No submissions found in the last 7 days")
    print("\nChecking ALL submissions...")
    recent_submissions = DocumentSubmission.objects.all().order_by('-submitted_at')[:20]

print(f"\n📊 Found {recent_submissions.count()} recent submissions\n")

for doc in recent_submissions:
    print(f"\n{'=' * 80}")
    print(f"📄 Document ID: {doc.id}")
    print(f"👤 Student: {doc.student.username} ({doc.student.get_full_name()})")
    print(f"   Student ID: {doc.student.student_id}")
    print(f"📋 Document Type: {doc.get_document_type_display()}")
    print(f"📅 Submitted: {doc.submitted_at}")
    print(f"⚡ Status: {doc.status.upper()}")
    
    if hasattr(doc, 'ai_confidence_score') and doc.ai_confidence_score:
        print(f"🤖 AI Score: {doc.ai_confidence_score:.2f}%")
    
    # Check if rejected
    if doc.status == 'rejected':
        print(f"\n❌ REJECTION DETAILS:")
        print(f"   Reviewed by: {doc.reviewed_by.username if doc.reviewed_by else 'N/A'}")
        print(f"   Reviewed at: {doc.reviewed_at if doc.reviewed_at else 'N/A'}")
        
        if doc.admin_notes:
            print(f"   📝 Admin Notes: {doc.admin_notes}")
        else:
            print(f"   📝 Admin Notes: (No notes provided)")
        
        # Check AI analysis results
        if hasattr(doc, 'ai_analysis_result') and doc.ai_analysis_result:
            print(f"\n   🤖 AI Analysis Summary:")
            ai_result = doc.ai_analysis_result
            
            if isinstance(ai_result, dict):
                if 'verification_result' in ai_result:
                    verification = ai_result['verification_result']
                    print(f"      Status: {verification.get('status', 'N/A')}")
                    print(f"      Valid: {verification.get('is_valid', 'N/A')}")
                    print(f"      Confidence: {verification.get('confidence', 0) * 100:.2f}%")
                    
                    if 'recommendations' in verification:
                        print(f"      Recommendations:")
                        for rec in verification['recommendations']:
                            print(f"         • {rec}")
                    
                    if 'issues' in verification:
                        print(f"      Issues Found:")
                        for issue in verification['issues']:
                            print(f"         • {issue}")
                
                if 'algorithms_results' in ai_result:
                    print(f"\n      Algorithm Results:")
                    for algo_name, algo_data in ai_result['algorithms_results'].items():
                        if isinstance(algo_data, dict):
                            print(f"         {algo_data.get('name', algo_name)}: {algo_data.get('confidence', 0) * 100:.2f}%")
    
    elif doc.status == 'needs_review':
        print(f"\n⚠️ NEEDS MANUAL REVIEW")
        if doc.admin_notes:
            print(f"   📝 Notes: {doc.admin_notes}")
    
    elif doc.status == 'verified':
        print(f"\n✅ VERIFIED")
        if doc.reviewed_by:
            print(f"   Reviewed by: {doc.reviewed_by.username}")
    
    elif doc.status == 'pending':
        print(f"\n⏳ PENDING (Awaiting AI analysis)")
    
    elif doc.status == 'ai_processing':
        print(f"\n🤖 AI PROCESSING...")

print("\n" + "=" * 80)
print("\n📊 STATUS SUMMARY:")
status_counts = {}
for doc in recent_submissions:
    status_counts[doc.status] = status_counts.get(doc.status, 0) + 1

for status, count in status_counts.items():
    print(f"   {status.upper()}: {count}")

print("\n" + "=" * 80)
