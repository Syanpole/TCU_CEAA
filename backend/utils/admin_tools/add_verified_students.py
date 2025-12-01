"""
Quick script to add verified students to the database
Run: python manage.py shell < add_verified_students.py
"""

from myapp.models import VerifiedStudent

# Sample verified students
verified_students = [
    {
        'student_id': '22-00001',
        'first_name': 'John',
        'last_name': 'Smith',
        'middle_initial': 'A.',
        'sex': 'M',
        'course': 'BSCS',
        'year_level': 3,
        'is_active': True,
        'notes': 'Added via script'
    },
    {
        'student_id': '22-00002',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'middle_initial': 'B.',
        'sex': 'F',
        'course': 'BSIT',
        'year_level': 2,
        'is_active': True,
        'notes': 'Added via script'
    },
]

print("Adding verified students...")
for student_data in verified_students:
    student, created = VerifiedStudent.objects.get_or_create(
        student_id=student_data['student_id'],
        defaults=student_data
    )
    if created:
        print(f"✅ Created: {student.first_name} {student.last_name} ({student.student_id})")
    else:
        print(f"⚠️  Already exists: {student.first_name} {student.last_name} ({student.student_id})")

print(f"\n✅ Total verified students: {VerifiedStudent.objects.count()}")
