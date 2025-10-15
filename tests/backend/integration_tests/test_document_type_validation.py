"""
Test script for document type validation
Tests the strict document type matching to prevent fraudulent submissions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from PIL import Image, ImageDraw, ImageFont
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from ai_verification.lightning_verifier import lightning_verifier

def create_test_document(document_text, filename="test_document.jpg"):
    """Create a test document image with specified text"""
    # Create a simple white image with text
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Add text to image (simulate document content)
    y_position = 50
    for line in document_text.split('\n'):
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 60
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Create uploaded file
    return SimpleUploadedFile(
        filename,
        img_bytes.read(),
        content_type='image/jpeg'
    )

class MockDocumentSubmission:
    """Mock document submission for testing"""
    def __init__(self, document_type):
        self.document_type = document_type

def test_birth_certificate_validation():
    """Test 1: Valid birth certificate should be approved"""
    print("\n" + "="*60)
    print("TEST 1: Valid Birth Certificate")
    print("="*60)
    
    # Create a mock birth certificate with correct text
    birth_cert_text = """
    REPUBLIC OF THE PHILIPPINES
    PHILIPPINE STATISTICS AUTHORITY
    CERTIFICATE OF LIVE BIRTH
    
    This certifies that on the date shown below
    A child was born to the parents listed
    
    Civil Registry Document No. 2024-001234
    PSA Certified True Copy
    """
    
    document_file = create_test_document(birth_cert_text, "birth_certificate.jpg")
    mock_submission = MockDocumentSubmission('birth_certificate')
    
    result = lightning_verifier.lightning_verify(mock_submission, document_file)
    
    print(f"Document Type: Birth Certificate")
    print(f"Valid: {result.get('is_valid_document', False)}")
    print(f"Type Match: {result.get('document_type_match', False)}")
    print(f"Confidence: {result.get('confidence_score', 0):.2%}")
    print(f"Processing Time: {result.get('processing_time', 0):.3f}s")
    
    if result.get('rejection_reason'):
        print(f"❌ Rejection Reason: {result.get('rejection_reason')}")
    else:
        print(f"✅ Matched Keywords: {', '.join(result.get('matched_keywords', []))}")
    
    return result.get('is_valid_document', False)

def test_birth_cert_as_coe():
    """Test 2: Birth certificate uploaded as COE should be rejected"""
    print("\n" + "="*60)
    print("TEST 2: Birth Certificate Uploaded as COE (Should REJECT)")
    print("="*60)
    
    # Create a mock birth certificate
    birth_cert_text = """
    REPUBLIC OF THE PHILIPPINES
    PHILIPPINE STATISTICS AUTHORITY
    CERTIFICATE OF LIVE BIRTH
    
    This certifies that on the date shown below
    A child was born to the parents listed
    
    Civil Registry Document No. 2024-001234
    PSA Certified True Copy
    """
    
    document_file = create_test_document(birth_cert_text, "fake_coe.jpg")
    mock_submission = MockDocumentSubmission('certificate_of_enrollment')  # Wrong type!
    
    result = lightning_verifier.lightning_verify(mock_submission, document_file)
    
    print(f"Declared Type: Certificate of Enrollment")
    print(f"Actual Content: Birth Certificate")
    print(f"Valid: {result.get('is_valid_document', False)}")
    print(f"Type Match: {result.get('document_type_match', False)}")
    print(f"Confidence: {result.get('confidence_score', 0):.2%}")
    print(f"Processing Time: {result.get('processing_time', 0):.3f}s")
    
    if result.get('rejection_reason'):
        print(f"❌ Rejection Reason: {result.get('rejection_reason')}")
        print(f"🎯 Expected Type: {result.get('expected_type', 'N/A')}")
        print(f"🔍 Detected Type: {result.get('detected_type', 'N/A')}")
    else:
        print(f"⚠️ WARNING: Document was incorrectly approved!")
    
    return not result.get('is_valid_document', True)  # Should be rejected (invalid)

def test_valid_coe():
    """Test 3: Valid COE should be approved"""
    print("\n" + "="*60)
    print("TEST 3: Valid Certificate of Enrollment")
    print("="*60)
    
    # Create a mock COE with correct text
    coe_text = """
    TAGUIG CITY UNIVERSITY
    CERTIFICATE OF ENROLLMENT
    
    This is to certify that the student named below
    is currently enrolled in this institution
    
    School Year: 2024-2025
    Semester: First Semester
    
    Student Number: 2024-123456
    """
    
    document_file = create_test_document(coe_text, "coe_document.jpg")
    mock_submission = MockDocumentSubmission('certificate_of_enrollment')
    
    result = lightning_verifier.lightning_verify(mock_submission, document_file)
    
    print(f"Document Type: Certificate of Enrollment")
    print(f"Valid: {result.get('is_valid_document', False)}")
    print(f"Type Match: {result.get('document_type_match', False)}")
    print(f"Confidence: {result.get('confidence_score', 0):.2%}")
    print(f"Processing Time: {result.get('processing_time', 0):.3f}s")
    
    if result.get('rejection_reason'):
        print(f"❌ Rejection Reason: {result.get('rejection_reason')}")
    else:
        print(f"✅ Matched Keywords: {', '.join(result.get('matched_keywords', []))}")
    
    return result.get('is_valid_document', False)

def test_grade_card_as_diploma():
    """Test 4: Grade card uploaded as diploma should be rejected"""
    print("\n" + "="*60)
    print("TEST 4: Grade 10 Report Card as Diploma (Should REJECT)")
    print("="*60)
    
    # Create a mock grade 10 report card
    grade_card_text = """
    DEPARTMENT OF EDUCATION
    GRADE 10 REPORT CARD
    
    Student Name: Juan Dela Cruz
    School Year: 2022-2023
    Grade Level: Grade 10 (Fourth Year)
    
    Subject Grades:
    Mathematics - 90
    Science - 88
    English - 92
    """
    
    document_file = create_test_document(grade_card_text, "fake_diploma.jpg")
    mock_submission = MockDocumentSubmission('diploma')  # Wrong type!
    
    result = lightning_verifier.lightning_verify(mock_submission, document_file)
    
    print(f"Declared Type: Diploma")
    print(f"Actual Content: Grade 10 Report Card")
    print(f"Valid: {result.get('is_valid_document', False)}")
    print(f"Type Match: {result.get('document_type_match', False)}")
    print(f"Confidence: {result.get('confidence_score', 0):.2%}")
    print(f"Processing Time: {result.get('processing_time', 0):.3f}s")
    
    if result.get('rejection_reason'):
        print(f"❌ Rejection Reason: {result.get('rejection_reason')}")
        print(f"🎯 Expected Type: {result.get('expected_type', 'N/A')}")
        print(f"🔍 Detected Type: {result.get('detected_type', 'N/A')}")
    else:
        print(f"⚠️ WARNING: Document was incorrectly approved!")
    
    return not result.get('is_valid_document', True)  # Should be rejected

def run_all_tests():
    """Run all document validation tests"""
    print("\n" + "="*60)
    print("DOCUMENT TYPE VALIDATION TEST SUITE")
    print("Testing strict document type matching")
    print("="*60)
    
    results = {
        'test_1_valid_birth_cert': test_birth_certificate_validation(),
        'test_2_birth_as_coe': test_birth_cert_as_coe(),
        'test_3_valid_coe': test_valid_coe(),
        'test_4_grade_as_diploma': test_grade_card_as_diploma()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Document validation is working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the validation logic.")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
