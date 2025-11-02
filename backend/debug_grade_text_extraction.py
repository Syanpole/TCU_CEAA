"""
Debug: Check what text is being extracted from grade sheet
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from PIL import Image
import easyocr
import numpy as np

print("=" * 80)
print("🔍 GRADE SHEET TEXT EXTRACTION DEBUG")
print("=" * 80)
print()

grade = GradeSubmission.objects.latest('id')

print(f"Grade ID: {grade.id}")
print(f"Student: {grade.student.first_name} {grade.student.last_name}")
print(f"File: {grade.grade_sheet.name}")
print(f"File path: {grade.grade_sheet.path}")
print()

# Load image
img = Image.open(grade.grade_sheet.path)
print(f"Image size: {img.width}x{img.height}")
print(f"Image mode: {img.mode}")
print()

# Convert to array
img_array = np.array(img)
print(f"Array shape: {img_array.shape}")
print()

# Initialize EasyOCR
print("Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=False)
print("✅ EasyOCR ready")
print()

# Extract text
print("Extracting text... (this may take 5-10 seconds)")
results = reader.readtext(img_array)
print(f"✅ Extraction complete! Found {len(results)} text regions")
print()

if results:
    print("EXTRACTED TEXT:")
    print("-" * 80)
    for i, (bbox, text, conf) in enumerate(results, 1):
        print(f"{i}. '{text}' (confidence: {conf:.2%})")
    print()
    print("-" * 80)
    print()
    
    # Full text
    full_text = ' '.join([text for (bbox, text, conf) in results])
    print("FULL COMBINED TEXT:")
    print(full_text)
    print()
    print(f"Total characters: {len(full_text)}")
    print()
    
    # Check for student name
    student_name = f"{grade.student.first_name} {grade.student.last_name}".lower()
    print(f"Looking for: '{student_name}'")
    
    if student_name in full_text.lower():
        print("✅ Student name FOUND in text!")
    else:
        print("❌ Student name NOT FOUND in text")
        print()
        print("Checking individual parts:")
        if grade.student.first_name.lower() in full_text.lower():
            print(f"  ✅ First name '{grade.student.first_name}' found")
        else:
            print(f"  ❌ First name '{grade.student.first_name}' NOT found")
        
        if grade.student.last_name.lower() in full_text.lower():
            print(f"  ✅ Last name '{grade.student.last_name}' found")
        else:
            print(f"  ❌ Last name '{grade.student.last_name}' NOT found")
else:
    print("❌ NO TEXT EXTRACTED!")
    print()
    print("Possible reasons:")
    print("  - Image is too low quality")
    print("  - Image is blank or corrupted")
    print("  - Text is too small or blurry")
    print("  - Image format not supported properly")

print()
print("=" * 80)
