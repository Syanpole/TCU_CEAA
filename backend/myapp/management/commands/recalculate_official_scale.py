from django.core.management.base import BaseCommand
from myapp.models import GradeSubmission

class Command(BaseCommand):
    help = 'Recalculate allowance eligibility for all grades using the new official university grading scale'

    def handle(self, *args, **options):
        grades = GradeSubmission.objects.all()
        updated_count = 0
        
        self.stdout.write("=" * 80)
        self.stdout.write("RECALCULATING ELIGIBILITY - OFFICIAL UNIVERSITY GRADING SCALE")
        self.stdout.write("=" * 80)
        self.stdout.write("")
        self.stdout.write("New Eligibility Thresholds:")
        self.stdout.write("  Basic Allowance: >= 80% (GWA <= 1.9)")
        self.stdout.write("  Merit Incentive: >= 87% (GWA <= 1.6)")
        self.stdout.write("")
        self.stdout.write("-" * 80)
        
        for grade in grades:
            # Get converted percentages using new scale
            gwa_percent = grade.get_gwa_percentage()
            swa_percent = grade.get_swa_percentage()
            
            # Store old values
            old_basic = grade.qualifies_for_basic_allowance
            old_merit = grade.qualifies_for_merit_incentive
            
            # New eligibility based on official scale
            # Basic: GWA >= 80% (GWA <= 1.9 = 81.5%)
            new_basic = gwa_percent >= 80.0
            
            # Merit: GWA >= 87% (GWA <= 1.6 = 87.5%)
            new_merit = swa_percent >= 87.0
            
            # Update if changed
            if old_basic != new_basic or old_merit != new_merit:
                grade.qualifies_for_basic_allowance = new_basic
                grade.qualifies_for_merit_incentive = new_merit
                grade.save()
                updated_count += 1
                
                # Show what changed
                basic_change = f"{old_basic} -> {new_basic}" if old_basic != new_basic else str(new_basic)
                merit_change = f"{old_merit} -> {new_merit}" if old_merit != new_merit else str(new_merit)
                
                self.stdout.write(
                    f"Grade #{grade.id}: "
                    f"GWA {grade.general_weighted_average} ({gwa_percent:.2f}%) | "
                    f"Basic: {basic_change} | "
                    f"Merit: {merit_change}"
                )
        
        self.stdout.write("-" * 80)
        self.stdout.write("")
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Successfully updated {updated_count} grade submission(s)"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ All grades already up-to-date with new scale"
                )
            )
        
        self.stdout.write("")
        self.stdout.write("=" * 80)
