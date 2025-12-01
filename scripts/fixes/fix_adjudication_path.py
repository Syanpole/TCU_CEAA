import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

import boto3
from django.conf import settings
from myapp.models import VerificationAdjudication

print("="*80)
print(" FINDING ACTUAL SCHOOL ID IN S3")
print("="*80)

s3_client = boto3.client(
    's3',
    region_name=settings.AWS_S3_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

bucket = settings.AWS_STORAGE_BUCKET_NAME

# List all school IDs for this student
print(f"\n Listing all school-id files in S3:\n")
try:
    response = s3_client.list_objects_v2(
        Bucket=bucket,
        Prefix='media/documents/2025/11/school-id',
        MaxKeys=50
    )
    
    if 'Contents' in response:
        for obj in response['Contents']:
            size_kb = obj['Size'] / 1024
            print(f"    {obj['Key']}")
            print(f"     Size: {size_kb:.2f} KB, Modified: {obj['LastModified']}")
    else:
        print("   (no school-id files found)")
except Exception as e:
    print(f"   Error: {e}")

# Get the adjudication and update it
adj = VerificationAdjudication.objects.order_by('-created_at').first()
if adj:
    print(f"\n Current Adjudication (ID: {adj.id}):")
    print(f"   School ID Path: '{adj.school_id_image_path}'")
    print(f"   Created: {adj.created_at}")
    
    # Update to correct path
    correct_path = 'media/documents/2025/11/school-id_22-00417_20251129_001834.jpg'
    print(f"\n Updating to correct path:")
    print(f"   New Path: '{correct_path}'")
    
    adj.school_id_image_path = correct_path
    adj.save()
    print(f"    Updated!")

print("\n" + "="*80)
