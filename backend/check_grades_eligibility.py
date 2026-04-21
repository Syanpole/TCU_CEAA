"""
Check approved grades eligibility status
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

def check_grades_status():
    """Check all approved grades and their eligibility status"""
    
    approved_grades = GradeSubmission.objects.filter(status='approved').select_related('student')
    
    print(f"\n{'='*80}")
    print(f"APPROVED GRADES ELIGIBILITY STATUS")
    print(f"{'='*80}\n")
    
    for grade in approved_grades:
        print(f"Grade ID: {grade.id}")
        print(f"  Student: {grade.student.get_full_name()} ({grade.student.student_id})")
        print(f"  Academic Year: {grade.academic_year}, Semester: {grade.semester}")
        print(f"  GWA: {grade.general_weighted_average}")
        print(f"  Units: {grade.total_units}")
        print(f"  Failing: {grade.has_failing_grades}, Incomplete: {grade.has_incomplete_grades}, Dropped: {grade.has_dropped_subjects}")
        print(f"  ✅ Qualifies for Basic Allowance: {grade.qualifies_for_basic_allowance}")
        print(f"  🏆 Qualifies for Merit Incentive: {grade.qualifies_for_merit_incentive}")
        print(f"  Status: {grade.status}")
        print(f"  Reviewed by: {grade.reviewed_by.get_full_name() if grade.reviewed_by else 'Auto-approved'}")
        print(f"  Reviewed at: {grade.reviewed_at}")
        print()
    
    # Summary
    basic_count = approved_grades.filter(qualifies_for_basic_allowance=True).count()
    merit_count = approved_grades.filter(qualifies_for_merit_incentive=True).count()
    neither_count = approved_grades.filter(
        qualifies_for_basic_allowance=False,
        qualifies_for_merit_incentive=False
    ).count()
    
    print(f"{'='*80}")
    print(f"SUMMARY:")
    print(f"  Total approved grades: {approved_grades.count()}")
    print(f"  Qualifies for Basic Allowance: {basic_count}")
    print(f"  Qualifies for Merit Incentive: {merit_count}")
    print(f"  Does not qualify for either: {neither_count}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    check_grades_status()
