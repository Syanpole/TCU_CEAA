import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.birth_certificate_verification_service import get_birth_certificate_verification_service

print("="*80)
print("TESTING: LLOYD KENNETH SALAMEDA BIRTH CERTIFICATE")
print("="*80)

# User's application data from the form
user_application_data = {
    'first_name': 'LLOYD KENNETH',
    'middle_name': 'SALAMEDA',
    'last_name': 'RAMOS',  # This is the issue - the birth cert shows SALAMEDA as last name
    'date_of_birth': 'January 28, 2001',  # From birth cert: (month) January (day) 28 (year) 2001
    'sex': 'MALE',
    'place_of_birth': 'PASAY CITY',  # From birth cert: Name of Hospital/Clinic/Institution: PASAY CITY
    'mother_name': 'MARIA GREGARIA VERGARA SALAMEDA',  # Maiden name from cert
    'father_name': 'ALBERT ROSAL RAMOS',  # Father's name - corrected
}

print("\n📋 User Application Data:")
print(f"   Full Name: {user_application_data['first_name']} {user_application_data.get('middle_name', '')} {user_application_data['last_name']}")
print(f"   Date of Birth: {user_application_data['date_of_birth']}")
print(f"   Sex: {user_application_data['sex']}")
print(f"   Place of Birth: {user_application_data['place_of_birth']}")
print(f"   Mother's Name: {user_application_data['mother_name']}")
print(f"   Father's Name: {user_application_data['father_name']}")

# Path to the birth certificate image
# You'll need to update this with the actual path
test_file = "media/documents/lloyd_birth_cert.jpg"  # Update this path

if not os.path.exists(test_file):
    print(f"\n❌ Test file not found: {test_file}")
    print("Please save the birth certificate image and update the path in this script.")
    print("\nExpected extraction from the document:")
    print("   Child Name: LLOYD KENNETH SALAMEDA (no RAMOS)")
    print("   DOB: January 28, 2001")
    print("   Sex: MALE")
    print("   Place: PASAY CITY")
    print("   Mother: MARIA GREGARIA VERGARA SALAMEDA")
    print("   Father: ALBERT ROSAL RAMOS")
    print("\n🔍 The system should:")
    print("   1. Extract father's name from birth cert")
    print("   2. Notice child name is LLOYD KENNETH SALAMEDA (partial match - missing RAMOS)")
    print("   3. Compare extracted father with application: ALBERT ROSAL RAMOS")
    print("   4. If father's name matches → APPROVE the document based on parent verification")
    exit(1)

print(f"\n📄 Testing: {test_file}")

# Initialize service
service = get_birth_certificate_verification_service()

# Run verification
print("\n" + "="*80)
print("RUNNING VERIFICATION WITH USER DATA COMPARISON")
print("="*80)

result = service.verify_birth_certificate_document(
    image_path=test_file,
    user_application_data=user_application_data
)

print(f"\n✅ Verification Complete!")
print(f"   Success: {result.get('success')}")
print(f"   Is Valid: {result.get('is_valid')}")
print(f"   Status: {result.get('status')}")
print(f"   Confidence: {result.get('confidence', 0)*100:.1f}%")

print("\n" + "="*80)
print("EXTRACTED FIELDS")
print("="*80)
for field, value in result.get('extracted_fields', {}).items():
    print(f"   {field}: {value}")

if result.get('field_matches'):
    print("\n" + "="*80)
    print("FIELD MATCHING RESULTS")
    print("="*80)
    for field, match_data in result.get('field_matches', {}).items():
        icon = "✓" if match_data.get('match') else "✗"
        score = match_data.get('score', 0) * 100
        extracted = match_data.get('extracted', 'N/A')
        application = match_data.get('application', 'N/A')
        print(f"   {icon} {field}: {score:.0f}%")
        print(f"      Extracted: '{extracted}'")
        print(f"      Application: '{application}'")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)
for rec in result.get('recommendations', []):
    print(rec)

print("\n" + "="*80)
print("TEST EXPECTATIONS")
print("="*80)
print("""
✅ WHAT SHOULD HAPPEN:
   1. Extract child name as: LLOYD KENNETH SALAMEDA
   2. Notice it doesn't exactly match: LLOYD KENNETH SALAMEDA RAMOS
   3. Calculate partial name match score (~70-80%)
   4. Extract father's name from birth certificate
   5. Compare with application father: ALBERT ROSAL RAMOS
   6. If father's name MATCHES ✓
   7. APPROVE document based on parent verification
   8. Status should be: VALID
   9. Recommendations should show father verification

❌ WHAT SHOULD NOT HAPPEN:
   - Reject due to missing "RAMOS" in child name
   - Ignore father's name match
   - Status should NOT be: INVALID
""")

if result.get('is_valid'):
    print("\n🎉 SUCCESS! Document approved with parent verification!")
else:
    print("\n⚠️ ISSUE: Document was rejected. Check the logic above.")
    
print("\n" + "="*80)
