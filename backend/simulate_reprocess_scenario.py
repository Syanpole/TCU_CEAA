import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

print("=" * 80)
print("SIMULATING REPROCESS SCENARIO")
print("=" * 80)

# Reset IT 102 to simulate a grade needing reprocessing
it102 = GradeSubmission.objects.get(
    student_id=25,
    subject_code='IT 102',
    academic_year='2025-2026',
    semester='1st'
)

print(f"\n📝 Resetting IT 102 to simulate OCR failure scenario...")
print(f"   Current Status: {it102.status}")
print(f"   Current Confidence: {it102.ai_confidence_score:.0%}")

# Simulate the state before reprocessing
it102.status = 'pending'
it102.ai_confidence_score = 0.0
it102.ai_evaluation_notes = """✓ Authenticity Check: PASSED (2/3 logos detected)
  Detected: Taguig City University Logo (90%), CITY OF TAGUIG LOGO (87%)
  Missing: enrolled_status
✓ Subject in COE: YES
✓ Grade Match: PENDING MANUAL REVIEW
  - No grades extracted from document via OCR. Please ensure the Final Grade field is filled in and clearly visible.
✓ AI Confidence: 0.00%
  - User Input: 1.50
  - Extracted Grade: None

⚠️ PENDING REVIEW: Manual verification required"""

it102.save()

print(f"\n✅ Reset complete!")
print(f"   New Status: {it102.status}")
print(f"   New Confidence: {it102.ai_confidence_score:.0%}")
print(f"\n💡 This simulates a grade where:")
print(f"   • Document is authentic (logos detected)")
print(f"   • Subject is in COE")
print(f"   • Student manually entered grade: {it102.grade_received}")
print(f"   • But OCR couldn't read the grade from image")
print(f"\n📊 Now test the reprocess button in the admin UI!")
print(f"   It should:")
print(f"   1. Re-run AI verification")
print(f"   2. Boost confidence to 85% (authentic + manual grade)")
print(f"   3. Auto-approve the grade")
