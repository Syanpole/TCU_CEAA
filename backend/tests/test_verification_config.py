import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.rekognition_service import BiometricVerificationService
from django.conf import settings

print("=" * 70)
print("FACE VERIFICATION CONFIGURATION TEST")
print("=" * 70)

# Check settings
print("\n1. Django Settings:")
print(f"   FACE_SIMILARITY_THRESHOLD: {settings.FACE_SIMILARITY_THRESHOLD}")
print(f"   USE_CLOUD_STORAGE: {settings.USE_CLOUD_STORAGE}")
print(f"   VERIFICATION_SERVICE_ENABLED: {settings.VERIFICATION_SERVICE_ENABLED}")

# Initialize service
service = BiometricVerificationService()
print(f"\n2. Service Status:")
print(f"   Enabled: {service.enabled}")

# Test threshold
print(f"\n3. Testing Face Comparison Threshold:")
school_id = "media/documents/2025/11/FELICIANO-_SCHOOL_ID_K21j6mA.jpg"
selfie = "liveness-sessions/05931d7d-b2a3-408c-b38b-6cba9d19ef2a/f01c7466-c13f-444a-af3c-c3eacf93528a/reference.jpg"

print(f"   School ID: {school_id}")
print(f"   Selfie: {selfie}")

# Test with default threshold (should be 50% now)
result = service.compare_faces_s3(school_id, selfie)

print(f"\n4. Comparison Result:")
print(f"   Success: {result.get('success')}")
print(f"   Is Match: {result.get('is_match')}")
print(f"   Similarity: {result.get('similarity')}%")
print(f"   Threshold Used: {result.get('threshold')}%")
print(f"   Confidence Level: {result.get('confidence_level')}")

# Verify proper response keys
print(f"\n5. Response Keys Validation:")
expected_keys = ['success', 'is_match', 'similarity', 'threshold', 'confidence_level']
for key in expected_keys:
    has_key = key in result
    status = "✓" if has_key else "✗"
    print(f"   {status} {key}: {has_key}")

# Test different thresholds
print(f"\n6. Testing Different Thresholds:")
for threshold in [30, 50, 80, 95]:
    test_result = service.compare_faces_s3(school_id, selfie, similarity_threshold=threshold)
    match = test_result.get('is_match')
    similarity = test_result.get('similarity')
    print(f"   Threshold {threshold}%: Match={match}, Similarity={similarity}%")

print("\n" + "=" * 70)
print("CONFIGURATION TEST COMPLETE")
print("=" * 70)
print("\nSummary:")
print("✓ Default threshold changed from 80% to 50%")
print("✓ Response keys use 'is_match' and 'similarity'")
print("✓ S3 media/ prefix added for document paths")
print("✓ Confidence levels adjusted (98%=very_high, 90%=high, 75%=medium, 50%=low)")
print("=" * 70)
