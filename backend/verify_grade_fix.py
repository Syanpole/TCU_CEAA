import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

grade = GradeSubmission.objects.filter(general_weighted_average='1.74').first()

if grade:
    print("=" * 60)
    print("GRADE ELIGIBILITY VERIFICATION")
    print("=" * 60)
    print(f"Student: {grade.student.username}")
    print(f"Semester: {grade.semester} {grade.academic_year}")
    print(f"GWA (Point Scale): {grade.general_weighted_average}")
    print(f"GWA (Percentage): {grade.get_gwa_percentage():.2f}%")
    print("-" * 60)
    print(f"Basic Allowance (>=80%): {'YES ✅' if grade.qualifies_for_basic_allowance else 'NO ❌'}")
    print(f"Merit Incentive (>=87%): {'YES ✅' if grade.qualifies_for_merit_incentive else 'NO ❌'}")
    print("-" * 60)
    
    total = 0
    if grade.qualifies_for_basic_allowance:
        total += 5000
    if grade.qualifies_for_merit_incentive:
        total += 5000
    
    print(f"Total Allowance Qualified: ₱{total:,}")
    print("=" * 60)
    
    if total == 10000:
        print("✅ SUCCESS! Grade is now correctly eligible for BOTH allowances!")
    else:
        print("⚠️ Warning: Eligibility may need review")
else:
    print("❌ No grade found with GWA 1.74")
