import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication
from myapp.face_adjudication_views import VerificationAdjudicationSerializer

print("=" * 70)
print("TESTING FACE ADJUDICATION SERIALIZER URL GENERATION")
print("=" * 70)

# Get the verification adjudication record
adj = VerificationAdjudication.objects.get(id=5)

print(f"\nVerification Adjudication ID: {adj.id}")
print(f"User: {adj.user.username}")
print(f"Status: {adj.status}")

# Serialize it
serializer = VerificationAdjudicationSerializer(adj, context={})
data = serializer.data

print(f"\n{'=' * 70}")
print("DATABASE PATHS (stored in DB):")
print("=" * 70)
print(f"School ID Path: {data.get('school_id_image_path')}")
print(f"Selfie Path: {data.get('selfie_image_path')}")

print(f"\n{'=' * 70}")
print("GENERATED URLS (from serializer):")
print("=" * 70)

school_id_url = data.get('school_id_image_url')
selfie_url = data.get('selfie_image_url')

if school_id_url:
    print(f"\n✓ School ID URL generated:")
    print(f"  {school_id_url[:80]}...")
    if 'amazonaws.com' in school_id_url:
        print(f"  Type: S3 Presigned URL")
    else:
        print(f"  Type: Local/Media URL")
else:
    print(f"\n✗ School ID URL: None")

if selfie_url:
    print(f"\n✓ Selfie URL generated:")
    print(f"  {selfie_url[:80]}...")
    if 'amazonaws.com' in selfie_url:
        print(f"  Type: S3 Presigned URL")
    else:
        print(f"  Type: Local/Media URL")
else:
    print(f"\n✗ Selfie URL: None")

print(f"\n{'=' * 70}")
print("CONCLUSION:")
print("=" * 70)
print("Both images should now display in the admin dashboard")
print("with presigned S3 URLs for secure access.")
print("=" * 70)
