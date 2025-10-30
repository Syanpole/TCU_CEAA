"""
Management command to recalculate grade eligibility for all students
This will update all grade submissions to use the corrected eligibility criteria:
- Basic Allowance: GWA >= 80% (2.25 or better on 10-point scale)
- Merit Incentive: GWA >= 84.5% (2.0 or better on 10-point scale)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import GradeSubmission


class Command(BaseCommand):
    help = 'Recalculate grade eligibility for all grade submissions with corrected criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('RECALCULATING GRADE ELIGIBILITY WITH CORRECTED CRITERIA'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
        
        self.stdout.write('Corrected Eligibility Criteria:')
        self.stdout.write('  • Basic Allowance: GWA >= 80% (2.25 or better)')
        self.stdout.write('  • Merit Incentive: GWA >= 84.5% (2.0 or better)')
        self.stdout.write('')
        
        # Get all grade submissions
        all_grades = GradeSubmission.objects.all().select_related('student')
        total_count = all_grades.count()
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING('No grade submissions found.'))
            return
        
        self.stdout.write(f'Found {total_count} grade submission(s) to process\n')
        
        changes_made = 0
        basic_count = 0
        merit_count = 0
        both_count = 0
        neither_count = 0
        
        for grade in all_grades:
            self.stdout.write('-' * 80)
            self.stdout.write(f'\nStudent: {grade.student.get_full_name()} ({grade.student.student_id})')
            self.stdout.write(f'Academic Year: {grade.academic_year}')
            self.stdout.write(f'Semester: {grade.get_semester_display()}')
            self.stdout.write(f'GWA (10-point): {grade.general_weighted_average}')
            
            # Store old values
            old_basic = grade.qualifies_for_basic_allowance
            old_merit = grade.qualifies_for_merit_incentive
            
            # Get percentages
            gwa_percent = grade.get_gwa_percentage()
            self.stdout.write(f'GWA (percentage): {gwa_percent:.2f}%')
            self.stdout.write(f'Total Units: {grade.total_units}')
            self.stdout.write(f'Failing Grades: {grade.has_failing_grades}')
            self.stdout.write(f'Incomplete Grades: {grade.has_incomplete_grades}')
            self.stdout.write(f'Dropped Subjects: {grade.has_dropped_subjects}')
            
            # Calculate new eligibility
            basic_eligible = (
                gwa_percent >= 80.0 and
                grade.total_units >= 15 and
                not grade.has_failing_grades and
                not grade.has_incomplete_grades and
                not grade.has_dropped_subjects
            )
            
            merit_eligible = (
                gwa_percent >= 84.5 and
                grade.total_units >= 15 and
                not grade.has_failing_grades and
                not grade.has_incomplete_grades and
                not grade.has_dropped_subjects
            )
            
            self.stdout.write('\nOLD Eligibility:')
            self.stdout.write(f'  Basic Allowance: {"YES ✅" if old_basic else "NO ❌"}')
            self.stdout.write(f'  Merit Incentive: {"YES ✅" if old_merit else "NO ❌"}')
            
            self.stdout.write('\nNEW Eligibility:')
            self.stdout.write(f'  Basic Allowance: {"YES ✅" if basic_eligible else "NO ❌"}')
            self.stdout.write(f'  Merit Incentive: {"YES ✅" if merit_eligible else "NO ❌"}')
            
            # Check if changes needed
            if old_basic != basic_eligible or old_merit != merit_eligible:
                changes_made += 1
                self.stdout.write(self.style.WARNING('\n⚠️  CHANGES DETECTED!'))
                
                if not dry_run:
                    grade.qualifies_for_basic_allowance = basic_eligible
                    grade.qualifies_for_merit_incentive = merit_eligible
                    grade.save(update_fields=[
                        'qualifies_for_basic_allowance',
                        'qualifies_for_merit_incentive'
                    ])
                    self.stdout.write(self.style.SUCCESS('✅ Updated successfully'))
                else:
                    self.stdout.write(self.style.WARNING('🔄 Would be updated (dry run)'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✓ No changes needed'))
            
            # Count totals
            if basic_eligible and merit_eligible:
                both_count += 1
            elif basic_eligible:
                basic_count += 1
            elif merit_eligible:
                merit_count += 1
            else:
                neither_count += 1
            
            self.stdout.write('')
        
        # Summary
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*80)
        self.stdout.write(f'Total grade submissions processed: {total_count}')
        self.stdout.write(f'Changes detected: {changes_made}')
        self.stdout.write('')
        self.stdout.write('Final Eligibility Distribution:')
        self.stdout.write(f'  • Both allowances: {both_count} students')
        self.stdout.write(f'  • Basic only: {basic_count} students')
        self.stdout.write(f'  • Merit only: {merit_count} students')
        self.stdout.write(f'  • Neither: {neither_count} students')
        self.stdout.write('')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes were saved'))
            self.stdout.write(self.style.WARNING('Run without --dry-run to apply changes'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ ALL CHANGES SAVED SUCCESSFULLY!'))
        
        self.stdout.write('')
