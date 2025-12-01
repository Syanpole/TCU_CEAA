import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.birth_certificate_verification_service import get_birth_certificate_verification_service

def main():
    print("="*80)
    print("TESTING BIRTH CERTIFICATE WITH APPLICATION DATA COMPARISON")
    print("="*80)
    
    # Initialize service
    service = get_birth_certificate_verification_service()
    
    # Test file
    test_file = "media/documents/2025/11/FELICIANO- BIRTH CERTIFICATE.jpg"
    
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        return
    
    print(f"\n📄 Testing: {test_file}")
    
    # Simulate user's full application data
    user_application_data = {
        'first_name': 'Sean Paul',
        'middle_name': 'Cuevas',
        'last_name': 'Feliciano',
        'date_of_birth': date(2004, 5, 19),  # May 19, 2004
        'sex': 'Male',
        'place_of_birth': 'Philippine General Hospital, Manila',
        'mother_name': 'Jocelyn Cuevas Recta',
        'father_name': 'Florido Cuevas Feliciano',
    }
    
    print("\n📋 User Application Data:")
    print(f"   Name: {user_application_data['first_name']} {user_application_data['middle_name']} {user_application_data['last_name']}")
    print(f"   DOB: {user_application_data['date_of_birth']}")
    print(f"   Sex: {user_application_data['sex']}")
    print(f"   Place: {user_application_data['place_of_birth']}")
    print(f"   Mother: {user_application_data['mother_name']}")
    print(f"   Father: {user_application_data['father_name']}")
    
    print("\n" + "="*80)
    print("RUNNING BIRTH CERTIFICATE VERIFICATION WITH COMPARISON")
    print("="*80)
    
    # Verify with application data
    result = service.verify_birth_certificate_document(test_file, user_application_data=user_application_data)
    
    if not result['success']:
        print("\n❌ Verification failed!")
        for error in result['errors']:
            print(f"   Error: {error}")
        return
    
    print(f"\n✅ Verification Complete!")
    print(f"📊 Success: {result['success']}")
    print(f"📊 Is Valid: {result['is_valid']}")
    print(f"📊 Status: {result['status']}")
    print(f"📊 Confidence: {result['confidence']*100:.2f}%")
    print(f"📊 Document Type Match: {result['document_type_match']}")
    
    # Show extracted fields
    print("\n" + "="*80)
    print("EXTRACTED FIELDS")
    print("="*80)
    extracted_fields = result.get('extracted_fields', {})
    if extracted_fields:
        for field_name, field_value in extracted_fields.items():
            print(f"   {field_name.replace('_', ' ').title()}: {field_value}")
    else:
        print("   No fields extracted")
    
    # Show field matches
    print("\n" + "="*80)
    print("FIELD COMPARISON WITH APPLICATION")
    print("="*80)
    field_matches = result.get('field_matches', {})
    if field_matches:
        for field_name, match_info in field_matches.items():
            match_icon = "✅" if match_info.get('match') else "❌"
            score = match_info.get('score', 0.0) * 100
            extracted = match_info.get('extracted', 'N/A')
            application = match_info.get('application', 'N/A')
            
            print(f"\n{match_icon} {field_name.replace('_', ' ').title()}: {score:.1f}% match")
            print(f"   Extracted:   {extracted}")
            print(f"   Application: {application}")
    else:
        print("   No field comparisons performed")
    
    # Show recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    for recommendation in result.get('recommendations', []):
        print(f"   {recommendation}")
    
    # Show errors
    print("\n" + "="*80)
    print("ERRORS")
    print("="*80)
    if result.get('errors'):
        for error in result['errors']:
            print(f"   ❌ {error}")
    else:
        print("   ✅ No errors")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
