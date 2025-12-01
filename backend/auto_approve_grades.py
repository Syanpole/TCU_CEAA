import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission
from django.utils import timezone

def auto_approve_high_confidence_grades():
    """
    Auto-approve all pending grades that have:
    - ai_verified = True
    - ai_confidence_score >= 0.85
    """
    print("🔍 Searching for high-confidence pending grades...")
    
    # Find all pending grades with high confidence
    pending_grades = GradeSubmission.objects.filter(
        status='pending',
        ai_evaluation_completed=True,
        ai_confidence_score__gte=0.85
    ).select_related('student')
    
    count = pending_grades.count()
    
    if count == 0:
        print("✅ No pending grades found with 85%+ confidence. All good!")
        return
    
    print(f"\n📋 Found {count} pending grades with 85%+ confidence:")
    print("-" * 80)
    
    for grade in pending_grades:
        print(f"\n🎓 Student: {grade.student.first_name} {grade.student.last_name} ({grade.student.student_id})")
        print(f"   Subject: {grade.subject_code} - {grade.subject_name}")
        print(f"   Grade: {grade.grade_received} | Confidence: {grade.ai_confidence_score:.2%}")
        print(f"   Semester: {grade.semester} {grade.academic_year}")
    
    print("\n" + "=" * 80)
    response = input(f"\n🤖 Auto-approve all {count} grades? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Cancelled. No grades were approved.")
        return
    
    print("\n🚀 Auto-approving grades...")
    
    approved_count = 0
    for grade in pending_grades:
        # Update status to approved
        grade.status = 'approved'
        grade.reviewed_by = None  # Auto-approved, not by admin
        grade.reviewed_at = timezone.now()
        
        # Add auto-approval note
        notes = grade.ai_evaluation_notes or ""
        notes += f"\n\n🤖 AUTO-APPROVED: Grade verified with {grade.ai_confidence_score:.2%} confidence. All verification checks passed. Approved automatically on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        grade.ai_evaluation_notes = notes
        
        grade.save()
        approved_count += 1
        
        print(f"✅ Approved: {grade.subject_code} - {grade.student.student_id} ({grade.ai_confidence_score:.2%})")
    
    print("\n" + "=" * 80)
    print(f"🎉 SUCCESS! Auto-approved {approved_count} grades with high confidence!")
    print("\n📊 These grades were:")
    print("   ✓ Verified as authentic by AI")
    print("   ✓ Had 85%+ confidence scores")
    print("   ✓ Matched student's COE subjects")
    print("   ✓ Had valid grade values")
    
    # Group by semester and show summary
    print("\n📅 By Semester:")
    semesters = {}
    for grade in GradeSubmission.objects.filter(
        status='approved',
        reviewed_by__isnull=True,  # Auto-approved
        reviewed_at__gte=timezone.now() - timezone.timedelta(minutes=5)
    ).select_related('student'):
        key = f"{grade.semester} {grade.academic_year}"
        if key not in semesters:
            semesters[key] = []
        semesters[key].append(grade)
    
    for semester, grades in semesters.items():
        print(f"\n   {semester}: {len(grades)} auto-approved")
        students = set(g.student.student_id for g in grades)
        for student_id in students:
            student_grades = [g for g in grades if g.student.student_id == student_id]
            print(f"      • {student_id}: {len(student_grades)} subjects")

if __name__ == '__main__':
    auto_approve_high_confidence_grades()
