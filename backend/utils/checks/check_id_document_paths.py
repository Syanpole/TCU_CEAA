"""Check ID document paths in database"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission, VerificationAdjudication

print("=" * 80)
print("CHECKING ID DOCUMENT PATHS")
print("=" * 80)

# Check student 22-00417's ID documents
student_id = "22-00417"
print(f"\n🔍 Looking for {student_id}'s ID documents...\n")

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    user = User.objects.get(student_id=student_id)
    print(f"✅ Found user: {user.get_full_name()} ({user.student_id})")
    
    # Get ALL documents to see what was uploaded
    docs = DocumentSubmission.objects.filter(
        student=user
    ).order_by('-submitted_at')
    
    print(f"\n📄 Found {docs.count()} ID documents:")
    for doc in docs:
        print(f"\n  📋 {doc.document_type} - {doc.status}")
        print(f"     Submitted: {doc.submitted_at}")
        if doc.document_file:
            print(f"     File name: {doc.document_file.name}")
            print(f"     File path: {doc.document_file.path if hasattr(doc.document_file, 'path') else 'S3 storage'}")
            print(f"     File URL: {doc.document_file.url if hasattr(doc.document_file, 'url') else 'N/A'}")
        else:
            print(f"     ❌ No file attached")
    
    # Check VerificationAdjudication records
    print(f"\n\n🔍 Checking VerificationAdjudication records...")
    adjudications = VerificationAdjudication.objects.filter(user=user).order_by('-created_at')
    
    print(f"\n📊 Found {adjudications.count()} adjudication records:")
    for adj in adjudications[:3]:  # Show last 3
        print(f"\n  🎭 Adjudication #{adj.id} - {adj.status}")
        print(f"     Created: {adj.created_at}")
        print(f"     School ID path: {adj.school_id_image_path}")
        print(f"     Selfie path: {adj.selfie_image_path}")
        print(f"     Similarity: {adj.automated_similarity_score}")
        
except User.DoesNotExist:
    print(f"❌ User with student_id {student_id} not found")

print("\n" + "=" * 80)
