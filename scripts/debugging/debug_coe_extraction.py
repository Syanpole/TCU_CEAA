"""
Debug COE Text Extraction - Show raw OCR output
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.coe_verification_service import COEVerificationService
import re

# Path to the COE we know exists
coe_path = r"D:\Python\TCU_CEAA\backend\media\documents\2025\11\FELICIANO-_CERTIFICATE_OF_ENROLLMENT.jpg"

print("=" * 80)
print("COE TEXT EXTRACTION DEBUG")
print("=" * 80)
print(f"\n📄 File: {coe_path}")
print(f"📊 Exists: {os.path.exists(coe_path)}")

if not os.path.exists(coe_path):
    print("\n❌ File not found!")
    sys.exit(1)

service = COEVerificationService()

# Use the proper extract_coe_text method
print("\n" + "=" * 80)
print("EXTRACTING COE TEXT")
print("=" * 80)

try:
    extraction_result = service.extract_coe_text(coe_path)
    
    if extraction_result['success']:
        result = extraction_result['raw_text']
        print(f"\n✅ OCR returned {len(result)} characters")
        print(f"📊 Confidence: {extraction_result['ocr_confidence']:.2%}")
        print(f"🔧 Method: {extraction_result.get('method', 'unknown')}")
        print(f"\n📚 Subjects found: {extraction_result['subject_count']}")
        
        if extraction_result['subjects']:
            print("\n✨ Extracted subjects:")
            for i, subj in enumerate(extraction_result['subjects'], 1):
                print(f"   {i}. {subj['subject_code']} - {subj['subject_name']}")
        
        print("\n📝 Full extracted text:")
        print("-" * 80)
        print(result)
        print("-" * 80)
    else:
        print(f"\n❌ Extraction failed")
        print(f"🔴 Errors: {extraction_result.get('errors', [])}")
        result = None
        
except Exception as e:
    print(f"\n❌ Extraction failed: {e}")
    import traceback
    traceback.print_exc()
    result = None

# Test regex patterns on the extracted text
if result:
    print("\n" + "=" * 80)
    print("TESTING REGEX PATTERNS")
    print("=" * 80)
    
    patterns = [
        (r'([A-Z]{2,4}\s*\d{1,3}[A-Z]?)\s*[-–—]\s*([^\n]{3,50})', "Pattern 1: CODE - NAME"),
        (r'([A-Z]{2,4}\s+\d{1,3}[A-Z]?)\s+([A-Z][a-zA-Z\s/\-]{3,50})', "Pattern 2: CODE NAME"),
        (r'([A-Z]{1,2}\s*[A-Z]{1,2}\s*\d{1,3}[A-Z]?)\s+([A-Za-z][A-Za-z\s/\-]{3,50})', "Pattern 3: CO DE NAME"),
    ]
    
    for pattern, description in patterns:
        print(f"\n🔍 Testing: {description}")
        print(f"   Pattern: {pattern}")
        matches = re.findall(pattern, result, re.IGNORECASE)
        print(f"   Matches found: {len(matches)}")
        
        if matches:
            for i, match in enumerate(matches[:10], 1):  # Show first 10
                print(f"   {i}. Code: '{match[0]}' | Name: '{match[1]}'")
        else:
            print("   ❌ No matches")
    
    # Try to find any course-like patterns
    print("\n" + "=" * 80)
    print("SEARCHING FOR COURSE-LIKE PATTERNS")
    print("=" * 80)
    
    # Look for lines with course codes
    lines = result.split('\n')
    print(f"\n📋 Total lines: {len(lines)}")
    print("\n🔍 Lines containing potential course codes:")
    
    course_pattern = r'[A-Z]{2,4}\s*\d{1,3}'
    for i, line in enumerate(lines):
        if re.search(course_pattern, line) and len(line.strip()) > 5:
            print(f"   Line {i}: {line.strip()[:100]}")

print("\n" + "=" * 80)
print("Expected subjects from image:")
print("1. IT 102 - Social Media And Presentation")
print("2. ELEC 5 - System Fundamentals")  
print("3. THS 102 - CS Thesis Writing 2")
print("4. ELEC 4A - Graphics And Visual Computing")
print("5. HCI 102 - Technopreneurship/E-Commerce")
print("=" * 80)
