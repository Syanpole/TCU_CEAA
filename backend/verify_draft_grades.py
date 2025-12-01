import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.tasks import verify_grade_sheet_task

# Get user
username = '4peytonly'
academic_year = '2025-2026'
semester = '1st'

user = CustomUser.objects.get(username=username)

print("=" * 80)
print(f"🔄 RUNNING AI VERIFICATION FOR ALL DRAFT GRADES")
print(f"Student: {username}")
print(f"Period: {academic_year} {semester}")
print("=" * 80)

# Get all draft grades
grades = GradeSubmission.objects.filter(
    student=user,
    academic_year=academic_year,
    semester=semester,
    status='draft'
)

print(f"\nFound {grades.count()} draft submissions")

if grades.count() == 0:
    print("\n✅ No draft grades to process")
else:
    print("\n🔄 Running AI verification on all drafts...\n")
    
    for i, grade in enumerate(grades, 1):
        print(f"[{i}/{grades.count()}] {grade.subject_code} - {grade.subject_name}")
        print(f"  Grade Sheet: {grade.grade_sheet.name if grade.grade_sheet else 'None'}")
        
        try:
            # Run AI verification
            verify_grade_sheet_task(grade.id)
            
            # Refresh from database
            grade.refresh_from_db()
            
            print(f"  ✅ AI Confidence: {grade.ai_confidence_score:.1%}")
            
            if grade.ai_extracted_grades:
                is_authentic = grade.ai_extracted_grades.get('is_authentic', False)
                detected = grade.ai_extracted_grades.get('detected_count', 0)
                subject_in_coe = grade.ai_extracted_grades.get('subject_in_coe', False)
                grade_matches = grade.ai_extracted_grades.get('grade_matches', False)
                
                print(f"  • Authentic: {'✓' if is_authentic else '✗'} ({detected}/3 logos)")
                print(f"  • Subject in COE: {'✓' if subject_in_coe else '✗'}")
                print(f"  • Grade Matches: {'✓' if grade_matches else '✗'}")
                
                if grade.ai_extracted_grades.get('detections'):
                    detections = [d['label'] for d in grade.ai_extracted_grades['detections']]
                    print(f"  • Detected: {', '.join(detections)}")
            else:
                print(f"  ⚠️ No AI data extracted")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()
    
    # Summary
    print("=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    
    grades = GradeSubmission.objects.filter(
        student=user,
        academic_year=academic_year,
        semester=semester,
        status='draft'
    )
    
    verified = [g for g in grades if g.ai_confidence_score > 0]
    authentic = [g for g in grades if g.ai_extracted_grades and g.ai_extracted_grades.get('is_authentic', False)]
    
    print(f"\nTotal Drafts: {grades.count()}")
    print(f"Verified: {len(verified)}/{grades.count()}")
    print(f"Authentic: {len(authentic)}/{len(verified)}")
    
    if verified:
        avg_confidence = sum(g.ai_confidence_score for g in verified) / len(verified)
        print(f"Average Confidence: {avg_confidence:.1%}")

print("\n" + "=" * 80)
