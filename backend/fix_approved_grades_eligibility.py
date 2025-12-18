"""
Fix approved grades that don't have eligibility flags set.
This script updates all approved grades to calculate their allowance eligibility.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

def fix_approved_grades():
    """Update all approved grades to calculate their allowance eligibility"""
    
    # Get all approved grades
    approved_grades = GradeSubmission.objects.filter(status='approved')
    
    print(f"Found {approved_grades.count()} approved grade submissions")
    
    updated_count = 0
    needs_fix_count = 0
    
    for grade in approved_grades:
        # Check if eligibility flags need to be set
        if not grade.qualifies_for_basic_allowance and not grade.qualifies_for_merit_incentive:
            needs_fix_count += 1
            print(f"\nProcessing grade {grade.id} for {grade.student.get_full_name()}")
            print(f"  Academic Year: {grade.academic_year}, Semester: {grade.semester}")
            print(f"  GWA: {grade.general_weighted_average}")
            
            try:
                # Calculate eligibility
                grade.calculate_allowance_eligibility()
                grade.save()
                
                print(f"  ✅ Updated - Basic: {grade.qualifies_for_basic_allowance}, Merit: {grade.qualifies_for_merit_incentive}")
                updated_count += 1
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
        else:
            print(f"Grade {grade.id} already has eligibility set - skipping")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total approved grades: {approved_grades.count()}")
    print(f"  Needed fixing: {needs_fix_count}")
    print(f"  Successfully updated: {updated_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    fix_approved_grades()
