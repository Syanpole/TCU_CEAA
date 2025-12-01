"""
Check student ID data consistency
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, DocumentSubmission

print("=" * 80)
print("👤 STUDENT DATA VERIFICATION")
print("=" * 80)

# Get the user
user = CustomUser.objects.get(username='4peytonly')
print(f"\n📋 User Information:")
print(f"   Username: {user.username}")
print(f"   Full Name: {user.get_full_name()}")
print(f"   First Name: {user.first_name}")
print(f"   Last Name: {user.last_name}")
print(f"   Student ID in System: {user.student_id}")
print(f"   Email: {user.email}")

print(f"\n📄 Document Submission:")
doc = DocumentSubmission.objects.get(id=5)
print(f"   Document ID: {doc.id}")
print(f"   File: {doc.document_file.name}")
print(f"   Type: {doc.get_document_type_display()}")

print(f"\n🔍 ID Card Analysis:")
print(f"   ID card shows: 22-00417")
print(f"   System has: {user.student_id}")
print(f"   Match: {'✅ YES' if user.student_id == '22-00417' else '❌ NO'}")

print(f"\n💡 FINDINGS:")
if user.student_id == '21-0417':
    print(f"   The system has student ID: 21-0417")
    print(f"   But the ID card shows: 22-00417")
    print(f"   This could mean:")
    print(f"   1. The student ID in the system is incorrect (typo)")
    print(f"   2. The student uploaded someone else's ID")
    print(f"   3. The OCR misread the ID (21 vs 22)")

print("\n" + "=" * 80)
