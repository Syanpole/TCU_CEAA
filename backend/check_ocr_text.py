import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from myapp.grades_detection_service import GradesDetectionService

# Get latest grade submission
grade = GradeSubmission.objects.latest('submitted_at')

print("=" * 80)
print(f"📄 Checking OCR Text for Grade #{grade.id}")
print("=" * 80)
print(f"Student: {grade.student.username}")
print(f"Subject: {grade.subject_code} - {grade.subject_name}")
print(f"Grade Sheet Path: {grade.grade_sheet.path if grade.grade_sheet else 'None'}")
print()

if grade.grade_sheet:
    service = GradesDetectionService()
    result = service.analyze_grade_sheet(grade.grade_sheet.path)
    
    print("=" * 80)
    print("📝 RAW OCR TEXT:")
    print("=" * 80)
    print(result.get('raw_text', 'No text extracted'))
    print()
    print("=" * 80)
    print("🔍 Looking for key terms:")
    print("=" * 80)
    raw_text = result.get('raw_text', '').upper()
    keywords = ['CLASS CARD', 'CLASSCARD', 'GRADE', 'FINAL', 'ENROLLMENT', 'TCU', 'TAGUIG']
    for keyword in keywords:
        found = keyword in raw_text
        print(f"  {'✓' if found else '✗'} {keyword}: {'FOUND' if found else 'NOT FOUND'}")
else:
    print("❌ No grade sheet file attached")
