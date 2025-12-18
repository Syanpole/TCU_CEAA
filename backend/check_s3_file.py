import boto3
import os

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id='AKIAWZNMCNNJEXB7DKWK',
    aws_secret_access_key='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',
    region_name='us-east-1'
)

bucket = 'tcu-ceaa-documents'
key = 'media/documents/2025/12/school-id_22-00417_20251210_111659.jpg'

print(f"\n🔍 Checking S3 file: {key}")
print(f"📦 Bucket: {bucket}\n")

# List all files in media/documents/2025/
print(f"📂 Listing ALL files in media/documents/2025/:")
paginator = s3.get_paginator('list_objects_v2')
found_files = []
try:
    for page in paginator.paginate(Bucket=bucket, Prefix='media/documents/2025/', MaxKeys=50):
        if 'Contents' in page:
            found_files.extend([obj['Key'] for obj in page['Contents']])
    
    if found_files:
        print(f"\nFound {len(found_files)} files:")
        for file_key in found_files[:20]:  # Show first 20
            print(f"   - {file_key}")
        if len(found_files) > 20:
            print(f"   ... and {len(found_files) - 20} more files")
    else:
        print("   No files found")
except Exception as e:
    print(f"❌ Error listing files: {str(e)}")

print("\n" + "="*60)
