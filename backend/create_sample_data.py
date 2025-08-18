import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import Task, Student

def create_sample_data():
    """Create sample tasks and students for testing"""
    
    # Create sample tasks
    tasks_data = [
        {
            'title': 'Complete Project Setup',
            'description': 'Set up Django, React, and TailwindCSS integration',
            'completed': True
        },
        {
            'title': 'Design Database Schema',
            'description': 'Create models for students and tasks',
            'completed': True
        },
        {
            'title': 'Implement API Endpoints',
            'description': 'Create REST API endpoints for CRUD operations',
            'completed': False
        },
        {
            'title': 'Build Frontend Components',
            'description': 'Create React components with TailwindCSS styling',
            'completed': False
        },
        {
            'title': 'Testing and Documentation',
            'description': 'Write tests and comprehensive documentation',
            'completed': False
        }
    ]
    
    # Create sample students
    students_data = [
        {
            'student_id': 'TCU001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@tcu.edu'
        },
        {
            'student_id': 'TCU002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@tcu.edu'
        },
        {
            'student_id': 'TCU003',
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'email': 'michael.johnson@tcu.edu'
        },
        {
            'student_id': 'TCU004',
            'first_name': 'Emily',
            'last_name': 'Davis',
            'email': 'emily.davis@tcu.edu'
        },
        {
            'student_id': 'TCU005',
            'first_name': 'David',
            'last_name': 'Wilson',
            'email': 'david.wilson@tcu.edu'
        }
    ]
    
    # Clear existing data
    Task.objects.all().delete()
    Student.objects.all().delete()
    
    # Create tasks
    for task_data in tasks_data:
        task = Task.objects.create(**task_data)
        print(f"Created task: {task.title}")
    
    # Create students
    for student_data in students_data:
        student = Student.objects.create(**student_data)
        print(f"Created student: {student.first_name} {student.last_name}")
    
    print("\nSample data created successfully!")
    print(f"Total tasks: {Task.objects.count()}")
    print(f"Total students: {Student.objects.count()}")

if __name__ == "__main__":
    create_sample_data()
