import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from django.utils import timezone
from datetime import timedelta

# Get grades from last 3 hours
recent_time = timezone.now() - timedelta(hours=3)
grades = GradeSubmission.objects.filter(submitted_at__gte=recent_time).order_by('-submitted_at')

print(f'\n{"="*80}')
print(f'📊 LATEST GRADE SUBMISSIONS (Last 3 hours)')
print(f'{"="*80}\n')

if not grades.exists():
    print('❌ No recent grade submissions found in the last 3 hours.\n')
    print('Showing ALL grade submissions instead:\n')
    grades = GradeSubmission.objects.all().order_by('-submitted_at')[:10]

for grade in grades[:10]:
    print(f'{"─"*80}')
    print(f'📝 GRADE SUBMISSION #{grade.id}')
    print(f'{"─"*80}')
    print(f'👤 Student: {grade.student.username} (ID: {grade.student.student_id})')
    print(f'📚 Subject: {grade.subject_code} - {grade.subject_name}')
    print(f'📊 User Input Grade: {grade.grade_received}')
    print(f'🔢 Units: {grade.units}')
    print(f'📅 Academic Year: {grade.academic_year}')
    print(f'📆 Semester: {grade.semester}')
    print(f'⏰ Submitted: {grade.submitted_at.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'✅ Status: {grade.status.upper()}')
    
    print(f'\n🤖 AI VERIFICATION RESULTS:')
    print(f'   • Evaluation Completed: {"✓ YES" if grade.ai_evaluation_completed else "✗ NO"}')
    print(f'   • Confidence Score: {grade.ai_confidence_score * 100 if grade.ai_confidence_score else 0:.1f}%')
    print(f'   • GPA Calculated: {grade.ai_gwa_calculated if grade.ai_gwa_calculated else "Not yet"}')
    print(f'   • Merit Level: {grade.ai_merit_level or "N/A"}')
    print(f'   • Qualifies for Merit: {"✓ YES" if grade.qualifies_for_merit_incentive else "✗ NO"}')
    
    if grade.ai_extracted_grades:
        print(f'\n📊 AI EXTRACTED DATA:')
        data = grade.ai_extracted_grades
        print(f'   • Is Authentic: {"✓ YES" if data.get("is_authentic") else "✗ NO"}')
        print(f'   • Subject in COE: {"✓ YES" if data.get("subject_in_coe") else "✗ NO"}')
        print(f'   • Grade Matches: {"✓ YES" if data.get("grade_matches") else "✗ NO"}')
        print(f'   • Extracted Grade: {data.get("extracted_grade", "N/A")}')
        print(f'   • User Input Grade: {data.get("user_input_grade", "N/A")}')
        if data.get('coe_subject'):
            print(f'   • COE Subject Data: {data.get("coe_subject")}')
    else:
        print(f'\n📊 AI EXTRACTED DATA: None (AI verification not run or failed)')
    
    if grade.ai_evaluation_notes:
        print(f'\n📝 AI EVALUATION NOTES:')
        for line in grade.ai_evaluation_notes.split('\n'):
            if line.strip():
                print(f'   {line}')
    
    print(f'\n')

print(f'{"="*80}\n')
