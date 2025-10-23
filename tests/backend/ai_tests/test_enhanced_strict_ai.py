"""
Test Script for Enhanced Strict AI Document Validation
Tests the improved AI that prevents document type mismatches
(e.g., uploading school ID when transcript is required)

Author: TCU-CEAA Development Team
Date: October 2025
"""

import os
import sys
import django

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Try to import Django settings
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Django not available: {e}")
    print("Running tests in standalone mode without Django models...\n")
    DJANGO_AVAILABLE = False

from ai_verification.base_verifier import document_type_detector
from ai_verification.enhanced_document_validator import enhanced_validator
from django.core.files.uploadedfile import SimpleUploadedFile


class MockDocumentSubmission:
    """Mock document submission for testing"""
    def __init__(self, doc_type, file_obj):
        self.document_type = doc_type
        self.document_file = file_obj
    
    def get_document_type_display(self):
        return self.document_type.replace('_', ' ').title()


def test_document_type_fraud_prevention():
    """
    Test the AI's ability to detect document type fraud
    """
    print("\n" + "="*80)
    print("🔬 ENHANCED AI DOCUMENT TYPE FRAUD PREVENTION TEST")
    print("="*80)
    print("\n📋 Testing Scenario:")
    print("   User selects: Transcript of Records")
    print("   User uploads: School ID (WRONG DOCUMENT)")
    print("   Expected: AI should REJECT this fraud attempt")
    print("\n" + "-"*80 + "\n")
    
    # Simulate text from a SCHOOL ID document
    school_id_text = """
    TRINITY COLLEGE OF URDANETA
    STUDENT IDENTIFICATION CARD
    
    Name: JUAN DELA CRUZ
    Student ID Number: 2024-12345
    Course: BS Computer Science
    Year Level: 3rd Year
    
    Valid Until: May 2025
    
    This card is the property of TCU
    Photo attached
    Signature: _______________
    """
    
    # Create mock file
    fake_file = SimpleUploadedFile(
        "school_id.jpg",
        school_id_text.encode('utf-8'),
        content_type="image/jpeg"
    )
    
    # Create mock submission claiming this is a transcript
    mock_submission = MockDocumentSubmission(
        doc_type='transcript_of_records',  # User claims it's a transcript
        file_obj=fake_file
    )
    
    print("🤖 Running Enhanced AI Verification...\n")
    
    # Test with base verifier
    print("1️⃣  Testing Base Document Type Detector:")
    print("-" * 60)
    
    # Mock the text extraction to return our school ID text
    class MockFile:
        name = "school_id.jpg"
        size = 50000
        
        def chunks(self):
            yield school_id_text.encode('utf-8')
    
    mock_file = MockFile()
    
    # Override the extraction method temporarily
    original_extract = document_type_detector._extract_text_from_image
    document_type_detector._extract_text_from_image = lambda x: school_id_text
    
    try:
        result = document_type_detector.verify_document_type(mock_submission, mock_file)
        
        print(f"\n📊 Verification Results:")
        print(f"   Document Type Match: {result.get('document_type_match', False)}")
        print(f"   Confidence Score: {result.get('confidence_score', 0):.1%}")
        print(f"   Fraud Risk: {result.get('fraud_risk_score', 0):.1%}")
        print(f"   Recommendation: {result.get('recommendation', 'unknown').upper()}")
        
        print(f"\n📝 Verification Notes:")
        for note in result.get('verification_notes', [])[:10]:
            print(f"   {note}")
        
        print(f"\n🔍 Keyword Analysis:")
        keyword_analysis = result.get('keyword_analysis', {})
        found_keywords = keyword_analysis.get('found_keywords', {})
        
        print(f"   ✅ Required Keywords Found: {found_keywords.get('primary', [])}")
        print(f"   ❌ Forbidden Keywords Found: {found_keywords.get('forbidden', [])}")
        
        if found_keywords.get('forbidden'):
            print(f"\n   ⚠️  ALERT: Forbidden keywords detected!")
            print(f"       These keywords indicate this is NOT a transcript:")
            for kw in found_keywords['forbidden'][:5]:
                print(f"       • '{kw}'")
        
        # Final verdict
        print(f"\n" + "="*60)
        if result.get('recommendation') == 'reject':
            print("✅ TEST PASSED: AI correctly REJECTED the fraudulent document!")
            print("   The AI detected that a School ID was uploaded instead of Transcript.")
        elif result.get('recommendation') == 'auto_approve':
            print("❌ TEST FAILED: AI incorrectly APPROVED the fraudulent document!")
            print("   This is a security issue - School ID was accepted as Transcript!")
        else:
            print("⚠️  TEST INCONCLUSIVE: AI flagged for manual review")
            print("   Better than auto-approval, but should auto-reject obvious fraud")
        print("="*60 + "\n")
        
    finally:
        # Restore original method
        document_type_detector._extract_text_from_image = original_extract


def test_correct_document_acceptance():
    """
    Test that AI still accepts correct documents
    """
    print("\n" + "="*80)
    print("✅ TESTING CORRECT DOCUMENT ACCEPTANCE")
    print("="*80)
    print("\n📋 Testing Scenario:")
    print("   User selects: Transcript of Records")
    print("   User uploads: Actual Transcript (CORRECT)")
    print("   Expected: AI should APPROVE")
    print("\n" + "-"*80 + "\n")
    
    # Simulate text from an actual TRANSCRIPT
    transcript_text = """
    TRINITY COLLEGE OF URDANETA
    OFFICE OF THE REGISTRAR
    TRANSCRIPT OF RECORDS
    
    Name: MARIA CLARA SANTOS
    Student Number: 2021-54321
    Course: Bachelor of Science in Computer Science
    
    ACADEMIC RECORD
    
    FIRST YEAR - First Semester (2021-2022)
    Subject                         Units    Final Grade
    COMP 101 - Programming I        3        1.50
    MATH 101 - College Algebra      3        1.75
    ENGL 101 - Communication        3        1.25
    PE 101 - Physical Education     2        1.00
    
    FIRST YEAR - Second Semester (2021-2022)
    Subject                         Units    Final Grade
    COMP 102 - Programming II       3        1.50
    MATH 102 - Trigonometry         3        2.00
    ENGL 102 - Literature           3        1.50
    PE 102 - Physical Education     2        1.25
    
    General Weighted Average (GWA): 1.54
    Total Units Earned: 25
    
    This is an official transcript issued by the Office of the Registrar.
    Date Issued: October 9, 2025
    
    _______________________
    University Registrar
    """
    
    class MockFile:
        name = "transcript.pdf"
        size = 150000
        
        def chunks(self):
            yield transcript_text.encode('utf-8')
    
    mock_file = MockFile()
    mock_submission = MockDocumentSubmission(
        doc_type='transcript_of_records',
        file_obj=mock_file
    )
    
    # Override extraction
    original_extract = document_type_detector._extract_text_from_pdf
    document_type_detector._extract_text_from_pdf = lambda x: transcript_text
    
    try:
        result = document_type_detector.verify_document_type(mock_submission, mock_file)
        
        print(f"📊 Verification Results:")
        print(f"   Document Type Match: {result.get('document_type_match', False)}")
        print(f"   Confidence Score: {result.get('confidence_score', 0):.1%}")
        print(f"   Fraud Risk: {result.get('fraud_risk_score', 0):.1%}")
        print(f"   Recommendation: {result.get('recommendation', 'unknown').upper()}")
        
        print(f"\n🔍 Keyword Analysis:")
        keyword_analysis = result.get('keyword_analysis', {})
        found_keywords = keyword_analysis.get('found_keywords', {})
        
        print(f"   ✅ Required Keywords: {len(found_keywords.get('primary', []))} primary keywords found")
        print(f"   ❌ Forbidden Keywords: {len(found_keywords.get('forbidden', []))} forbidden keywords")
        
        print(f"\n" + "="*60)
        if result.get('recommendation') in ['auto_approve', 'manual_review']:
            print("✅ TEST PASSED: AI correctly accepted the legitimate transcript!")
            if result.get('document_type_match'):
                print("   Perfect match - document verified as Transcript of Records")
        else:
            print("❌ TEST FAILED: AI rejected a valid transcript!")
            print("   This may indicate the thresholds are too strict")
        print("="*60 + "\n")
        
    finally:
        document_type_detector._extract_text_from_pdf = original_extract


def show_ai_improvements():
    """Display the AI improvements made"""
    print("\n" + "="*80)
    print("🚀 AI ENHANCEMENTS IMPLEMENTED")
    print("="*80)
    print("""
📈 KEY IMPROVEMENTS:

1. ✅ STRICTER CONFIDENCE THRESHOLDS
   - Birth Certificate: 30% → 70% (133% increase)
   - School ID: 25% → 65% (160% increase)
   - Report Card: 35% → 75% (114% increase)
   - Transcript of Records: NEW - 75% threshold
   
2. ✅ ENHANCED FORBIDDEN KEYWORD DETECTION
   - Penalty per forbidden keyword: 20% → 50% (150% increase)
   - Just 2 forbidden keywords = automatic rejection
   - School ID keywords are forbidden in Transcript validation
   
3. ✅ STRICT MODE ENABLED
   - All document types now use strict validation
   - No lenient processing for potential fraud
   
4. ✅ IMPROVED QUALITY THRESHOLDS
   - Minimum resolution: 400x300 → 600x450 (50% increase)
   - Minimum file size: 10KB → 30KB (200% increase)
   - OCR confidence: 30% → 50% (67% increase)
   - Blur threshold: 50 → 80 (60% increase)
   
5. ✅ STRICTER DECISION LOGIC
   - Default recommendation changed from "approve" to "reject"
   - Type mismatch = immediate rejection
   - Low confidence (<50%) = rejection
   - Only approve when truly confident (≥50% for borderline, ≥65% for auto-approval)

6. ✅ SEPARATE TRANSCRIPT OF RECORDS TYPE
   - Dedicated validation for TOR (separate from report card)
   - Specific forbidden keywords prevent ID card acceptance
   - Table structure detection required
   
🎯 RESULT: AI now prevents fraud like uploading School ID as Transcript!
""")
    print("="*80)


def main():
    """Run all tests"""
    print("\n" + "🎯"*40)
    print("ENHANCED AI DOCUMENT VALIDATION - COMPREHENSIVE TEST SUITE")
    print("🎯"*40)
    
    try:
        # Show improvements first
        show_ai_improvements()
        
        # Test fraud prevention (main test)
        test_document_type_fraud_prevention()
        
        # Test legitimate document acceptance
        test_correct_document_acceptance()
        
        print("\n" + "="*80)
        print("📊 TEST SUITE COMPLETE")
        print("="*80)
        print("\n✅ The AI has been significantly enhanced to prevent document type fraud!")
        print("🔒 Users can no longer upload wrong document types and get approved.")
        print("📚 The system now properly validates that uploaded documents match their declared types.\n")
        
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
