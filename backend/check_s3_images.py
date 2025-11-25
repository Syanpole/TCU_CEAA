#!/usr/bin/env python
import boto3
import os

# Load environment variables from .env if it exists
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("S3 IMAGE CHECK")
print("=" * 60)

# Check AWS credentials
aws_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME', 'tcu-ceaa-documents')

print(f"\nAWS Configuration:")
print(f"  Access Key ID: {'Set ✓' if aws_key_id else 'Not Set ✗'}")
print(f"  Secret Access Key: {'Set ✓' if aws_secret else 'Not Set ✗'}")
print(f"  Region: {aws_region}")
print(f"  Bucket: {bucket_name}")

if not aws_key_id or not aws_secret:
    print("\n⚠️ WARNING: AWS credentials not configured!")
    print("Images from AWS Rekognition liveness will not be accessible.")
else:
    print("\n✓ AWS credentials configured")

# Check S3 bucket contents
print(f"\n{'=' * 60}")
print("CHECKING S3 BUCKET CONTENTS")
print(f"{'=' * 60}")

try:
    s3_client = boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_secret
    )
    
    # List liveness session images
    print("\nLiveness Session Images in S3:")
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix='liveness-sessions/',
        MaxKeys=20
    )
    
    if response.get('KeyCount', 0) > 0:
        print(f"  Found {response['KeyCount']} objects:")
        for obj in response.get('Contents', []):
            size_kb = obj['Size'] / 1024
            print(f"    - {obj['Key']} ({size_kb:.1f} KB)")
    else:
        print("  No liveness session images found in S3")
    
    # Check if documents are in S3
    print("\nDocument Images in S3:")
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix='documents/',
        MaxKeys=10
    )
    
    if response.get('KeyCount', 0) > 0:
        print(f"  Found {response['KeyCount']} objects:")
        for obj in response.get('Contents', []):
            size_kb = obj['Size'] / 1024
            print(f"    - {obj['Key']} ({size_kb:.1f} KB)")
    else:
        print("  No document images found in S3")
        
except Exception as e:
    print(f"\n✗ Error accessing S3: {str(e)}")

# Check database records
print(f"\n{'=' * 60}")
print("DATABASE CHECK - Use Django Shell")
print(f"{'=' * 60}")
print("\nTo check database records, run:")
print("  python manage.py shell")
print("Then:")
print("  from myapp.models import VerificationAdjudication")
print("  adj = VerificationAdjudication.objects.first()")
print("  print(f'School ID: {adj.school_id_image_path}')")
print("  print(f'Selfie: {adj.selfie_image_path}')")

print("=" * 60)
print("CHECK COMPLETE")
print("=" * 60)
