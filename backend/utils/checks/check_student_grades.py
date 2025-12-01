import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser, DocumentSubmission
from decimal import Decimal

# Get user
user = CustomUser.objects.get(username='4peytonly')
print("=" * 80)
print(f"📊 Grade Submissions for {user.username} ({user.student_id})")
print("=" * 80)

# Get all grade submissions
grades = GradeSubmission.objects.filter(
    student=user,
    academic_year='2025-2026',
    semester='1st Semester'
).order_by('subject_code')

print(f"\nTotal Submissions: {grades.count()}")
print("\n" + "=" * 80)

total_grade_points = Decimal('0')
total_units = Decimal('0')

for grade in grades:
    print(f"\n📝 Grade ID: {grade.id}")
    print(f"   Subject: {grade.subject_code} - {grade.subject_name}")
    print(f"   Units: {grade.units}")
    print(f"   Grade: {grade.grade_received}")
    print(f"   Status: {grade.status}")
    print(f"   AI Verified: {grade.is_ai_verified}")
    print(f"   AI Confidence: {grade.ai_confidence_score}%")
    print(f"   Grade Sheet: {'✓' if grade.grade_sheet else '✗'}")
    
    if grade.ai_extracted_grades:
        data = grade.ai_extracted_grades
        print(f"   Document Type: {data.get('document_type', 'N/A')}")
        print(f"   Authentic: {data.get('is_authentic', False)}")
        print(f"   Subject in COE: {data.get('subject_in_coe', False)}")
        print(f"   Extracted Grade: {data.get('extracted_grade', 'None')}")
        print(f"   Validation Note: {data.get('grade_validation_note', 'N/A')}")
    
    # Calculate grade points
    if grade.grade_received and grade.units:
        grade_points = Decimal(str(grade.grade_received)) * Decimal(str(grade.units))
        total_grade_points += grade_points
        total_units += Decimal(str(grade.units))
        print(f"   Grade Points: {grade_points} ({grade.grade_received} × {grade.units})")

print("\n" + "=" * 80)
print("📊 GWA CALCULATION")
print("=" * 80)

if total_units > 0:
    gwa = total_grade_points / total_units
    print(f"Total Grade Points: {total_grade_points}")
    print(f"Total Units: {total_units}")
    print(f"GWA: {gwa:.2f}")
    print()
    
    # Determine merit level
    if gwa <= 1.50:
        merit = "HIGH HONORS"
        eligible = True
    elif gwa <= 2.00:
        merit = "HONORS"
        eligible = True
    elif gwa <= 2.50:
        merit = "MERIT"
        eligible = True
    elif gwa <= 3.00:
        merit = "REGULAR"
        eligible = False
    else:
        merit = "BELOW REGULAR"
        eligible = False
    
    print(f"Merit Level: {merit}")
    print(f"Eligible for Merit: {'YES ✓' if eligible else 'NO ✗'}")
else:
    print("No valid grades to calculate GWA")

print("\n" + "=" * 80)
print("🔍 VERIFICATION STATUS")
print("=" * 80)

# Check COE
coe_docs = DocumentSubmission.objects.filter(
    student=user,
    document_type='certificate_of_enrollment',
    status='approved'
)

if coe_docs.exists():
    coe = coe_docs.first()
    print(f"✓ COE Approved: {coe.extracted_subjects.get('subjects', []) if coe.extracted_subjects else []}")
    subjects_in_coe = len(coe.extracted_subjects.get('subjects', [])) if coe.extracted_subjects else 0
    print(f"  Subjects in COE: {subjects_in_coe}")
else:
    print("✗ No approved COE")

# Check IDs
id_docs = DocumentSubmission.objects.filter(
    student=user,
    document_type='valid_id',
    status='approved'
).count()

print(f"✓ Approved IDs: {id_docs}")

print("\n" + "=" * 80)
