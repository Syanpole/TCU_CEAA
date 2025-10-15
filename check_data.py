import os
import sys
import django

sys.path.insert(0, 'backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, DocumentSubmission, GradeSubmission

print("=== DATABASE CHECK ===\n")

# Check admins
admins = CustomUser.objects.filter(role='admin')
print(f"Admins: {admins.count()}")
for admin in admins:
    print(f"  - {admin.username} (Active: {admin.is_active})")

# Check students
students = CustomUser.objects.filter(role='student')
print(f"\nStudents: {students.count()}")
for student in students[:5]:
    print(f"  - {student.username}")

# Check documents
docs = DocumentSubmission.objects.all()
print(f"\nDocuments: {docs.count()}")
for doc in docs[:5]:
    print(f"  - {doc.document_type} by {doc.student.username} - Status: {doc.status}")

# Check grades
grades = GradeSubmission.objects.all()
print(f"\nGrades: {grades.count()}")

print("\n=== END CHECK ===")
