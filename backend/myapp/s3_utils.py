"""
S3 Utilities for Presigned URL Generation
==========================================

This module provides utility functions for generating presigned URLs
for private S3 objects, enabling temporary secure access to files.

Author: TCU CEAA Development Team
Date: November 2025
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_presigned_url(object_key, expiration=3600):
    """
    Generate a presigned URL for an S3 object.
    
    Args:
        object_key (str): The S3 object key (path within bucket)
        expiration (int): URL expiration time in seconds (default: 1 hour)
    
    Returns:
        str: Presigned URL or None if generation fails
    """
    if not settings.USE_CLOUD_STORAGE:
        logger.warning("Cloud storage is disabled. Cannot generate presigned URL.")
        return None
    
    if not object_key:
        return None
    
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Clean the object key - remove any leading slashes
        clean_key = object_key.lstrip('/')
        
        # If the key doesn't start with 'media/', add it (for document files)
        # Only liveness-sessions/ is stored at root level without media/ prefix
        if not clean_key.startswith(('media/', 'liveness-sessions/')):
            clean_key = f'media/{clean_key}'
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': clean_key
            },
            ExpiresIn=expiration
        )
        
        logger.debug(f"Generated presigned URL for: {clean_key}")
        return presigned_url
        
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        return None
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL for {object_key}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL: {e}")
        return None


def check_object_exists(object_key):
    """
    Check if an object exists in S3.
    
    Args:
        object_key (str): The S3 object key
    
    Returns:
        bool: True if object exists, False otherwise
    """
    if not settings.USE_CLOUD_STORAGE:
        return False
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        clean_key = object_key.lstrip('/')
        if not clean_key.startswith(('media/', 'liveness-sessions/')):
            clean_key = f'media/{clean_key}'
        
        s3_client.head_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=clean_key
        )
        return True
    except ClientError:
        return False
    except Exception as e:
        logger.error(f"Error checking object existence: {e}")
        return False


def download_s3_file_to_temp(s3_key):
    """
    Download a file from S3 to a temporary local file for processing.
    IMPORTANT: Caller must clean up the temp file after use.
    
    Args:
        s3_key (str): S3 object key (path)
    
    Returns:
        str: Path to temporary local file or None if failed
    """
    import tempfile
    import os
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Clean the key and ensure media/ prefix for documents and grades
        clean_key = s3_key.lstrip('/')
        logger.info(f"📥 S3 Download - Original key: {s3_key}")
        logger.info(f"📥 S3 Download - Cleaned key: {clean_key}")
        
        if not clean_key.startswith(('media/', 'liveness-sessions/')):
            clean_key = f'media/{clean_key}'
            logger.info(f"📥 S3 Download - Added media/ prefix: {clean_key}")
        
        # Create temporary file with appropriate extension
        suffix = os.path.splitext(clean_key)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = temp_file.name
        temp_file.close()
        
        logger.info(f"📥 S3 Download - Attempting download from bucket: {settings.AWS_STORAGE_BUCKET_NAME}, key: {clean_key}")
        
        # Download from S3
        s3_client.download_file(
            settings.AWS_STORAGE_BUCKET_NAME,
            clean_key,
            temp_path
        )
        
        logger.info(f"✅ Downloaded S3 file to temp: {clean_key} -> {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"❌ Error downloading S3 file {s3_key}: {str(e)}")
        return None


def upload_file_to_s3(local_path, s3_key, extra_args=None):
    """
    Upload a local file to S3.
    
    Args:
        local_path (str): Path to local file
        s3_key (str): Destination S3 key (path)
        extra_args (dict): Optional extra arguments for upload
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Clean the key
        clean_key = s3_key.lstrip('/')
        
        # Default extra args
        if extra_args is None:
            extra_args = {'ServerSideEncryption': 'AES256'}
        
        s3_client.upload_file(
            local_path,
            settings.AWS_STORAGE_BUCKET_NAME,
            clean_key,
            ExtraArgs=extra_args
        )
        
        logger.info(f"✅ Uploaded file to S3: {local_path} -> {clean_key}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error uploading file to S3: {str(e)}")
        return False


def get_file_path_for_processing(file_field):
    """
    Get a local file path for processing from a Django FileField.
    Downloads from S3 if necessary and returns a tuple indicating if cleanup is needed.
    
    Args:
        file_field: Django FileField instance
    
    Returns:
        tuple: (file_path, is_temp) where is_temp indicates if file should be cleaned up
    """
    import os
    
    try:
        # Get the file name relative to storage location
        s3_key = file_field.name
        logger.info(f"🔍 Getting file path for processing - FileField name: {s3_key}")
        
        # Get storage location if available and prepend to key
        if hasattr(file_field, 'storage') and hasattr(file_field.storage, 'location'):
            storage_location = file_field.storage.location
            if storage_location and not s3_key.startswith(storage_location):
                s3_key = f"{storage_location}/{s3_key}"
                logger.info(f"📂 Prepended storage location - Full S3 key: {s3_key}")
        
        # For S3-only storage, always download from S3
        # Don't check hasattr(file_field, 'path') as it triggers the property getter
        # which raises NotImplementedError for S3 storage
        logger.info(f"📥 Downloading from S3 - Key: {s3_key}")
        temp_path = download_s3_file_to_temp(s3_key)
        
        if temp_path:
            logger.info(f"✅ Downloaded S3 file for processing: {s3_key} -> {temp_path}")
            return temp_path, True
        else:
            logger.error(f"❌ S3 download failed for key: {s3_key}")
            return None, False
        
    except Exception as e:
        logger.error(f"❌ Error getting file path for processing: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None, False


def cleanup_temp_file(temp_path):
    """
    Clean up a temporary file.
    
    Args:
        temp_path (str): Path to temporary file
    """
    import os
    
    try:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"🗑️ Cleaned up temp file: {temp_path}")
    except Exception as e:
        logger.error(f"Error cleaning up temp file {temp_path}: {str(e)}")
