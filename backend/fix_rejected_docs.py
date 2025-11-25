from myapp.models import DocumentSubmission
from django.utils import timezone

# Find all rejected documents with 0% confidence (failed AI)
rejected_docs = DocumentSubmission.objects.filter(
    status='rejected',
    ai_confidence_score=0.0,
    ai_analysis_completed=True
)

print(f"Found {rejected_docs.count()} documents rejected due to AI failure")

# Update them to pending for manual review
for doc in rejected_docs:
    doc.status = 'pending'
    doc.ai_confidence_score = 0.5
    doc.ai_analysis_notes = "Document Re-queued for Manual Review\n\n" \
        "This document was previously auto-rejected because the AI verification system was unavailable.\n\n" \
        "Status changed from 'rejected' to 'pending' for manual admin review.\n\n" \
        f"Original Document Type: {doc.get_document_type_display()}\n" \
        f"Originally Submitted: {doc.submitted_at}\n" \
        f"Re-queued: {timezone.now()}\n\n" \
        f"Admin: Please manually review and approve/reject this document."
    doc.save()
    print(f"✅ Updated Document {doc.id} ({doc.get_document_type_display()}) - Student: {doc.student.get_full_name()}")

print(f"\n✅ Successfully updated {rejected_docs.count()} documents to pending status")
