#!/usr/bin/env python
"""
Debug IT 102 grade sheet OCR extraction
See what text the OCR is actually extracting from the image
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.ai_service import AIGradeAnalyzer
import json

def debug_it102_ocr():
    """
    Debug IT 102 OCR extraction to see what's happening
    """
    
    print("=" * 80)
    print("🔍 DEBUGGING IT 102 OCR EXTRACTION")
    print("=" * 80)
    
    try:
        # Find IT 102 grade
        student = CustomUser.objects.get(id=25)
        it102_grade = GradeSubmission.objects.get(
            student=student,
            subject_code='IT 102',
            academic_year='2025-2026',
            semester='1st'
        )
        
        print(f"\n📋 Grade: {it102_grade.subject_code} - {it102_grade.subject_name}")
        print(f"   File: {it102_grade.grade_sheet}")
        print(f"   Current Confidence: {it102_grade.ai_confidence_score:.0%}")
        
        # Get the image path
        if it102_grade.grade_sheet:
            media_root = '/mnt/c/Users/SEANPA~1/AppData/Local/Temp'  # or check settings
            image_path = os.path.join('media', str(it102_grade.grade_sheet))
            print(f"\n   Image path: {image_path}")
            print(f"   File exists: {os.path.exists(image_path)}")
        
        # Run OCR analysis directly
        print(f"\n🚀 Running OCR Analysis...")
        analyzer = AIGradeAnalyzer()
        
        # Call the private method to see the extracted data
        if it102_grade.grade_sheet:
            extracted_result = analyzer._analyze_grade_sheet(it102_grade.grade_sheet)
            
            print(f"\n✅ OCR Extraction Result:")
            print(f"   Analysis Confidence: {extracted_result.get('analysis_confidence', 0):.1%}")
            print(f"   GWA Found: {extracted_result.get('gwa_found', False)}")
            print(f"   SWA Found: {extracted_result.get('swa_found', False)}")
            print(f"   Subjects Found: {extracted_result.get('subjects_found', False)}")
            print(f"   Units Found: {extracted_result.get('units_found', False)}")
            print(f"   Semester Info Found: {extracted_result.get('semester_info', False)}")
            
            # Print extracted text
            extracted_text = extracted_result.get('extracted_text', '')
            if extracted_text:
                print(f"\n   📝 Extracted Text ({len(extracted_text)} chars):")
                print(f"   {'-'*76}")
                # Print first 500 chars
                print(extracted_text[:500])
                if len(extracted_text) > 500:
                    print(f"\n   ... ({len(extracted_text) - 500} more characters)")
                print(f"   {'-'*76}")
            else:
                print(f"\n   ❌ NO TEXT EXTRACTED - OCR FAILED")
            
            # Print other extracted fields
            print(f"\n   📊 Extracted Fields:")
            for key, value in extracted_result.items():
                if key not in ['extracted_text', 'analysis_confidence']:
                    print(f"      - {key}: {value}")
        else:
            print(f"\n   ❌ No grade sheet file attached")
        
        # Check other subjects for comparison
        print(f"\n\n🔄 Comparing with OTHER SUBJECTS (for reference)...")
        all_grades = GradeSubmission.objects.filter(
            student=student,
            academic_year='2025-2026',
            semester='1st'
        ).order_by('subject_code')
        
        for grade in all_grades:
            if grade.subject_code != 'IT 102' and grade.grade_sheet:
                print(f"\n   {grade.subject_code}: Confidence {grade.ai_confidence_score:.0%}")
                extracted = grade.ai_extracted_grades or {}
                print(f"      - Analysis Confidence: {extracted.get('analysis_confidence', 0):.1%}")
                print(f"      - Text extracted: {len(extracted.get('extracted_text', ''))} chars")
                print(f"      - GWA found: {extracted.get('gwa_found', False)}")
                print(f"      - Subjects found: {extracted.get('subjects_found', False)}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_it102_ocr()
