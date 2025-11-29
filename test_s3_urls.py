import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication
from myapp.s3_utils import generate_presigned_url, check_object_exists

print("="*80)
print(" TESTING S3 PRESIGNED URL GENERATION")
print("="*80)

recent = VerificationAdjudication.objects.order_by('-created_at').first()

if recent:
    school_id_path = recent.school_id_image_path
    selfie_path = recent.selfie_image_path
    
    print(f"\n Testing School ID Image:")
    print(f"   Path: {school_id_path}")
    
    # Check if exists in S3
    exists = check_object_exists(school_id_path)
    print(f"   Exists in S3: {' Yes' if exists else ' No'}")
    
    if exists:
        # Generate presigned URL
        url = generate_presigned_url(school_id_path)
        if url:
            print(f"   Presigned URL:  Generated")
            print(f"   URL: {url[:100]}...")
        else:
            print(f"   Presigned URL:  Failed")
    
    print(f"\n Testing Selfie Image:")
    print(f"   Path: {selfie_path}")
    
    # Check if exists in S3
    exists = check_object_exists(selfie_path)
    print(f"   Exists in S3: {' Yes' if exists else ' No'}")
    
    if exists:
        # Generate presigned URL
        url = generate_presigned_url(selfie_path)
        if url:
            print(f"   Presigned URL:  Generated")
            print(f"   URL: {url[:100]}...")
        else:
            print(f"   Presigned URL:  Failed")
else:
    print("\n No adjudication records found")

print("\n" + "="*80)
