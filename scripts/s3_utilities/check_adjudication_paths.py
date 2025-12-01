import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication

print("="*80)
print(" CHECKING VERIFICATION ADJUDICATION IMAGE PATHS")
print("="*80)

recent = VerificationAdjudication.objects.order_by('-created_at').first()

if recent:
    print(f"\nMost Recent Adjudication (ID: {recent.id}):")
    print(f"   User: {recent.user.username} ({recent.user.student_id})")
    print(f"   School ID Path: '{recent.school_id_image_path}'")
    print(f"   Selfie Path: '{recent.selfie_image_path}'")
    print(f"   Created: {recent.created_at}")
    
    # Check if paths start with different prefixes
    print(f"\n Path Analysis:")
    print(f"   School ID starts with 'documents/': {recent.school_id_image_path.startswith('documents/')}")
    print(f"   School ID starts with 'media/': {recent.school_id_image_path.startswith('media/')}")
    print(f"   School ID starts with 'liveness': {recent.school_id_image_path.startswith('liveness')}")
    print(f"   Selfie starts with 'liveness': {recent.selfie_image_path.startswith('liveness')}")
    
    # Try to construct S3 key
    school_id_key = recent.school_id_image_path
    if not school_id_key.startswith('media/') and not school_id_key.startswith('liveness'):
        school_id_key = f"media/{school_id_key}"
    
    print(f"\n S3 Keys:")
    print(f"   School ID S3 Key: '{school_id_key}'")
    print(f"   Selfie S3 Key: '{recent.selfie_image_path}'")
else:
    print("\n No adjudication records found")

print("\n" + "="*80)
