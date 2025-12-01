import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, DocumentSubmission, CustomUser, AllowanceApplication

student = CustomUser.objects.get(id=25)

print("=" * 80)
print("STUDENT APPLICATION ELIGIBILITY CHECK")
print("=" * 80)
print(f"\nStudent: {student.first_name} {student.last_name} ({student.student_id})")

# Check grades
print("\n--- GRADES STATUS ---")
grades = GradeSubmission.objects.filter(
    student=student,
    academic_year='2025-2026',
    semester='1st'
)
approved_grades = grades.filter(status='approved')
pending_grades = grades.filter(status='pending')

print(f"Total Grades: {grades.count()}")
print(f"✅ Approved: {approved_grades.count()}")
print(f"⏳ Pending: {pending_grades.count()}")

if approved_grades.exists():
    print("\nApproved Grades:")
    for g in approved_grades:
        print(f"  {g.subject_code}: Grade {g.grade_received} | Confidence: {g.ai_confidence_score:.0%}")
        print(f"    Basic Allowance: {'YES' if g.qualifies_for_basic_allowance else 'NO'}")
        print(f"    Merit Incentive: {'YES' if g.qualifies_for_merit_incentive else 'NO'}")

# Check documents
print("\n--- DOCUMENTS STATUS ---")
docs = DocumentSubmission.objects.filter(student=student)
approved_docs = docs.filter(status='approved')

print(f"Total Documents: {docs.count()}")
print(f"✅ Approved: {approved_docs.count()}")

for d in docs:
    status_emoji = '✅' if d.status == 'approved' else '⏳' if d.status == 'pending' else '❌'
    print(f"  {status_emoji} {d.get_document_type_display()}: {d.status}")

# Check applications
print("\n--- EXISTING APPLICATIONS ---")
apps = AllowanceApplication.objects.filter(student=student)
print(f"Total Applications: {apps.count()}")
for app in apps:
    print(f"  {app.get_application_type_display()}: {app.status} - ₱{app.amount}")

# Check eligibility
print("\n--- ELIGIBILITY CHECK ---")
print(f"Approved Documents: {approved_docs.count()} (Need at least 2)")
print(f"Approved Grades: {approved_grades.count()}")

# Check if any grade qualifies
qualifies_basic = approved_grades.filter(qualifies_for_basic_allowance=True).exists()
qualifies_merit = approved_grades.filter(qualifies_for_merit_incentive=True).exists()

print(f"Qualifies for Basic Allowance: {'YES ✅' if qualifies_basic else 'NO ❌'}")
print(f"Qualifies for Merit Incentive: {'YES ✅' if qualifies_merit else 'NO ❌'}")

# Final verdict
print("\n" + "=" * 80)
can_apply = approved_docs.count() >= 2 and approved_grades.count() > 0 and (qualifies_basic or qualifies_merit)

if can_apply:
    print("✅ ELIGIBLE TO APPLY!")
    print("   You can now submit an allowance application.")
else:
    print("❌ NOT ELIGIBLE YET")
    if approved_docs.count() < 2:
        print(f"   ⚠️  Need {2 - approved_docs.count()} more approved documents")
    if approved_grades.count() == 0:
        print("   ⚠️  Need approved grades")
    if not (qualifies_basic or qualifies_merit):
        print("   ⚠️  Grades don't qualify for allowances (GWA might be too low)")
