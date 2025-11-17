import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from myapp.tasks import verify_grade_sheet_task

# Get the latest grade submission
latest_grade = GradeSubmission.objects.latest('submitted_at')

print(f"\n{'='*80}")
print(f"🔄 Re-running AI Verification on Grade #{latest_grade.id}")
print(f"{'='*80}\n")
print(f"Student: {latest_grade.student.username}")
print(f"Subject: {latest_grade.subject_code} - {latest_grade.subject_name}")
print(f"Grade: {latest_grade.grade_received}")
print(f"Status Before: {latest_grade.status}")
print(f"\nRunning verification...\n")

# Run verification
verify_grade_sheet_task(latest_grade.id)

# Reload from database
latest_grade.refresh_from_db()

print(f"\n{'='*80}")
print(f"✅ Verification Complete")
print(f"{'='*80}\n")
print(f"Status After: {latest_grade.status}")
print(f"AI Confidence: {latest_grade.ai_confidence_score * 100 if latest_grade.ai_confidence_score else 0:.1f}%")
print(f"\n📝 AI Evaluation Notes:")
print(latest_grade.ai_evaluation_notes)
print(f"\n📊 AI Extracted Data:")
import json
print(json.dumps(latest_grade.ai_extracted_grades, indent=2))
