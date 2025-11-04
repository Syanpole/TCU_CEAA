"""
Test the database-backed student verification system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import VerifiedStudent

def test_database_verification():
    print("=" * 60)
    print("TESTING DATABASE-BACKED VERIFICATION SYSTEM")
    print("=" * 60)
    
    # Check database has records
    total_students = VerifiedStudent.objects.count()
    print(f"\n✓ Total verified students in database: {total_students}")
    
    # Test Case 1: Valid student
    print("\n1. Testing valid student (22-00001 - Vennee Jones Abaigar):")
    try:
        student = VerifiedStudent.objects.get(student_id="22-00001", is_active=True)
        result = student.verify_identity("Vennee Jones", "Abaigar", "R")
        print(f"   Verified: {result['verified']}")
        print(f"   Message: {result['message']}")
    except VerifiedStudent.DoesNotExist:
        print("   ✗ Student not found in database!")
    
    # Test Case 2: Student with N/A middle initial
    print("\n2. Testing student with N/A middle initial (22-00319 - Adrian Alejandro):")
    try:
        student = VerifiedStudent.objects.get(student_id="22-00319", is_active=True)
        result = student.verify_identity("Adrian", "Alejandro", "")
        print(f"   Verified: {result['verified']}")
        print(f"   Message: {result['message']}")
    except VerifiedStudent.DoesNotExist:
        print("   ✗ Student not found in database!")
    
    # Test Case 3: Wrong first name
    print("\n3. Testing with wrong first name:")
    try:
        student = VerifiedStudent.objects.get(student_id="22-00001", is_active=True)
        result = student.verify_identity("Wrong Name", "Abaigar", "R")
        print(f"   Verified: {result['verified']}")
        print(f"   Message: {result['message']}")
    except VerifiedStudent.DoesNotExist:
        print("   ✗ Student not found in database!")
    
    # Test Case 4: Case insensitive
    print("\n4. Testing case insensitive matching:")
    try:
        student = VerifiedStudent.objects.get(student_id="22-00001", is_active=True)
        result = student.verify_identity("VENNEE JONES", "abaigar", "r")
        print(f"   Verified: {result['verified']}")
        print(f"   Message: {result['message']}")
    except VerifiedStudent.DoesNotExist:
        print("   ✗ Student not found in database!")
    
    # Test Case 5: Student with space in last name
    print("\n5. Testing student with space in last name (22-00363 - Angelo Dela Cruz):")
    try:
        student = VerifiedStudent.objects.get(student_id="22-00363", is_active=True)
        result = student.verify_identity("Angelo", "Dela Cruz", "A")
        print(f"   Verified: {result['verified']}")
        print(f"   Message: {result['message']}")
    except VerifiedStudent.DoesNotExist:
        print("   ✗ Student not found in database!")
    
    # Test Case 6: Registration status check
    print("\n6. Testing registration status:")
    student = VerifiedStudent.objects.get(student_id="22-00001", is_active=True)
    print(f"   Has registered: {student.has_registered}")
    print(f"   Is active: {student.is_active}")
    print(f"   Registered user: {student.registered_user}")
    
    # Test Case 7: List some students
    print("\n7. Sample of verified students in database:")
    for student in VerifiedStudent.objects.all()[:5]:
        print(f"   - {student}")
    
    print("\n" + "=" * 60)
    print("✅ DATABASE VERIFICATION TESTS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_database_verification()
