import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

print("=" * 80)
print("CHECKING ALL GRADES STATUS")
print("=" * 80)

grades = GradeSubmission.objects.filter(
    student_id=25,
    academic_year='2025-2026',
    semester='1st'
).order_by('subject_code')

print(f"\nFound {grades.count()} grades for 1st Semester 2025-2026\n")

for grade in grades:
    status_emoji = {
        'approved': '✅',
        'pending': '⏳',
        'rejected': '❌',
        'draft': '📝'
    }.get(grade.status, '❓')
    
    print(f"{status_emoji} {grade.subject_code:10} | {grade.subject_name:40} | Grade: {grade.grade_received} | Status: {grade.status:8} | Confidence: {grade.ai_confidence_score:.0%}")

print("\n" + "=" * 80)

# Summary
approved = grades.filter(status='approved').count()
pending = grades.filter(status='pending').count()
total = grades.count()

print(f"\n📊 SUMMARY:")
print(f"   Total: {total}")
print(f"   ✅ Approved: {approved}")
print(f"   ⏳ Pending: {pending}")

if approved == total:
    print("\n🎉 ALL GRADES APPROVED! Student can proceed to liveness detection.")
elif pending > 0:
    print(f"\n⚠️  {pending} grades still pending review")
