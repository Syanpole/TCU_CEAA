"""
Test COE Subject Extraction
Test the subject extraction on the provided COE image
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.coe_verification_service import COEVerificationService

def test_coe_extraction():
    """Test subject extraction from COE image"""
    print("=" * 60)
    print("Testing COE Subject Extraction")
    print("=" * 60)
    
    # Path to the COE image (you'll need to save the image first)
    coe_image_path = input("Enter path to COE image (or press Enter to use default): ").strip()
    
    if not coe_image_path:
        # Try to find the image in common locations
        possible_paths = [
            r"D:\Python\TCU_CEAA\test_coe.jpg",
            r"D:\Python\TCU_CEAA\backend\media\test_coe.jpg",
            r"D:\Python\TCU_CEAA\coe_test.jpg",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                coe_image_path = path
                break
        
        if not coe_image_path:
            print("\n❌ No COE image found. Please provide the path to the COE image.")
            print("\nExpected subjects from the image:")
            print("1. IT 102 - Social Media And Presentation")
            print("2. ELEC 5 - System Fundamentals")
            print("3. THS 102 - CS Thesis Writing 2")
            print("4. ELEC 4A - Graphics And Visual Computing")
            print("5. HCI 102 - Technopreneurship/E-Commerce")
            return
    
    if not os.path.exists(coe_image_path):
        print(f"\n❌ File not found: {coe_image_path}")
        return
    
    print(f"\n📄 Testing COE: {coe_image_path}")
    print("-" * 60)
    
    # Create service instance
    service = COEVerificationService()
    
    # Extract subjects
    print("\n🔍 Extracting subjects...")
    result = service.extract_subject_list(coe_image_path)
    
    print("\n" + "=" * 60)
    print("EXTRACTION RESULTS")
    print("=" * 60)
    
    if result['success']:
        print(f"✅ Extraction successful!")
        print(f"\n📊 Found {result['subject_count']} subject(s)")
        print(f"🎯 Confidence: {result['confidence']}")
        
        if result['subjects']:
            print("\n📚 Extracted Subjects:")
            print("-" * 60)
            for i, subject in enumerate(result['subjects'], 1):
                print(f"{i}. {subject['subject_code']} - {subject['subject_name']}")
        else:
            print("\n⚠️ No subjects extracted")
    else:
        print(f"❌ Extraction failed")
        if result.get('errors'):
            print("\n🔴 Errors:")
            for error in result['errors']:
                print(f"  • {error}")
    
    # Show expected vs actual
    print("\n" + "=" * 60)
    print("VALIDATION CHECK")
    print("=" * 60)
    
    expected_subjects = [
        {"code": "IT 102", "name": "Social Media And Presentation"},
        {"code": "ELEC 5", "name": "System Fundamentals"},
        {"code": "THS 102", "name": "CS Thesis Writing 2"},
        {"code": "ELEC 4A", "name": "Graphics And Visual Computing"},
        {"code": "HCI 102", "name": "Technopreneurship/E-Commerce"},
    ]
    
    print(f"\n📋 Expected: {len(expected_subjects)} subjects")
    print(f"📋 Found: {result['subject_count']} subjects")
    
    if result['subjects']:
        print("\n🔍 Comparison:")
        extracted_codes = [s['subject_code'].upper().replace(' ', '') for s in result['subjects']]
        
        for expected in expected_subjects:
            expected_code = expected['code'].upper().replace(' ', '')
            if expected_code in extracted_codes:
                print(f"  ✅ {expected['code']} - Found")
            else:
                print(f"  ❌ {expected['code']} - Missing")
    
    # Show raw text if extraction failed
    if not result['success'] or result['subject_count'] == 0:
        print("\n" + "=" * 60)
        print("RAW TEXT EXTRACTION (for debugging)")
        print("=" * 60)
        
        try:
            text_result = service.extract_coe_text(coe_image_path)
            if text_result.get('text'):
                print("\n📝 Extracted Text:")
                print("-" * 60)
                print(text_result['text'][:1000])  # First 1000 chars
                print("-" * 60)
        except Exception as e:
            print(f"\n❌ Could not extract text: {e}")

if __name__ == "__main__":
    try:
        test_coe_extraction()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
