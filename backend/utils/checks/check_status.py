import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

grades = GradeSubmission.objects.filter(
    student__username='4peytonly',
    academic_year='2025-2026',
    semester='1st'
)

print(f"Total: {grades.count()}")
print(f"Approved: {grades.filter(status='approved').count()}")
print(f"Pending: {grades.filter(status='pending').count()}")

for g in grades:
    print(f"{g.subject_code}: {g.status}")
