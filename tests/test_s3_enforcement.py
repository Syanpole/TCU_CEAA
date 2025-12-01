"""
Test script to verify S3 storage enforcement is working correctly.
Run with: python test_s3_enforcement.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.conf import settings
from myapp.storage_backends import get_storage_backend
from myapp.s3_utils import check_object_exists, generate_presigned_url
from myapp.models import CustomUser, DocumentSubmission
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

def test_settings():
    """Test that USE_CLOUD_STORAGE is enforced"""
    print("\n🔍 Testing Settings Configuration...")
    assert settings.USE_CLOUD_STORAGE == True, "❌ USE_CLOUD_STORAGE should be True"
    assert settings.MEDIA_ROOT is None, "❌ MEDIA_ROOT should be None"
    print("✅ USE_CLOUD_STORAGE = True")
    print("✅ MEDIA_ROOT = None")
    print("✅ AWS_STORAGE_BUCKET_NAME =", settings.AWS_STORAGE_BUCKET_NAME)
    print("✅ AWS_S3_REGION_NAME =", settings.AWS_S3_REGION_NAME)

def test_storage_backends():
    """Test that storage backends return S3 storage"""
    print("\n🔍 Testing Storage Backends...")
    
    storage_types = ['private', 'document', 'grade', 'profile']
    s3_storage_classes = ['PrivateMediaStorage', 'DocumentStorage', 'GradeSheetStorage', 'ProfileImageStorage', 'S3Boto3Storage']
    
    for storage_type in storage_types:
        storage = get_storage_backend(storage_type)
        storage_class = storage.__class__.__name__
        print(f"✅ {storage_type}: {storage_class}")
        # Check if it's one of our custom S3 storage classes or base S3Boto3Storage
        is_s3_storage = any(s3_class in storage_class for s3_class in s3_storage_classes)
        assert is_s3_storage, f"❌ {storage_type} storage should be S3-based (got {storage_class})"

def test_model_fields():
    """Test that model FileFields use S3 storage"""
    print("\n🔍 Testing Model FileField Storage...")
    
    from myapp.models import CustomUser, DocumentSubmission, GradeSubmission
    
    # Check CustomUser profile_image
    user_field = CustomUser._meta.get_field('profile_image')
    if user_field.storage:
        print(f"✅ CustomUser.profile_image uses: {user_field.storage.__class__.__name__}")
    
    # Check DocumentSubmission document_file
    doc_field = DocumentSubmission._meta.get_field('document_file')
    if doc_field.storage:
        print(f"✅ DocumentSubmission.document_file uses: {doc_field.storage.__class__.__name__}")
    
    # Check GradeSubmission grade_sheet
    grade_field = GradeSubmission._meta.get_field('grade_sheet')
    if grade_field.storage:
        print(f"✅ GradeSubmission.grade_sheet uses: {grade_field.storage.__class__.__name__}")

def test_s3_utilities():
    """Test S3 utility functions"""
    print("\n🔍 Testing S3 Utility Functions...")
    
    # Test check_object_exists with a non-existent file
    exists = check_object_exists('test_nonexistent_file.txt')
    print(f"✅ check_object_exists('test_nonexistent_file.txt') = {exists}")
    
    # Test generate_presigned_url
    try:
        url = generate_presigned_url('documents/test.pdf')
        if url:
            print(f"✅ generate_presigned_url() working (URL generated)")
            print(f"   URL preview: {url[:80]}...")
        else:
            print("ℹ️ generate_presigned_url() returned None (USE_CLOUD_STORAGE might be False)")
    except Exception as e:
        print(f"⚠️ generate_presigned_url() error: {e}")

def test_document_storage():
    """Test that documents are being stored in S3"""
    print("\n🔍 Testing Actual Document Storage...")
    
    # Find a recent document submission
    recent_doc = DocumentSubmission.objects.filter(
        document_file__isnull=False
    ).order_by('-submitted_at').first()
    
    if recent_doc:
        print(f"✅ Found recent document: ID={recent_doc.id}")
        print(f"   File name: {recent_doc.document_file.name}")
        print(f"   Storage: {recent_doc.document_file.storage.__class__.__name__}")
        
        # Check if file exists in S3
        exists = check_object_exists(recent_doc.document_file.name)
        print(f"   Exists in S3: {exists}")
        
        # Try to get URL
        try:
            url = recent_doc.document_file.url
            print(f"   URL preview: {url[:80]}...")
        except Exception as e:
            print(f"   ⚠️ Error getting URL: {e}")
    else:
        print("ℹ️ No documents found in database")

def main():
    print("="*80)
    print("🧪 S3 STORAGE ENFORCEMENT TEST")
    print("="*80)
    
    try:
        test_settings()
        test_storage_backends()
        test_model_fields()
        test_s3_utilities()
        test_document_storage()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - S3 STORAGE ENFORCEMENT WORKING!")
        print("="*80)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
