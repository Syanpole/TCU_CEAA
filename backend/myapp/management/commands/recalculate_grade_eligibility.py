from django.core.management.base import BaseCommand
from myapp.models import GradeSubmission

class Command(BaseCommand):
    help = 'Recalculate allowance eligibility for all grade submissions using the new conversion function'

    def handle(self, *args, **options):
        grades = GradeSubmission.objects.all()
        updated_count = 0
        
        self.stdout.write("Starting grade eligibility recalculation...")
        self.stdout.write("-" * 60)
        
        for grade in grades:
            # Get converted percentages
            gwa_percent = grade.get_gwa_percentage()
            swa_percent = grade.get_swa_percentage()
            
            # Recalculate eligibility
            old_basic = grade.qualifies_for_basic_allowance
            old_merit = grade.qualifies_for_merit_incentive
            
            # Basic: GWA >= 80%
            new_basic = gwa_percent >= 80.0
            
            # Merit: SWA >= 87% (GWA 1.75 or better)
            new_merit = swa_percent >= 87.0
            
            # Update if changed
            if old_basic != new_basic or old_merit != new_merit:
                grade.qualifies_for_basic_allowance = new_basic
                grade.qualifies_for_merit_incentive = new_merit
                grade.save()
                updated_count += 1
                
                self.stdout.write(
                    f"Updated Grade #{grade.id}: "
                    f"GWA {grade.general_weighted_average} ({gwa_percent:.2f}%) | "
                    f"Basic: {old_basic} -> {new_basic} | "
                    f"Merit: {old_merit} -> {new_merit}"
                )
        
        self.stdout.write("-" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {updated_count} grade submission(s)"
            )
        )
