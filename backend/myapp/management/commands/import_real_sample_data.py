from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models, transaction
from myapp.models import CustomUser, GradeSubmission, DocumentSubmission, AllowanceApplication
from decimal import Decimal
import csv
import os

class Command(BaseCommand):
    help = 'Import real sample data for AI scholarship evaluation testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students-file',
            type=str,
            help='CSV file path containing student data'
        )
        parser.add_argument(
            '--grades-file', 
            type=str,
            help='CSV file path containing grade submissions'
        )
        parser.add_argument(
            '--scholarships-file',
            type=str,
            help='CSV file path containing historical scholarship data'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview data import without saving to database'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Real Sample Data Import Utility'))
        self.stdout.write(self.style.WARNING('📋 Status: AWAITING SAMPLE DATA FILES'))
        
        # Check if sample data files are provided
        students_file = options.get('students_file')
        grades_file = options.get('grades_file')
        scholarships_file = options.get('scholarships_file')
        
        if not any([students_file, grades_file, scholarships_file]):
            self.show_usage_instructions()
            return
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No data will be saved'))
        
        try:
            with transaction.atomic():
                if students_file:
                    self.import_students(students_file, options['dry_run'])
                
                if grades_file:
                    self.import_grades(grades_file, options['dry_run'])
                
                if scholarships_file:
                    self.import_scholarships(scholarships_file, options['dry_run'])
                
                if options['dry_run']:
                    # Rollback transaction for dry run
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.SUCCESS('✅ Dry run completed - no data was saved'))
                else:
                    self.stdout.write(self.style.SUCCESS('✅ Real data import completed successfully!'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Import failed: {str(e)}'))
    
    def show_usage_instructions(self):
        self.stdout.write(self.style.WARNING('''
📄 SAMPLE DATA FILE REQUIREMENTS:

1. STUDENTS FILE (students.csv):
   Required columns: student_id, first_name, last_name, email, program, year_level
   Example:
   student_id,first_name,last_name,email,program,year_level
   25-00001,Maria,Santos,maria.santos@tcu.edu,BSIT,2
   25-00002,John,Cruz,john.cruz@tcu.edu,BSCS,3

2. GRADES FILE (grades.csv):
   Required columns: student_id, academic_year, semester, gwa, swa, units, failing_grades, incomplete_grades, dropped_subjects
   Example:
   student_id,academic_year,semester,gwa,swa,units,failing_grades,incomplete_grades,dropped_subjects
   25-00001,2024-2025,1st,92.5,94.2,18,False,False,False
   25-00002,2024-2025,1st,85.3,87.1,15,False,False,False

3. SCHOLARSHIPS FILE (scholarships.csv):
   Required columns: student_id, academic_year, semester, allowance_type, amount, status, date_applied
   Example:
   student_id,academic_year,semester,allowance_type,amount,status,date_applied
   25-00001,2024-2025,1st,both,10000,approved,2024-09-01
   25-00002,2024-2025,1st,basic,5000,approved,2024-09-01

📋 USAGE:
python manage.py import_real_sample_data --students-file students.csv --grades-file grades.csv --scholarships-file scholarships.csv

🔍 TEST FIRST:
python manage.py import_real_sample_data --students-file students.csv --dry-run
        '''))
    
    def import_students(self, file_path, dry_run=False):
        """Import student data from CSV file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Students file not found: {file_path}')
        
        self.stdout.write(f'📚 Importing students from: {file_path}')
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            students_created = 0
            
            for row in reader:
                student_id = row['student_id']
                
                # Check if student already exists
                if CustomUser.objects.filter(student_id=student_id).exists():
                    self.stdout.write(f'  ⚠️  Student {student_id} already exists, skipping')
                    continue
                
                if not dry_run:
                    student = CustomUser.objects.create_user(
                        username=f"student_{student_id.replace('-', '')}",
                        email=row['email'],
                        role='student',
                        student_id=student_id,
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        password='student123'  # Default password
                    )
                    students_created += 1
                    self.stdout.write(f'  ✅ Created student: {row["first_name"]} {row["last_name"]} ({student_id})')
                else:
                    self.stdout.write(f'  🔍 Would create: {row["first_name"]} {row["last_name"]} ({student_id})')
        
        if not dry_run:
            self.stdout.write(f'📊 Students imported: {students_created}')
    
    def import_grades(self, file_path, dry_run=False):
        """Import grade submissions from CSV file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Grades file not found: {file_path}')
        
        self.stdout.write(f'📝 Importing grades from: {file_path}')
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            grades_created = 0
            
            for row in reader:
                student_id = row['student_id']
                
                # Find the student
                try:
                    student = CustomUser.objects.get(student_id=student_id, role='student')
                except CustomUser.DoesNotExist:
                    self.stdout.write(f'  ❌ Student {student_id} not found, skipping grade record')
                    continue
                
                # Check if grade submission already exists
                academic_year = row['academic_year']
                semester = row['semester']
                
                if GradeSubmission.objects.filter(
                    student=student, 
                    academic_year=academic_year, 
                    semester=semester
                ).exists():
                    self.stdout.write(f'  ⚠️  Grade submission for {student_id} {academic_year} {semester} already exists')
                    continue
                
                if not dry_run:
                    grade_submission = GradeSubmission.objects.create(
                        student=student,
                        academic_year=academic_year,
                        semester=semester,
                        total_units=int(row['units']),
                        general_weighted_average=Decimal(row['gwa']),
                        semestral_weighted_average=Decimal(row['swa']),
                        grade_sheet=f'grades/real_data_{student_id}_{academic_year}_{semester}.pdf',
                        has_failing_grades=row['failing_grades'].lower() == 'true',
                        has_incomplete_grades=row['incomplete_grades'].lower() == 'true',
                        has_dropped_subjects=row['dropped_subjects'].lower() == 'true',
                        status='approved'
                    )
                    
                    # Run AI evaluation
                    grade_submission.calculate_allowance_eligibility()
                    grade_submission.save()
                    
                    grades_created += 1
                    self.stdout.write(f'  ✅ Created grade submission: {student_id} {academic_year} {semester}')
                else:
                    self.stdout.write(f'  🔍 Would create grade: {student_id} {academic_year} {semester}')
        
        if not dry_run:
            self.stdout.write(f'📊 Grade submissions imported: {grades_created}')
    
    def import_scholarships(self, file_path, dry_run=False):
        """Import historical scholarship data from CSV file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Scholarships file not found: {file_path}')
        
        self.stdout.write(f'💰 Importing scholarships from: {file_path}')
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            scholarships_created = 0
            
            for row in reader:
                student_id = row['student_id']
                academic_year = row['academic_year']
                semester = row['semester']
                
                # Find the student and grade submission
                try:
                    student = CustomUser.objects.get(student_id=student_id, role='student')
                    grade_submission = GradeSubmission.objects.get(
                        student=student,
                        academic_year=academic_year,
                        semester=semester
                    )
                except (CustomUser.DoesNotExist, GradeSubmission.DoesNotExist):
                    self.stdout.write(f'  ❌ Student or grade submission not found for {student_id} {academic_year} {semester}')
                    continue
                
                if not dry_run:
                    allowance_app = AllowanceApplication.objects.create(
                        student=student,
                        grade_submission=grade_submission,
                        application_type=row['allowance_type'],
                        amount=Decimal(row['amount']),
                        status=row['status'],
                        applied_at=row['date_applied']
                    )
                    
                    scholarships_created += 1
                    self.stdout.write(f'  ✅ Created scholarship: {student_id} {row["allowance_type"]} ₱{row["amount"]}')
                else:
                    self.stdout.write(f'  🔍 Would create scholarship: {student_id} {row["allowance_type"]} ₱{row["amount"]}')
        
        if not dry_run:
            self.stdout.write(f'📊 Scholarship applications imported: {scholarships_created}')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Ready for AI analysis with real data!'))
