import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.rekognition_service import BiometricVerificationService

print("=" * 70)
print("TESTING FACE COMPARISON BOTH WAYS")
print("=" * 70)

rekognition = BiometricVerificationService()

school_id_s3_key = "media/documents/2025/11/FELICIANO-_SCHOOL_ID_K21j6mA.jpg"
selfie_s3_key = "liveness-sessions/05931d7d-b2a3-408c-b38b-6cba9d19ef2a/f01c7466-c13f-444a-af3c-c3eacf93528a/reference.jpg"

print("\nTest 1: School ID as SOURCE, Selfie as TARGET")
print("=" * 70)
try:
    result1 = rekognition.compare_faces_s3(
        source_image_path=school_id_s3_key,
        target_image_path=selfie_s3_key,
        similarity_threshold=80.0
    )
    print(f"Match: {result1.get('match_result')}")
    print(f"Similarity: {result1.get('similarity_score', 0):.2f}%")
    print(f"Confidence: {result1.get('confidence_level')}")
except Exception as e:
    print(f"Error: {str(e)}")

print("\n\nTest 2: Selfie as SOURCE, School ID as TARGET")
print("=" * 70)
try:
    result2 = rekognition.compare_faces_s3(
        source_image_path=selfie_s3_key,
        target_image_path=school_id_s3_key,
        similarity_threshold=80.0
    )
    print(f"Match: {result2.get('match_result')}")
    print(f"Similarity: {result2.get('similarity_score', 0):.2f}%")
    print(f"Confidence: {result2.get('confidence_level')}")
except Exception as e:
    print(f"Error: {str(e)}")

print("\n\nTest 3: Lower threshold (50%)")
print("=" * 70)
try:
    result3 = rekognition.compare_faces_s3(
        source_image_path=school_id_s3_key,
        target_image_path=selfie_s3_key,
        similarity_threshold=50.0
    )
    print(f"Match: {result3.get('match_result')}")
    print(f"Similarity: {result3.get('similarity_score', 0):.2f}%")
    print(f"Confidence: {result3.get('confidence_level')}")
except Exception as e:
    print(f"Error: {str(e)}")

print("\n" + "=" * 70)
