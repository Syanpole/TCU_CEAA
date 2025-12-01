"""
Test script to verify automatic COE subject extraction via signals.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TESTING AUTOMATIC COE SUBJECT EXTRACTION")
print("=" * 80)

# Find a COE without subjects
user = User.objects.get(username='4peytonly')
coe = DocumentSubmission.objects.filter(
    student=user,
    document_type='certificate_of_enrollment',
    status='approved'
).filter(
    extracted_subjects__isnull=True
).first() or DocumentSubmission.objects.filter(
    student=user,
    document_type='certificate_of_enrollment',
    status='approved',
    extracted_subjects=[]
).first()

if coe:
    print(f"\nFound COE without subjects: ID {coe.id}")
    print(f"Status: {coe.status}")
    print(f"Current subject count: {coe.subject_count}")
    
    print("\n🔄 Simulating status change to trigger signal...")
    print("   (Changing status to 'pending' then back to 'approved')")
    
    # Change status temporarily
    coe.status = 'pending'
    coe.save()
    print("   Status changed to 'pending'")
    
    # Change back to approved (should trigger signal)
    coe.status = 'approved'
    coe.save()
    print("   Status changed to 'approved'")
    
    # Reload from database
    coe.refresh_from_db()
    
    print(f"\n📊 After signal processing:")
    print(f"Subject count: {coe.subject_count}")
    print(f"Has extracted_subjects: {bool(coe.extracted_subjects)}")
    
    if coe.extracted_subjects:
        print(f"\n✅ SUCCESS! Subjects extracted automatically:")
        for idx, subject in enumerate(coe.extracted_subjects, 1):
            print(f"  {idx}. {subject['subject_code']} - {subject['subject_name']}")
    else:
        print("\n❌ FAILED: Subjects were not extracted")
        print("Check the logs for errors")
else:
    print("\nAll COEs already have extracted subjects!")
    print("Signal is working correctly or not needed.")

print("\n" + "=" * 80)
