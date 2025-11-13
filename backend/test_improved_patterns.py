import re

# Read the OCR text
with open('birth_cert_ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

text_upper = text.upper()

print("="*80)
print("TESTING IMPROVED REGEX PATTERNS")
print("="*80)

# Test Child's Name extraction
print("\n1. CHILD'S NAME EXTRACTION:")
print("-"*80)

# Based on observed structure:
# Line: 1. NAME
# Line: (First)
# Line: (Middle)
# Line: (LABILICIANO  <- This has (LAST) corrupted into part of name
# Line: SEAN PAUL <- First name
# Line: CUEVAS <- Middle name

child_name_patterns = [
    # Pattern 1: Extract the three name lines, including corrupted label line
    # Format seen: (LABILICIANO\nSEAN PAUL\nCUEVAS
    r"1\.\s*NAME[^\n]*\n[^\n]*\n[^\n]*\n\s*(.+?)\s*\n\s*([A-Z\s]+?)\s*\n\s*([A-Z]+)",
]

for i, pattern in enumerate(child_name_patterns, 1):
    match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
    if match:
        print(f"✅ Pattern {i} matched!")
        print(f"   Raw groups: {match.groups()}")
        name_parts = [g.strip() for g in match.groups() if g and g.strip()]
        
        # Try to clean the last name if it has label artifacts
        # Check if first part looks like a corrupted label + name (e.g., "(LABILICIANO")
        last_name = name_parts[0]
        
        # Remove opening parenthesis if present
        if last_name.startswith('('):
            last_name = last_name[1:]
            print(f"   Removed '(' prefix, now: {last_name}")
        
        # Check if it starts with common label remnants from "(LAST)"
        # Most likely patterns: "LAST*", "LA*" where * is start of actual name
        if last_name.startswith('LAST'):
            last_name = last_name[4:]  # Remove "LAST"
            print(f"   Removed 'LAST' prefix, now: {last_name}")
        elif last_name.startswith('LA') and len(last_name) > 4:
            # Only remove "LA" if there's a substantial name after
            # "LABILICIANO" -> "BILICIANO" (OCR error: F became B, so real name likely "FELICIANO")
            last_name = last_name[2:]  # Remove "LA"
            print(f"   Removed 'LA' prefix, now: {last_name}")
        
        name_parts[0] = last_name
        
        if len(name_parts) == 3:
            # Rearrange from Last, First, Middle to First Middle Last
            full_name = f"{name_parts[1]} {name_parts[2]} {name_parts[0]}"
            print(f"   Cleaned last name: {last_name}")
            print(f"   Full Name: {full_name}")
    else:
        print(f"❌ Pattern {i} did not match")

# Test Date of Birth extraction
print("\n2. DATE OF BIRTH EXTRACTION:")
print("-"*80)

# Based on observed structure:
# Line: 3. DATE OF BIRTH
# Line: 19 <- Day
# Line: May <- Month
# (Year 2004 appears earlier in the document)

dob_patterns = [
    # Pattern 1: Look for day and month right after "3. DATE OF BIRTH"
    r"3\.\s*DATE OF BIRTH\s*\n\s*(\d{1,2})\s*\n\s*(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)",
    # Pattern 2: Generic - find day and month near each other
    r"(\d{1,2})\s*\n\s*(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)",
]

# Also try to find the year separately
year_patterns = [
    r"REGISTRY NO\.\s*(\d{4})",  # Year often matches registry number
    r"\(YEAR\)\s*\n\s*(\d{4})",
    r"DATE OF BIRTH.*?(\d{4})",
]

year_found = None
for pattern in year_patterns:
    match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
    if match:
        year_found = match.group(1)
        print(f"✅ Year found: {year_found}")
        break

for i, pattern in enumerate(dob_patterns, 1):
    match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
    if match:
        print(f"✅ Date Pattern {i} matched!")
        print(f"   Groups: {match.groups()}")
        if year_found:
            dob = f"{match.group(1)} {match.group(2)} {year_found}"
            print(f"   Date of Birth: {dob}")
        else:
            dob = f"{match.group(1)} {match.group(2)}"
            print(f"   Date of Birth (partial): {dob}")
        break
    else:
        print(f"❌ Pattern {i} did not match")

# Test Sex extraction
print("\n3. SEX EXTRACTION:")
print("-"*80)

sex_patterns = [
    r"2\.\s*SEX.*?1\s*MALE",
    r"2\.\s*SEX.*?2\s*FEMALE",
    r"(?:2\.\s*)?SEX[:\s]*(MALE|FEMALE)",
]

for i, pattern in enumerate(sex_patterns, 1):
    match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
    if match:
        print(f"✅ Pattern {i} matched!")
        if "MALE" in match.group(0):
            print(f"   Sex: MALE")
        elif "FEMALE" in match.group(0):
            print(f"   Sex: FEMALE")
    else:
        print(f"❌ Pattern {i} did not match")

print("\n" + "="*80)
print("PATTERN TESTING COMPLETE")
print("="*80)
