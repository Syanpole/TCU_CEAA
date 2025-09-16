import os
import sys
import django
from datetime import datetime, timedelta
from django.core.files.base import ContentFile

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication
from django.contrib.auth.hashers import make_password

def create_test_data():
    """Create test users and documents for testing the admin dashboard"""
    
    print("Creating test data...")
    
    # Clear existing test documents to avoid conflicts
    print("Clearing existing test documents...")
    DocumentSubmission.objects.all().delete()
    GradeSubmission.objects.all().delete()
    AllowanceApplication.objects.all().delete()
    print("Cleared existing data.")
    
    # Create admin user if not exists
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@tcu.edu',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'password': make_password('admin123')
        }
    )
    if created:
        print("Created admin user: admin/admin123")
    else:
        print("Admin user already exists")
    
    # Create test students
    students_data = [
        {
            'username': 'student1',
            'email': 'juan.delacruz@tcu.edu',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'role': 'student',
            'student_id': '22-00001',
            'password': make_password('student123')
        },
        {
            'username': 'student2',
            'email': 'maria.santos@tcu.edu',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'role': 'student',
            'student_id': '22-00002',
            'password': make_password('student123')
        },
        {
            'username': 'student3',
            'email': 'jose.garcia@tcu.edu',
            'first_name': 'Jose',
            'last_name': 'Garcia',
            'role': 'student',
            'student_id': '22-00003',
            'password': make_password('student123')
        },
        {
            'username': 'student4',
            'email': 'ana.reyes@tcu.edu',
            'first_name': 'Ana',
            'last_name': 'Reyes',
            'role': 'student',
            'student_id': '23-00001',
            'password': make_password('student123')
        },
        {
            'username': 'student5',
            'email': 'carlos.lopez@tcu.edu',
            'first_name': 'Carlos',
            'last_name': 'Lopez',
            'role': 'student',
            'student_id': '23-00002',
            'password': make_password('student123')
        }
    ]
    
    students = []
    for student_data in students_data:
        try:
            student, created = CustomUser.objects.get_or_create(
                student_id=student_data['student_id'],  # Use student_id as the unique field
                defaults=student_data
            )
            students.append(student)
            if created:
                print(f"Created student: {student.first_name} {student.last_name} ({student.student_id})")
            else:
                print(f"Student already exists: {student.first_name} {student.last_name} ({student.student_id})")
        except Exception as e:
            print(f"Error creating student {student_data['first_name']}: {e}")
            # Try to get existing student by username
            try:
                student = CustomUser.objects.get(username=student_data['username'])
                students.append(student)
                print(f"Found existing student by username: {student.first_name} {student.last_name}")
            except CustomUser.DoesNotExist:
                print(f"Could not find or create student {student_data['first_name']}")
                continue
    
    # Create test documents
    document_types = [
        'birth_certificate',
        'school_id',
        'report_card',
        'enrollment_certificate',
        'barangay_clearance',
        'parents_id',
        'voter_certification'
    ]
    
    statuses = ['pending', 'approved', 'rejected']
    
    # Create sample documents
    for i, student in enumerate(students):
        # Each student has 2-4 documents
        num_docs = 2 + (i % 3)
        for j in range(num_docs):
            doc_type = document_types[j % len(document_types)]
            status = statuses[j % len(statuses)]
            
            # Create a fake file content
            file_content = f"Test document content for {student.first_name} {student.last_name} - {doc_type}"
            fake_file = ContentFile(file_content.encode(), name=f"{doc_type}_{student.student_id}.txt")
            
            document = DocumentSubmission.objects.create(
                student=student,
                document_type=doc_type,
                document_file=fake_file,
                description=f"Sample {doc_type.replace('_', ' ')} for testing",
                status=status,
                submitted_at=datetime.now() - timedelta(days=i+j)
            )
            
            if status in ['approved', 'rejected']:
                document.reviewed_at = datetime.now() - timedelta(days=i+j-1)
                document.reviewed_by = admin_user
                document.admin_notes = f"Document {status} during testing"
                document.save()
            
            print(f"Created document: {document.get_document_type_display()} for {student.first_name} - {status}")
    
    # Create test grade submissions
    for i, student in enumerate(students):
        if i < 3:  # Only create grades for first 3 students
            grade = GradeSubmission.objects.create(
                student=student,
                academic_year="2024-2025",
                semester="1st",
                total_units=18 + i,
                general_weighted_average=85.5 + i * 2,
                semestral_weighted_average=87.0 + i * 1.5,
                has_failing_grades=False,
                has_incomplete_grades=False,
                has_dropped_subjects=False,
                status='pending' if i == 0 else 'approved',
                submitted_at=datetime.now() - timedelta(days=i+1)
            )
            
            # Run AI evaluation
            grade.calculate_allowance_eligibility()
            grade.save()
            
            if grade.status == 'approved':
                grade.reviewed_at = datetime.now() - timedelta(days=i)
                grade.reviewed_by = admin_user
                grade.save()
            
            print(f"Created grade submission for {student.first_name} - GWA: {grade.general_weighted_average}")
    
    # Create test allowance applications
    approved_grades = GradeSubmission.objects.filter(status='approved')
    for i, grade in enumerate(approved_grades):
        if grade.qualifies_for_basic_allowance or grade.qualifies_for_merit_incentive:
            app_type = 'basic' if grade.qualifies_for_basic_allowance else 'merit'
            if grade.qualifies_for_basic_allowance and grade.qualifies_for_merit_incentive:
                app_type = 'both'
            
            amount = 5000 if app_type in ['basic', 'merit'] else 10000
            
            application = AllowanceApplication.objects.create(
                student=grade.student,
                grade_submission=grade,
                application_type=app_type,
                amount=amount,
                status='pending' if i == 0 else 'approved',
                applied_at=datetime.now() - timedelta(days=i)
            )
            
            if application.status == 'approved':
                application.processed_at = datetime.now() - timedelta(hours=i*12)
                application.processed_by = admin_user
                application.save()
            
            print(f"Created allowance application for {grade.student.first_name} - {app_type} - ₱{amount}")
    
    print("\n" + "="*50)
    print("TEST DATA SUMMARY")
    print("="*50)
    print(f"Total Users: {CustomUser.objects.count()}")
    print(f"Total Students: {CustomUser.objects.filter(role='student').count()}")
    print(f"Total Documents: {DocumentSubmission.objects.count()}")
    print(f"  - Pending: {DocumentSubmission.objects.filter(status='pending').count()}")
    print(f"  - Approved: {DocumentSubmission.objects.filter(status='approved').count()}")
    print(f"  - Rejected: {DocumentSubmission.objects.filter(status='rejected').count()}")
    print(f"Total Grade Submissions: {GradeSubmission.objects.count()}")
    print(f"  - Pending: {GradeSubmission.objects.filter(status='pending').count()}")
    print(f"  - Approved: {GradeSubmission.objects.filter(status='approved').count()}")
    print(f"Total Applications: {AllowanceApplication.objects.count()}")
    print(f"  - Pending: {AllowanceApplication.objects.filter(status='pending').count()}")
    print(f"  - Approved: {AllowanceApplication.objects.filter(status='approved').count()}")
    print("\nLogin credentials:")
    print("Admin: admin / admin123")
    print("Students: student1, student2, etc. / student123")
    print("\nTest data created successfully!")

if __name__ == "__main__":
    create_test_data()
