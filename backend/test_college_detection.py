"""
TCU College Detection Test
==========================

Tests the college/department detection for all 6 TCU colleges
"""

import sys
import os

# Setup Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

import django
django.setup()

from myapp.id_verification_service import IDVerificationService

def test_college_detection():
    """Test college detection with sample text"""
    print("="*80)
    print("🎓 Testing TCU College Detection")
    print("="*80)
    print()
    
    service = IDVerificationService()
    
    # Test cases for each college
    test_cases = [
        {
            'text': """
            TAGUIG CITY UNIVERSITY
            COLLEGE OF INFORMATION AND COMMUNICATION TECHNOLOGY
            Student Name: JOHN DOE
            Student Number: 19-12345
            """,
            'expected_college': 'College of Information and Communication Technology',
            'expected_code': 'CICT'
        },
        {
            'text': """
            TAGUIG CITY UNIVERSITY
            COLLEGE OF CRIMINAL JUSTICE
            Student Name: JANE SMITH
            Student Number: 20-54321
            """,
            'expected_college': 'College of Criminal Justice',
            'expected_code': 'CCJ'
        },
        {
            'text': """
            TAGUIG CITY UNIVERSITY
            COLLEGE OF BUSINESS MANAGEMENT
            Student Name: MARIA SANTOS
            Student Number: 21-11111
            """,
            'expected_college': 'College of Business Management',
            'expected_code': 'CBM'
        },
        {
            'text': """
            TAGUIG CITY UNIVERSITY
            COLLEGE OF ARTS AND SCIENCE
            Student Name: PEDRO CRUZ
            Student Number: 22-22222
            """,
            'expected_college': 'College of Arts and Science',
            'expected_code': 'CAS'
        },
        {
            'text': """
            TAGUIG CITY UNIVERSITY
            COLLEGE OF EDUCATION
            Student Name: ANNA REYES
            Student Number: 23-33333
            """,
            'expected_college': 'College of Education',
            'expected_code': 'CED'
        },
        {
            'text': """
            TAGUIG CITY UNIVERSITY
            COLLEGE OF HOSPITALITY, TOURISM, AND MANAGEMENT
            Student Name: LUIS GARCIA
            Student Number: 24-44444
            """,
            'expected_college': 'College of Hospitality, Tourism, and Management',
            'expected_code': 'CHTM'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['expected_code']}")
        
        # Extract fields from text
        fields = service._extract_id_fields(test['text'], [], 'student_id')
        
        detected_college = fields.get('college')
        detected_code = fields.get('college_code')
        
        if detected_college == test['expected_college'] and detected_code == test['expected_code']:
            print(f"  ✅ PASS: {detected_code} - {detected_college}")
            passed += 1
        else:
            print(f"  ❌ FAIL:")
            print(f"     Expected: {test['expected_code']} - {test['expected_college']}")
            print(f"     Got:      {detected_code} - {detected_college}")
            failed += 1
        
        print()
    
    print("="*80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80)
    print()
    
    return failed == 0


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                    🎓 TCU COLLEGE DETECTION TEST                          ║")
    print("║                       6 Colleges Verification                             ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    success = test_college_detection()
    
    if success:
        print()
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                            ║")
        print("║                     ✅ ALL COLLEGE TESTS PASSED!                          ║")
        print("║                                                                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print()
        return 0
    else:
        print()
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                            ║")
        print("║                     ❌ SOME TESTS FAILED                                  ║")
        print("║                                                                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
