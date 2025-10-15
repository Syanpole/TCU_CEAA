"""
Test Grade Verification with Autonomous AI - Detailed Analysis
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from myapp.ai_service import grade_analyzer

print("=" * 80)
print("🤖 AUTONOMOUS AI GRADE VERIFICATION - DETAILED TEST")
print("=" * 80)
print()

grades = GradeSubmission.objects.all().order_by('-id')

if not grades.exists():
    print("❌ No grade submissions found")
    sys.exit(1)

grade = grades.first()

print(f"Testing Grade Submission ID: {grade.id}")
print(f"Student: {grade.student.first_name} {grade.student.last_name}")
print(f"Username: {grade.student.username}")
print(f"Current Status: {grade.status}")
print(f"Grade Sheet: {grade.grade_sheet.name if grade.grade_sheet else 'No file'}")
print()
print("=" * 80)
print("RUNNING NAME VERIFICATION...")
print("=" * 80)
print()

try:
    result = grade_analyzer._verify_grade_sheet_ownership(grade)
    
    print("VERIFICATION RESULTS:")
    print("-" * 80)
    print(f"Name Match:          {result['name_match']}")
    print(f"Confidence:          {result['confidence']:.0%}")
    print(f"Expected Name:       {result['expected_name']}")
    print(f"Matched Name:        {result.get('matched_name', 'N/A')}")
    print(f"Verification Method: {result.get('verification_method', 'unknown')}")
    print()
    
    if result.get('found_names'):
        print(f"Found Names on Document:")
        for name in result['found_names'][:5]:
            print(f"  - {name.title()}")
        print()
    
    if result['name_match']:
        print("✅ STATUS: APPROVED")
        print(f"   Reason: Name verified with {result['confidence']:.0%} confidence")
    else:
        print("❌ STATUS: REJECTED")
        print(f"   Reason: {result.get('mismatch_reason', 'Unknown')}")
    
    print()
    print("-" * 80)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print()

# Check what OCR is available
print("OCR Availability:")
print()

try:
    import easyocr
    print(f"✅ EasyOCR (Autonomous AI): Installed")
    print(f"   Version: {easyocr.__version__ if hasattr(easyocr, '__version__') else 'Unknown'}")
    print(f"   Status: PRIMARY OCR METHOD")
except ImportError:
    print("❌ EasyOCR: Not installed")

print()

try:
    import pytesseract
    version = pytesseract.get_tesseract_version()
    print(f"✅ Tesseract OCR: Installed")
    print(f"   Version: {version}")
    print(f"   Status: FALLBACK METHOD")
except Exception:
    print("❌ Tesseract OCR: Not installed")
    print("   Status: Not available (fallback)")

print()
print("=" * 80)
print("SECURITY ANALYSIS")
print("=" * 80)
print()

if result['name_match']:
    print("⚠️  SECURITY STATUS: Grade was APPROVED")
    print()
    print("This grade submission passed name verification.")
    print(f"The name '{result['expected_name'].title()}' was found on the grade sheet.")
    print()
else:
    print("✅ SECURITY STATUS: Grade was REJECTED")
    print()
    print("The system correctly prevented a fraudulent submission:")
    print(f"  - Expected: {result['expected_name'].title()}")
    print(f"  - Confidence: {result['confidence']:.0%}")
    print(f"  - Reason: {result.get('mismatch_reason', 'N/A')[:200]}")
    print()
    print("🔒 FRAUD PREVENTION: Working as intended!")

print()
print("=" * 80)
