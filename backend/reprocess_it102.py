import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from myapp.tasks import verify_grade_sheet_task

print("=" * 80)
print("REPROCESSING IT 102 GRADE")
print("=" * 80)

try:
    grade = GradeSubmission.objects.get(
        student_id=25, 
        subject_code='IT 102', 
        academic_year='2025-2026', 
        semester='1st'
    )
    
    print(f"\nFound: {grade.subject_code} - {grade.subject_name}")
    print(f"Current Status: {grade.status}")
    print(f"Current Confidence: {grade.ai_confidence_score:.0%}")
    print(f"User Input Grade: {grade.grade_received}")
    
    print("\n🔄 Triggering AI verification task...")
    
    # Trigger verification
    verify_grade_sheet_task(grade.id)
    
    # Refresh from database
    grade.refresh_from_db()
    
    print("\n✅ REPROCESSING COMPLETE!")
    print(f"New Status: {grade.status}")
    print(f"New Confidence: {grade.ai_confidence_score:.0%}")
    
    if grade.ai_confidence_score >= 0.85:
        print("\n🎉 HIGH CONFIDENCE! Grade should be auto-approved!")
    elif grade.ai_confidence_score >= 0.70:
        print("\n⚠️ MEDIUM CONFIDENCE - Needs manual review")
    else:
        print("\n❌ LOW CONFIDENCE - Needs manual review")
        
    print("\nLatest AI Notes:")
    if grade.ai_evaluation_notes:
        print(grade.ai_evaluation_notes[-500:])  # Last 500 chars
        
except GradeSubmission.DoesNotExist:
    print("❌ IT 102 grade not found!")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
