import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

print("=" * 80)
print("TESTING AUTOMATIC GWA CALCULATION")
print("=" * 80)

# Reset one grade to pending to simulate the flow
it102 = GradeSubmission.objects.get(
    student_id=25,
    subject_code='IT 102',
    academic_year='2025-2026',
    semester='1st'
)

print(f"\n1. Resetting IT 102 to pending...")
it102.status = 'pending'
it102.qualifies_for_basic_allowance = False
it102.qualifies_for_merit_incentive = False
it102.save()
print(f"   Status: {it102.status}")
print(f"   Basic Allowance: {it102.qualifies_for_basic_allowance}")
print(f"   Merit Incentive: {it102.qualifies_for_merit_incentive}")

# Check current eligibility for all grades
print(f"\n2. Current eligibility status:")
grades = GradeSubmission.objects.filter(
    student_id=25,
    academic_year='2025-2026',
    semester='1st'
)
for g in grades:
    print(f"   {g.subject_code}: Basic={g.qualifies_for_basic_allowance}, Merit={g.qualifies_for_merit_incentive}")

# Simulate approval (like the admin would do)
print(f"\n3. Approving IT 102...")
it102.status = 'approved'
it102.save()
print(f"   Status: {it102.status}")

# Trigger the auto-approval semester check (which should calculate GWA)
print(f"\n4. Triggering semester auto-approval check...")
from myapp.tasks import auto_approve_semester_if_ready
auto_approve_semester_if_ready(25, '2025-2026', '1st')

# Check if eligibility was set
print(f"\n5. After auto-approval check:")
it102.refresh_from_db()
print(f"   IT 102 Basic Allowance: {it102.qualifies_for_basic_allowance}")
print(f"   IT 102 Merit Incentive: {it102.qualifies_for_merit_incentive}")

# Check all grades
print(f"\n6. All grades eligibility:")
grades = GradeSubmission.objects.filter(
    student_id=25,
    academic_year='2025-2026',
    semester='1st'
)

all_eligible = True
for g in grades:
    if not g.qualifies_for_basic_allowance or not g.qualifies_for_merit_incentive:
        all_eligible = False
    status = '✅' if (g.qualifies_for_basic_allowance and g.qualifies_for_merit_incentive) else '❌'
    print(f"   {status} {g.subject_code}: Basic={g.qualifies_for_basic_allowance}, Merit={g.qualifies_for_merit_incentive}")

print("\n" + "=" * 80)
if all_eligible:
    print("✅ SUCCESS! All grades have eligibility flags set!")
    print("   Students can now apply for allowances without manual intervention.")
else:
    print("❌ ISSUE: Some grades missing eligibility flags")
    print("   Need to investigate why GWA calculation didn't run")
