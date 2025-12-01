import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication, CustomUser, AllowanceApplication

print("\n" + "="*60)
print("CREATING TEST FACE VERIFICATION RECORD")
print("="*60 + "\n")

# Get or create a test user
try:
    test_user = CustomUser.objects.filter(role='student').first()
    if not test_user:
        print("❌ No student users found. Please create a student user first.")
        exit(1)
    
    print(f"✅ Using test user: {test_user.email}")
    
    # Create test verification records with different confidence levels
    test_records = [
        {
            'automated_confidence_level': 'very_high',
            'automated_similarity_score': 0.995,
            'automated_liveness_score': 0.98,
            'automated_match_result': True,
            'notes': 'Very high confidence match - automated approval candidate'
        },
        {
            'automated_confidence_level': 'high',
            'automated_similarity_score': 0.965,
            'automated_liveness_score': 0.95,
            'automated_match_result': True,
            'notes': 'High confidence match - good for testing'
        },
        {
            'automated_confidence_level': 'low',
            'automated_similarity_score': 0.87,
            'automated_liveness_score': 0.82,
            'automated_match_result': False,
            'notes': 'Low confidence - requires careful review'
        },
        {
            'automated_confidence_level': 'very_low',
            'automated_similarity_score': 0.75,
            'automated_liveness_score': 0.70,
            'automated_match_result': False,
            'notes': 'Very low confidence - potential fraud attempt'
        },
    ]
    
    created_count = 0
    for record_data in test_records:
        verification = VerificationAdjudication.objects.create(
            user=test_user,
            school_id_image_path='/media/test/school_id.jpg',
            selfie_image_path='/media/test/selfie.jpg',
            verification_backend='rekognition',
            automated_liveness_score=record_data['automated_liveness_score'],
            automated_match_result=record_data['automated_match_result'],
            automated_similarity_score=record_data['automated_similarity_score'],
            automated_confidence_level=record_data['automated_confidence_level'],
            automated_verification_data={
                'test_record': True,
                'created_by': 'create_test_verification.py',
                'timestamp': datetime.now().isoformat()
            },
            liveness_data={
                'confidence': record_data['automated_liveness_score'],
                'status': 'SUCCEEDED'
            },
            status='pending_review',
            admin_decision='pending',
            admin_notes=record_data['notes']
        )
        created_count += 1
        print(f"\n✅ Created verification record #{created_count}:")
        print(f"   ID: {verification.id}")
        print(f"   Confidence Level: {verification.automated_confidence_level}")
        print(f"   Similarity Score: {verification.automated_similarity_score * 100:.1f}%")
        print(f"   Liveness Score: {verification.automated_liveness_score * 100:.1f}%")
        print(f"   Status: {verification.status}")
    
    print("\n" + "="*60)
    print(f"✅ Successfully created {created_count} test verification records!")
    print("\n💡 Now you can:")
    print("   1. Refresh the Admin Dashboard")
    print("   2. Click on the 'Face Verification' tab")
    print("   3. See the test records in the pending queue")
    print("   4. Review and approve/reject them")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ Error creating test records: {str(e)}")
    import traceback
    traceback.print_exc()
