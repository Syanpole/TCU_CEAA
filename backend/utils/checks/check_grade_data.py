import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser

# Get user
username = '4peytonly'
academic_year = '2025-2026'
semester = '1st'

user = CustomUser.objects.get(username=username)

print("=" * 80)
print(f"📊 CHECKING GRADE DATA FOR {username}")
print("=" * 80)

# Get all grades for this semester
grades = GradeSubmission.objects.filter(
    student=user,
    academic_year=academic_year,
    semester=semester
).order_by('subject_code')

print(f"\nTotal Grades: {grades.count()}")

for grade in grades:
    print(f"\n{'='*60}")
    print(f"Subject: {grade.subject_code} - {grade.subject_name}")
    print(f"Status: {grade.status}")
    print(f"AI Confidence: {grade.ai_confidence_score:.1%}")
    print(f"Grade: {grade.grade_received}")
    
    if grade.ai_extracted_grades:
        print(f"\nAI Extracted Data:")
        print(f"  - Authentic: {grade.ai_extracted_grades.get('is_authentic', False)}")
        print(f"  - Detected Logos: {grade.ai_extracted_grades.get('detected_count', 0)}/3")
        print(f"  - Grade Matches: {grade.ai_extracted_grades.get('grade_matches', False)}")
        print(f"  - Subject in COE: {grade.ai_extracted_grades.get('subject_in_coe', False)}")
        
        if grade.ai_extracted_grades.get('detections'):
            print(f"  - Detections: {[d['label'] for d in grade.ai_extracted_grades['detections']]}")
    else:
        print("\n⚠️ No AI extracted data!")

print("\n" + "=" * 80)
