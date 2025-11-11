"""
Test COE Verification Service with OCR Integration
===================================================

This script tests the enhanced COE verification service that includes:
- YOLO element detection
- Advanced OCR text extraction
- Intelligent text interpretation

Author: TCU CEAA Development Team
Date: November 11, 2025
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.coe_verification_service import get_coe_verification_service
import json


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"🎓 {text}")
    print("="*80 + "\n")


def print_section(text):
    """Print a formatted section."""
    print(f"\n{'─'*80}")
    print(f"📋 {text}")
    print('─'*80)


def test_coe_service(image_path):
    """
    Test the COE verification service with OCR.
    
    Args:
        image_path: Path to the COE image to test
    """
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "    🎓 COE VERIFICATION SERVICE TEST (WITH OCR)".center(78) + "║")
    print("║" + "    Enhanced COE Analysis with Text Extraction".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"\n❌ Error: Image file not found: {image_path}")
        return
    
    print(f"\n   📷 Image: {os.path.basename(image_path)}")
    print(f"   📁 Path: {image_path}")
    
    # Get service instance
    print_header("Phase 1: Service Initialization")
    service = get_coe_verification_service()
    status = service.get_verification_status()
    
    print("   🔍 Service Status:")
    print(f"      YOLO Detection: {'✅ Available' if status['coe_detection'] else '❌ Not Available'}")
    print(f"      OCR Extraction: {'✅ Available' if status['ocr_available'] else '❌ Not Available'}")
    print(f"      Model Path: {status['model_path']}")
    print(f"      Fully Operational: {'✅ Yes' if status['fully_operational'] else '❌ No'}")
    
    if not status['fully_operational']:
        print("\n   ⚠️ Warning: Service not fully operational. Some features may not work.")
        return
    
    # Run verification with OCR
    print_header("Phase 2: COE Verification with OCR")
    print("   🔍 Running comprehensive COE verification...")
    
    result = service.verify_coe_document(
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
    
    print("\n   🔍 Detected COE Elements:")
    detected = result['detected_elements']
    for element, data in detected.items():
        element_name = element.replace('_', ' ').title()
        status_icon = "✅" if data['present'] else "❌"
        if data['present']:
            print(f"      {status_icon} {element_name}: {data['count']} instance(s) - Confidence: {data['confidence']:.2%}")
        else:
            print(f"      {status_icon} {element_name}: Not detected")
    
    # Display OCR extraction results
    if result.get('ocr_data'):
        print_section("OCR Text Extraction Results")
        ocr_data = result['ocr_data']
        
        if ocr_data['success']:
            print(f"   ✅ OCR Extraction: Success")
            print(f"   📊 OCR Confidence: {ocr_data['ocr_confidence']:.2%}")
            print(f"   📊 Text Length: {len(ocr_data['raw_text'])} characters")
            
            # Display interpreted fields
            print("\n   🧠 AI-Interpreted Fields:")
            extracted = result['extracted_info']
            
            field_display = {
                'student_name': 'Student Name',
                'student_id': 'Student ID',
                'program': 'Program',
                'year_level': 'Year Level',
                'semester': 'Semester',
                'enrollment_date': 'Enrollment Date'
            }
            
            for field_key, field_label in field_display.items():
                value = extracted.get(field_key)
                if value:
                    # Get interpretation details
                    interpreted = ocr_data['interpreted_fields'].get(field_key, {})
                    confidence = interpreted.get('confidence', 0) * 100
                    reasoning = interpreted.get('reasoning', 'N/A')
                    
                    print(f"      ✨ {field_label}: {value}")
                    print(f"         Confidence: {confidence:.0f}% | {reasoning}")
                else:
                    print(f"      ❌ {field_label}: Not extracted")
            
            # Display raw text preview
            print("\n   📄 Raw OCR Text Preview (first 500 chars):")
            print("   " + "─"*76)
            preview = ocr_data['raw_text'][:500].replace('\n', '\n   ')
            print(f"   {preview}")
            print("   " + "─"*76)
        else:
            print("   ❌ OCR Extraction failed")
            print(f"   Errors: {', '.join(ocr_data.get('errors', []))}")
    
    # Display validation checks
    print_section("Validation Checks")
    checks = result['validation_checks']
    for check_name, passed in checks.items():
        check_label = check_name.replace('_', ' ').title()
        icon = "✅" if passed else "❌"
        print(f"   {icon} {check_label}")
    
    # Display final status
    print_section("Final Verification Status")
    print(f"   📊 Status: {result['status']}")
    print(f"   📊 Is Valid: {'✅ Yes' if result['is_valid'] else '❌ No'}")
    print(f"   📊 Overall Confidence: {result['confidence']:.2%}")
    
    if result['recommendations']:
        print("\n   💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"      • {rec}")
    
    print_header("Test Complete")
    print("   ✅ COE verification with OCR completed successfully")
    print("   📊 Results show comprehensive document analysis with text extraction")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_coe_service_with_ocr.py <path_to_coe_image>")
        print("\nExample:")
        print('  python test_coe_service_with_ocr.py "media/documents/2025/11/Certificate_of_Enrollment.jpg"')
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_coe_service(image_path)
