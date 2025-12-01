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
print("CHECKING ALL COE DOCUMENTS STATUS")
print("=" * 80)

# Get all COEs (not just approved)
user = User.objects.get(username='4peytonly')
coes = DocumentSubmission.objects.filter(
    student=user,
    document_type='certificate_of_enrollment'
).order_by('-submitted_at')

print(f"\nUser: {user.username} ({user.get_full_name()})")
print(f"Total COEs: {coes.count()}")

for idx, coe in enumerate(coes, 1):
    print(f"\n{'='*80}")
    print(f"COE #{idx}")
    print(f"{'='*80}")
    print(f"Document ID: {coe.id}")
    print(f"Submitted: {coe.submitted_at}")
    print(f"Status: {coe.status}")
    print(f"Subject count: {coe.subject_count}")
    print(f"Has extracted_subjects: {bool(coe.extracted_subjects)}")
    print(f"AI Analysis Completed: {coe.ai_analysis_completed}")
    print(f"AI Confidence: {coe.ai_confidence_score if coe.ai_confidence_score else 'N/A'}")
    
    if coe.extracted_subjects:
        print(f"\n✅ Extracted subjects ({len(coe.extracted_subjects)}):")
        for s in coe.extracted_subjects:
            print(f"  - {s['subject_code']}: {s['subject_name']}")
    else:
        print("\n⚠️ No extracted subjects")

print("\n" + "="*80)
