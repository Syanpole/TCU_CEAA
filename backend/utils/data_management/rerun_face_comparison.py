import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication
from myapp.rekognition_service import BiometricVerificationService

print("=" * 70)
print("RE-RUNNING FACE COMPARISON WITH CORRECT SCHOOL ID")
print("=" * 70)

# Get the verification adjudication record
adj = VerificationAdjudication.objects.get(id=5)

print(f"\nVerification Adjudication ID: {adj.id}")
print(f"User: {adj.user.username}")
print(f"Current Status: {adj.status}")
print(f"\nSchool ID: {adj.school_id_image_path}")
print(f"Selfie: {adj.selfie_image_path}")

# Initialize Rekognition service
rekognition = BiometricVerificationService()

print(f"\n{'=' * 70}")
print("PERFORMING FACE COMPARISON")
print("=" * 70)

try:
    # Compare faces using S3 paths
    school_id_s3_key = f"media/{adj.school_id_image_path}"
    selfie_s3_key = adj.selfie_image_path  # Already has correct path
    
    print(f"\nSource (School ID): {school_id_s3_key}")
    print(f"Target (Selfie): {selfie_s3_key}")
    print("\nCalling AWS Rekognition CompareFaces...")
    
    result = rekognition.compare_faces_s3(
        source_image_path=school_id_s3_key,
        target_image_path=selfie_s3_key,
        similarity_threshold=50.0  # Lower threshold to detect matches
    )
    
    print(f"\n{'=' * 70}")
    print("FACE COMPARISON RESULTS")
    print("=" * 70)
    
    if result.get('success'):
        print(f"\n✓ Face comparison completed successfully!")
        print(f"\n  Match Result: {'✓ MATCHED' if result.get('is_match') else '✗ NOT MATCHED'}")
        print(f"  Similarity Score: {result.get('similarity', 0):.2f}%")
        print(f"  Confidence Level: {result.get('confidence_level', 'unknown').upper()}")
        print(f"  Threshold Used: {result.get('threshold', 0):.2f}%")
        
        # Update the adjudication record
        adj.automated_match_result = result.get('is_match', False)
        adj.automated_similarity_score = result.get('similarity', 0)
        adj.automated_confidence_level = result.get('confidence_level', 'very_low')
        adj.save()
        
        print(f"\n✓ Updated VerificationAdjudication record")
        
        print(f"\n{'=' * 70}")
        print("UPDATED DATABASE VALUES")
        print("=" * 70)
        print(f"  Match Result: {adj.automated_match_result}")
        print(f"  Similarity: {adj.automated_similarity_score:.2f}%")
        print(f"  Confidence: {adj.automated_confidence_level}")
        
    else:
        print(f"\n✗ Face comparison failed")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"\n✗ Error during face comparison: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n{'=' * 70}")
print("COMPLETE - Refresh admin dashboard to see updated results")
print("=" * 70)
