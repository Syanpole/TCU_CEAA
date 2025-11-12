"""
Test Identity Verification
===========================

Tests the identity verification feature that compares logged-in user's
details with extracted ID card information.

Run: python test_identity_verification.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.id_verification_service import IDVerificationService
from myapp.models import CustomUser


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80 + "\n")


def print_result(label: str, value: any, success: bool = None):
    """Print formatted result."""
    if success is None:
        icon = "📊"
    elif success:
        icon = "✅"
    else:
        icon = "❌"
    print(f"   {icon} {label}: {value}")


def create_test_user():
    """Create a test user matching the ID card."""
    print_header("Creating Test User")
    
    # Check if user exists
    try:
        user = CustomUser.objects.get(username='lloyd.ramos')
        print_result("Test user", "Already exists", True)
        print_result("Name", f"{user.first_name} {user.middle_initial} {user.last_name}", None)
        print_result("Student ID", user.student_id, None)
        return user
    except CustomUser.DoesNotExist:
        pass
    
    # Create new user
    user = CustomUser.objects.create_user(
        username='lloyd.ramos',
        email='lloyd.ramos@tcu.edu.ph',
        password='test123',
        first_name='Lloyd Kenneth',
        last_name='Ramos',
        middle_initial='S.',
        student_id='19-00648',
        role='student'
    )
    
    print_result("Test user created", f"{user.first_name} {user.middle_initial} {user.last_name}", True)
    print_result("Student ID", user.student_id, True)
    
    return user


def create_mismatched_user():
    """Create a user that doesn't match the ID card."""
    print_header("Creating Mismatched Test User")
    
    # Check if user exists
    try:
        user = CustomUser.objects.get(username='john.doe')
        print_result("Mismatched user", "Already exists", True)
        print_result("Name", f"{user.first_name} {user.middle_initial} {user.last_name}", None)
        print_result("Student ID", user.student_id, None)
        return user
    except CustomUser.DoesNotExist:
        pass
    
    # Create new user
    user = CustomUser.objects.create_user(
        username='john.doe',
        email='john.doe@tcu.edu.ph',
        password='test123',
        first_name='John',
        last_name='Doe',
        middle_initial='A.',
        student_id='20-12345',
        role='student'
    )
    
    print_result("Mismatched user created", f"{user.first_name} {user.middle_initial} {user.last_name}", True)
    print_result("Student ID", user.student_id, True)
    
    return user


def test_identity_verification():
    """Test ID verification with identity matching."""
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "🆔 IDENTITY VERIFICATION TEST".center(78) + "║")
    print("║" + "ID Card vs Logged-in User Comparison".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    # Initialize service
    print_header("Initializing ID Verification Service")
    service = IDVerificationService()
    status = service.get_verification_status()
    
    print_result("YOLO Detection", status['yolo_detection'], status['yolo_detection'])
    print_result("Advanced OCR", status['advanced_ocr'], status['advanced_ocr'])
    print_result("Fully Operational", status['fully_operational'], status['fully_operational'])
    
    if not status['fully_operational']:
        print("\n❌ Service not operational. Cannot proceed with test.")
        return
    
    # Find test image
    test_image = Path(BASE_DIR) / 'media' / 'documents' / '2025' / '09' / 'ID_PIC_g7t6DG3.jpg'
    if not test_image.exists():
        print(f"\n❌ Test image not found: {test_image}")
        return
    
    print_result("Test Image", test_image.name, True)
    
    # Test 1: Matching User
    print_header("Test 1: Matching User (Should PASS)")
    matching_user = create_test_user()
    
    print("\n📷 Verifying ID with matching user...")
    result = service.verify_id_card(str(test_image), user=matching_user)
    
    print("\n📊 Verification Results:")
    print_result("Status", result['status'], result['status'] == 'VALID')
    print_result("Valid", result['is_valid'], result['is_valid'])
    print_result("Confidence", f"{result['confidence']:.2%}", result['confidence'] >= 0.8)
    print_result("Checks Passed", f"{result['checks_passed']}/{len(result['validation_checks'])}", 
                 result['checks_passed'] >= 7)
    
    print("\n🎯 Identity Verification:")
    identity = result.get('identity_verification', {})
    if identity:
        print_result("Match", identity.get('match', False), identity.get('match', False))
        print_result("Name Match", identity.get('name_match', False), identity.get('name_match', False))
        print_result("Student Number Match", identity.get('student_number_match', False), 
                     identity.get('student_number_match', False))
        print_result("Message", identity.get('message', 'N/A'), identity.get('match', False))
        
        details = identity.get('details', {})
        if details:
            print("\n   📋 Comparison Details:")
            print(f"      • Extracted Name: {details.get('extracted_name', 'N/A')}")
            print(f"      • User Name: {details.get('user_name', 'N/A')}")
            print(f"      • Extracted Student #: {details.get('extracted_student_number', 'N/A')}")
            print(f"      • User Student #: {details.get('user_student_number', 'N/A')}")
    
    print("\n✅ Validation Checks:")
    for check, passed in result['validation_checks'].items():
        print_result(check.replace('_', ' ').title(), passed, passed)
    
    # Test 2: Mismatched User
    print_header("Test 2: Mismatched User (Should FAIL)")
    mismatched_user = create_mismatched_user()
    
    print("\n📷 Verifying ID with mismatched user...")
    result2 = service.verify_id_card(str(test_image), user=mismatched_user)
    
    print("\n📊 Verification Results:")
    print_result("Status", result2['status'], result2['status'] == 'INVALID')
    print_result("Valid", result2['is_valid'], not result2['is_valid'])
    print_result("Confidence", f"{result2['confidence']:.2%}", None)
    
    print("\n🎯 Identity Verification:")
    identity2 = result2.get('identity_verification', {})
    if identity2:
        print_result("Match", identity2.get('match', False), not identity2.get('match', False))
        print_result("Name Match", identity2.get('name_match', False), not identity2.get('name_match', False))
        print_result("Student Number Match", identity2.get('student_number_match', False), 
                     not identity2.get('student_number_match', False))
        print_result("Message", identity2.get('message', 'N/A'), not identity2.get('match', False))
        
        details2 = identity2.get('details', {})
        if details2:
            print("\n   📋 Comparison Details:")
            print(f"      • Extracted Name: {details2.get('extracted_name', 'N/A')}")
            print(f"      • User Name: {details2.get('user_name', 'N/A')}")
            print(f"      • Extracted Student #: {details2.get('extracted_student_number', 'N/A')}")
            print(f"      • User Student #: {details2.get('user_student_number', 'N/A')}")
    
    if result2.get('errors'):
        print("\n❌ Errors:")
        for error in result2['errors']:
            print(f"   • {error}")
    
    if result2.get('recommendations'):
        print("\n💡 Recommendations:")
        for rec in result2['recommendations']:
            print(f"   • {rec}")
    
    # Test 3: No User (Standard Verification)
    print_header("Test 3: No User Provided (Should PASS)")
    
    print("\n📷 Verifying ID without user (standard verification)...")
    result3 = service.verify_id_card(str(test_image))
    
    print("\n📊 Verification Results:")
    print_result("Status", result3['status'], result3['status'] == 'VALID')
    print_result("Valid", result3['is_valid'], result3['is_valid'])
    print_result("Confidence", f"{result3['confidence']:.2%}", result3['confidence'] >= 0.8)
    print_result("Checks Passed", f"{result3['checks_passed']}/{len(result3['validation_checks'])}", 
                 result3['checks_passed'] >= 6)
    
    print("\n✅ Validation Checks:")
    for check, passed in result3['validation_checks'].items():
        print_result(check.replace('_', ' ').title(), passed, passed)
    
    # Summary
    print_header("Test Summary")
    
    test1_pass = result['status'] == 'VALID' and identity.get('match', False)
    test2_pass = result2['status'] == 'INVALID' and not identity2.get('match', False)
    test3_pass = result3['status'] == 'VALID'
    
    print_result("Test 1: Matching User", "PASS" if test1_pass else "FAIL", test1_pass)
    print_result("Test 2: Mismatched User", "PASS" if test2_pass else "FAIL", test2_pass)
    print_result("Test 3: No User", "PASS" if test3_pass else "FAIL", test3_pass)
    
    all_pass = test1_pass and test2_pass and test3_pass
    print("\n" + "=" * 80)
    if all_pass:
        print("🎉 ALL IDENTITY VERIFICATION TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    try:
        test_identity_verification()
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
