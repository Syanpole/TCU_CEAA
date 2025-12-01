import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'tcu-ceaa-documents'

print("Checking media/ prefix in S3:")
resp = s3.list_objects_v2(Bucket=bucket, Prefix='media/', MaxKeys=30)

if resp.get('KeyCount', 0) > 0:
    print(f"\nFound {resp['KeyCount']} objects:\n")
    for obj in resp.get('Contents', []):
        size_kb = obj['Size'] / 1024
        print(f"  {obj['Key']} ({size_kb:.1f} KB)")
else:
    print("\nNo objects found with media/ prefix")
