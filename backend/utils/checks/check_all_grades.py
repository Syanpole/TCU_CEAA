import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser

# Get all grade submissions in the system
print("=" * 80)
print("📊 ALL GRADE SUBMISSIONS IN DATABASE")
print("=" * 80)

all_grades = GradeSubmission.objects.all().order_by('-submitted_at')

print(f"\nTotal: {all_grades.count()} submissions\n")

for grade in all_grades:
    print(f"ID: {grade.id} | Student: {grade.student.username} ({grade.student.student_id})")
    print(f"   Subject: {grade.subject_code} - {grade.subject_name}")
    print(f"   Grade: {grade.grade_received} | Units: {grade.units}")
    print(f"   Status: {grade.status}")
    print(f"   AI Confidence: {grade.ai_confidence_score}%")
    print(f"   Submitted: {grade.submitted_at}")
    if grade.ai_extracted_grades:
        data = grade.ai_extracted_grades
        print(f"   Document Type: {data.get('document_type', 'N/A')}")
        print(f"   Authentic: {data.get('is_authentic', False)}")
        print(f"   Extracted Grade: {data.get('extracted_grade', 'None')}")
    print()
