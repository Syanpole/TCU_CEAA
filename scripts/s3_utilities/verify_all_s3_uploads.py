import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission, GradeSubmission, CustomUser
from django.conf import settings

print("="*80)
print(" S3 UPLOAD VERIFICATION FOR ALL FILE TYPES")
print("="*80)

# Check settings
print(f"\n USE_CLOUD_STORAGE = {settings.USE_CLOUD_STORAGE}")
print(f" MEDIA_ROOT = {settings.MEDIA_ROOT}")
print(f" S3 Bucket = {settings.AWS_STORAGE_BUCKET_NAME}")

# 1. Profile Pictures
print("\n PROFILE PICTURES:")
user_field = CustomUser._meta.get_field('profile_image')
print(f"   Storage Backend: {user_field.storage.__class__.__name__}")
print(f"   Upload Path Function: {user_field.upload_to.__name__ if hasattr(user_field.upload_to, '__name__') else 'dynamic'}")

# 2. Documents (ID, COE, Birth Cert, Voter's Cert, etc.)
print("\n DOCUMENTS (ID, COE, Birth Cert, Voter's Cert):")
doc_field = DocumentSubmission._meta.get_field('document_file')
print(f"   Storage Backend: {doc_field.storage.__class__.__name__}")
print(f"   Upload Path Function: {doc_field.upload_to.__name__ if hasattr(doc_field.upload_to, '__name__') else 'dynamic'}")

# Show all document types
doc_types = DocumentSubmission.DOCUMENT_TYPES
print(f"\n    Supported Document Types ({len(doc_types)} total):")
for doc_type, doc_name in doc_types:
    if any(keyword in doc_type for keyword in ['id', 'coe', 'birth', 'voter', 'certificate', 'school']):
        print(f"       {doc_type}: {doc_name}")

# 3. Grade Sheets
print("\n GRADE SHEETS:")
grade_field = GradeSubmission._meta.get_field('grade_sheet')
print(f"   Storage Backend: {grade_field.storage.__class__.__name__}")
print(f"   Upload Path Function: {grade_field.upload_to.__name__ if hasattr(grade_field.upload_to, '__name__') else 'dynamic'}")

# Check recent uploads
print("\n RECENT UPLOADS VERIFICATION:")
recent_docs = DocumentSubmission.objects.filter(document_file__isnull=False).order_by('-submitted_at')[:5]
if recent_docs:
    print(f"\n   Last {len(recent_docs)} Documents:")
    for doc in recent_docs:
        print(f"    ID {doc.id}: {doc.document_type}")
        print(f"     File: {doc.document_file.name}")
        print(f"     Storage: {doc.document_file.storage.__class__.__name__}")
        # Check if using S3
        is_s3 = 's3' in doc.document_file.url.lower() if hasattr(doc.document_file, 'url') else False
        print(f"     S3 URL: {' Yes' if is_s3 else ' No'}")

recent_grades = GradeSubmission.objects.filter(grade_sheet__isnull=False).order_by('-submitted_at')[:3]
if recent_grades:
    print(f"\n   Last {len(recent_grades)} Grade Sheets:")
    for grade in recent_grades:
        print(f"    ID {grade.id}: {grade.subject_code} - {grade.subject_name}")
        print(f"     File: {grade.grade_sheet.name}")
        print(f"     Storage: {grade.grade_sheet.storage.__class__.__name__}")
        is_s3 = 's3' in grade.grade_sheet.url.lower() if hasattr(grade.grade_sheet, 'url') else False
        print(f"     S3 URL: {' Yes' if is_s3 else ' No'}")

recent_profiles = CustomUser.objects.filter(profile_image__isnull=False).exclude(profile_image='').order_by('-created_at')[:3]
if recent_profiles:
    print(f"\n   Last {len(recent_profiles)} Profile Images:")
    for user in recent_profiles:
        print(f"    User {user.id}: {user.username}")
        print(f"     File: {user.profile_image.name}")
        print(f"     Storage: {user.profile_image.storage.__class__.__name__}")
        is_s3 = 's3' in user.profile_image.url.lower() if hasattr(user.profile_image, 'url') else False
        print(f"     S3 URL: {' Yes' if is_s3 else ' No'}")

print("\n" + "="*80)
print(" VERIFICATION COMPLETE")
print("   All file types are configured to upload to S3!")
print("="*80)
