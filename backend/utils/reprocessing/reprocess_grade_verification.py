import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.tasks import verify_grade_sheet_task

# Get user
username = '4peytonly'
academic_year = '2025-2026'
semester = '1st'

user = CustomUser.objects.get(username=username)

print("=" * 80)
print(f"🔄 RE-PROCESSING GRADE VERIFICATION FOR {username}")
print("=" * 80)

# Get all pending grades with 0% confidence
grades = GradeSubmission.objects.filter(
    student=user,
    academic_year=academic_year,
    semester=semester,
    status='pending',
    ai_confidence_score=0.0
)

print(f"\nFound {grades.count()} grades needing AI verification")

if grades.count() == 0:
    print("\n✅ No grades need re-processing")
else:
    print("\n🔄 Starting AI verification...")
    
    for grade in grades:
        print(f"\n📄 Processing: {grade.subject_code} - {grade.subject_name}")
        try:
            verify_grade_sheet_task(grade.id)
            
            # Refresh from database to get updated values
            grade.refresh_from_db()
            
            print(f"   ✅ Verified: {grade.ai_confidence_score:.1%} confidence")
            print(f"   Status: {grade.status}")
            
            if grade.ai_extracted_grades:
                is_authentic = grade.ai_extracted_grades.get('is_authentic', False)
                detected = grade.ai_extracted_grades.get('detected_count', 0)
                print(f"   Authentic: {'YES' if is_authentic else 'NO'} ({detected}/3 logos)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ AI VERIFICATION COMPLETE")
    print("=" * 80)
    
    # Summary
    verified_grades = GradeSubmission.objects.filter(
        student=user,
        academic_year=academic_year,
        semester=semester,
        ai_confidence_score__gt=0.0
    )
    
    authentic_count = sum(
        1 for g in verified_grades 
        if g.ai_extracted_grades and g.ai_extracted_grades.get('is_authentic', False)
    )
    
    print(f"\n📊 Summary:")
    print(f"   Total Grades: {grades.count()}")
    print(f"   Verified: {verified_grades.count()}")
    print(f"   Authentic: {authentic_count}/{verified_grades.count()}")
    print(f"   Average Confidence: {sum(g.ai_confidence_score for g in verified_grades) / verified_grades.count():.1%}")

print("\n" + "=" * 80)
