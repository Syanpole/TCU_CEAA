"""Test S3 presigned URL generation for adjudication images"""
import os
import sys
import django
import boto3
from botocore.exceptions import ClientError

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication
from django.conf import settings

print("=" * 80)
print("TESTING S3 PRESIGNED URL GENERATION")
print("=" * 80)

# Get adjudication #8
adjudication = VerificationAdjudication.objects.get(id=8)

print(f"\n📋 Adjudication #{adjudication.id}")
print(f"   School ID path: {adjudication.school_id_image_path}")
print(f"   Selfie path: {adjudication.selfie_image_path}")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=settings.AWS_S3_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

bucket_name = settings.AWS_STORAGE_BUCKET_NAME

print(f"\n☁️  S3 Configuration:")
print(f"   Bucket: {bucket_name}")
print(f"   Region: {settings.AWS_S3_REGION_NAME}")

# Test different path variations
test_paths = [
    adjudication.school_id_image_path,
    f"media/{adjudication.school_id_image_path}",
    adjudication.school_id_image_path.replace('documents/', 'media/documents/'),
]

print(f"\n🔍 Testing which path exists in S3...")
for test_path in test_paths:
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=test_path)
        print(f"\n✅ FOUND: {test_path}")
        print(f"   Size: {response['ContentLength']} bytes")
        print(f"   Last Modified: {response['LastModified']}")
        
        # Generate presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_path},
            ExpiresIn=3600
        )
        print(f"   Presigned URL: {url[:100]}...")
        
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"❌ NOT FOUND: {test_path}")
        else:
            print(f"⚠️  ERROR: {test_path} - {e}")

# Also test selfie path
print(f"\n\n🔍 Testing selfie path...")
selfie_test_paths = [
    adjudication.selfie_image_path,
    f"media/{adjudication.selfie_image_path}",
]

for test_path in selfie_test_paths:
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=test_path)
        print(f"\n✅ FOUND: {test_path}")
        print(f"   Size: {response['ContentLength']} bytes")
        
        # Generate presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_path},
            ExpiresIn=3600
        )
        print(f"   Presigned URL: {url[:100]}...")
        
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"❌ NOT FOUND: {test_path}")
        else:
            print(f"⚠️  ERROR: {test_path} - {e}")

print("\n" + "=" * 80)
