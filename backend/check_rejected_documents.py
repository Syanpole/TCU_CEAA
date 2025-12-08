import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from myapp.models import Document
import json

# Get all documents ordered by most recent
documents = Document.objects.all().order_by('-uploaded_at')[:20]

print(f"\n{'='*80}")
print(f"RECENT DOCUMENTS - LAST 20 UPLOADS")
print(f"{'='*80}\n")

for doc in documents:
    print(f"\n{'='*80}")
    print(f"Document ID: {doc.id}")
    print(f"User: {doc.user.username} (ID: {doc.user.id})")
    print(f"Document Type: {doc.document_type}")
    print(f"Status: {doc.verification_status}")
    print(f"Uploaded: {doc.uploaded_at}")
    print(f"Processed: {doc.processed_at}")
    
    if doc.rejection_reason:
        print(f"\n❌ REJECTION REASON:")
        print(f"{doc.rejection_reason}")
    
    if doc.ai_analysis_result:
        try:
            analysis = json.loads(doc.ai_analysis_result)
            print(f"\n📊 AI ANALYSIS:")
            if 'status' in analysis:
                print(f"  Status: {analysis['status']}")
            if 'confidence' in analysis:
                print(f"  Confidence: {analysis['confidence']}")
            if 'message' in analysis:
                print(f"  Message: {analysis['message']}")
            if 'extracted_data' in analysis:
                print(f"  Extracted Data:")
                for key, value in analysis['extracted_data'].items():
                    if value:
                        print(f"    - {key}: {value}")
            if 'comparison_details' in analysis:
                print(f"  Comparison Details:")
                for key, value in analysis['comparison_details'].items():
                    print(f"    - {key}: {value}")
        except:
            print(f"  Raw: {doc.ai_analysis_result[:500]}...")
    
    print(f"{'='*80}")

# Get rejected documents count
rejected_count = Document.objects.filter(verification_status='REJECTED').count()
pending_count = Document.objects.filter(verification_status='PENDING').count()
verified_count = Document.objects.filter(verification_status='VERIFIED').count()

print(f"\n{'='*80}")
print(f"DOCUMENT STATUS SUMMARY")
print(f"{'='*80}")
print(f"Rejected: {rejected_count}")
print(f"Pending: {pending_count}")
print(f"Verified: {verified_count}")
print(f"Total: {rejected_count + pending_count + verified_count}")
print(f"{'='*80}\n")
