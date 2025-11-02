"""
Test Grade Verification - Check if name verification is working
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from myapp.ai_service import grade_analyzer

print("=" * 70)
print("🔍 GRADE VERIFICATION TEST")
print("=" * 70)
print()

grades = GradeSubmission.objects.all().order_by('-id')

if not grades.exists():
    print("❌ No grade submissions found")
    sys.exit(1)

for grade in grades[:3]:
    print(f"\nGrade Submission ID: {grade.id}")
    print(f"  Student: {grade.student.first_name} {grade.student.last_name}")
    print(f"  Status: {grade.status}")
    print(f"  Has Grade Sheet: {'Yes' if grade.grade_sheet else 'No'}")
    
    if grade.grade_sheet:
        print(f"  Grade Sheet File: {grade.grade_sheet.name}")
        
        # Test name verification
        print("\n  Testing name verification...")
        try:
            result = grade_analyzer._verify_grade_sheet_ownership(grade)
            
            print(f"  ✓ Name Match: {result['name_match']}")
            print(f"  ✓ Confidence: {result['confidence']:.0%}")
            print(f"  ✓ Expected: {result['expected_name']}")
            print(f"  ✓ Matched: {result.get('matched_name', 'N/A')}")
            
            if not result['name_match']:
                print(f"  ⚠️  Reason: {result['mismatch_reason']}")
            
            if result.get('found_names'):
                print(f"  ✓ Found names: {', '.join(result['found_names'][:3])}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print("-" * 70)

print()
print("=" * 70)
print("ANALYSIS")
print("=" * 70)
print()

# Check if Tesseract is available
print("Checking OCR availability...")
try:
    import pytesseract
    from PIL import Image
    # Try to get version
    version = pytesseract.get_tesseract_version()
    print(f"✅ Tesseract OCR is installed: {version}")
except Exception as e:
    print(f"❌ Tesseract OCR not available: {str(e)}")
    print()
    print("⚠️  WITHOUT OCR:")
    print("   - Grade verification CANNOT read names from grade sheets")
    print("   - System may be auto-approving due to error handling")
    print("   - SECURITY RISK: Students can submit other people's grades")
    print()
    print("✅ SOLUTION: Integrate Autonomous AI (EasyOCR) into grade analyzer")

print()
print("=" * 70)
