import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from myapp.s3_utils import upload_file_to_s3
from django.conf import settings
import os

print("="*80)
print(" MIGRATING LOCAL FILES TO S3")
print("="*80)

# Find documents that might still be local
docs = DocumentSubmission.objects.filter(
    document_file__isnull=False,
    submitted_at__date__gte='2025-11-29'
).order_by('-submitted_at')[:10]

print(f"\nFound {docs.count()} recent documents\n")

migrated = 0
for doc in docs:
    file_name = doc.document_file.name
    print(f" Document ID {doc.id}: {doc.document_type}")
    print(f"   Path: {file_name}")
    
    # Check if file exists locally
    local_path = os.path.join('d:', 'Python', 'TCU_CEAA', 'backend', 'media', file_name)
    
    if os.path.exists(local_path):
        print(f"    Found locally: {local_path}")
        
        # Upload to S3
        try:
            success = upload_file_to_s3(local_path, file_name)
            if success:
                print(f"    Migrated to S3!")
                migrated += 1
            else:
                print(f"    Migration failed")
        except Exception as e:
            print(f"    Error: {e}")
    else:
        print(f"   ℹ  Not found locally (may already be in S3)")
    print()

print(f" Migrated {migrated} files to S3")
print("="*80)
