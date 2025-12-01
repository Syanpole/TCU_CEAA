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
        # Liveness session files already have the correct path
        if not clean_key.startswith(('media/', 'liveness-sessions/', 'grades/', 'documents/')):
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
        if not clean_key.startswith(('media/', 'liveness-sessions/', 'grades/', 'documents/')):
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
