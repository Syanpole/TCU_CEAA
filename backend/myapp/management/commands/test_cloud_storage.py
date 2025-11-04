"""
Test Cloud Storage Connection
==============================

Management command to test S3 connection and verify bucket access.

Usage:
    python manage.py test_cloud_storage
"""

from django.core.management.base import BaseCommand
from django.conf import settings

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

import io


class Command(BaseCommand):
    help = 'Test cloud storage (S3) connection and permissions'
    
    def handle(self, *args, **options):
        if not BOTO3_AVAILABLE:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  boto3 is not installed. This command requires boto3 for S3 operations.'
            ))
            self.stdout.write(self.style.WARNING(
                'Install with: pip install boto3'
            ))
            return
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('CLOUD STORAGE CONNECTION TEST'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        
        # Check configuration
        if not settings.USE_CLOUD_STORAGE:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  Cloud storage is disabled. Set USE_CLOUD_STORAGE=True in .env'
            ))
            return
        
        self.stdout.write('\n📋 Configuration:')
        self.stdout.write(f'   Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
        self.stdout.write(f'   Region: {settings.AWS_S3_REGION_NAME}')
        
        # Initialize S3 client
        try:
            s3_client = boto3.client(
                's3',
                region_name=settings.AWS_S3_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Failed to initialize S3 client: {str(e)}'))
            return
        
        # Test 1: Check bucket exists and is accessible
        self.stdout.write('\n🔍 Test 1: Checking bucket access...')
        try:
            s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            self.stdout.write(self.style.SUCCESS(
                f'   ✅ Bucket \'{settings.AWS_STORAGE_BUCKET_NAME}\' is accessible'
            ))
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.stdout.write(self.style.ERROR('   ❌ Bucket does not exist'))
            elif error_code == '403':
                self.stdout.write(self.style.ERROR('   ❌ Access denied - check IAM permissions'))
            else:
                self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
            return
        
        # Test 2: Upload test file
        self.stdout.write('\n📤 Test 2: Uploading test file...')
        test_content = b'TCU CEAA Cloud Storage Test File'
        test_key = 'test/connection_test.txt'
        
        try:
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            self.stdout.write(self.style.SUCCESS('   ✅ Can write files to bucket'))
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Upload failed: {str(e)}'))
            return
        
        # Test 3: Read test file
        self.stdout.write('\n📥 Test 3: Reading test file...')
        try:
            response = s3_client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=test_key
            )
            retrieved_content = response['Body'].read()
            
            if retrieved_content == test_content:
                self.stdout.write(self.style.SUCCESS('   ✅ Can read files from bucket'))
            else:
                self.stdout.write(self.style.ERROR('   ❌ File content mismatch'))
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Read failed: {str(e)}'))
            return
        
        # Test 4: Delete test file
        self.stdout.write('\n🗑️  Test 4: Deleting test file...')
        try:
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=test_key
            )
            self.stdout.write(self.style.SUCCESS('   ✅ Can delete files from bucket'))
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Delete failed: {str(e)}'))
            return
        
        # Test 5: List objects
        self.stdout.write('\n📂 Test 5: Listing bucket contents...')
        try:
            response = s3_client.list_objects_v2(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                MaxKeys=10
            )
            
            object_count = response.get('KeyCount', 0)
            self.stdout.write(self.style.SUCCESS(f'   ✅ Found {object_count} object(s) in bucket'))
            
            if object_count > 0:
                self.stdout.write('   📁 Recent files:')
                for obj in response.get('Contents', [])[:5]:
                    size_kb = obj['Size'] / 1024
                    self.stdout.write(f'      - {obj["Key"]} ({size_kb:.2f} KB)')
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ List failed: {str(e)}'))
            return
        
        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ ALL TESTS PASSED'))
        self.stdout.write(self.style.SUCCESS('Cloud storage is properly configured and working!'))
        self.stdout.write('=' * 70 + '\n')
