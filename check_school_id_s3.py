import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission, VerificationAdjudication
from myapp.s3_utils import check_object_exists

print("="*80)
print(" CHECKING SCHOOL ID DOCUMENT IN S3")
print("="*80)

# Get the adjudication
adj = VerificationAdjudication.objects.order_by('-created_at').first()
print(f"\nAdjudication ID: {adj.id}")
print(f"School ID Path: {adj.school_id_image_path}")

# Find the actual document submission
school_id_doc = DocumentSubmission.objects.filter(
    student=adj.user,
    document_type='school_id'
).order_by('-submitted_at').first()

if school_id_doc:
    print(f"\n Found School ID Document:")
    print(f"   Document ID: {school_id_doc.id}")
    print(f"   File name: {school_id_doc.document_file.name}")
    print(f"   Storage: {school_id_doc.document_file.storage.__class__.__name__}")
    print(f"   Status: {school_id_doc.status}")
    
    # Check if exists
    exists = check_object_exists(school_id_doc.document_file.name)
    print(f"   Exists in S3: {' Yes' if exists else ' No'}")
    
    # Try to get URL
    try:
        url = school_id_doc.document_file.url
        print(f"   URL: {url[:100]}...")
    except Exception as e:
        print(f"   URL Error: {e}")
    
    # Compare paths
    print(f"\n Path Comparison:")
    print(f"   Adjudication path: {adj.school_id_image_path}")
    print(f"   Document file path: {school_id_doc.document_file.name}")
    print(f"   Match: {' Yes' if adj.school_id_image_path == school_id_doc.document_file.name else ' No'}")
else:
    print("\n No school ID document found for this user")

print("\n" + "="*80)
