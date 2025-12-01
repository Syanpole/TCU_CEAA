import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerificationAdjudication

# Get all verification records
all_verifications = VerificationAdjudication.objects.all()
pending_verifications = VerificationAdjudication.objects.filter(status='pending_review')
low_confidence = VerificationAdjudication.objects.filter(automated_confidence_level__in=['low', 'very_low'])

print(f"\n{'='*60}")
print("VERIFICATION ADJUDICATION RECORDS")
print(f"{'='*60}\n")

print(f"📊 Total Records: {all_verifications.count()}")
print(f"⏳ Pending Review: {pending_verifications.count()}")
print(f"⚠️  Low Confidence: {low_confidence.count()}")

if all_verifications.count() == 0:
    print("\n❌ No VerificationAdjudication records found in the database.")
    print("\n💡 This is why the Face Verification dashboard appears empty.")
    print("   To test the dashboard, you need to:")
    print("   1. Configure AWS Rekognition credentials in backend/.env")
    print("   2. Have users submit face verification through the app")
    print("   3. Or manually create test records in Django admin")
else:
    print("\n✅ Records found! Dashboard should display them.")
    print(f"\nFirst 5 records:")
    for i, v in enumerate(all_verifications[:5], 1):
        print(f"\n  {i}. ID: {v.id}")
        print(f"     Status: {v.status}")
        print(f"     Admin Decision: {v.admin_decision}")
        print(f"     Automated Confidence: {v.automated_confidence_level}")
        print(f"     Similarity Score: {v.automated_similarity_score}")
        print(f"     Liveness Score: {v.automated_liveness_score}")
        print(f"     User: {v.user.email if v.user else 'N/A'}")
        print(f"     Created: {v.created_at.strftime('%Y-%m-%d %H:%M')}")

print(f"\n{'='*60}\n")
