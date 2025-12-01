import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser, DocumentSubmission
from myapp.tasks import verify_grade_sheet_task
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
import json

print("=" * 80)
print("🧪 TESTING GRADE VERIFICATION AND AUTHENTICATION SYSTEM")
print("=" * 80)

# Test configuration
username = '4peytonly'
academic_year = '2025-2026'
semester = '1st'

try:
    user = CustomUser.objects.get(username=username)
    print(f"\n✅ Test User: {user.username} (ID: {user.id})")
except CustomUser.DoesNotExist:
    print(f"\n❌ User '{username}' not found!")
    sys.exit(1)

# Check if COE is approved
print("\n" + "=" * 80)
print("1️⃣  CHECKING COE STATUS")
print("=" * 80)

coe = DocumentSubmission.objects.filter(
    student=user,
    document_type='certificate_of_enrollment',
    status='approved'
).first()

if coe:
    subject_count = len(coe.extracted_subjects) if isinstance(coe.extracted_subjects, list) else coe.extracted_subjects.get('subject_count', 0) if coe.extracted_subjects else 0
    print(f"✅ COE Approved: {subject_count} subjects extracted")
    
    subjects = coe.extracted_subjects if isinstance(coe.extracted_subjects, list) else (coe.extracted_subjects.get('subjects', []) if coe.extracted_subjects else [])
    if subjects:
        print("\nCOE Subjects:")
        for subj in subjects[:3]:
            code = subj.get('subject_code') or subj.get('code', 'N/A')
            name = subj.get('subject_name') or subj.get('name', 'N/A')
            print(f"  • {code} - {name}")
        if len(subjects) > 3:
            print(f"  ... and {len(subjects) - 3} more")
else:
    print("⚠️  No approved COE found")

# Check existing grade submissions
print("\n" + "=" * 80)
print("2️⃣  CHECKING EXISTING GRADE SUBMISSIONS")
print("=" * 80)

grades = GradeSubmission.objects.filter(
    student=user,
    academic_year=academic_year,
    semester=semester
).order_by('-submitted_at')

print(f"\nTotal Submissions: {grades.count()}")

for grade in grades:
    print(f"\n📄 {grade.subject_code} - {grade.subject_name}")
    print(f"   Status: {grade.status}")
    print(f"   Grade: {grade.grade_received}")
    print(f"   AI Confidence: {grade.ai_confidence_score:.1%}")
    
    if grade.ai_extracted_grades:
        print(f"   ✓ AI Data Available:")
        print(f"     - Authentic: {grade.ai_extracted_grades.get('is_authentic', False)}")
        print(f"     - Detected Logos: {grade.ai_extracted_grades.get('detected_count', 0)}/3")
        print(f"     - Subject in COE: {grade.ai_extracted_grades.get('subject_in_coe', False)}")
        print(f"     - Grade Matches: {grade.ai_extracted_grades.get('grade_matches', False)}")
    else:
        print(f"   ⚠️  No AI verification data")

# Test AI Verification on a sample grade
print("\n" + "=" * 80)
print("3️⃣  TESTING AI VERIFICATION FUNCTION")
print("=" * 80)

if grades.exists():
    test_grade = grades.first()
    print(f"\nTesting on: {test_grade.subject_code} (ID: {test_grade.id})")
    print(f"Before: AI Confidence = {test_grade.ai_confidence_score:.1%}")
    
    try:
        print("\n🔄 Running AI verification...")
        verify_grade_sheet_task(test_grade.id)
        
        # Refresh from database
        test_grade.refresh_from_db()
        
        print(f"✅ After: AI Confidence = {test_grade.ai_confidence_score:.1%}")
        
        if test_grade.ai_extracted_grades:
            print("\n📊 Verification Results:")
            print(f"  • Authenticity: {'✓ PASSED' if test_grade.ai_extracted_grades.get('is_authentic') else '✗ FAILED'}")
            print(f"  • Logos Detected: {test_grade.ai_extracted_grades.get('detected_count', 0)}/3")
            
            if test_grade.ai_extracted_grades.get('detections'):
                detections = test_grade.ai_extracted_grades['detections']
                detected_items = ', '.join([f"{d['label']} ({d['confidence']:.0%})" for d in detections])
                print(f"  • Found: {detected_items}")
            
            if test_grade.ai_extracted_grades.get('missing_elements'):
                missing = test_grade.ai_extracted_grades['missing_elements']
                print(f"  • Missing: {', '.join(missing)}")
            
            print(f"  • Subject in COE: {'✓ YES' if test_grade.ai_extracted_grades.get('subject_in_coe') else '✗ NO'}")
            print(f"  • Grade Match: {'✓ YES' if test_grade.ai_extracted_grades.get('grade_matches') else '⚠️  PENDING'}")
            
            print(f"\n📝 AI Status: {test_grade.status.upper()}")
            
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("\n⚠️  No grades to test")

# Summary and Status
print("\n" + "=" * 80)
print("4️⃣  VERIFICATION SYSTEM STATUS")
print("=" * 80)

verified_grades = [g for g in grades if g.ai_confidence_score > 0]
authentic_grades = [g for g in grades if g.ai_extracted_grades and g.ai_extracted_grades.get('is_authentic')]

print(f"\n📊 Statistics:")
print(f"  Total Grades: {grades.count()}")
print(f"  AI Verified: {len(verified_grades)}/{grades.count()}")
print(f"  Authentic: {len(authentic_grades)}/{len(verified_grades) if verified_grades else 0}")

if verified_grades:
    avg_confidence = sum(g.ai_confidence_score for g in verified_grades) / len(verified_grades)
    print(f"  Average Confidence: {avg_confidence:.1%}")

print("\n✅ System Status:")
print(f"  • COE Integration: {'✓ WORKING' if coe else '✗ NO COE'}")
print(f"  • AI Verification: {'✓ WORKING' if verified_grades else '⚠️  NOT TESTED'}")
print(f"  • Authentication: {'✓ WORKING' if authentic_grades else '⚠️  NO AUTHENTIC GRADES'}")

if all([coe, verified_grades, authentic_grades]):
    print("\n🎉 ALL SYSTEMS OPERATIONAL!")
else:
    print("\n⚠️  Some systems need attention")

print("\n" + "=" * 80)
