"""
Test Voter Certificate Verification Service
============================================

This script tests the voter certificate verification service that includes:
- YOLO element detection
- Advanced OCR text extraction (AWS Textract)
- Intelligent field extraction

Author: TCU CEAA Development Team
Date: November 13, 2025
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.voter_certificate_verification_service import get_voter_certificate_verification_service
import json


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")


def print_section(text):
    """Print a formatted section."""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)


def test_voter_certificate_service(image_path):
    """Test the voter certificate verification service."""
    
    print_header("VOTER CERTIFICATE VERIFICATION TEST")
    
    print(f"📄 Testing voter certificate: {image_path}\n")
    
    # Initialize service
    print_section("Initializing Service")
    service = get_voter_certificate_verification_service()
    
    # Check service status
    status = service.get_verification_status()
    print(f"   ✅ Voter Certificate Detection: {status['voter_certificate_detection']}")
    print(f"   ✅ OCR Available: {status['ocr_available']}")
    print(f"   ✅ Advanced OCR: {status['advanced_ocr_enabled']}")
    print(f"   ✅ OCR Method: {status['ocr_method']}")
    print(f"   📊 Model Path: {status['model_path']}")
    print(f"   ✅ Fully Operational: {status['fully_operational']}")
    
    if not status['fully_operational']:
        print("\n   ⚠️ Service is not fully operational!")
        if not status['voter_certificate_detection']:
            print("   ❌ YOLO model not loaded")
        if not status['ocr_available']:
            print("   ❌ OCR not available")
        return
    
    # Run verification
    print_section("Running Voter Certificate Verification")
    print(f"   🔍 Analyzing document...")
    
    result = service.verify_voter_certificate_document(
        image_path=image_path,
        confidence_threshold=0.5,
        include_ocr=True
    )
    
    if not result['success']:
        print("\n   ❌ Verification failed!")
        print(f"   Errors: {', '.join(result['errors'])}")
        return
    
    # Display YOLO detection results
    print_section("YOLO Element Detection Results")
    print(f"   📊 Status: {result['status']}")
    print(f"   📊 Overall Confidence: {result['confidence']:.2%}")
    print(f"   📊 Elements Detected: {len(result['detections'])}")
    
    print("\n   🔍 Detected Voter Certificate Elements:")
    detected = result['detected_elements']
    for element, data in detected.items():
        element_name = element.replace('_', ' ').title()
        status_icon = "✅" if data['present'] else "❌"
        if data['present']:
            print(f"   {status_icon} {element_name}: Present (Confidence: {data['confidence']:.2%}, Count: {data['count']})")
        else:
            print(f"   {status_icon} {element_name}: Not detected")
    
    # Display validation checks
    print_section("Validation Checks")
    checks = result['validation_checks']
    for check_name, passed in checks.items():
        check_label = check_name.replace('_', ' ').title()
        status_icon = "✅" if passed else "❌"
        print(f"   {status_icon} {check_label}: {'PASS' if passed else 'FAIL'}")
    
    # Display OCR results if available
    if result.get('ocr_data') and result['ocr_data'].get('success'):
        print_section("OCR Text Extraction Results")
        ocr_data = result['ocr_data']
        
        print(f"   📊 OCR Confidence: {ocr_data['ocr_confidence']:.2%}")
        print(f"   📊 Extraction Method: {result.get('ocr_data', {}).get('method', 'Unknown')}")
        
        # Display extracted fields
        extracted_info = result.get('extracted_info', {})
        if any(extracted_info.values()):
            print("\n   📋 Extracted Voter Information:")
            
            if extracted_info.get('voter_name'):
                print(f"   👤 Voter Name: {extracted_info['voter_name']}")
            else:
                print(f"   ❌ Voter Name: Not extracted")
            
            if extracted_info.get('registration_number'):
                print(f"   🆔 Registration Number: {extracted_info['registration_number']}")
            else:
                print(f"   ❌ Registration Number: Not extracted")
            
            if extracted_info.get('precinct_number'):
                print(f"   🏛️ Precinct Number: {extracted_info['precinct_number']}")
            else:
                print(f"   ❌ Precinct Number: Not extracted")
            
            if extracted_info.get('address'):
                print(f"   🏠 Address: {extracted_info['address']}")
            else:
                print(f"   ❌ Address: Not extracted")
            
            if extracted_info.get('date_of_birth'):
                print(f"   📅 Date of Birth: {extracted_info['date_of_birth']}")
            else:
                print(f"   ❌ Date of Birth: Not extracted")
            
            if extracted_info.get('registration_date'):
                print(f"   📅 Registration Date: {extracted_info['registration_date']}")
            else:
                print(f"   ❌ Registration Date: Not extracted")
        
        # Display raw text (truncated)
        if ocr_data.get('raw_text'):
            print("\n   📝 Raw OCR Text (First 500 chars):")
            raw_text = ocr_data['raw_text']
            print(f"   {raw_text[:500]}...")
    
    # Display recommendations
    if result.get('recommendations'):
        print_section("Recommendations")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Final summary
    print_section("Final Verification Summary")
    
    validity_icon = "✅" if result['is_valid'] else "❌"
    print(f"\n   {validity_icon} Document Validity: {'VALID' if result['is_valid'] else 'INVALID'}")
    print(f"   📊 Status: {result['status']}")
    print(f"   📊 Confidence: {result['confidence']:.2%}")
    
    if result['is_valid']:
        print(f"\n   ✅ Document is a valid Voter's Certificate")
    else:
        print(f"\n   ❌ Document failed validation")
    
    # Export results to JSON
    print_section("Exporting Results")
    output_file = 'voter_certificate_verification_results.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"   ✅ Results exported to: {output_file}")
    
    print_header("TEST COMPLETE")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_voter_certificate_service.py <path_to_voter_certificate_image>")
        print("\nExample:")
        print('  python test_voter_certificate_service.py "media/documents/2025/11/Voter_Certificate.jpg"')
        print('  python test_voter_certificate_service.py "path/to/your/voters_cert.jpg"')
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Error: File not found: {image_path}")
        sys.exit(1)
    
    test_voter_certificate_service(image_path)
