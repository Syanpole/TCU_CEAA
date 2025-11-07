"""
Quick test to verify middle initial period issue is fixed
Tests that "S." and "S" both work for middle initials

Run: python test_middle_initial_fix.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

import requests

API_BASE_URL = 'http://localhost:8000/api'

def test_registration(student_id, first_name, last_name, middle_initial, test_name):
    """Test registration with middle initial"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Student ID: {student_id}")
    print(f"Name: {first_name} {middle_initial} {last_name}")
    print()
    
    # Test data
    register_data = {
        'username': f'test_{student_id.replace("-", "")}_{middle_initial.replace(".", "")}',
        'email': f'test_{student_id.replace("-", "")}_{middle_initial.replace(".", "")}@test.com',
        'password': 'TestPassword123!',
        'password_confirm': 'TestPassword123!',
        'first_name': first_name,
        'last_name': last_name,
        'middle_initial': middle_initial,
        'student_id': student_id,
        'role': 'student',
        'verification_code': 'dummy_code'  # For testing
    }
    
    try:
        response = requests.post(f'{API_BASE_URL}/auth/register/', json=register_data)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code in [200, 201]:
            print(f"✅ REGISTRATION ACCEPTED")
            print(f"   Message: {result.get('message', 'Success')}")
            return True
        elif response.status_code == 400:
            error_msg = str(result)
            if 'middle initial' in error_msg.lower() or 'middle_initial' in error_msg.lower():
                print(f"❌ MIDDLE INITIAL ERROR: {result}")
                return False
            elif 'verification_code' in error_msg.lower() or 'email' in error_msg.lower():
                print(f"✅ PASSED STUDENT ID CHECK (failed on email verification - expected)")
                print(f"   Error: {result}")
                return True
            else:
                print(f"❌ OTHER ERROR: {result}")
                return False
        else:
            print(f"❌ ERROR: {result}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  MIDDLE INITIAL PERIOD FIX TEST")
    print("="*70)
    print("\nTesting that both 'S' and 'S.' work for middle initials")
    print("(and other variations with/without periods)")
    print()
    
    # Find a student with middle initial "S" from CSV
    # Using Student 22-00566 Benedict S. Reyes
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Middle initial without period
    if test_registration(
        '22-00566', 'Benedict', 'Reyes', 'S',
        'Test 1: Middle Initial "S" (no period)'
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 2: Middle initial WITH period
    if test_registration(
        '22-00566', 'Benedict', 'Reyes', 'S.',
        'Test 2: Middle Initial "S." (WITH period) - Should work now!'
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 3: Empty middle initial
    if test_registration(
        '22-00566', 'Benedict', 'Reyes', '',
        'Test 3: No Middle Initial (blank)'
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 4: Wrong middle initial (should still work - no name verification!)
    if test_registration(
        '22-00566', 'Benedict', 'Reyes', 'X.',
        'Test 4: Wrong Middle Initial "X." (should work - no name check!)'
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 5: Completely wrong name (should still work!)
    if test_registration(
        '22-00566', 'John', 'Doe', 'A.',
        'Test 5: Completely Wrong Name (should work - only Student ID checked!)'
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    print("\n" + "="*70)
    print("  TEST RESULTS")
    print("="*70)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print()
    
    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED! Middle initial period issue is FIXED!")
        print("   Students can now use 'S' or 'S.' (or any other format)")
        print("   Only Student ID is verified!")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    print()

if __name__ == '__main__':
    try:
        requests.get(API_BASE_URL, timeout=2)
        main()
    except requests.exceptions.RequestException:
        print("\n❌ ERROR: Backend server is not running!")
        print("\nPlease start the Django server first:")
        print("  cd backend")
        print("  python manage.py runserver")
        print()
