# Cloud Storage & Advanced OCR Setup Guide

## Overview

This guide explains how to set up **Cloud Storage (Amazon S3)** and **Advanced OCR** capabilities for the TCU CEAA system. These features provide:

- **Cloud Storage**: Scalable, secure file storage for documents, grades, and profile images
- **Advanced OCR**: High-accuracy text extraction from documents using AI-powered cloud processing

> **Note**: The system uses industry-standard cloud services for enhanced reliability and accuracy. All terminology has been simplified for clarity.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Configuration](#configuration)
4. [Testing](#testing)
5. [Migration](#migration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Dependencies

Already included in `requirements.txt`:
- `boto3` - Cloud service SDK
- `django-storages` - Django cloud storage backend
- `botocore` - Core cloud service library

### Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

## AWS Account Setup

### Step 1: Create AWS Account

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process
4. **Note**: You'll need a credit card, but services have free tier limits

### Step 2: Create S3 Bucket

1. Log into AWS Console
2. Search for "S3" in the services menu
3. Click "Create bucket"
4. **Bucket settings**:
   - **Name**: `tcu-ceaa-documents` (must be globally unique)
   - **Region**: Choose closest to you (e.g., `us-east-1`)
   - **Block Public Access**: Keep ALL boxes checked (for security)
   - **Versioning**: Optional (recommended for production)
   - **Encryption**: Enable default encryption
5. Click "Create bucket"

### Step 3: Enable Advanced OCR Service

1. In AWS Console, search for "Textract"
2. Click on the service to access it
3. No additional setup needed - it's ready to use
4. **Note**: Textract charges per page processed (check current pricing)

### Step 4: Create IAM User

1. Search for "IAM" in AWS Console
2. Click "Users" → "Add users"
3. **User details**:
   - Username: `tcu-ceaa-system`
   - Access type: ✅ Programmatic access
4. **Permissions**:
   - Click "Attach policies directly"
   - Select these policies:
     - ✅ `AmazonS3FullAccess`
     - ✅ `AmazonTextractFullAccess`
5. Click through to create user
6. **IMPORTANT**: Save the credentials shown:
   - Access Key ID
   - Secret Access Key
   - ⚠️ You won't be able to see the secret key again!

---

## Configuration

### Step 1: Update `.env` File

Edit `backend/.env` and add your AWS credentials:

```env
# ============================================================================
# CLOUD STORAGE CONFIGURATION (Amazon S3)
# ============================================================================
# Set USE_CLOUD_STORAGE=True to enable S3, False for local storage
USE_CLOUD_STORAGE=True

# AWS Credentials (Required when USE_CLOUD_STORAGE=True)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=tcu-ceaa-documents
AWS_S3_REGION_NAME=us-east-1

# S3 Configuration
AWS_S3_CUSTOM_DOMAIN=
AWS_S3_FILE_OVERWRITE=False
AWS_DEFAULT_ACL=private
AWS_S3_OBJECT_PARAMETERS={'CacheControl': 'max-age=86400'}

# ============================================================================
# ADVANCED OCR CONFIGURATION
# ============================================================================
# Enable advanced cloud-based OCR processing for better accuracy
USE_ADVANCED_OCR=True

# OCR Processing Region (must match AWS region)
ADVANCED_OCR_REGION=us-east-1

# OCR Confidence Threshold (0-100, higher = stricter)
OCR_CONFIDENCE_THRESHOLD=80
```

### Step 2: Security Best Practices

⚠️ **IMPORTANT**: Never commit AWS credentials to Git!

Add to `.gitignore`:
```
.env
*.pem
*.key
credentials.json
```

### Step 3: Verify Configuration

Run Django check:
```powershell
cd backend
python manage.py check
```

Expected output:
```
System check identified no issues (0 silenced).
```

---

## Testing

### Test 1: Cloud Storage Connection

```powershell
cd backend
python manage.py test_cloud_storage
```

Expected output:
```
============================================================
CLOUD STORAGE TEST
============================================================
✅ S3 bucket 'tcu-ceaa-documents' is accessible
✅ Can write files to bucket
✅ Can read files from bucket
✅ Can delete files from bucket
============================================================
```

### Test 2: Advanced OCR Service

```powershell
python manage.py test_advanced_ocr
```

Expected output:
```
============================================================
ADVANCED OCR SERVICE TEST
============================================================
📋 Configuration Status:
   USE_ADVANCED_OCR: True
   OCR Region: us-east-1
   Confidence Threshold: 80%
   Service Enabled: True

✅ Advanced OCR Service is enabled and configured
============================================================
```

### Test 3: OCR with Sample Document

```powershell
python manage.py test_advanced_ocr --file path/to/sample-grade.pdf
```

Expected output:
```
🔍 Testing OCR with file: sample-grade.pdf
📄 Extracting text...
✅ Text extraction successful
   Confidence: 95.23%
   Blocks found: 142
   
📊 Extracting tables...
✅ Found 2 table(s)
   Table 1: 5 rows x 4 cols
   
📝 Extracting form fields...
✅ Found 8 form field(s)
   Student Name: John Doe (98.5%)
   Student ID: 2024-001 (99.2%)
```

---

## Migration

### Migrate Existing Files to Cloud

If you have existing files stored locally, migrate them to cloud storage:

#### Step 1: Dry Run (Preview)

```powershell
python manage.py migrate_to_cloud_storage --dry-run
```

This shows what would be migrated without actually moving files.

#### Step 2: Actual Migration

```powershell
python manage.py migrate_to_cloud_storage
```

Expected output:
```
============================================================
CLOUD STORAGE MIGRATION
============================================================
✅ Cloud storage is enabled
   Bucket: tcu-ceaa-documents
   Region: us-east-1

📸 Migrating profile images...
   Found 150 file(s) to process
   ✅ Migrated: profiles/user_1.jpg
   ✅ Migrated: profiles/user_2.jpg
   ... (progress shown)

📄 Migrating document submissions...
   Found 320 file(s) to process
   ... (progress shown)

📊 Migrating grade submissions...
   Found 450 file(s) to process
   ... (progress shown)

============================================================
MIGRATION SUMMARY
============================================================
✅ Successfully migrated: 920
⏭️  Skipped: 0
❌ Failed: 0

🎉 Migration completed successfully!
```

#### Step 3: Verify Migration

1. Check AWS S3 Console
2. Navigate to your bucket
3. Verify folders exist: `profiles/`, `documents/`, `grades/`
4. Check file counts match migration summary

---

## Usage

### In Views (Example)

```python
from myapp.advanced_ocr_service import get_advanced_ocr_service

def process_grade_submission(request):
    grade_file = request.FILES.get('grade_sheet')
    
    # Get OCR service
    ocr_service = get_advanced_ocr_service()
    
    if ocr_service.is_enabled():
        # Read file bytes
        file_bytes = grade_file.read()
        
        # Extract text with Advanced OCR
        result = ocr_service.extract_text(file_bytes)
        
        if result['success']:
            extracted_text = result['text']
            confidence = result['confidence']
            
            # Process extracted text
            # ... your logic here
        else:
            # Fallback to local OCR
            pass
    
    # File is automatically saved to S3 if USE_CLOUD_STORAGE=True
    submission.grade_sheet = grade_file
    submission.save()
```

### Storage Backend Usage

Files are automatically stored in S3 when `USE_CLOUD_STORAGE=True`:

```python
# Profile images → s3://bucket/profiles/
user.profile_image = uploaded_image
user.save()

# Documents → s3://bucket/documents/
doc.document_file = uploaded_doc
doc.save()

# Grades → s3://bucket/grades/ (encrypted)
grade.grade_sheet = uploaded_grade
grade.save()
```

---

## Cost Estimation

### S3 Storage Costs (US East Region)

- **Storage**: $0.023 per GB/month
- **Requests**: 
  - PUT/POST: $0.005 per 1,000 requests
  - GET: $0.0004 per 1,000 requests
- **Data Transfer**: 
  - First 1 GB/month: FREE
  - Next 9.999 TB: $0.09 per GB

**Example**: 100 GB storage + 10,000 uploads/month = ~$2.35/month

### Advanced OCR Costs

- **Page Processing**: ~$1.50 per 1,000 pages
- **Form/Table Extraction**: ~$15.00 per 1,000 pages

**Example**: 500 pages/month = ~$0.75/month

### Free Tier (First 12 Months)

- **S3**: 5 GB storage, 20,000 GET, 2,000 PUT requests
- **Advanced OCR**: 1,000 pages per month FREE for 3 months

---

## Troubleshooting

### Error: "The AWS Access Key Id you provided does not exist"

**Solution**: Check that:
1. Access Key ID is correct in `.env`
2. No extra spaces in the key
3. IAM user was created successfully

### Error: "Access Denied"

**Solution**: Ensure IAM user has these policies:
- `AmazonS3FullAccess`
- `AmazonTextractFullAccess`

### Error: "Bucket does not exist"

**Solution**: 
1. Check bucket name matches exactly
2. Verify bucket region matches `AWS_S3_REGION_NAME`
3. Ensure bucket is in the correct AWS account

### Error: "Advanced OCR Service not enabled"

**Solution**:
1. Set `USE_ADVANCED_OCR=True` in `.env`
2. Verify AWS credentials are correct
3. Check AWS region supports the Textract service

### Files Not Uploading to S3

**Solution**:
1. Verify `USE_CLOUD_STORAGE=True` in `.env`
2. Run: `python manage.py collectstatic` if needed
3. Check Django error logs for detailed error messages
4. Test connection: `python manage.py test_cloud_storage`

### High Costs

**Solution**:
1. Monitor AWS Cost Explorer
2. Implement lifecycle policies (auto-delete old files)
3. Use S3 Intelligent-Tiering for cost optimization
4. Cache OCR results to avoid re-processing

---

## Security Checklist

- [ ] AWS credentials stored in `.env` (not in code)
- [ ] `.env` file added to `.gitignore`
- [ ] S3 bucket has public access BLOCKED
- [ ] IAM user has minimum required permissions
- [ ] Files stored with `private` ACL
- [ ] Grade sheets use server-side encryption
- [ ] Regular AWS billing monitoring enabled
- [ ] CloudWatch alarms set for unusual activity

---

## Feature Comparison

### Local Storage vs Cloud Storage

| Feature | Local Storage | Cloud Storage |
|---------|--------------|---------------|
| **Scalability** | Limited by disk | Unlimited |
| **Reliability** | Single point of failure | 99.999999999% durability |
| **Cost** | Server costs only | Pay per GB |
| **Backup** | Manual | Automatic |
| **Access Speed** | Fast (local) | Network dependent |
| **Security** | Server security | AWS-grade security |

### Local OCR vs Advanced OCR

| Feature | Local OCR (Tesseract) | Advanced OCR (Cloud) |
|---------|---------------------|---------------------|
| **Accuracy** | ~85% | ~95-98% |
| **Speed** | Slower | Faster |
| **Table Detection** | Basic | Advanced |
| **Form Recognition** | Limited | Excellent |
| **Handwriting** | Poor | Good |
| **Cost** | Free | ~$1.50 per 1,000 pages |
| **Languages** | Multiple | 100+ languages |

---

## Support

For issues or questions:

1. Check logs: `backend/logs/django.log`
2. Review AWS CloudWatch logs
3. Run diagnostic commands above
4. Contact development team

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Author**: TCU CEAA Development Team
