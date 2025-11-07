"""
Test script to verify Student ID-only verification works correctly
This tests that students can register even with typos in their name.

Run: python test_student_id_verification.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

import requests
import json

# Test configuration
API_BASE_URL = 'http://localhost:8000/api'
VERIFY_ENDPOINT = f'{API_BASE_URL}/auth/verify-student/'

def test_verification(student_id, first_name='', last_name='', middle_initial='', test_name=''):
    """Test student verification"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Student ID: {student_id}")
    print(f"First Name: {first_name or '(not provided)'}")
    print(f"Last Name: {last_name or '(not provided)'}")
    print(f"Middle Initial: {middle_initial or '(not provided)'}")
    print()
    
    # Build request data
    data = {'student_id': student_id}
    if first_name:
        data['first_name'] = first_name
    if last_name:
        data['last_name'] = last_name
    if middle_initial:
        data['middle_initial'] = middle_initial
    
    try:
        response = requests.post(VERIFY_ENDPOINT, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ VERIFIED: {result.get('message')}")
            
            if result.get('student_data'):
                student_data = result['student_data']
                print("\nStudent Data from Database:")
                print(f"  - Student ID: {student_data.get('student_id')}")
                print(f"  - Name: {student_data.get('first_name')} {student_data.get('last_name')}")
                print(f"  - Middle Initial: {student_data.get('middle_initial')}")
                print(f"  - Course: {student_data.get('course')}")
                print(f"  - Year: {student_data.get('year_level')}")
                print(f"  - Sex: {student_data.get('sex')}")
            
            return True
        else:
            result = response.json()
            print(f"❌ VERIFICATION FAILED: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  STUDENT ID-ONLY VERIFICATION TEST")
    print("="*70)
    print("\nThis tests that students can register using ONLY their Student ID.")
    print("Name typos won't block registration.")
    print()
    
    # Test 1: Valid Student ID only (no name fields)
    test_verification(
        student_id='22-00001',
        test_name='Test 1: Valid Student ID Only (No Name Fields)'
    )
    
    # Test 2: Valid Student ID with correct name
    test_verification(
        student_id='22-00001',
        first_name='Vennee Jones',
        last_name='Abaigar',
        middle_initial='R',
        test_name='Test 2: Valid Student ID with Correct Name'
    )
    
    # Test 3: Valid Student ID with TYPO in name (should still work!)
    test_verification(
        student_id='22-00001',
        first_name='Venee',  # Typo: missing one 'n'
        last_name='Abaigar',
        middle_initial='R',
        test_name='Test 3: Valid Student ID with NAME TYPO (Should Still Work!)'
    )
    
    # Test 4: Valid Student ID with completely different name (should still work!)
    test_verification(
        student_id='22-00001',
        first_name='John',  # Wrong name
        last_name='Doe',    # Wrong name
        middle_initial='A', # Wrong initial
        test_name='Test 4: Valid Student ID with Wrong Name (Should Still Work!)'
    )
    
    # Test 5: Another student - Kenneth Abayon
    test_verification(
        student_id='21-00274',
        test_name='Test 5: Another Valid Student ID (Kenneth Abayon)'
    )
    
    # Test 6: Invalid Student ID (should fail)
    test_verification(
        student_id='99-99999',
        first_name='Invalid',
        last_name='Student',
        test_name='Test 6: Invalid Student ID (Should Fail)'
    )
    
    # Test 7: Empty Student ID (should fail)
    test_verification(
        student_id='',
        test_name='Test 7: Empty Student ID (Should Fail)'
    )
    
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print("\n✅ Expected Results:")
    print("  - Tests 1-5: Should PASS (verified successfully)")
    print("  - Tests 6-7: Should FAIL (invalid/empty Student ID)")
    print("\n✨ Key Point: Name typos don't block verification!")
    print("   Only Student ID matters for verification.")
    print()

if __name__ == '__main__':
    # Check if server is running
    try:
        requests.get(API_BASE_URL, timeout=2)
        main()
    except requests.exceptions.RequestException:
        print("\n❌ ERROR: Backend server is not running!")
        print("\nPlease start the Django server first:")
        print("  cd backend")
        print("  python manage.py runserver")
        print()
