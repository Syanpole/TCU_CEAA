"""
Background tasks for async processing
"""
import logging
import re
from typing import Dict
from decimal import Decimal

logger = logging.getLogger(__name__)


def _extract_final_grade_from_class_card(file_path, raw_text):
    """
    Extract the final grade value from a TCU Class Card.
    Class cards have a specific "Final Grade:" field we need to target.
    """
    # Pattern 1: "Final Grade:" followed by a grade value (1.00-5.00 or INC/DRP/etc)
    patterns = [
        r'FINAL\s+GRADE[:\s]*([0-9]\.[0-9]{1,2})',  # Final Grade: 1.50
        r'FINAL\s+GRADE[:\s]*(INC|DRP|W|P|F)',       # Final Grade: INC
        r'Final\s+Grade[:\s]*([0-9]\.[0-9]{1,2})',   # Final Grade: 1.50 (case variation)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            grade_str = match.group(1)
            # Validate numeric grades are in valid range
            if grade_str.replace('.', '').isdigit():
                grade_val = float(grade_str)
                if 1.0 <= grade_val <= 5.0:
                    logger.info(f"Extracted final grade from class card: {grade_val}")
                    return grade_val
            else:
                # Non-numeric grades like INC, DRP
                logger.info(f"Extracted special grade from class card: {grade_str}")
                return grade_str
    
    # Pattern 2: Look for isolated grade values near "Final Grade" text
    if 'FINAL GRADE' in raw_text.upper():
        # Find the position of "Final Grade" and look for numbers nearby
        lines = raw_text.split('\n')
        for i, line in enumerate(lines):
            if 'FINAL GRADE' in line.upper():
                # Check this line and next 2 lines for grade values
                search_lines = lines[i:min(i+3, len(lines))]
                for search_line in search_lines:
                    # Look for standalone grade values
                    grade_match = re.search(r'\b([1-5]\.[0-9]{1,2})\b', search_line)
                    if grade_match:
                        grade_val = float(grade_match.group(1))
                        logger.info(f"Found grade value near Final Grade field: {grade_val}")
                        return grade_val
    
    logger.warning("Could not extract final grade from class card - field may be empty")
    return None


def auto_approve_semester_if_ready(student_id: int, academic_year: str, semester: str):
    """
    Check if all grades for a semester are verified with high confidence and auto-approve them all.
    This runs after each grade verification to check if the semester is complete.
    """
    from .models import GradeSubmission
    
    logger.info(f"Checking if semester {semester} {academic_year} for student {student_id} can be auto-approved")
    
    # Get all submissions for this semester
    semester_grades = GradeSubmission.objects.filter(
        student_id=student_id,
        academic_year=academic_year,
        semester=semester
    ).exclude(status='rejected')  # Don't include rejected grades
    
    if not semester_grades.exists():
        logger.info("No grades found for this semester")
        return
    
    total_grades = semester_grades.count()
    verified_grades = semester_grades.filter(
        status__in=['approved', 'pending'],
        ai_evaluation_completed=True,
        ai_confidence_score__gte=0.85
    ).count()
    
    logger.info(f"Semester status: {verified_grades}/{total_grades} grades verified with 85%+ confidence")
    
    # If all grades are verified with high confidence, auto-approve any that are still pending
    if verified_grades == total_grades:
        pending_to_approve = semester_grades.filter(status='pending', ai_evaluation_completed=True, ai_confidence_score__gte=0.85)
        
        if pending_to_approve.exists():
            count = pending_to_approve.count()
            pending_to_approve.update(
                status='approved',
                reviewed_by_id=None,  # Auto-approved, not by admin
                reviewed_at=timezone.now()
            )
            
            logger.info(f"🎉 AUTO-APPROVED {count} grades for {semester} {academic_year}! All semester grades verified with high confidence.")
            
            # Add note to each approved grade
            for grade in pending_to_approve:
                notes = grade.ai_evaluation_notes or ""
                notes += f"\n\n🤖 SEMESTER AUTO-APPROVED: All {total_grades} grades for {semester} {academic_year} verified with 85%+ confidence. Approved automatically on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
                grade.ai_evaluation_notes = notes
                grade.save()
            
            # Calculate GWA and set eligibility flags
            try:
                from .services import gwa_calculation_service
                from .models import CustomUser
                student = CustomUser.objects.get(id=student_id)
                gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(student, academic_year, semester)
                if gwa_result:
                    logger.info(f"✅ GWA calculated: {gwa_result['gwa']:.2f} - {gwa_result['merit_level']}")
            except Exception as e:
                logger.error(f"Error calculating GWA: {str(e)}")
        else:
            logger.info(f"All {total_grades} grades already approved for {semester} {academic_year}")
            
            # Calculate GWA for already approved semester
            try:
                from .services import gwa_calculation_service
                from .models import CustomUser
                student = CustomUser.objects.get(id=student_id)
                gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(student, academic_year, semester)
                if gwa_result:
                    logger.info(f"✅ GWA calculated: {gwa_result['gwa']:.2f} - {gwa_result['merit_level']}")
            except Exception as e:
                logger.error(f"Error calculating GWA: {str(e)}")
    else:
        logger.info(f"Not ready for auto-approval: {total_grades - verified_grades} grades still need verification")


def verify_grade_sheet_task(grade_submission_id: int):
    """
    Verify a grade sheet submission using AI.
    
    This function:
    1. Verifies the grade sheet is authentic (has official COE elements)
    2. Extracts grade information via OCR
    3. Matches subject with COE subjects
    4. Validates user-inputted grade matches extracted grade
    5. Updates verification status
    """
    from .models import GradeSubmission, DocumentSubmission
    from .grades_detection_service import GradesDetectionService
    
    try:
        grade_submission = GradeSubmission.objects.get(id=grade_submission_id)
        logger.info(f"🔍 Starting AI verification for grade submission {grade_submission_id}")
        
        # Get COE document for cross-reference
        coe_doc = DocumentSubmission.objects.filter(
            student=grade_submission.student,
            document_type='certificate_of_enrollment',
            status='approved'
        ).first()
        
        if not coe_doc or not coe_doc.extracted_subjects:
            logger.warning(f"No approved COE found for student {grade_submission.student.id}")
            grade_submission.ai_evaluation_notes = "No approved COE found for verification"
            grade_submission.ai_evaluation_completed = True
            grade_submission.status = 'pending'
            grade_submission.save()
            return
        
        # Initialize AI service
        detection_service = GradesDetectionService()
        
        # Analyze the grade sheet
        file_path = grade_submission.grade_sheet.path
        analysis_result = detection_service.analyze_grade_sheet(file_path)
        
        # Get detailed detection results
        grade_sheet_elements = analysis_result.get('grade_sheet_elements', {})
        elements_detected = grade_sheet_elements.get('elements', {})
        detections = grade_sheet_elements.get('detections', [])
        missing_elements = grade_sheet_elements.get('missing_elements', [])
        
        logger.info(f"🔍 YOLO Detection Results for grade {grade_submission_id}:")
        logger.info(f"   - Detections: {detections}")
        logger.info(f"   - Missing: {missing_elements}")
        
        # Verify authenticity (check for official COE elements)
        # More lenient: consider authentic if at least 2 of 3 required elements detected
        detected_count = sum(1 for e in elements_detected.values() if e.get('detected', False))
        is_authentic = detected_count >= 2  # At least 2 out of 3 logos
        
        confidence_score = analysis_result.get('confidence', 0)
        
        # Extract grades from OCR
        extracted_grades = analysis_result.get('grades_detected', [])
        raw_text = analysis_result.get('raw_text', '')
        
        # Check if this is a class card (this IS the valid document type for TCU)
        is_class_card = 'CLASS CARD' in raw_text.upper()
        has_final_grade_field = 'FINAL GRADE' in raw_text.upper()
        
        # For class cards, try to extract the final grade value using targeted OCR
        if is_class_card or has_final_grade_field:
            extracted_grade_from_field = _extract_final_grade_from_class_card(file_path, raw_text)
            if extracted_grade_from_field and not extracted_grades:
                # Create a grade entry from the extracted value
                extracted_grades = [{
                    'subject_code': grade_submission.subject_code,
                    'subject': grade_submission.subject_name,
                    'grade': extracted_grade_from_field
                }]
        
        # Match subject with COE (handle spacing differences)
        subject_in_coe = False
        coe_subject = None
        for subj in coe_doc.extracted_subjects:
            # Normalize subject codes by removing spaces and converting to uppercase
            coe_code_normalized = subj['subject_code'].replace(' ', '').upper()
            submitted_code_normalized = grade_submission.subject_code.replace(' ', '').upper()
            
            if coe_code_normalized == submitted_code_normalized:
                subject_in_coe = True
                coe_subject = subj
                break
        
        # Validate user-inputted grade matches extracted grade
        grade_matches = False
        extracted_grade = None
        grade_validation_note = ""
        
        if not extracted_grades or len(extracted_grades) == 0:
            if is_class_card and has_final_grade_field:
                grade_validation_note = "TCU Class Card detected with empty Final Grade field. Please ensure the instructor has filled in the final grade before submitting."
            else:
                grade_validation_note = "No grades extracted from document via OCR. Please ensure the Final Grade field is filled in and clearly visible."
        else:
            for grade_entry in extracted_grades:
                # Check if this grade entry matches our subject
                subject_match = (
                    grade_entry.get('subject_code', '').replace(' ', '').upper() == grade_submission.subject_code.replace(' ', '').upper() or
                    grade_entry.get('subject', '').upper() in grade_submission.subject_name.upper()
                )
                
                if subject_match:
                    extracted_grade = grade_entry.get('grade')
                    
                    # Compare with user input (allow 0.25 difference for rounding)
                    if extracted_grade and grade_submission.grade_received:
                        grade_diff = abs(float(extracted_grade) - float(grade_submission.grade_received))
                        grade_matches = grade_diff <= 0.25
                        if not grade_matches:
                            grade_validation_note = f"Grade mismatch: OCR extracted {extracted_grade}, user input {grade_submission.grade_received} (diff: {grade_diff:.2f})"
                    break
            
            if not extracted_grade:
                grade_validation_note = f"Grade extracted from other subjects, but not for {grade_submission.subject_code}"
        
        # Build verification report
        verification_notes = []
        verification_notes.append(f"✓ Authenticity Check: {'PASSED' if is_authentic else 'FAILED'} ({detected_count}/3 logos detected)")
        if detections:
            verification_notes.append(f"  Detected: {', '.join([d['label'] + f' ({d['confidence']:.0%})' for d in detections])}")
        if missing_elements:
            verification_notes.append(f"  Missing: {', '.join(missing_elements)}")
        
        verification_notes.append(f"✓ Subject in COE: {'YES' if subject_in_coe else 'NO'}")
        
        if is_class_card:
            verification_notes.append(f"⚠️ Document Type: CLASS CARD (not a grade sheet)")
        
        verification_notes.append(f"✓ Grade Match: {'YES' if grade_matches else 'PENDING MANUAL REVIEW'}")
        if grade_validation_note:
            verification_notes.append(f"  - {grade_validation_note}")
        
        verification_notes.append(f"✓ AI Confidence: {confidence_score:.2%}")
        
        if extracted_grade:
            verification_notes.append(f"  - Extracted Grade: {extracted_grade}")
            verification_notes.append(f"  - User Input: {grade_submission.grade_received}")
        else:
            verification_notes.append(f"  - User Input: {grade_submission.grade_received}")
            verification_notes.append(f"  - Extracted Grade: None")
        
        # Store AI evaluation data
        grade_submission.ai_evaluation_completed = True
        grade_submission.ai_confidence_score = confidence_score
        grade_submission.ai_evaluation_notes = "\n".join(verification_notes)
        
        grade_submission.ai_extracted_grades = {
            'subject_code': grade_submission.subject_code,
            'subject_name': grade_submission.subject_name,
            'extracted_grade': float(extracted_grade) if extracted_grade else None,
            'user_input_grade': float(grade_submission.grade_received) if grade_submission.grade_received else None,
            'grade_matches': grade_matches,
            'is_authentic': is_authentic,
            'detected_count': detected_count,
            'detections': detections,
            'missing_elements': missing_elements,
            'subject_in_coe': subject_in_coe,
            'coe_subject': coe_subject,
            'document_type': 'CLASS_CARD' if is_class_card else 'GRADE_SHEET',
            'grade_validation_note': grade_validation_note
        }
        
        # Determine if grade is verified
        is_verified = is_authentic and subject_in_coe and grade_matches
        
        # Check if we should boost confidence for OCR failure cases
        # Boost if: authentic, subject in COE, user entered grade, but OCR failed
        if confidence_score < 0.85 and is_authentic and subject_in_coe and grade_submission.grade_received and not extracted_grade:
            old_confidence = confidence_score
            confidence_score = 0.85
            grade_submission.ai_confidence_score = confidence_score
            
            verification_notes.append("\n🔧 CONFIDENCE BOOST (Auto-Applied)")
            verification_notes.append(f"   Reason: OCR failed to extract grade, but document is authentic")
            verification_notes.append(f"   Evidence:")
            verification_notes.append(f"     • Document verified as authentic ({detected_count}/3 logos detected)")
            verification_notes.append(f"     • Subject verified in student's COE")
            verification_notes.append(f"     • Student manually entered grade: {grade_submission.grade_received}")
            verification_notes.append(f"   Confidence: {old_confidence:.0%} → {confidence_score:.0%}")
            
            # Update verification status with boost
            is_verified = True
            grade_matches = True  # Accept manual grade when OCR fails but doc is authentic
        
        # Auto-approve if all checks pass with high confidence
        if is_verified and confidence_score >= 0.85:
            grade_submission.status = 'approved'
            verification_notes.append("\n🎉 AUTO-APPROVED: All verification checks passed with high confidence")
        elif is_verified and confidence_score >= 0.70:
            grade_submission.status = 'pending'
            verification_notes.append("\n⚠️ PENDING REVIEW: Verification passed but confidence below threshold")
        else:
            grade_submission.status = 'pending'
            verification_notes.append("\n⚠️ PENDING REVIEW: Manual verification required")
        
        grade_submission.ai_evaluation_notes = "\n".join(verification_notes)
        grade_submission.save()
        
        logger.info(f"✅ AI verification completed for grade submission {grade_submission_id}: {grade_submission.status}")
        
        # Check if all grades for this semester are verified and can be auto-approved
        try:
            auto_approve_semester_if_ready(grade_submission.student.id, grade_submission.academic_year, grade_submission.semester)
        except Exception as e:
            logger.error(f"Error in auto-approval check: {str(e)}")
        
    except GradeSubmission.DoesNotExist:
        logger.error(f"Grade submission {grade_submission_id} not found")
    except Exception as e:
        logger.error(f"Error in AI verification task: {str(e)}", exc_info=True)
        try:
            grade_submission = GradeSubmission.objects.get(id=grade_submission_id)
            grade_submission.ai_evaluation_completed = True
            grade_submission.ai_evaluation_notes = f"Verification error: {str(e)}"
            grade_submission.status = 'pending'
            grade_submission.save()
        except:
            pass


def calculate_gpa_and_merit(student_id: int, academic_year: str, semester: str):
    """
    Calculate GPA from all verified/approved grades and determine merit eligibility.
    
    Args:
        student_id: ID of the student
        academic_year: Academic year (e.g., "2025-2026")
        semester: Semester (e.g., "1st", "2nd")
    
    Returns:
        Dictionary with GPA, merit level, and eligibility status
    """
    from .models import GradeSubmission, CustomUser
    from django.db.models import Avg, Sum, Q
    
    try:
        student = CustomUser.objects.get(id=student_id)
        
        # Get all approved grades for this period
        approved_grades = GradeSubmission.objects.filter(
            student=student,
            academic_year=academic_year,
            semester=semester,
            status='approved',
            subject_code__isnull=False,
            grade_received__isnull=False,
            units__isnull=False
        )
        
        if not approved_grades.exists():
            return {
                'success': False,
                'message': 'No approved grades found',
                'gpa': None,
                'merit_level': None
            }
        
        # Calculate weighted GPA (lower is better: 1.00 = highest, 5.00 = fail)
        total_grade_points = Decimal('0')
        total_units = 0
        
        grades_list = []
        for grade in approved_grades:
            grade_value = Decimal(str(grade.grade_received))
            units = int(grade.units)
            grade_points = grade_value * units
            
            total_grade_points += grade_points
            total_units += units
            
            grades_list.append({
                'subject_code': grade.subject_code,
                'subject_name': grade.subject_name,
                'grade': float(grade_value),
                'units': units
            })
        
        # Calculate GPA
        if total_units > 0:
            gpa = float(total_grade_points / total_units)
        else:
            return {
                'success': False,
                'message': 'Total units is zero',
                'gpa': None,
                'merit_level': None
            }
        
        # Determine merit level (1.00 = highest, 5.00 = fail)
        merit_level = None
        qualifies_for_merit = False
        
        if gpa <= 1.50:
            merit_level = 'HIGH_HONORS'
            qualifies_for_merit = True
        elif gpa <= 2.00:
            merit_level = 'HONORS'
            qualifies_for_merit = True
        elif gpa <= 2.50:
            merit_level = 'MERIT'
            qualifies_for_merit = True
        elif gpa <= 3.00:
            merit_level = 'REGULAR'
            qualifies_for_merit = False
        else:
            merit_level = 'BELOW_PASSING'
            qualifies_for_merit = False
        
        # Update all grade submissions with GPA data
        approved_grades.update(
            qualifies_for_merit_incentive=qualifies_for_merit,
            ai_gwa_calculated=gpa,
            ai_merit_level=merit_level
        )
        
        logger.info(f"📊 GPA calculated for {student.username}: {gpa:.2f} ({merit_level})")
        
        return {
            'success': True,
            'gpa': round(gpa, 2),
            'merit_level': merit_level,
            'qualifies_for_merit': qualifies_for_merit,
            'total_units': total_units,
            'grades_count': approved_grades.count(),
            'grades': grades_list
        }
        
    except CustomUser.DoesNotExist:
        logger.error(f"Student {student_id} not found")
        return {'success': False, 'message': 'Student not found'}
    except Exception as e:
        logger.error(f"Error calculating GPA: {str(e)}", exc_info=True)
        return {'success': False, 'message': str(e)}
