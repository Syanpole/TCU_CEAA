import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.birth_certificate_verification_service import get_birth_certificate_verification_service

def main():
    print("="*80)
    print("DEBUG: BIRTH CERTIFICATE OCR TEXT")
    print("="*80)
    
    # Initialize service
    service = get_birth_certificate_verification_service()
    
    # Test file
    test_file = "media/documents/2025/11/FELICIANO- BIRTH CERTIFICATE.jpg"
    
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        return
    
    print(f"\n📄 Testing: {test_file}")
    
    # Extract OCR text
    ocr_result = service._advanced_ocr_extraction(test_file)
    
    if not ocr_result['success']:
        print("❌ OCR extraction failed")
        return
    
    print(f"\n✅ OCR Method: {ocr_result['ocr_method']}")
    print(f"✅ OCR Confidence: {ocr_result['ocr_confidence']*100:.1f}%")
    print(f"\n{'='*80}")
    print("FULL OCR TEXT:")
    print("="*80)
    print(ocr_result['raw_text'])
    print("="*80)
    
    # Save to file for easier analysis
    with open('birth_cert_ocr_output.txt', 'w', encoding='utf-8') as f:
        f.write(ocr_result['raw_text'])
    
    print("\n✅ Full OCR text saved to: birth_cert_ocr_output.txt")

if __name__ == "__main__":
    main()
