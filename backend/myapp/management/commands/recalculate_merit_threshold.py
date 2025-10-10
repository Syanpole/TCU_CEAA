"""
Django management command to recalculate merit eligibility with new threshold (GWA ≤1.75)
Run: python manage.py recalculate_merit_threshold
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import GradeSubmission


class Command(BaseCommand):
    help = 'Recalculate merit eligibility with updated threshold (GWA ≤1.75, 84.5%)'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("🔄 Recalculating Merit Eligibility with New Threshold")
        self.stdout.write("=" * 60)
        self.stdout.write("\n📋 Old Threshold: GWA ≤1.6 (≥87%)")
        self.stdout.write("📋 New Threshold: GWA ≤1.75 (≥84.5%)")
        self.stdout.write("\n")

        # Get all grade submissions
        all_grades = GradeSubmission.objects.all().order_by('student__username', 'academic_year', 'semester')
        
        if not all_grades.exists():
            self.stdout.write(self.style.WARNING("⚠️  No grade submissions found in database"))
            return

        self.stdout.write(f"📊 Found {all_grades.count()} grade submission(s)\n")
        
        updated_count = 0
        changes_log = []

        for grade in all_grades:
            old_merit = grade.qualifies_for_merit_incentive
            old_basic = grade.qualifies_for_basic_allowance
            
            # Recalculate eligibility
            grade.calculate_allowance_eligibility()
            
            new_merit = grade.qualifies_for_merit_incentive
            new_basic = grade.qualifies_for_basic_allowance
            
            # Check if merit eligibility changed
            if old_merit != new_merit or old_basic != new_basic:
                grade.save()
                updated_count += 1
                
                student_name = grade.student.username
                gwa = grade.general_weighted_average
                percentage = grade._convert_to_percentage(gwa)
                
                change_info = {
                    'student': student_name,
                    'id': grade.id,
                    'academic_year': grade.academic_year,
                    'semester': grade.semester,
                    'gwa': float(gwa),
                    'percentage': percentage,
                    'old_basic': old_basic,
                    'new_basic': new_basic,
                    'old_merit': old_merit,
                    'new_merit': new_merit
                }
                changes_log.append(change_info)
                
                self.stdout.write(f"\n📝 Grade #{grade.id} - {student_name}")
                self.stdout.write(f"   📅 {grade.academic_year} {grade.semester} semester")
                self.stdout.write(f"   📊 GWA: {gwa} ({percentage:.2f}%)")
                
                if old_basic != new_basic:
                    self.stdout.write(self.style.WARNING(
                        f"   ⚠️  Basic: {old_basic} → {new_basic}"
                    ))
                else:
                    self.stdout.write(f"   ✓ Basic: {new_basic} (unchanged)")
                
                if old_merit != new_merit:
                    if new_merit:
                        self.stdout.write(self.style.SUCCESS(
                            f"   ✅ Merit: {old_merit} → {new_merit} (NOW ELIGIBLE!)"
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"   ❌ Merit: {old_merit} → {new_merit} (No longer eligible)"
                        ))
                else:
                    self.stdout.write(f"   ✓ Merit: {new_merit} (unchanged)")

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"✅ Successfully updated {updated_count} grade submission(s)")
        self.stdout.write(f"📋 Total processed: {all_grades.count()}")
        self.stdout.write(f"🔄 Unchanged: {all_grades.count() - updated_count}")
        
        # Show new eligibility thresholds
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📋 Current Eligibility Thresholds")
        self.stdout.write("=" * 60)
        self.stdout.write("✅ Basic Allowance (₱5,000):")
        self.stdout.write("   • GWA ≤1.9 (≥80%)")
        self.stdout.write("   • ≥15 units")
        self.stdout.write("   • No failing/incomplete/dropped subjects")
        self.stdout.write("\n✅ Merit Incentive (₱5,000):")
        self.stdout.write("   • GWA ≤1.75 (≥84.5%)")
        self.stdout.write("   • ≥15 units")
        self.stdout.write("   • No failing/incomplete/dropped subjects")
        
        # Detailed changes
        if changes_log:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("📋 Detailed Changes")
            self.stdout.write("=" * 60)
            
            newly_eligible = [c for c in changes_log if not c['old_merit'] and c['new_merit']]
            no_longer_eligible = [c for c in changes_log if c['old_merit'] and not c['new_merit']]
            
            if newly_eligible:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ {len(newly_eligible)} student(s) NOW ELIGIBLE for merit:"
                ))
                for change in newly_eligible:
                    self.stdout.write(
                        f"   • {change['student']} - GWA {change['gwa']} ({change['percentage']:.2f}%) "
                        f"- {change['academic_year']} {change['semester']}"
                    )
            
            if no_longer_eligible:
                self.stdout.write(self.style.ERROR(
                    f"\n❌ {len(no_longer_eligible)} student(s) no longer eligible for merit:"
                ))
                for change in no_longer_eligible:
                    self.stdout.write(
                        f"   • {change['student']} - GWA {change['gwa']} ({change['percentage']:.2f}%) "
                        f"- {change['academic_year']} {change['semester']}"
                    )
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ Recalculation complete!"))
        self.stdout.write("=" * 60 + "\n")
