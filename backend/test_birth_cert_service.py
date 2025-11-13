import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.birth_certificate_verification_service import get_birth_certificate_verification_service

print("=" * 80)
print("TESTING BIRTH CERTIFICATE VERIFICATION SERVICE")
print("=" * 80)

# Initialize service
service = get_birth_certificate_verification_service()

# Check service status
print("\n📊 Service Status:")
status = service.get_verification_status()
for key, value in status.items():
    print(f"   {key}: {value}")

# Test with Feliciano birth certificate
image_path = "media/documents/2025/11/FELICIANO- BIRTH CERTIFICATE.jpg"

print(f"\n📄 Testing with: {image_path}")
print(f"📁 File exists: {os.path.exists(image_path)}")

if os.path.exists(image_path):
    print("\n" + "=" * 80)
    print("RUNNING BIRTH CERTIFICATE VERIFICATION")
    print("=" * 80)
    
    result = service.verify_birth_certificate_document(image_path)
    
    print(f"\n✅ Verification Complete!")
    print(f"📊 Success: {result.get('success')}")
    print(f"📊 Is Valid: {result.get('is_valid')}")
    print(f"📊 Status: {result.get('status')}")
    print(f"📊 Confidence: {result.get('confidence', 0)*100:.2f}%")
    print(f"📊 Document Type Match: {result.get('document_type_match')}")
    
    print("\n" + "=" * 80)
    print("EXTRACTED FIELDS")
    print("=" * 80)
    
    fields = result.get('extracted_fields', {})
    if fields:
        for field_name, field_value in fields.items():
            print(f"   {field_name.replace('_', ' ').title()}: {field_value}")
    else:
        print("   (No fields extracted)")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = result.get('recommendations', [])
    if recommendations:
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print("   (No recommendations)")
    
    print("\n" + "=" * 80)
    print("ERRORS")
    print("=" * 80)
    
    errors = result.get('errors', [])
    if errors:
        for error in errors:
            print(f"   ❌ {error}")
    else:
        print("   ✅ No errors")
    
    print("\n" + "=" * 80)
    print("OCR TEXT SAMPLE (First 500 chars)")
    print("=" * 80)
    
    ocr_text = result.get('ocr_text', '')
    if ocr_text:
        print(f"   {ocr_text[:500]}...")
    else:
        print("   (No OCR text)")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
