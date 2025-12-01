"""
Fix adjudication record paths that are missing the storage location prefix
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication
import boto3
from django.conf import settings

def check_s3_file_exists(key):
    """Check if a file exists in S3"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3_client.head_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key
        )
        return True
    except:
        return False

def fix_adjudication_paths():
    """Fix adjudication records with incorrect paths"""
    adjudications = VerificationAdjudication.objects.all()
    
    print(f"\nChecking {adjudications.count()} adjudication records...")
    
    fixed_count = 0
    for adj in adjudications:
        if not adj.school_id_image_path:
            continue
            
        current_path = adj.school_id_image_path
        
        # Skip if already correct
        if current_path.startswith('media/documents/'):
            # Verify it exists
            if check_s3_file_exists(current_path):
                print(f"✓ ID {adj.id}: Already correct - {current_path}")
                continue
            else:
                print(f"⚠️ ID {adj.id}: Path is correct format but file not found in S3 - {current_path}")
                continue
        
        # Try different path variations
        possible_paths = [
            f"media/documents/{current_path}",  # Prepend full storage location
            current_path,  # Original
            f"media/{current_path}",  # Just media prefix
        ]
        
        correct_path = None
        for test_path in possible_paths:
            if check_s3_file_exists(test_path):
                correct_path = test_path
                break
        
        if correct_path and correct_path != current_path:
            print(f"✓ ID {adj.id}: Fixing path")
            print(f"  Old: {current_path}")
            print(f"  New: {correct_path}")
            
            adj.school_id_image_path = correct_path
            adj.save()
            fixed_count += 1
        elif correct_path:
            print(f"✓ ID {adj.id}: Path is correct - {current_path}")
        else:
            print(f"❌ ID {adj.id}: Could not find file in S3 for any path variation")
            print(f"   Tried: {current_path}")
    
    print(f"\n✅ Fixed {fixed_count} adjudication records")

if __name__ == '__main__':
    fix_adjudication_paths()
