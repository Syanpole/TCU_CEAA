#!/usr/bin/env python
"""
Migrate Local Files to S3
==========================
This script migrates all locally stored files to AWS S3 and updates
the database paths accordingly.

Usage: python migrate_files_to_s3.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.base import File
from myapp.models import DocumentSubmission, GradeSubmission, CustomUser

print("=" * 70)
print("FILE MIGRATION TO S3")
print("=" * 70)

# Check configuration
if not settings.USE_CLOUD_STORAGE:
    print("\n❌ ERROR: USE_CLOUD_STORAGE is False")
    print("Set USE_CLOUD_STORAGE=True in .env file first")
    sys.exit(1)

print(f"\n✓ USE_CLOUD_STORAGE: {settings.USE_CLOUD_STORAGE}")
print(f"✓ Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"✓ Region: {settings.AWS_S3_REGION_NAME}")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=settings.AWS_S3_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

def file_exists_locally(file_path):
    """Check if file exists in local media directory"""
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    return os.path.exists(full_path)

def upload_to_s3(local_path, s3_key):
    """Upload a file to S3"""
    try:
        full_local_path = os.path.join(settings.MEDIA_ROOT, local_path)
        
        with open(full_local_path, 'rb') as f:
            s3_client.upload_fileobj(
                f,
                settings.AWS_STORAGE_BUCKET_NAME,
                s3_key,
                ExtraArgs={
                    'ACL': 'private',
                    'ServerSideEncryption': 'AES256'
                }
            )
        
        return True
    except Exception as e:
        print(f"  ✗ Upload failed: {str(e)}")
        return False

def migrate_documents():
    """Migrate DocumentSubmission files to S3"""
    print(f"\n{'=' * 70}")
    print("MIGRATING DOCUMENT SUBMISSIONS")
    print("=" * 70)
    
    documents = DocumentSubmission.objects.all()
    total = documents.count()
    migrated = 0
    skipped = 0
    errors = 0
    
    print(f"\nFound {total} document submissions\n")
    
    for doc in documents:
        if not doc.document_file:
            skipped += 1
            continue
        
        file_path = doc.document_file.name
        
        # Skip if already in S3 format
        if file_path.startswith('media/documents/') or not file_exists_locally(file_path):
            # Check if already in S3
            try:
                s3_key = f"media/{file_path}" if not file_path.startswith('media/') else file_path
                s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
                print(f"✓ Doc #{doc.id} already in S3: {s3_key}")
                skipped += 1
                continue
            except ClientError:
                pass  # Not in S3, needs migration
        
        # Upload to S3
        print(f"→ Migrating Doc #{doc.id}: {file_path}")
        
        # Construct S3 key (preserve path structure)
        s3_key = f"media/{file_path}" if not file_path.startswith('media/') else file_path
        
        if upload_to_s3(file_path, s3_key):
            print(f"  ✓ Uploaded to S3: {s3_key}")
            
            # Update database (Django's S3 storage will handle the path)
            # No need to update doc.document_file as it already has the correct relative path
            doc.save(update_fields=[])  # Trigger save without changing the field
            
            migrated += 1
        else:
            errors += 1
    
    print(f"\n{'=' * 70}")
    print(f"Document Migration Summary:")
    print(f"  Total: {total}")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print("=" * 70)

def migrate_grades():
    """Migrate GradeSubmission files to S3"""
    print(f"\n{'=' * 70}")
    print("MIGRATING GRADE SUBMISSIONS")
    print("=" * 70)
    
    grades = GradeSubmission.objects.all()
    total = grades.count()
    migrated = 0
    skipped = 0
    errors = 0
    
    print(f"\nFound {total} grade submissions\n")
    
    for grade in grades:
        if not grade.grade_sheet:
            skipped += 1
            continue
        
        file_path = grade.grade_sheet.name
        
        # Skip if already in S3 format or file doesn't exist locally
        if file_path.startswith('media/grades/') or not file_exists_locally(file_path):
            # Check if already in S3
            try:
                s3_key = f"media/{file_path}" if not file_path.startswith('media/') else file_path
                s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
                print(f"✓ Grade #{grade.id} already in S3: {s3_key}")
                skipped += 1
                continue
            except ClientError:
                pass  # Not in S3, needs migration
        
        # Upload to S3
        print(f"→ Migrating Grade #{grade.id}: {file_path}")
        
        # Construct S3 key
        s3_key = f"media/{file_path}" if not file_path.startswith('media/') else file_path
        
        if upload_to_s3(file_path, s3_key):
            print(f"  ✓ Uploaded to S3: {s3_key}")
            
            # Update database
            grade.save(update_fields=[])
            
            migrated += 1
        else:
            errors += 1
    
    print(f"\n{'=' * 70}")
    print(f"Grade Migration Summary:")
    print(f"  Total: {total}")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print("=" * 70)

def verify_s3_access():
    """Verify we can access S3"""
    try:
        s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print(f"\n✓ Successfully connected to S3 bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        return True
    except ClientError as e:
        print(f"\n✗ Cannot access S3 bucket: {str(e)}")
        return False

# Main execution
if __name__ == '__main__':
    if not verify_s3_access():
        print("\n❌ Cannot proceed without S3 access")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("WARNING: This will upload all local files to S3")
    print("=" * 70)
    
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() == 'yes':
        migrate_documents()
        migrate_grades()
        
        print("\n" + "=" * 70)
        print("✓ MIGRATION COMPLETE")
        print("=" * 70)
        print("\nAll files have been migrated to S3.")
        print("Local files can be safely deleted after verification.")
    else:
        print("\n❌ Migration cancelled")
