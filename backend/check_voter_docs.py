import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.models import DocumentSubmission

def main():
    print("="*80)
    print("CHECKING FOR REJECTED VOTER CERTIFICATE DOCUMENTS")
    print("="*80)
    
    # Find rejected voter certificate documents
    voter_doc_types = ['voters_id', 'voter_id', 'voters_certificate', 'voter_certification', 'comelec_stub']
    
    rejected_docs = DocumentSubmission.objects.filter(
        document_type__in=voter_doc_types,
        status='rejected'
    ).order_by('-submitted_at')
    
    if not rejected_docs.exists():
        print("\n✅ No rejected voter certificate documents found!")
        
        # Check for any voter documents
        all_voter_docs = DocumentSubmission.objects.filter(
            document_type__in=voter_doc_types
        ).order_by('-submitted_at')
        
        if all_voter_docs.exists():
            print(f"\n📊 Found {all_voter_docs.count()} voter certificate document(s):")
            for doc in all_voter_docs:
                print(f"\n   Document ID: {doc.id}")
                print(f"   Student: {doc.student.username} (ID: {doc.student.id})")
                print(f"   Type: {doc.document_type}")
                print(f"   Status: {doc.status}")
                print(f"   Confidence: {doc.ai_confidence_score*100:.1f}%")
                print(f"   Auto-Approved: {doc.ai_auto_approved}")
                print(f"   Submitted: {doc.submitted_at}")
        else:
            print("\n📊 No voter certificate documents found in the system.")
        
        return
    
    print(f"\n❌ Found {rejected_docs.count()} rejected voter certificate document(s):\n")
    
    for doc in rejected_docs:
        print(f"   Document ID: {doc.id}")
        print(f"   Student: {doc.student.username} (ID: {doc.student.id})")
        print(f"   Type: {doc.document_type}")
        print(f"   Status: {doc.status}")
        print(f"   Confidence: {doc.ai_confidence_score*100:.1f}%")
        print(f"   File: {doc.document_file.name}")
        print(f"   Submitted: {doc.submitted_at}")
        print()

if __name__ == "__main__":
    main()
