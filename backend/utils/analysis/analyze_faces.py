import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.rekognition_service import BiometricVerificationService
import boto3

print("=" * 70)
print("ANALYZING FACES IN BOTH IMAGES")
print("=" * 70)

rekognition = BiometricVerificationService()

school_id_s3_key = "media/documents/2025/11/FELICIANO-_SCHOOL_ID_K21j6mA.jpg"
selfie_s3_key = "liveness-sessions/05931d7d-b2a3-408c-b38b-6cba9d19ef2a/f01c7466-c13f-444a-af3c-c3eacf93528a/reference.jpg"

print("\n1. Analyzing School ID Image")
print("=" * 70)
print(f"S3 Key: {school_id_s3_key}")

try:
    response = rekognition.client.detect_faces(
        Image={
            'S3Object': {
                'Bucket': 'tcu-ceaa-documents',
                'Name': school_id_s3_key
            }
        },
        Attributes=['ALL']
    )
    
    face_count = len(response['FaceDetails'])
    print(f"\n✓ Faces detected: {face_count}")
    
    if face_count > 0:
        for i, face in enumerate(response['FaceDetails'], 1):
            print(f"\n  Face #{i}:")
            print(f"    Confidence: {face['Confidence']:.2f}%")
            print(f"    Age Range: {face.get('AgeRange', {}).get('Low', 0)}-{face.get('AgeRange', {}).get('High', 0)}")
            print(f"    Gender: {face.get('Gender', {}).get('Value', 'Unknown')} ({face.get('Gender', {}).get('Confidence', 0):.1f}%)")
            print(f"    Emotions: {', '.join([e['Type'] for e in face.get('Emotions', [])][:3])}")
    else:
        print("\n  ✗ No faces detected in school ID image!")
        print("  This could be why comparison failed.")
        
except Exception as e:
    print(f"\n✗ Error analyzing school ID: {str(e)}")

print("\n\n2. Analyzing Selfie Image")
print("=" * 70)
print(f"S3 Key: {selfie_s3_key}")

try:
    response = rekognition.client.detect_faces(
        Image={
            'S3Object': {
                'Bucket': 'tcu-ceaa-documents',
                'Name': selfie_s3_key
            }
        },
        Attributes=['ALL']
    )
    
    face_count = len(response['FaceDetails'])
    print(f"\n✓ Faces detected: {face_count}")
    
    if face_count > 0:
        for i, face in enumerate(response['FaceDetails'], 1):
            print(f"\n  Face #{i}:")
            print(f"    Confidence: {face['Confidence']:.2f}%")
            print(f"    Age Range: {face.get('AgeRange', {}).get('Low', 0)}-{face.get('AgeRange', {}).get('High', 0)}")
            print(f"    Gender: {face.get('Gender', {}).get('Value', 'Unknown')} ({face.get('Gender', {}).get('Confidence', 0):.1f}%)")
            print(f"    Emotions: {', '.join([e['Type'] for e in face.get('Emotions', [])][:3])}")
    else:
        print("\n  ✗ No faces detected in selfie!")
        
except Exception as e:
    print(f"\n✗ Error analyzing selfie: {str(e)}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
