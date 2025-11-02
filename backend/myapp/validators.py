"""
File Upload Validators for TCU-CEAA System
Provides comprehensive file validation for security and quality control.
"""

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import os


@deconstructible
class FileSizeValidator:
    """
    Validator to check file size limits.
    Usage: validators=[FileSizeValidator(max_size_mb=10, min_size_kb=1)]
    """
    
    def __init__(self, max_size_mb=10, min_size_kb=1):
        self.max_size_mb = max_size_mb
        self.min_size_kb = min_size_kb
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.min_size_bytes = min_size_kb * 1024
    
    def __call__(self, value):
        file_size = value.size
        
        # Check maximum size
        if file_size > self.max_size_bytes:
            raise ValidationError(
                f'File size exceeds maximum allowed size of {self.max_size_mb}MB. '
                f'Your file is {file_size / (1024 * 1024):.2f}MB.'
            )
        
        # Check minimum size
        if file_size < self.min_size_bytes:
            raise ValidationError(
                f'File is too small ({file_size} bytes). Minimum size is {self.min_size_kb}KB. '
                f'Please ensure you uploaded a valid document.'
            )
    
    def __eq__(self, other):
        return (
            isinstance(other, FileSizeValidator) and
            self.max_size_mb == other.max_size_mb and
            self.min_size_kb == other.min_size_kb
        )


@deconstructible
class FileTypeValidator:
    """
    Validator to check file types based on content (magic numbers), not just extension.
    More secure than checking file extension alone.
    """
    
    # Comprehensive MIME type mappings
    ALLOWED_TYPES = {
        'document': {
            'application/pdf': ['.pdf'],
            'application/msword': ['.doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'application/vnd.ms-excel': ['.xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        },
        'image': {
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'image/gif': ['.gif'],
            'image/bmp': ['.bmp'],
            'image/tiff': ['.tiff', '.tif'],
        },
        'grade_sheet': {
            'application/pdf': ['.pdf'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls'],
        }
    }
    
    def __init__(self, allowed_category='document'):
        """
        allowed_category: 'document', 'image', or 'grade_sheet'
        """
        self.allowed_category = allowed_category
        self.allowed_types = self.ALLOWED_TYPES.get(allowed_category, self.ALLOWED_TYPES['document'])
    
    def __call__(self, value):
        # Get file extension
        filename = value.name if hasattr(value, 'name') else ''
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Get MIME type from content
        content_type = value.content_type if hasattr(value, 'content_type') else None
        
        # Validate content type
        if content_type not in self.allowed_types:
            allowed_extensions = set()
            for exts in self.allowed_types.values():
                allowed_extensions.update(exts)
            
            raise ValidationError(
                f'Invalid file type: {content_type or "unknown"}. '
                f'Allowed types: {", ".join(sorted(allowed_extensions))}. '
                f'Please upload a valid {self.allowed_category} file.'
            )
        
        # Validate file extension matches content type
        expected_extensions = self.allowed_types[content_type]
        if file_ext not in expected_extensions:
            raise ValidationError(
                f'File extension "{file_ext}" does not match file type. '
                f'Expected extensions for {content_type}: {", ".join(expected_extensions)}. '
                f'File may be corrupted or renamed incorrectly.'
            )
    
    def __eq__(self, other):
        return (
            isinstance(other, FileTypeValidator) and
            self.allowed_category == other.allowed_category
        )


@deconstructible
class MaliciousFileValidator:
    """
    Validator to detect potentially malicious files.
    Checks for:
    - Executable content in disguise
    - Script injections
    - Suspicious file patterns
    """
    
    # Known malicious file signatures (magic numbers)
    MALICIOUS_SIGNATURES = [
        b'MZ',  # Windows executable
        b'\x7fELF',  # Linux executable
        b'#!',  # Shell script
        b'<script',  # HTML/JS script (case insensitive check done separately)
        b'<?php',  # PHP script
    ]
    
    # Dangerous extensions that should never be uploaded
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.app', '.deb', '.rpm', '.sh', '.bash', '.php', '.asp',
        '.aspx', '.jsp', '.cgi', '.pl', '.py', '.rb', '.dll', '.so'
    ]
    
    def __call__(self, value):
        filename = value.name if hasattr(value, 'name') else ''
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Check for dangerous extensions
        if file_ext in self.DANGEROUS_EXTENSIONS:
            raise ValidationError(
                f'File type "{file_ext}" is not allowed for security reasons. '
                f'Please upload document or image files only.'
            )
        
        # Read first 1KB to check for malicious signatures
        try:
            value.seek(0)
            file_header = value.read(1024)
            value.seek(0)
            
            # Check for malicious signatures
            for signature in self.MALICIOUS_SIGNATURES:
                if file_header.startswith(signature):
                    raise ValidationError(
                        'File contains suspicious content and cannot be uploaded. '
                        'If you believe this is an error, please contact support.'
                    )
            
            # Check for script injection attempts (case insensitive)
            file_header_lower = file_header.lower()
            if b'<script' in file_header_lower or b'javascript:' in file_header_lower:
                raise ValidationError(
                    'File contains script content and cannot be uploaded for security reasons.'
                )
            
        except Exception as e:
            # If we can't read the file, be cautious and reject
            raise ValidationError(
                f'Unable to validate file security. Please try again or contact support. '
                f'Error: {str(e)}'
            )
    
    def __eq__(self, other):
        return isinstance(other, MaliciousFileValidator)


@deconstructible
class ProfileImageValidator:
    """
    Specialized validator for profile images.
    Ensures images are appropriate size and format.
    """
    
    def __init__(self, max_size_mb=5, max_width=2000, max_height=2000):
        self.max_size_mb = max_size_mb
        self.max_width = max_width
        self.max_height = max_height
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def __call__(self, value):
        from PIL import Image
        
        # Check file size
        if value.size > self.max_size_bytes:
            raise ValidationError(
                f'Image size exceeds {self.max_size_mb}MB. '
                f'Please upload a smaller image or compress it.'
            )
        
        # Check image dimensions
        try:
            value.seek(0)
            img = Image.open(value)
            width, height = img.size
            value.seek(0)
            
            if width > self.max_width or height > self.max_height:
                raise ValidationError(
                    f'Image dimensions ({width}x{height}) exceed maximum allowed '
                    f'({self.max_width}x{self.max_height}). Please resize your image.'
                )
            
            # Check if image is valid (can be opened and processed)
            img.verify()
            
        except Exception as e:
            raise ValidationError(
                f'Invalid or corrupted image file. Please upload a valid image. '
                f'Error: {str(e)}'
            )
    
    def __eq__(self, other):
        return (
            isinstance(other, ProfileImageValidator) and
            self.max_size_mb == other.max_size_mb and
            self.max_width == other.max_width and
            self.max_height == other.max_height
        )


# Validation constants for easy reuse
MAX_DOCUMENT_SIZE_MB = 10  # 10MB for documents
MAX_IMAGE_SIZE_MB = 5      # 5MB for images
MAX_GRADE_SHEET_SIZE_MB = 10  # 10MB for grade sheets
MIN_FILE_SIZE_KB = 1       # 1KB minimum to prevent empty files

# Pre-configured validators for common use cases
document_validators = [
    FileSizeValidator(max_size_mb=MAX_DOCUMENT_SIZE_MB, min_size_kb=MIN_FILE_SIZE_KB),
    FileTypeValidator(allowed_category='document'),
    MaliciousFileValidator(),
]

grade_sheet_validators = [
    FileSizeValidator(max_size_mb=MAX_GRADE_SHEET_SIZE_MB, min_size_kb=MIN_FILE_SIZE_KB),
    FileTypeValidator(allowed_category='grade_sheet'),
    MaliciousFileValidator(),
]

profile_image_validators = [
    FileSizeValidator(max_size_mb=MAX_IMAGE_SIZE_MB, min_size_kb=MIN_FILE_SIZE_KB),
    FileTypeValidator(allowed_category='image'),
    ProfileImageValidator(max_size_mb=MAX_IMAGE_SIZE_MB),
    MaliciousFileValidator(),
]
