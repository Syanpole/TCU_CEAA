"""Test if name verification works on existing grade sheets"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from myapp.ai_service import grade_analyzer

print("\n" + "=" * 80)
print("TESTING NAME VERIFICATION ON EXISTING GRADES")
print("=" * 80)

grade = GradeSubmission.objects.filter(grade_sheet__isnull=False).first()

if grade:
    print(f"\nTesting Grade #{grade.id}")
    print(f"Student: {grade.student.username}")
    print(f"Name: {grade.student.first_name} {grade.student.last_name}")
    print(f"Grade Sheet: {grade.grade_sheet.name}")
    print(f"Full Path: {grade.grade_sheet.path}")
    print()
    
    # Test name verification
    print("Running name verification...")
    try:
        result = grade_analyzer._verify_grade_sheet_ownership(grade)
        print(f"\nVerification Result:")
        print(f"  Name Match: {result.get('name_match', False)}")
        print(f"  Confidence: {result.get('confidence', 0.0):.1%}")
        print(f"  Expected Name: {result.get('expected_name', 'N/A')}")
        print(f"  Matched Name: {result.get('matched_name', 'N/A')}")
        if result.get('found_names'):
            print(f"  Found Names: {', '.join(result['found_names'][:5])}")
        if result.get('mismatch_reason'):
            print(f"  Mismatch Reason: {result['mismatch_reason']}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("\nNo grade submissions with grade sheets found")

print("\n" + "=" * 80)
