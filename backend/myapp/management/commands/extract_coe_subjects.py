"""
Management command to extract subjects from approved COEs that are missing subject data.
This will process all approved Certificate of Enrollment documents and extract the subject list.
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from myapp.models import DocumentSubmission
from myapp.coe_verification_service import get_coe_verification_service


class Command(BaseCommand):
    help = 'Extract subjects from approved COEs that are missing subject data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Re-extract subjects from all COEs, even those that already have subjects',
        )
        parser.add_argument(
            '--student-id',
            type=str,
            help='Extract subjects only for a specific student ID',
        )

    def handle(self, *args, **options):
        extract_all = options['all']
        student_id = options.get('student_id')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('EXTRACTING SUBJECTS FROM COE DOCUMENTS'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
        
        # Build query for approved COEs
        query = Q(document_type='certificate_of_enrollment', status='approved')
        
        if student_id:
            query &= Q(student__student_id=student_id)
        
        if not extract_all:
            # Only get COEs without subjects
            query &= (Q(extracted_subjects__isnull=True) | Q(extracted_subjects=[]))
        
        coes = DocumentSubmission.objects.filter(query).order_by('-submitted_at')
        
        if not coes.exists():
            if extract_all:
                self.stdout.write(self.style.WARNING('No approved COEs found'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ All approved COEs already have extracted subjects!'))
            return
        
        self.stdout.write(f"Found {coes.count()} COE(s) to process\n")
        
        # Initialize COE service
        coe_service = get_coe_verification_service()
        
        success_count = 0
        fail_count = 0
        
        for coe in coes:
            self.stdout.write('='*80)
            self.stdout.write(f"Processing COE for: {coe.student.username} ({coe.student.get_full_name()})")
            self.stdout.write(f"Student ID: {coe.student.student_id}")
            self.stdout.write(f"Submitted: {coe.submitted_at}")
            self.stdout.write(f"Document ID: {coe.id}")
            
            if coe.extracted_subjects and not extract_all:
                self.stdout.write(self.style.WARNING(f"⚠️ Already has {len(coe.extracted_subjects)} subjects, skipping..."))
                continue
            
            try:
                # Get the file path
                file_path = None
                try:
                    if hasattr(coe.document_file, 'path'):
                        file_path = coe.document_file.path
                    elif hasattr(coe.document_file, 'file'):
                        file_path = coe.document_file.file.name
                except Exception as path_error:
                    self.stdout.write(self.style.ERROR(f"❌ Could not get file path: {str(path_error)}"))
                    fail_count += 1
                    continue
                
                if not file_path:
                    self.stdout.write(self.style.ERROR("❌ No file path available"))
                    fail_count += 1
                    continue
                
                self.stdout.write(f"File path: {file_path}")
                
                # Extract subjects
                self.stdout.write("🔍 Extracting subjects...")
                subject_result = coe_service.extract_subject_list(file_path)
                
                if subject_result['success'] and subject_result['subjects']:
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully extracted {subject_result['subject_count']} subjects!"))
                    self.stdout.write(f"Confidence: {subject_result['confidence']:.2%}")
                    
                    # Display extracted subjects
                    self.stdout.write("\nExtracted subjects:")
                    for idx, subject in enumerate(subject_result['subjects'], 1):
                        self.stdout.write(f"  {idx}. {subject['subject_code']} - {subject['subject_name']}")
                    
                    # Save to database
                    coe.extracted_subjects = subject_result['subjects']
                    coe.subject_count = subject_result['subject_count']
                    coe.save()
                    
                    self.stdout.write(self.style.SUCCESS("\n💾 Subjects saved to database!"))
                    success_count += 1
                    
                else:
                    self.stdout.write(self.style.ERROR("❌ Failed to extract subjects"))
                    if subject_result.get('errors'):
                        for error in subject_result['errors']:
                            self.stdout.write(self.style.ERROR(f"  - {error}"))
                    fail_count += 1
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error processing COE: {str(e)}"))
                fail_count += 1
            
            self.stdout.write('')  # Empty line
        
        # Summary
        self.stdout.write('='*80)
        self.stdout.write(self.style.SUCCESS('EXTRACTION COMPLETE'))
        self.stdout.write('='*80)
        self.stdout.write(f"Processed: {coes.count()} COE(s)")
        self.stdout.write(self.style.SUCCESS(f"✅ Success: {success_count}"))
        if fail_count > 0:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {fail_count}"))
        self.stdout.write('')
