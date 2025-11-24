import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

bucket = os.getenv('AWS_STORAGE_BUCKET_NAME', 'tcu-ceaa-documents')
s3_key = 'media/documents/2025/11/FELICIANO-_SCHOOL_ID_K21j6mA.jpg'

print("=" * 70)
print("TESTING SCHOOL ID PRESIGNED URL GENERATION")
print("=" * 70)

print(f"\nS3 Key: {s3_key}")
print(f"Bucket: {bucket}")

# Check if file exists
try:
    response = s3_client.head_object(Bucket=bucket, Key=s3_key)
    print(f"✓ File exists in S3")
    print(f"  Size: {response['ContentLength'] / 1024:.1f} KB")
    print(f"  Last Modified: {response['LastModified']}")
except Exception as e:
    print(f"✗ File not found: {str(e)}")
    exit(1)

# Generate presigned URL
try:
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket,
            'Key': s3_key
        },
        ExpiresIn=3600  # 1 hour
    )
    
    print(f"\n✓ Presigned URL generated successfully!")
    print(f"\nURL (valid for 1 hour):")
    print(f"{url}\n")
    print("=" * 70)
    print("Copy this URL and paste it in your browser to test image access")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Error generating presigned URL: {str(e)}")
