#!/usr/bin/env python
"""
Re-analyze IT 102 grade sheet with AI
Uses existing grade sheet image and runs full OCR + AI analysis
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.services import gwa_calculation_service
from myapp.ai_service import AIGradeAnalyzer
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def reanalyze_it102_with_ai():
    """
    Re-analyze IT 102 grade sheet with AI
    Uses OCR to extract data from existing grade sheet image
    """
    
    print("=" * 80)
    print("🤖 RE-ANALYZING IT 102 WITH AI - FULL OCR EXTRACTION")
    print("=" * 80)
    
    try:
        # Find student
        student = CustomUser.objects.get(id=25)
        print(f"\n✅ Found student: {student.first_name} {student.last_name} (ID: {student.id})")
        
        # Find IT 102 grade submission
        it102_grade = GradeSubmission.objects.get(
            student=student,
            subject_code='IT 102',
            academic_year='2025-2026',
            semester='1st'
        )
        
        print(f"\n📋 Current Grade Submission:")
        print(f"   Subject: {it102_grade.subject_code} - {it102_grade.subject_name}")
        print(f"   Grade: {it102_grade.grade_received}")
        print(f"   Units: {it102_grade.units}")
        print(f"   Grade Sheet: {it102_grade.grade_sheet}")
        print(f"   Current Status: {it102_grade.status}")
        print(f"   Current Confidence: {it102_grade.ai_confidence_score:.1%}")
        
        # STEP 1: Run AI Analysis
        print(f"\n🚀 STEP 1: Running AI Analysis on grade sheet...")
        
        analyzer = AIGradeAnalyzer()
        analysis_result = analyzer.analyze_grades(it102_grade)
        
        print(f"\n   ✅ AI Analysis Complete:")
        print(f"      - Basic Allowance Eligible: {analysis_result.get('basic_allowance_analysis', {}).get('eligible', False)}")
        print(f"      - Merit Incentive Eligible: {analysis_result.get('merit_incentive_analysis', {}).get('eligible', False)}")
        print(f"      - Confidence Score: {analysis_result.get('confidence_score', 0):.1%}")
        
        # Print extracted data
        extracted = analysis_result.get('extracted_grades', {})
        if extracted:
            print(f"\n      📊 Extracted Data from Grade Sheet:")
            print(f"         - Analysis Confidence: {extracted.get('analysis_confidence', 0):.1%}")
            print(f"         - Text Extracted: {len(extracted.get('extracted_text', ''))} chars")
            print(f"         - GWA Found: {extracted.get('gwa_found', False)}")
            print(f"         - SWA Found: {extracted.get('swa_found', False)}")
            print(f"         - Subjects Found: {extracted.get('subjects_found', False)}")
        
        # Print validation issues
        validation = analysis_result.get('grade_validation', {})
        if validation.get('issues'):
            print(f"\n      ⚠️  Validation Issues:")
            for issue in validation['issues']:
                print(f"         - {issue}")
        
        if validation.get('warnings'):
            print(f"\n      ℹ️  Warnings:")
            for warning in validation['warnings']:
                print(f"         - {warning}")
        
        # STEP 2: Update grade submission with AI results
        print(f"\n✅ STEP 2: Updating grade submission with AI results...")
        
        old_confidence = it102_grade.ai_confidence_score
        old_status = it102_grade.status
        
        # Update with AI results
        it102_grade.qualifies_for_basic_allowance = analysis_result.get('basic_allowance_analysis', {}).get('eligible', False)
        it102_grade.qualifies_for_merit_incentive = analysis_result.get('merit_incentive_analysis', {}).get('eligible', False)
        it102_grade.ai_evaluation_completed = True
        it102_grade.ai_confidence_score = analysis_result.get('confidence_score', 0.0)
        it102_grade.ai_extracted_grades = analysis_result.get('extracted_grades', {})
        it102_grade.ai_grade_validation = analysis_result.get('grade_validation', {})
        it102_grade.ai_recommendations = analysis_result.get('recommendations', [])
        
        evaluation_notes = analysis_result.get('analysis_notes', [])
        it102_grade.ai_evaluation_notes = "\n".join(evaluation_notes)
        
        # Auto-approve if confidence is reasonable
        if it102_grade.ai_confidence_score >= 0.30:
            it102_grade.status = 'approved'
            it102_grade.reviewed_at = timezone.now()
            it102_grade.admin_notes = f"✅ Re-analyzed with AI (Confidence: {it102_grade.ai_confidence_score:.1%})"
        else:
            it102_grade.admin_notes = f"⚠️ Re-analyzed with AI (Low confidence: {it102_grade.ai_confidence_score:.1%}) - Manual review recommended"
        
        it102_grade.save()
        
        print(f"   ✅ Status: {old_status} → {it102_grade.status}")
        print(f"   ✅ Confidence: {old_confidence:.0%} → {it102_grade.ai_confidence_score:.1%}")
        print(f"   ✅ Eligibility - Basic: {it102_grade.qualifies_for_basic_allowance}, Merit: {it102_grade.qualifies_for_merit_incentive}")
        
        # STEP 3: Recalculate GWA for semester
        print(f"\n📊 STEP 3: Recalculating GWA for semester...")
        gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(
            student=student,
            academic_year='2025-2026',
            semester='1st'
        )
        
        if gwa_result:
            print(f"   ✅ GWA Recalculated:")
            print(f"      - GWA: {gwa_result.get('gwa', 'N/A'):.2f}")
            print(f"      - Total Units: {gwa_result.get('total_units', 0)}")
            print(f"      - Merit Level: {gwa_result.get('merit_level', 'N/A')}")
            print(f"      - Basic Eligible: {gwa_result.get('basic_allowance_eligible', False)}")
            print(f"      - Merit Eligible: {gwa_result.get('merit_incentive_eligible', False)}")
            print(f"      - Total Allowance: ₱{gwa_result.get('total_allowance', 0):,.0f}")
        else:
            print(f"   ⚠️  GWA calculation returned None")
        
        # STEP 4: Summary of all semester subjects
        print(f"\n🔍 STEP 4: Summary of all subjects in semester...")
        all_grades = GradeSubmission.objects.filter(
            student=student,
            academic_year='2025-2026',
            semester='1st'
        ).order_by('subject_code')
        
        print(f"\n   {len(all_grades)} Subjects in 2025-2026 Sem 1st:")
        print(f"   {'Code':<12} {'Name':<30} {'Grade':<8} {'Units':<6} {'Status':<12} {'Confidence':<12}")
        print(f"   {'-'*80}")
        
        for grade in all_grades:
            print(f"   {grade.subject_code:<12} {grade.subject_name[:28]:<30} {float(grade.grade_received):<8.2f} {grade.units:<6} {grade.status:<12} {grade.ai_confidence_score:<11.0%}")
        
        # Final summary
        approved_count = all_grades.filter(status='approved').count()
        pending_count = all_grades.filter(status='pending').count()
        
        print(f"\n   Summary: {approved_count} Approved, {pending_count} Pending")
        
        print("\n" + "=" * 80)
        print("✅ RE-ANALYSIS COMPLETE")
        print("=" * 80)
        
        # Result interpretation
        if it102_grade.ai_confidence_score >= 0.85:
            print("\n✅ EXCELLENT: High confidence score achieved!")
            print("   Grade is validated and can proceed to allowance application")
        elif it102_grade.ai_confidence_score >= 0.50:
            print("\n✅ GOOD: Acceptable confidence score")
            print("   Grade passes AI validation")
        elif it102_grade.ai_confidence_score >= 0.30:
            print("\n⚠️  MODERATE: Confidence score is acceptable but not high")
            print("   Grade can proceed but may need additional review")
        else:
            print("\n❌ LOW: Confidence score is too low")
            print("   Grade sheet OCR extraction failed - may need:")
            print("      1. Better quality image upload")
            print("      2. Manual verification by admin")
            print("      3. Re-check of grade sheet image for clarity")
        
        if approved_count == len(all_grades):
            print(f"\n🎉 ALL SUBJECTS NOW APPROVED!")
            print("   Workflow complete - student ready for allowance application")
        
        return True
        
    except GradeSubmission.DoesNotExist:
        print("\n❌ ERROR: IT 102 grade not found")
        return False
        
    except CustomUser.DoesNotExist:
        print("\n❌ ERROR: Student ID 25 not found")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = reanalyze_it102_with_ai()
    sys.exit(0 if success else 1)
