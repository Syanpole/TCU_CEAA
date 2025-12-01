import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.s3_utils import check_object_exists
import boto3
from django.conf import settings

print("="*80)
print(" CHECKING POSSIBLE S3 PATHS")
print("="*80)

base_path = "school-id_22-00417_20251129_141353.jpg"
date_path = "2025/11"

# Possible paths
paths_to_check = [
    f"documents/{date_path}/{base_path}",
    f"documents/documents/{date_path}/{base_path}",
    f"media/documents/{date_path}/{base_path}",
    f"{date_path}/{base_path}",
]

s3_client = boto3.client(
    's3',
    region_name=settings.AWS_S3_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

bucket = settings.AWS_STORAGE_BUCKET_NAME

print(f"\nChecking S3 bucket: {bucket}\n")

for path in paths_to_check:
    try:
        s3_client.head_object(Bucket=bucket, Key=path)
        print(f" FOUND: {path}")
    except Exception as e:
        print(f" NOT FOUND: {path}")

# List all objects with prefix
print(f"\n Listing all objects in 'documents/2025/11/':")
try:
    response = s3_client.list_objects_v2(
        Bucket=bucket,
        Prefix='documents/2025/11/',
        MaxKeys=20
    )
    
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"    {obj['Key']}")
    else:
        print("   (no objects found)")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*80)
