"""Check grade submissions and their status"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

print("\n" + "=" * 80)
print("GRADE SUBMISSIONS CHECK")
print("=" * 80)

grades = GradeSubmission.objects.all()
print(f"\nTotal Grade Submissions: {grades.count()}\n")

for grade in grades:
    print(f"Grade #{grade.id}:")
    print(f"  Student: {grade.student.username}")
    print(f"  Name: {grade.student.first_name} {grade.student.last_name}")
    print(f"  Status: {grade.status}")
    print(f"  GWA: {grade.general_weighted_average}%")
    print(f"  Has Grade Sheet: {'Yes' if grade.grade_sheet else 'No'}")
    if grade.grade_sheet:
        print(f"  Grade Sheet: {grade.grade_sheet.name}")
    print(f"  AI Completed: {grade.ai_evaluation_completed}")
    print(f"  AI Confidence: {grade.ai_confidence_score}")
    if grade.admin_notes:
        print(f"  Admin Notes: {grade.admin_notes[:150]}...")
    print()

print("=" * 80)
