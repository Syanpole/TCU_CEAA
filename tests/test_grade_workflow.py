"""
Test script for grade submission workflow refactor
Tests COE subject extraction and grade validation services
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.grade_validation_service import get_grade_validation_service

def test_validation_service():
    """Test the grade validation service"""
    print("=" * 60)
    print("Testing Grade Validation Service")
    print("=" * 60)
    
    # Test data
    coe_subjects = [
        {'subject_code': 'GE101', 'subject_name': 'Technopreneurship'},
        {'subject_code': 'MATH102', 'subject_name': 'College Algebra'},
        {'subject_code': 'ENG101', 'subject_name': 'Communication Skills'},
    ]
    
    # Test Case 1: Perfect match
    print("\n📋 Test Case 1: Perfect Match")
    print("-" * 60)
    submissions_perfect = [
        {'subject_code': 'GE101', 'subject_name': 'Technopreneurship'},
        {'subject_code': 'MATH102', 'subject_name': 'College Algebra'},
        {'subject_code': 'ENG101', 'subject_name': 'Communication Skills'},
    ]
    
    service = get_grade_validation_service()
    result = service.validate_grade_submissions(coe_subjects, submissions_perfect)
    
    print(service.get_validation_summary(result))
    
    # Test Case 2: Missing subject
    print("\n📋 Test Case 2: Missing Subject")
    print("-" * 60)
    submissions_missing = [
        {'subject_code': 'GE101', 'subject_name': 'Technopreneurship'},
        {'subject_code': 'MATH102', 'subject_name': 'College Algebra'},
    ]
    
    result = service.validate_grade_submissions(coe_subjects, submissions_missing)
    print(service.get_validation_summary(result))
    
    # Test Case 3: Extra subject
    print("\n📋 Test Case 3: Extra Subject")
    print("-" * 60)
    submissions_extra = [
        {'subject_code': 'GE101', 'subject_name': 'Technopreneurship'},
        {'subject_code': 'MATH102', 'subject_name': 'College Algebra'},
        {'subject_code': 'ENG101', 'subject_name': 'Communication Skills'},
        {'subject_code': 'CS101', 'subject_name': 'Computer Science'},
    ]
    
    result = service.validate_grade_submissions(coe_subjects, submissions_extra)
    print(service.get_validation_summary(result))
    
    # Test Case 4: Subject name variation (fuzzy match)
    print("\n📋 Test Case 4: Subject Name Variation")
    print("-" * 60)
    submissions_variation = [
        {'subject_code': 'GE101', 'subject_name': 'Technopreneurship'},
        {'subject_code': 'MATH102', 'subject_name': 'College Algebra I'},  # Slightly different
        {'subject_code': 'ENG101', 'subject_name': 'Communication Skils'},  # Typo
    ]
    
    result = service.validate_grade_submissions(coe_subjects, submissions_variation)
    print(service.get_validation_summary(result))
    
    print("\n" + "=" * 60)
    print("✅ All validation tests completed!")
    print("=" * 60)

def test_subject_extraction():
    """Test subject extraction from COE"""
    from myapp.coe_verification_service import get_coe_verification_service
    from myapp.models import DocumentSubmission
    
    print("\n" + "=" * 60)
    print("Testing COE Subject Extraction")
    print("=" * 60)
    
    # Find a COE document
    coe_docs = DocumentSubmission.objects.filter(
        document_type='certificate_of_enrollment'
    ).order_by('-submitted_at')[:3]
    
    if not coe_docs:
        print("❌ No COE documents found in database")
        return
    
    service = get_coe_verification_service()
    
    for coe in coe_docs:
        print(f"\n📄 Testing COE: {coe.id} - {coe.student.get_full_name()}")
        print(f"   Status: {coe.status}")
        print(f"   Submitted: {coe.submitted_at}")
        
        # Check if file exists
        try:
            if hasattr(coe.document_file, 'path'):
                file_path = coe.document_file.path
                if os.path.exists(file_path):
                    print(f"   File: {file_path}")
                    
                    # Extract subjects
                    result = service.extract_subject_list(file_path)
                    
                    if result['success']:
                        print(f"   ✅ Extracted {result['subject_count']} subjects:")
                        for i, subject in enumerate(result['subjects'], 1):
                            print(f"      {i}. {subject['subject_code']} - {subject['subject_name']}")
                    else:
                        print(f"   ❌ Extraction failed: {result['errors']}")
                else:
                    print(f"   ⚠️ File not found at path")
            else:
                print(f"   ⚠️ File is stored in cloud (S3)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        # Test validation service
        test_validation_service()
        
        # Test subject extraction
        test_subject_extraction()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
