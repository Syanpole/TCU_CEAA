"""
COE Verification Service Test
==============================

Test the COE verification service with a sample document.

Usage:
    python test_coe_verification.py [path_to_coe_image]

Author: TCU CEAA Development Team
Date: November 11, 2025
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

from myapp.coe_verification_service import get_coe_verification_service


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"🎓 {title}")
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


def test_coe_verification(image_path: str = None):
    """Test COE verification service."""
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "🎓 COE VERIFICATION SERVICE TEST".center(78) + "║")
    print("║" + "Certificate of Enrollment Detection".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    # Initialize service
    print_header("Initializing COE Verification Service")
    service = get_coe_verification_service()
    status = service.get_verification_status()
    
    print_result("COE Detection Model", status['coe_detection'], status['coe_detection'])
    print_result("Model Path", status['model_path'], None)
    print_result("Fully Operational", status['fully_operational'], status['fully_operational'])
    
    if not status['fully_operational']:
        print("\n❌ Service not operational. Cannot proceed with test.")
        print("\n💡 Make sure the model file exists at:")
        print(f"   {status['model_path']}")
        return
    
    # Find test image
    if image_path:
        test_image = Path(image_path)
    else:
        # Look for sample COE in organized dataset
        test_image = Path(BASE_DIR) / 'COE_YOLO' / 'images' / 'test'
        if test_image.exists():
            images = list(test_image.glob('*.jpg')) + list(test_image.glob('*.png'))
            if images:
                test_image = images[0]
            else:
                print("\n❌ No test images found in COE_YOLO/images/test/")
                return
        else:
            print("\n❌ Test image directory not found")
            return
    
    if not test_image.exists():
        print(f"\n❌ Test image not found: {test_image}")
        return
    
    print_result("Test Image", test_image.name, True)
    
    # Run verification
    print_header("Running COE Verification")
    print(f"📷 Analyzing: {test_image.name}")
    
    result = service.verify_coe_document(str(test_image), confidence_threshold=0.5)
    
    # Display results
    print("\n📊 Verification Results:")
    print_result("Success", result['success'], result['success'])
    print_result("Status", result['status'], result['is_valid'])
    print_result("Valid", result['is_valid'], result['is_valid'])
    print_result("Confidence", f"{result['confidence']:.2%}", result['confidence'] >= 0.6)
    
    # Show detected elements
    print("\n🔍 Detected Elements:")
    detected_elements = result.get('detected_elements', {})
    for element_name, data in detected_elements.items():
        if data.get('present'):
            print_result(
                element_name.replace('_', ' ').title(),
                f"{data.get('count', 0)} instance(s), {data.get('confidence', 0):.2%} confidence",
                True
            )
    
    # Show validation checks
    print("\n✅ Validation Checks:")
    checks = result.get('validation_checks', {})
    for check_name, passed in checks.items():
        print_result(
            check_name.replace('_', ' ').title(),
            "PASS" if passed else "FAIL",
            passed
        )
    
    print_result(
        "Checks Passed",
        f"{sum(1 for v in checks.values() if v)}/{len(checks)}",
        None
    )
    
    # Show detections details
    print("\n📋 Detection Details:")
    detections = result.get('detections', [])
    print(f"   Total Detections: {len(detections)}")
    for i, detection in enumerate(detections, 1):
        class_name = detection.get('class_name', 'Unknown')
        confidence = detection.get('confidence', 0)
        print(f"   {i}. {class_name}: {confidence:.2%}")
    
    # Show recommendations
    if result.get('recommendations'):
        print("\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
    
    # Show errors
    if result.get('errors'):
        print("\n❌ Errors:")
        for error in result['errors']:
            print(f"   • {error}")
    
    # Summary
    print_header("Test Summary")
    
    if result['success'] and result['is_valid']:
        print("   🎉 COE VERIFICATION SUCCESSFUL!")
        print(f"   ✅ Document is a valid Certificate of Enrollment")
        print(f"   📊 Confidence: {result['confidence']:.1%}")
    elif result['success'] and result['status'] == 'QUESTIONABLE':
        print("   ⚠️  COE VERIFICATION QUESTIONABLE")
        print(f"   📊 Confidence: {result['confidence']:.1%}")
        print("   💡 Manual review recommended")
    elif result['success']:
        print("   ❌ COE VERIFICATION FAILED")
        print(f"   📊 Confidence: {result['confidence']:.1%}")
        print("   ⚠️  Document may not be a valid COE")
    else:
        print("   ❌ VERIFICATION ERROR")
        print("   Check errors above")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        test_coe_verification(image_path)
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
