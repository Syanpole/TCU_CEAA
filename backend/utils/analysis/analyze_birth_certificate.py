import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.voter_certificate_verification_service import get_voter_certificate_verification_service

print("=" * 80)
print("BIRTH CERTIFICATE - ADVANCED OCR ANALYSIS")
print("=" * 80)

# Get the service (it has advanced OCR capabilities)
service = get_voter_certificate_verification_service()

# Check service status
status = service.get_verification_status()
print(f"\n📊 OCR Service Status:")
print(f"   OCR Available: {status.get('ocr_available', False)}")
print(f"   Advanced OCR: {status.get('advanced_ocr_enabled', False)}")
print(f"   OCR Method: {status.get('ocr_method', 'Unknown')}")

# Path to birth certificate
image_path = "media/documents/2025/11/BirthCertificate-PSA_OnuoIrB.jpg"

print(f"\n📄 Analyzing: {image_path}")

# Use advanced OCR extraction
print("\n" + "=" * 80)
print("RUNNING ADVANCED OCR EXTRACTION")
print("=" * 80)

result = service._advanced_ocr_extraction(image_path)

print(f"\n✅ OCR Completed!")
print(f"📊 OCR Confidence: {result.get('ocr_confidence', 0)*100:.2f}%")
print(f"🔧 OCR Method: {result.get('ocr_method', 'Unknown')}")

print("\n" + "=" * 80)
print("EXTRACTED TEXT (Full)")
print("=" * 80)
print(result.get('raw_text', 'No text extracted'))

print("\n" + "=" * 80)
print("TEXT ANALYSIS")
print("=" * 80)

raw_text = result.get('raw_text', '')
lines = raw_text.split('\n')
print(f"\nTotal Lines: {len(lines)}")
print(f"Total Characters: {len(raw_text)}")

# Try to identify key sections
print("\n📋 Detected Keywords:")
keywords = [
    'BIRTH', 'CERTIFICATE', 'REPUBLIC', 'PHILIPPINES', 
    'PSA', 'NATIONAL', 'STATISTICS', 'OFFICE',
    'NAME', 'SEX', 'DATE', 'PLACE', 'MOTHER', 'FATHER',
    'REGISTRY', 'CIVIL', 'REGISTRAR'
]

for keyword in keywords:
    if keyword in raw_text.upper():
        print(f"   ✅ Found: {keyword}")

print("\n" + "=" * 80)
print("ATTEMPTING TO EXTRACT BIRTH CERTIFICATE FIELDS")
print("=" * 80)

import re

# Try to extract common birth certificate fields
fields = {}

# Child's name patterns
name_patterns = [
    r"(?:CHILD'S NAME|NAME OF CHILD|CHILD NAME)[\s:]*([A-Z\s,]+?)(?:\n|SEX|DATE)",
    r"(?:NAME)[\s:]*([A-Z][A-Z\s,]+?)(?:SEX|MALE|FEMALE)",
]

for pattern in name_patterns:
    match = re.search(pattern, raw_text.upper())
    if match:
        fields['child_name'] = match.group(1).strip()
        break

# Date of birth
dob_patterns = [
    r"(?:DATE OF BIRTH|BIRTH DATE|DATE)[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
    r"(?:BORN ON)[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
]

for pattern in dob_patterns:
    match = re.search(pattern, raw_text, re.IGNORECASE)
    if match:
        fields['date_of_birth'] = match.group(1).strip()
        break

# Sex
sex_patterns = [
    r"(?:SEX)[\s:]*([A-Z]+)",
    r"(?:MALE|FEMALE)",
]

for pattern in sex_patterns:
    match = re.search(pattern, raw_text.upper())
    if match:
        fields['sex'] = match.group(0).strip() if 'MALE' in match.group(0) or 'FEMALE' in match.group(0) else match.group(1).strip()
        break

# Place of birth
place_patterns = [
    r"(?:PLACE OF BIRTH|BIRTH PLACE)[\s:]*([A-Z][A-Z\s,]+?)(?:\n|MOTHER|FATHER)",
]

for pattern in place_patterns:
    match = re.search(pattern, raw_text.upper())
    if match:
        fields['place_of_birth'] = match.group(1).strip()
        break

# Mother's name
mother_patterns = [
    r"(?:MOTHER'S NAME|MOTHER NAME|NAME OF MOTHER)[\s:]*([A-Z][A-Z\s,]+?)(?:\n|FATHER)",
]

for pattern in mother_patterns:
    match = re.search(pattern, raw_text.upper())
    if match:
        fields['mother_name'] = match.group(1).strip()
        break

# Father's name
father_patterns = [
    r"(?:FATHER'S NAME|FATHER NAME|NAME OF FATHER)[\s:]*([A-Z][A-Z\s,]+?)(?:\n|DATE|PLACE)",
]

for pattern in father_patterns:
    match = re.search(pattern, raw_text.upper())
    if match:
        fields['father_name'] = match.group(1).strip()
        break

# Registry number
registry_patterns = [
    r"(?:REGISTRY|REG|CERTIFICATE)[\s#NO:]*(\d{4,}[-]?\d*)",
]

for pattern in registry_patterns:
    match = re.search(pattern, raw_text.upper())
    if match:
        fields['registry_number'] = match.group(1).strip()
        break

print("\n🔍 Extracted Fields:")
if fields:
    for field, value in fields.items():
        print(f"   {field.replace('_', ' ').title()}: {value}")
else:
    print("   ⚠️ No fields could be extracted with standard patterns")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
