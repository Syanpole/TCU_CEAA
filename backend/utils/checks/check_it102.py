import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

try:
    grade = GradeSubmission.objects.get(
        student_id=25, 
        subject_code='IT 102', 
        academic_year='2025-2026', 
        semester='1st'
    )
    
    print("=" * 80)
    print("IT 102 GRADE DETAILS")
    print("=" * 80)
    print(f"Subject: {grade.subject_code} - {grade.subject_name}")
    print(f"Student ID: {grade.student.student_id}")
    print(f"Status: {grade.status}")
    print(f"Grade: {grade.grade_received}")
    print(f"\nAI ANALYSIS:")
    print(f"  AI Confidence Score: {grade.ai_confidence_score}")
    print(f"  AI Evaluation Completed: {grade.ai_evaluation_completed}")
    print(f"  Grade Sheet: {grade.grade_sheet.name if grade.grade_sheet else 'None'}")
    print(f"\nAI Evaluation Notes:")
    if grade.ai_evaluation_notes:
        print(grade.ai_evaluation_notes)
    else:
        print("  (No notes)")
    
    print(f"\nAI Extracted Grades:")
    if grade.ai_extracted_grades:
        import json
        print(json.dumps(grade.ai_extracted_grades, indent=2))
    else:
        print("  (No extracted data)")
        
except GradeSubmission.DoesNotExist:
    print("IT 102 grade not found!")
