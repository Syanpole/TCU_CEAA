"""Test current Django storage configuration"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage

print("=" * 80)
print("DJANGO STORAGE CONFIGURATION")
print("=" * 80)

print(f"\n📊 Settings:")
print(f"   USE_CLOUD_STORAGE: {settings.USE_CLOUD_STORAGE}")
print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
print(f"   AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
print(f"   AWS_S3_REGION_NAME: {getattr(settings, 'AWS_S3_REGION_NAME', 'Not set')}")

print(f"\n💾 Active Storage Backend:")
print(f"   Type: {type(default_storage)}")
print(f"   Class: {default_storage.__class__.__name__}")
print(f"   Module: {default_storage.__class__.__module__}")

if hasattr(default_storage, 'location'):
    print(f"   Location: {default_storage.location}")
if hasattr(default_storage, 'bucket_name'):
    print(f"   Bucket: {default_storage.bucket_name}")

print("\n" + "=" * 80)
