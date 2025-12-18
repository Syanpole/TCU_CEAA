"""
Test COE subject extraction logic with TCU format
"""
import re

# Sample TCU COE text (from user's actual document)
sample_text = """
1127 IT 102 Social Media And Presentation
1125 ELEC 5 System Fundamentals
1123 THS 102 CS Thesis Writing 2
1237 SE 101 Software Engineering 1
1124 ELEC 4A Graphics And Visual Computing
1126 HCI 102 Technopreneurship/E-Commerce
"""

print("Testing COE Subject Extraction")
print("=" * 60)

lines = [line.strip() for line in sample_text.split('\n') if line.strip()]

subjects = []
for i, line in enumerate(lines):
    # TCU COE format regex
    match = re.search(r'^\s*(\d{4})\s+([A-Z]{2,6})\s+(\d{1,3}[A-Z]?)\s+(.*?)(?:\s+\d+\.?\d*\s+.*)?$', line)
    
    if match:
        prefix = match.group(1).strip()
        code_letters = match.group(2).strip()
        code_numbers = match.group(3).strip()
        description = match.group(4).strip()
        
        subject_code = f"{code_letters} {code_numbers}"
        
        # Clean subject name
        subject_name = re.sub(r'\s+\d+\.?\d*\s+.*$', '', description).strip()
        subject_name = re.sub(r'\s+\d+-\d+\s+(am|pm).*$', '', subject_name).strip()
        subject_name = re.sub(r'\s+[A-Z]\s+\d+$', '', subject_name).strip()
        
        subjects.append({
            'code': subject_code,
            'name': subject_name
        })
        
        print(f"✓ Extracted: {subject_code} - {subject_name}")

print("\n" + "=" * 60)
print(f"Total subjects extracted: {len(subjects)}")
print("\nSubjects list:")
for s in subjects:
    print(f"  - {s['code']}: {s['name']}")

expected = ['IT 102', 'ELEC 5', 'THS 102', 'SE 101', 'ELEC 4A', 'HCI 102']
extracted = [s['code'] for s in subjects]

print("\n" + "=" * 60)
print(f"Expected: {expected}")
print(f"Extracted: {extracted}")
print(f"Match: {expected == extracted}")
