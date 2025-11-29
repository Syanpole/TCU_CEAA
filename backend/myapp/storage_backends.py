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
from storages.backends.s3boto3 import S3Boto3Storage
import logging

logger = logging.getLogger(__name__)


class PrivateMediaStorage(S3Boto3Storage):
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


class PublicMediaStorage(S3Boto3Storage):
    """
    Public storage backend for non-sensitive files.
    
    Files uploaded using this storage are publicly accessible.
    Use this for files that don't contain sensitive information.
    """
    location = 'media/public'
    default_acl = 'public-read'
    file_overwrite = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Public Media Storage initialized (Cloud Storage)")


class DocumentStorage(S3Boto3Storage):
    """
    Specialized storage for document files (PDFs, Word docs, etc.).
    
    Provides optimized settings for document storage and retrieval.
    """
    location = 'documents'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    object_parameters = {
        'CacheControl': 'max-age=86400',
        'ContentDisposition': 'inline',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Document Storage initialized (Cloud Storage)")


class GradeSheetStorage(S3Boto3Storage):
    """
    Specialized storage for grade sheets and transcripts.
    
    Highly secure storage with strict access controls for
    sensitive academic documents.
    """
    location = 'grades'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    object_parameters = {
        'CacheControl': 'no-cache',
        'ServerSideEncryption': 'AES256',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Grade Sheet Storage initialized (Cloud Storage - Encrypted)")


class ProfileImageStorage(S3Boto3Storage):
    """
    Specialized storage for profile images.
    
    Optimized for image files with appropriate caching and
    content type settings.
    """
    location = 'profiles'
    default_acl = 'private'
    file_overwrite = True  # Allow profile image updates
    custom_domain = False
    object_parameters = {
        'CacheControl': 'max-age=604800',  # 7 days
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Profile Image Storage initialized (Cloud Storage)")


def get_storage_backend(storage_type='private'):
    """
    Get the appropriate storage backend - S3 ONLY.
    
    Args:
        storage_type: Type of storage ('private', 'public', 'document', 'grade', 'profile')
    
    Returns:
        S3 Storage backend instance - LOCAL STORAGE NOT ALLOWED
    """
    # S3 is mandatory - no fallback to local storage
    if not getattr(settings, 'USE_CLOUD_STORAGE', False):
        logger.error(f"❌ CRITICAL: Cloud storage is disabled but required! Forcing S3 for {storage_type}")
        # Force enable cloud storage if somehow disabled
        settings.USE_CLOUD_STORAGE = True
    
    storage_map = {
        'private': PrivateMediaStorage,
        'public': PublicMediaStorage,
        'document': DocumentStorage,
        'grade': GradeSheetStorage,
        'profile': ProfileImageStorage,
    }
    
    storage_class = storage_map.get(storage_type, PrivateMediaStorage)
    logger.info(f"✅ Using S3 storage backend: {storage_class.__name__} for {storage_type}")
    return storage_class()
