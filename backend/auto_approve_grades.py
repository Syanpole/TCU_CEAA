import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.tasks import calculate_gpa_and_merit

# Get user
username = '4peytonly'
academic_year = '2025-2026'
semester = '1st'

user = CustomUser.objects.get(username=username)

print("=" * 80)
print(f"🔄 AUTO-APPROVING GRADES FOR {username}")
print("=" * 80)

# Get all pending grades
grades = GradeSubmission.objects.filter(
    student=user,
    academic_year=academic_year,
    semester=semester,
    status='pending'
)

print(f"\nFound {grades.count()} pending grade submissions")

# Check if all are authentic
all_authentic = True
for grade in grades:
    if grade.ai_extracted_grades:
        is_authentic = grade.ai_extracted_grades.get('is_authentic', False)
        if not is_authentic:
            all_authentic = False
            print(f"❌ {grade.subject_code} is NOT authentic")
        else:
            print(f"✅ {grade.subject_code} is authentic")

if all_authentic and grades.count() > 0:
    print("\n" + "=" * 80)
    print("✅ ALL DOCUMENTS AUTHENTIC - PROCEEDING WITH AUTO-APPROVAL")
    print("=" * 80)
    
    # Approve all grades
    count = grades.update(status='approved')
    print(f"\n✅ Approved {count} grade submissions")
    
    # Calculate GPA
    print("\n📊 Calculating GPA...")
    gpa_result = calculate_gpa_and_merit(user.id, academic_year, semester)
    
    if gpa_result:
        print("\n" + "=" * 80)
        print("📊 FINAL GWA CALCULATION")
        print("=" * 80)
        print(f"GPA: {gpa_result['gpa']:.2f}")
        print(f"Merit Level: {gpa_result['merit_level']}")
        print(f"Qualifies for Merit: {'YES ✅' if gpa_result['qualifies_for_merit'] else 'NO ❌'}")
        print(f"Total Units: {gpa_result['total_units']}")
        
        print("\n" + "=" * 80)
        print("🎯 NEXT STEP: LIVENESS DETECTION")
        print("=" * 80)
        print(f"✅ Student {username} can now proceed to liveness detection")
        print(f"   GWA: {gpa_result['gpa']:.2f} - {gpa_result['merit_level']}")
        
else:
    print("\n❌ Cannot auto-approve - not all documents are authentic")

print("\n" + "=" * 80)
