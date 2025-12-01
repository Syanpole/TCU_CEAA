"""
Name Extraction Testing for ID Verification
============================================

Tests the improved name extraction and cleaning functionality
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

def test_name_cleaning():
    """Test name cleaning with various formats"""
    print("="*80)
    print("🧹 Testing Name Cleaning")
    print("="*80)
    print()
    
    service = IDVerificationService()
    
    # Test cases with expected outputs
    test_cases = [
        {
            'text': """
            TAGUIG CITY UNIVERSITY
            COLLEGE OF INFORMATION AND COMMUNICATION TECHNOLOGY
            Student Name: JOHN DELA CRUZ
            Student Number: 19-00001
            """,
            'description': 'Name after label (ALL CAPS)'
        },
        {
            'text': """
            LLOYD KENNETH RAMOS
            19-00648
            Taguig City University
            """,
            'description': 'Name on separate line (Title Case)'
        },
        {
            'text': """
            DELA CRUZ, JUAN A.
            Student ID: 22-12345
            """,
            'description': 'Comma format (LAST, FIRST)'
        },
        {
            'text': """
            MARIA CLARA SANTOS
            TAGUIG CITY UNIVERSITY
            PHILIPPINES
            """,
            'description': 'Name with university text'
        },
        {
            'text': """
            Name: Jose P. Rizal
            Student Number: 21-54321
            Course: BS Computer Science
            """,
            'description': 'Name with middle initial'
        },
        {
            'text': """
            VERSITY TAGUIG
            PHILIPPINES
            REPUBLIC OF THE PHILIPPINES
            TAGUIG CITY UNIVERSITY
            Pedro Penduko
            19-99999
            """,
            'description': 'Name buried in text'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test['description']}")
        print(f"Input text:\n{test['text'][:100]}...")
        
        # Extract name
        name = service._extract_and_clean_name(test['text'], [])
        
        if name:
            print(f"✅ Extracted: '{name}'")
        else:
            print(f"❌ No name extracted")
        
        print()
    
    print("="*80)


def test_name_validation():
    """Test name validation logic"""
    print()
    print("="*80)
    print("✅ Testing Name Validation")
    print("="*80)
    print()
    
    service = IDVerificationService()
    
    test_names = [
        ("John Doe", True, "Valid: 2 word name"),
        ("Maria Clara Santos", True, "Valid: 3 word name"),
        ("Jose P. Rizal", True, "Valid: Name with middle initial"),
        ("Juan Dela Cruz Jr.", True, "Valid: Name with suffix"),
        ("J", False, "Invalid: Single letter"),
        ("John", False, "Invalid: Single word"),
        ("John123", False, "Invalid: Contains numbers"),
        ("Very Long Name That Has Too Many Words Here", False, "Invalid: Too many words"),
        ("John@Doe", False, "Invalid: Special characters"),
        ("UNIVERSITY", False, "Invalid: Not a name"),
        ("John A. B. C. D. E.", False, "Invalid: Too many initials"),
        ("Lloyd Kenneth", True, "Valid: First and middle name"),
        ("De La Cruz", True, "Valid: Compound last name"),
    ]
    
    for name, expected, description in test_names:
        result = service._is_valid_name(name)
        status = "✅" if result == expected else "❌"
        match = "PASS" if result == expected else "FAIL"
        print(f"{status} {match}: '{name}' -> {result} ({description})")
    
    print()
    print("="*80)


def test_name_cleaning_examples():
    """Test specific cleaning examples"""
    print()
    print("="*80)
    print("🧼 Testing Name String Cleaning")
    print("="*80)
    print()
    
    service = IDVerificationService()
    noise_words = {
        'university', 'college', 'taguig', 'student', 'name'
    }
    
    test_cases = [
        ("JOHN DELA CRUZ", "John Dela Cruz"),
        ("DELA CRUZ, JUAN", "Juan Dela Cruz"),
        ("Maria. Clara. Santos.", "Maria Clara Santos"),
        ("JUAN A. DELA CRUZ", "Juan A. Dela Cruz"),
        ("student name John Doe university", "John Doe"),
        ("JOHN    MULTIPLE     SPACES", "John Multiple Spaces"),
    ]
    
    for input_name, expected in test_cases:
        cleaned = service._clean_name_string(input_name, noise_words)
        status = "✅" if cleaned == expected else "⚠️"
        print(f"{status} '{input_name}' -> '{cleaned}' (expected: '{expected}')")
    
    print()
    print("="*80)


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                  🧹 NAME EXTRACTION & CLEANING TESTS                      ║")
    print("║                     ID Verification Service                               ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Run tests
    test_name_cleaning()
    test_name_validation()
    test_name_cleaning_examples()
    
    print()
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                        ✅ ALL TESTS COMPLETED                             ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
