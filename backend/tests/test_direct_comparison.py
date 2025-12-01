import boto3
import os
from dotenv import load_dotenv

load_dotenv()

rekognition = boto3.client('rekognition', region_name='us-east-1')

school_id = "media/documents/2025/11/FELICIANO-_SCHOOL_ID_K21j6mA.jpg"
selfie = "liveness-sessions/05931d7d-b2a3-408c-b38b-6cba9d19ef2a/f01c7466-c13f-444a-af3c-c3eacf93528a/reference.jpg"
bucket = "tcu-ceaa-documents"

print("Testing direct AWS Rekognition CompareFaces API\n")
print(f"School ID: {school_id}")
print(f"Selfie: {selfie}")
print(f"Threshold: 50%\n")

try:
    response = rekognition.compare_faces(
        SourceImage={'S3Object': {'Bucket': bucket, 'Name': school_id}},
        TargetImage={'S3Object': {'Bucket': bucket, 'Name': selfie}},
        SimilarityThreshold=50.0,
        QualityFilter='AUTO'
    )
    
    print(f"Matched Faces: {len(response.get('FaceMatches', []))}")
    print(f"Unmatched Faces: {len(response.get('UnmatchedFaces', []))}")
    
    if response.get('FaceMatches'):
        for match in response['FaceMatches']:
            print(f"\n✓ MATCH FOUND!")
            print(f"  Similarity: {match['Similarity']:.2f}%")
            print(f"  Face Confidence: {match['Face']['Confidence']:.2f}%")
    else:
        print("\n✗ NO MATCHES FOUND")
        
    # Try with even lower threshold
    print("\n" + "="*50)
    print("Trying with 10% threshold...")
    
    response2 = rekognition.compare_faces(
        SourceImage={'S3Object': {'Bucket': bucket, 'Name': school_id}},
        TargetImage={'S3Object': {'Bucket': bucket, 'Name': selfie}},
        SimilarityThreshold=10.0,
        QualityFilter='AUTO'
    )
    
    if response2.get('FaceMatches'):
        for match in response2['FaceMatches']:
            print(f"\n✓ MATCH at 10% threshold!")
            print(f"  Similarity: {match['Similarity']:.2f}%")
    else:
        print("\n✗ Still no matches even at 10% threshold")
        print("This suggests the faces are genuinely very different")
        
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
