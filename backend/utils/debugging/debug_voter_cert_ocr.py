import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.voter_certificate_verification_service import get_voter_certificate_verification_service

def main():
    print("="*80)
    print("DEBUG: VOTER CERTIFICATE OCR TEXT")
    print("="*80)
    
    # Initialize service
    service = get_voter_certificate_verification_service()
    
    # Test file
    test_file = "media/documents/2025/11/IMG20251111053738.jpg"
    
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        return
    
    print(f"\n📄 Testing: {test_file}")
    
    # Extract OCR text
    ocr_result = service.extract_voter_certificate_text(test_file)
    
    if not ocr_result['success']:
        print("❌ OCR extraction failed")
        for error in ocr_result.get('errors', []):
            print(f"   Error: {error}")
        return
    
    print(f"\n✅ OCR Success!")
    print(f"📊 OCR Confidence: {ocr_result['ocr_confidence']*100:.1f}%")
    
    print(f"\n{'='*80}")
    print("FULL OCR TEXT:")
    print("="*80)
    print(ocr_result['raw_text'])
    print("="*80)
    
    print(f"\n{'='*80}")
    print("EXTRACTED FIELDS:")
    print("="*80)
    print(f"   Voter Name: {ocr_result.get('voter_name', 'NOT FOUND')}")
    print(f"   Registration Number: {ocr_result.get('registration_number', 'NOT FOUND')}")
    print(f"   Precinct Number: {ocr_result.get('precinct_number', 'NOT FOUND')}")
    print(f"   Address: {ocr_result.get('address', 'NOT FOUND')}")
    print(f"   Date of Birth: {ocr_result.get('date_of_birth', 'NOT FOUND')}")
    print(f"   Registration Date: {ocr_result.get('registration_date', 'NOT FOUND')}")
    
    # Save to file for easier analysis
    with open('voter_cert_ocr_output.txt', 'w', encoding='utf-8') as f:
        f.write(ocr_result['raw_text'])
    
    print(f"\n✅ Full OCR text saved to: voter_cert_ocr_output.txt")

if __name__ == "__main__":
    main()
