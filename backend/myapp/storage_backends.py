"""
Custom Storage Backends for Cloud Storage
==========================================

This module provides custom storage backends for handling file uploads
to cloud storage services. It extends Django's default storage system
to support cloud-based file management.

Features:
- Automatic cloud upload for user files
- Private file access with signed URLs
- Configurable storage paths
- Fallback to local storage if cloud is unavailable

Author: TCU CEAA Development Team
Date: November 2025
"""

from django.conf import settings
from django.core.files.storage import FileSystemStorage
import logging

logger = logging.getLogger(__name__)

# Try to import S3 storage, fallback to local storage if not available
try:
    from storages.backends.s3boto3 import S3Boto3Storage
    S3_AVAILABLE = True
except ImportError:
    logger.warning("django-storages not available, using local storage fallback")
    S3Boto3Storage = FileSystemStorage  # Fallback to local storage
    S3_AVAILABLE = False


class PrivateMediaStorage(S3Boto3Storage if S3_AVAILABLE else FileSystemStorage):
    """
    Private storage backend for sensitive user files.
    
    Files uploaded using this storage are private by default
    and require signed URLs for access.
    """
    location = 'media'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Private Media Storage initialized (Cloud Storage)")


class PublicMediaStorage(S3Boto3Storage if S3_AVAILABLE else FileSystemStorage):
    """
    Public storage backend for non-sensitive files.
    
    Files uploaded using this storage are publicly accessible.
    Use this for files that don't contain sensitive information.
    """
    location = 'media/public'
    default_acl = 'public-read' if S3_AVAILABLE else None
    file_overwrite = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Public Media Storage initialized (Cloud Storage)")


class DocumentStorage(S3Boto3Storage if S3_AVAILABLE else FileSystemStorage):
    """
    Specialized storage for document files (PDFs, Word docs, etc.).
    
    Provides optimized settings for document storage and retrieval.
    """
    location = 'media/documents'
    default_acl = 'private' if S3_AVAILABLE else None
    file_overwrite = False
    custom_domain = False
    object_parameters = {
        'CacheControl': 'max-age=86400',
        'ContentDisposition': 'inline',
    } if S3_AVAILABLE else {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Document Storage initialized (Cloud Storage)")


class GradeSheetStorage(S3Boto3Storage if S3_AVAILABLE else FileSystemStorage):
    """
    Specialized storage for grade sheets and transcripts.
    
    Highly secure storage with strict access controls for
    sensitive academic documents.
    """
    location = 'media/grades'
    default_acl = 'private' if S3_AVAILABLE else None
    file_overwrite = False
    custom_domain = False
    object_parameters = {
        'CacheControl': 'no-cache',
        'ServerSideEncryption': 'AES256',
    } if S3_AVAILABLE else {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Grade Sheet Storage initialized (Cloud Storage - Encrypted)")


class ProfileImageStorage(S3Boto3Storage if S3_AVAILABLE else FileSystemStorage):
    """
    Specialized storage for profile images.
    
    Optimized for image files with appropriate caching and
    content type settings.
    """
    location = 'media/profiles'
    default_acl = 'private' if S3_AVAILABLE else None
    file_overwrite = True  # Allow profile image updates
    custom_domain = False
    object_parameters = {
        'CacheControl': 'max-age=604800',  # 7 days
    } if S3_AVAILABLE else {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        storage_type = "Cloud Storage" if S3_AVAILABLE else "Local Storage (Fallback)"
        logger.info(f"Profile Image Storage initialized ({storage_type})")


def get_storage_backend(storage_type='private'):
    """
    Get the appropriate storage backend.
    
    Args:
        storage_type: Type of storage ('private', 'public', 'document', 'grade', 'profile')
    
    Returns:
        Storage backend instance (S3 if available, FileSystemStorage as fallback)
    """
    # Check if S3 is available and enabled
    use_s3 = S3_AVAILABLE and getattr(settings, 'USE_CLOUD_STORAGE', False)
    
    if not use_s3 and S3_AVAILABLE:
        logger.warning(f"⚠️ Cloud storage available but disabled for {storage_type}")
    elif not S3_AVAILABLE:
        logger.warning(f"⚠️ django-storages not available, using local storage fallback for {storage_type}")
    
    storage_map = {
        'private': PrivateMediaStorage,
        'public': PublicMediaStorage,
        'document': DocumentStorage,
        'grade': GradeSheetStorage,
        'profile': ProfileImageStorage,
    }
    
    storage_class = storage_map.get(storage_type, PrivateMediaStorage)
    backend_type = "S3" if (use_s3 and S3_AVAILABLE) else "Local"
    logger.info(f"✅ Using {backend_type} storage backend: {storage_class.__name__} for {storage_type}")
    return storage_class()
