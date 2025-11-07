"""
Management command to safely delete a user account and all related records
Usage: python manage.py delete_user_account <username>
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from myapp.models import (
    CustomUser, DocumentSubmission, GradeSubmission, 
    AllowanceApplication, EmailVerification, VerifiedStudent
)
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Safely delete a user account and all related records'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the account to delete')
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')

        # Gather statistics about what will be deleted
        documents = DocumentSubmission.objects.filter(student=user).count()
        grades = GradeSubmission.objects.filter(student=user).count()
        applications = AllowanceApplication.objects.filter(student=user).count()
        verifications = EmailVerification.objects.filter(user=user).count()
        
        # Check for VerifiedStudent record
        verified_student = None
        try:
            verified_student = VerifiedStudent.objects.get(registered_user=user)
        except VerifiedStudent.DoesNotExist:
            pass

        # Display summary
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('USER ACCOUNT DELETION SUMMARY'))
        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(f'\n👤 User: {user.username} ({user.get_full_name()})')
        self.stdout.write(f'   Email: {user.email}')
        self.stdout.write(f'   Role: {user.role}')
        self.stdout.write(f'   Student ID: {user.student_id or "N/A"}')
        self.stdout.write(f'   Joined: {user.created_at.strftime("%Y-%m-%d")}')
        
        self.stdout.write(self.style.WARNING('\n📊 RECORDS TO BE DELETED:'))
        self.stdout.write(f'   • {documents} Document Submissions')
        self.stdout.write(f'   • {grades} Grade Submissions')
        self.stdout.write(f'   • {applications} Allowance Applications')
        self.stdout.write(f'   • {verifications} Email Verifications')
        self.stdout.write(f'   • 1 User Account')
        
        total_records = documents + grades + applications + verifications + 1
        
        self.stdout.write(self.style.WARNING(f'\n   TOTAL: {total_records} records will be permanently deleted'))
        
        if verified_student:
            self.stdout.write(self.style.NOTICE('\n📝 VERIFIED STUDENT RECORD:'))
            self.stdout.write(f'   • VerifiedStudent record will be PRESERVED')
            self.stdout.write(f'   • Status will be reset to allow re-registration')
            self.stdout.write(f'   • Student: {verified_student.first_name} {verified_student.last_name}')
        
        self.stdout.write(self.style.NOTICE('\n🔒 PRESERVED RECORDS (Audit Trail):'))
        self.stdout.write('   • AuditLog entries (admin actions/reviews)')
        self.stdout.write('   • Documents reviewed by this user (if admin)')
        self.stdout.write('   • Grades reviewed by this user (if admin)')
        self.stdout.write('   • Applications processed by this user (if admin)')
        
        # Confirm deletion
        if not options['confirm']:
            self.stdout.write(self.style.ERROR('\n⚠️  WARNING: This action CANNOT be undone!'))
            confirm = input('\nType the username to confirm deletion: ')
            if confirm != username:
                self.stdout.write(self.style.ERROR('\n❌ Deletion cancelled - username mismatch'))
                return

        # Perform deletion in a transaction
        try:
            with transaction.atomic():
                # Delete auth token if exists
                Token.objects.filter(user=user).delete()
                
                # Reset VerifiedStudent record if exists
                if verified_student:
                    verified_student.has_registered = False
                    verified_student.registered_user = None
                    verified_student.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'\n✅ Reset VerifiedStudent record for {verified_student.student_id}'
                    ))
                
                # Get counts before deletion for confirmation
                deleted_docs = documents
                deleted_grades = grades
                deleted_apps = applications
                deleted_verifications = verifications
                
                # Delete the user (CASCADE will handle related records)
                user.delete()
                
                # Success message
                self.stdout.write(self.style.SUCCESS('\n' + '='*60))
                self.stdout.write(self.style.SUCCESS('✅ USER ACCOUNT SUCCESSFULLY DELETED'))
                self.stdout.write(self.style.SUCCESS('='*60))
                self.stdout.write(f'\n✅ Deleted {deleted_docs} document submissions')
                self.stdout.write(f'✅ Deleted {deleted_grades} grade submissions')
                self.stdout.write(f'✅ Deleted {deleted_apps} allowance applications')
                self.stdout.write(f'✅ Deleted {deleted_verifications} email verifications')
                self.stdout.write(f'✅ Deleted user account: {username}')
                
                if verified_student:
                    self.stdout.write(f'✅ Reset VerifiedStudent record (can register again)')
                
                self.stdout.write(self.style.SUCCESS(f'\n✨ Total: {total_records} records deleted successfully\n'))
                
        except Exception as e:
            raise CommandError(f'Error during deletion: {str(e)}')
