"""
Django Management Command: Fix Grade Eligibility (FINAL CORRECT VERSION)

This command recalculates allowance eligibility for ALL grade submissions
using the OFFICIAL TCU-CEAA criteria:

ELIGIBILITY RULES:
==================
- GWA 1.0 to 1.75  → Basic (₱5,000) + Merit (₱5,000) = ₱10,000
- GWA 1.76 to 2.5  → Basic (₱5,000) ONLY
- GWA 2.51 and above → NOT ELIGIBLE

USAGE:
======
python manage.py fix_grade_eligibility_final [--dry-run]

--dry-run: Preview changes without saving to database
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import GradeSubmission


class Command(BaseCommand):
    help = 'Recalculate grade eligibility for all submissions using OFFICIAL TCU-CEAA criteria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving to database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("🔧 GRADE ELIGIBILITY FIX - OFFICIAL TCU-CEAA CRITERIA"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No changes will be saved"))
            self.stdout.write("")
        
        # Display official criteria
        self.stdout.write(self.style.HTTP_INFO("📋 OFFICIAL ELIGIBILITY CRITERIA:"))
        self.stdout.write("=" * 80)
        self.stdout.write("GWA 1.0 to 1.75  → Basic (₱5,000) + Merit (₱5,000) = ₱10,000")
        self.stdout.write("GWA 1.76 to 2.5  → Basic (₱5,000) ONLY")
        self.stdout.write("GWA 2.51 and above → NOT ELIGIBLE")
        self.stdout.write("")
        self.stdout.write("Additional Requirements (all allowances):")
        self.stdout.write("  • Total Units ≥ 15")
        self.stdout.write("  • No Failing Grades")
        self.stdout.write("  • No Incomplete Grades")
        self.stdout.write("  • No Dropped Subjects")
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # Get all grade submissions
        all_submissions = GradeSubmission.objects.all().select_related('student')
        total_count = all_submissions.count()
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING("⚠️  No grade submissions found in database."))
            return
        
        self.stdout.write(f"📊 Found {total_count} grade submission(s) to analyze...")
        self.stdout.write("")
        
        # Tracking statistics
        stats = {
            'total': total_count,
            'changed': 0,
            'unchanged': 0,
            'basic_added': 0,
            'basic_removed': 0,
            'merit_added': 0,
            'merit_removed': 0,
        }
        
        changes = []
        
        # Process each submission
        for submission in all_submissions:
            gwa_value = float(submission.general_weighted_average)
            gwa_percent = submission.get_gwa_percentage()
            
            # Calculate NEW eligibility using OFFICIAL criteria
            new_basic = (
                gwa_value <= 2.5 and
                submission.total_units >= 15 and
                not submission.has_failing_grades and
                not submission.has_incomplete_grades and
                not submission.has_dropped_subjects
            )
            
            new_merit = (
                gwa_value <= 1.75 and
                submission.total_units >= 15 and
                not submission.has_failing_grades and
                not submission.has_incomplete_grades and
                not submission.has_dropped_subjects
            )
            
            # Get OLD eligibility
            old_basic = submission.qualifies_for_basic_allowance
            old_merit = submission.qualifies_for_merit_incentive
            
            # Check if anything changed
            basic_changed = old_basic != new_basic
            merit_changed = old_merit != new_merit
            
            if basic_changed or merit_changed:
                stats['changed'] += 1
                
                if basic_changed:
                    if new_basic:
                        stats['basic_added'] += 1
                    else:
                        stats['basic_removed'] += 1
                
                if merit_changed:
                    if new_merit:
                        stats['merit_added'] += 1
                    else:
                        stats['merit_removed'] += 1
                
                changes.append({
                    'submission': submission,
                    'gwa_value': gwa_value,
                    'gwa_percent': gwa_percent,
                    'old_basic': old_basic,
                    'new_basic': new_basic,
                    'old_merit': old_merit,
                    'new_merit': new_merit,
                    'basic_changed': basic_changed,
                    'merit_changed': merit_changed,
                })
            else:
                stats['unchanged'] += 1
        
        # Display detailed changes
        if changes:
            self.stdout.write(self.style.WARNING(f"⚠️  {len(changes)} submission(s) will be updated:"))
            self.stdout.write("")
            
            for i, change in enumerate(changes, 1):
                sub = change['submission']
                student = sub.student
                
                self.stdout.write("-" * 80)
                self.stdout.write(f"Student #{i}: {student.first_name} {student.last_name} ({student.username})")
                self.stdout.write(f"  GWA: {change['gwa_value']} ({change['gwa_percent']:.2f}%)")
                self.stdout.write(f"  Semester: {sub.academic_year} - {sub.semester}")
                self.stdout.write(f"  Units: {sub.total_units}")
                self.stdout.write("")
                
                # Show Basic Allowance changes
                if change['basic_changed']:
                    old_status = "✅" if change['old_basic'] else "❌"
                    new_status = "✅" if change['new_basic'] else "❌"
                    self.stdout.write(f"  Basic Allowance: {old_status} → {new_status}")
                else:
                    status = "✅" if change['old_basic'] else "❌"
                    self.stdout.write(f"  Basic Allowance: {status} (unchanged)")
                
                # Show Merit Incentive changes
                if change['merit_changed']:
                    old_status = "✅" if change['old_merit'] else "❌"
                    new_status = "✅" if change['new_merit'] else "❌"
                    self.stdout.write(f"  Merit Incentive: {old_status} → {new_status}")
                else:
                    status = "✅" if change['old_merit'] else "❌"
                    self.stdout.write(f"  Merit Incentive: {status} (unchanged)")
                
                # Calculate allowance change
                old_amount = (5000 if change['old_basic'] else 0) + (5000 if change['old_merit'] else 0)
                new_amount = (5000 if change['new_basic'] else 0) + (5000 if change['new_merit'] else 0)
                
                self.stdout.write(f"  Total Allowance: ₱{old_amount:,} → ₱{new_amount:,}")
                self.stdout.write("")
            
            self.stdout.write("-" * 80)
            self.stdout.write("")
        
        # Display summary statistics
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("📊 SUMMARY STATISTICS"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"Total Submissions: {stats['total']}")
        self.stdout.write(f"  • Changed: {stats['changed']}")
        self.stdout.write(f"  • Unchanged: {stats['unchanged']}")
        self.stdout.write("")
        self.stdout.write("Eligibility Changes:")
        self.stdout.write(f"  • Basic Added: {stats['basic_added']}")
        self.stdout.write(f"  • Basic Removed: {stats['basic_removed']}")
        self.stdout.write(f"  • Merit Added: {stats['merit_added']}")
        self.stdout.write(f"  • Merit Removed: {stats['merit_removed']}")
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # Apply changes if not dry run
        if not dry_run:
            if changes:
                self.stdout.write(self.style.WARNING("💾 Saving changes to database..."))
                self.stdout.write("")
                
                for change in changes:
                    submission = change['submission']
                    submission.qualifies_for_basic_allowance = change['new_basic']
                    submission.qualifies_for_merit_incentive = change['new_merit']
                    
                    # Update AI evaluation notes
                    notes = []
                    notes.append("🔧 Eligibility Recalculated - OFFICIAL TCU-CEAA Criteria")
                    notes.append("=" * 40)
                    
                    if change['new_basic']:
                        notes.append("✅ Qualifies for Basic Educational Assistance (₱5,000)")
                    else:
                        notes.append("❌ Does not qualify for Basic Allowance")
                    
                    if change['new_merit']:
                        notes.append("✅ Qualifies for Merit Incentive (₱5,000)")
                    else:
                        notes.append("❌ Does not qualify for Merit Incentive")
                    
                    total_amount = (5000 if change['new_basic'] else 0) + (5000 if change['new_merit'] else 0)
                    notes.append(f"💰 Total Allowance Qualified: ₱{total_amount:,}")
                    
                    if total_amount > 0:
                        notes.append("🎉 Eligible for TCU-CEAA allowance!")
                    
                    notes.append(f"\n⚡ Updated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    submission.ai_evaluation_notes = "\n".join(notes)
                    submission.save()
                
                self.stdout.write(self.style.SUCCESS(f"✅ Successfully updated {len(changes)} submission(s)!"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ No changes needed - all submissions already correct!"))
        else:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN COMPLETE - No changes were saved."))
            self.stdout.write("")
            self.stdout.write("To apply these changes, run:")
            self.stdout.write(self.style.SUCCESS("python manage.py fix_grade_eligibility_final"))
        
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("✅ GRADE ELIGIBILITY FIX COMPLETE!"))
        self.stdout.write("=" * 80)
