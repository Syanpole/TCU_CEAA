"""
Management command to recalculate grade eligibility with new 10-point scale

This command:
1. Updates all existing grade submissions
2. Recalculates eligibility using new thresholds (Merit: 1.75/87%, Basic: 2.25/80%)
3. Logs all changes
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import GradeSubmission
from decimal import Decimal

class Command(BaseCommand):
    help = 'Recalculate grade eligibility using new 10-point official scale (Merit: GWA ≤1.75, Basic: GWA ≤2.25)'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS('RECALCULATING GRADES WITH NEW 10-POINT SCALE'))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # Get all grade submissions
        all_grades = GradeSubmission.objects.all()
        total_count = all_grades.count()
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING("No grade submissions found."))
            return
        
        self.stdout.write(f"📊 Found {total_count} grade submission(s)")
        self.stdout.write("")
        self.stdout.write("New Thresholds:")
        self.stdout.write("  • Merit Incentive: GWA ≤ 1.75 (≥87%)")
        self.stdout.write("  • Basic Allowance: GWA ≤ 2.25 (≥80%)")
        self.stdout.write("")
        self.stdout.write("-" * 80)
        
        updated_count = 0
        changes = []
        
        for grade in all_grades:
            # Store old values
            old_basic = grade.qualifies_for_basic_allowance
            old_merit = grade.qualifies_for_merit_incentive
            
            # Get percentage using new conversion
            gwa_percent = grade.get_gwa_percentage()
            swa_percent = grade.get_swa_percentage()
            
            # Calculate new eligibility (must meet ALL criteria)
            new_basic = (
                gwa_percent >= 80.0 and  # GWA 2.25 or better
                grade.total_units >= 15 and
                not grade.has_failing_grades and
                not grade.has_incomplete_grades and
                not grade.has_dropped_subjects
            )
            
            new_merit = (
                swa_percent >= 87.0 and  # GWA 1.75 or better
                grade.total_units >= 15 and
                not grade.has_failing_grades and
                not grade.has_incomplete_grades and
                not grade.has_dropped_subjects
            )
            
            # Check if changed
            basic_changed = old_basic != new_basic
            merit_changed = old_merit != new_merit
            
            if basic_changed or merit_changed:
                # Update the grade submission
                grade.qualifies_for_basic_allowance = new_basic
                grade.qualifies_for_merit_incentive = new_merit
                grade.save(update_fields=[
                    'qualifies_for_basic_allowance',
                    'qualifies_for_merit_incentive'
                ])
                
                updated_count += 1
                
                # Record change
                change_detail = {
                    'id': grade.id,
                    'student': grade.student.username,
                    'gwa': float(grade.general_weighted_average),
                    'percent': gwa_percent,
                    'semester': f"{grade.academic_year} {grade.semester}",
                    'basic_old': old_basic,
                    'basic_new': new_basic,
                    'merit_old': old_merit,
                    'merit_new': new_merit,
                }
                changes.append(change_detail)
                
                # Display change
                self.stdout.write("")
                self.stdout.write(f"Grade #{grade.id} - {grade.student.username}")
                self.stdout.write(f"  GWA: {grade.general_weighted_average} ({gwa_percent:.2f}%)")
                self.stdout.write(f"  Semester: {grade.academic_year} {grade.semester}")
                self.stdout.write(f"  Units: {grade.total_units}, Fails: {grade.has_failing_grades}, Inc: {grade.has_incomplete_grades}, Drops: {grade.has_dropped_subjects}")
                
                if basic_changed:
                    old_str = "✅" if old_basic else "❌"
                    new_str = "✅" if new_basic else "❌"
                    self.stdout.write(self.style.WARNING(
                        f"  Basic: {old_str} → {new_str}"
                    ))
                
                if merit_changed:
                    old_str = "✅" if old_merit else "❌"
                    new_str = "✅" if new_merit else "❌"
                    self.stdout.write(self.style.WARNING(
                        f"  Merit: {old_str} → {new_str}"
                    ))
        
        # Summary
        self.stdout.write("")
        self.stdout.write("-" * 80)
        self.stdout.write("")
        
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(
                f"✅ Successfully updated {updated_count} grade submission(s)"
            ))
            
            # Show summary of changes
            self.stdout.write("")
            self.stdout.write("📋 Summary of Changes:")
            for change in changes:
                basic_change = ""
                merit_change = ""
                
                if change['basic_old'] != change['basic_new']:
                    basic_change = f"Basic: {'✅' if change['basic_new'] else '❌'}"
                
                if change['merit_old'] != change['merit_new']:
                    merit_change = f"Merit: {'✅' if change['merit_new'] else '❌'}"
                
                changes_str = ", ".join([c for c in [basic_change, merit_change] if c])
                self.stdout.write(
                    f"  • Grade #{change['id']}: {change['student']} (GWA {change['gwa']}, {change['percent']:.2f}%) - {changes_str}"
                )
        else:
            self.stdout.write(self.style.SUCCESS(
                "✅ All grades are already up to date with the new scale!"
            ))
        
        self.stdout.write("")
        self.stdout.write("=" * 80)
