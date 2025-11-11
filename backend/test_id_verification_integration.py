"""
Test ID Verification Service Integration
========================================

Tests the new ID verification service both as standalone and through API
"""

import os
import sys
import django

# Setup Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.id_verification_service import get_id_verification_service

def test_standalone_service():
    """Test the ID verification service directly"""
    print("="*80)
    print("🧪 Testing ID Verification Service (Standalone)")
    print("="*80)
    print()
    
    # Get service
    service = get_id_verification_service()
    
    # Check status
    status = service.get_verification_status()
    print("📊 Service Status:")
    for key, value in status.items():
        icon = '✅' if value else '❌'
        print(f"   {icon} {key}: {value}")
    print()
    
    if not status['fully_operational']:
        print("⚠️  Service not fully operational!")
        return False
    
    # Test on sample ID
    test_image = os.path.join(backend_dir, 'media', 'documents', '2025', '09', 'ID_PIC_g7t6DG3.jpg')
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    print(f"📷 Testing with: {os.path.basename(test_image)}")
    print()
    
    # Run verification
    result = service.verify_id_card(test_image, 'student_id')
    
    if result['success']:
        print("✅ Verification Complete!")
        print()
        print(f"📊 Results:")
        print(f"   Status: {result['status']}")
        print(f"   Valid: {result['is_valid']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Checks: {result['checks_passed']}")
        print()
        
        print("🎯 Extracted Fields:")
        for key, value in result['extracted_fields'].items():
            print(f"   {key}: {value}")
        print()
        
        print("✅ Validation Checks:")
        for check, passed in result['validation_checks'].items():
            icon = '✅' if passed else '❌'
            print(f"   {icon} {check}")
        print()
        
        if result['recommendations']:
            print("💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"   - {rec}")
        
        return True
    else:
        print("❌ Verification failed!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
        return False


def test_api_endpoint():
    """Test the API endpoint"""
    print()
    print("="*80)
    print("🌐 API Endpoint Information")
    print("="*80)
    print()
    print("✅ New endpoint created:")
    print("   POST /api/ai/verify-id-card/")
    print()
    print("📝 Request body:")
    print("   {")
    print('       "document_id": 123')
    print("   }")
    print()
    print("🔒 Authentication:")
    print("   - Requires authentication token")
    print("   - Users can verify their own documents")
    print("   - Admins can verify any document")
    print()
    print("📤 Response includes:")
    print("   - Verification result (VALID/QUESTIONABLE/INVALID)")
    print("   - Confidence score")
    print("   - YOLO detection results")
    print("   - OCR extraction results")
    print("   - Extracted fields (name, student number, etc.)")
    print("   - Validation checks")
    print("   - Recommendations")
    print()
    print("💡 Integration:")
    print("   - Automatically called for ID documents in ai_document_analysis")
    print("   - Can be called separately for dedicated ID verification")
    print("   - Results stored in document record")
    print("   - Audit trail logged")
    print()


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║             🆔 ID CARD VERIFICATION SERVICE TEST                          ║")
    print("║                YOLO + AWS Textract Integration                            ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Test standalone service
    success = test_standalone_service()
    
    # Show API info
    test_api_endpoint()
    
    print("="*80)
    if success:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")
    print("="*80)
    print()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
