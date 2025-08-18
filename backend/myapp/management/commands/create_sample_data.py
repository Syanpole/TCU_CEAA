from django.core.management.base import BaseCommand
from myapp.models import Task, Student

class Command(BaseCommand):
    help = 'Create sample data for development'

    def handle(self, *args, **options):
        # Create sample tasks
        tasks_data = [
            {
                'title': 'Complete Math Assignment 1',
                'description': 'Solve problems 1-20 from Chapter 3: Algebra basics',
                'completed': False
            },
            {
                'title': 'Submit English Essay',
                'description': 'Write a 500-word essay about your career goals',
                'completed': True
            },
            {
                'title': 'Attend Science Lab Session',
                'description': 'Laboratory experiment on chemical reactions - Room 203',
                'completed': False
            },
            {
                'title': 'Group Project Presentation',
                'description': 'Present your business plan to the class (15 minutes)',
                'completed': False
            }
        ]

        for task_data in tasks_data:
            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                defaults=task_data
            )
            self.stdout.write(f"Task {'created' if created else 'exists'}: {task.title}")

        # Create sample students
        students_data = [
            {
                'student_id': '22-00001',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@student.tcu.edu.ph'
            },
            {
                'student_id': '22-00002',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@student.tcu.edu.ph'
            },
            {
                'student_id': '23-00001',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'email': 'michael.johnson@student.tcu.edu.ph'
            },
            {
                'student_id': '23-00002',
                'first_name': 'Emily',
                'last_name': 'Brown',
                'email': 'emily.brown@student.tcu.edu.ph'
            }
        ]

        for student_data in students_data:
            student, created = Student.objects.get_or_create(
                student_id=student_data['student_id'],
                defaults=student_data
            )
            self.stdout.write(f"Student {'created' if created else 'exists'}: {student.first_name} {student.last_name}")

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data')
        )
