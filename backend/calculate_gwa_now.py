import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.services import gwa_calculation_service

print("=" * 80)
print("CALCULATING GWA AND ALLOWANCE ELIGIBILITY")
print("=" * 80)

student = CustomUser.objects.get(id=25)
academic_year = '2025-2026'
semester = '1st'

print(f"\nStudent: {student.first_name} {student.last_name} ({student.student_id})")
print(f"Semester: {semester} {academic_year}")

# Get grades before
grades = GradeSubmission.objects.filter(
    student=student,
    academic_year=academic_year,
    semester=semester
)

print(f"\nGrades: {grades.count()} subjects")
for g in grades:
    print(f"  {g.subject_code}: {g.grade_received} ({g.units} units)")

# Calculate GWA
print("\n🔄 Calculating GWA and merit level...")
result = gwa_calculation_service.trigger_automated_gwa_calculation(
    student, academic_year, semester
)

if result:
    print("\n✅ GWA CALCULATED!")
    print(f"   GWA: {result['gwa']:.2f}")
    print(f"   Merit Level: {result['merit_level']}")
    print(f"   Total Units: {result['total_units']}")
    print(f"   Qualifies for Merit: {'YES ✅' if result['qualifies_for_merit'] else 'NO'}")
    print(f"   Basic Allowance: {result['basic_allowance_amount']}")
    print(f"   Merit Incentive: {result['merit_incentive_amount']}")
    
    # Check updated grades
    print("\n📊 Updated Grade Eligibility:")
    grades = GradeSubmission.objects.filter(
        student=student,
        academic_year=academic_year,
        semester=semester
    )
    
    for g in grades:
        basic = '✅' if g.qualifies_for_basic_allowance else '❌'
        merit = '✅' if g.qualifies_for_merit_incentive else '❌'
        print(f"  {g.subject_code}: Basic {basic} | Merit {merit}")
    
    print("\n" + "=" * 80)
    print("🎉 STUDENT CAN NOW APPLY FOR ALLOWANCES!")
else:
    print("\n❌ GWA calculation failed!")
