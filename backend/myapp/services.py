"""
Centralized services for the TCU-CEAA application
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from django.db.models import Q

from .models import GradeSubmission, CustomUser

logger = logging.getLogger(__name__)


class GWACalculationService:
    """
    Centralized service for GWA (General Weighted Average) calculations.
    Handles grouping by user, semester, and school year, and eligibility determination.
    """

    # Official TCU grading scale conversion table
    GRADING_SCALE = [
        (1.0, 98.0),    # 96-100 → Excellent
        (1.25, 94.0),   # 93-95 → Very Good
        (1.5, 91.0),    # 90-92 → Good
        (1.75, 87.0),   # 87-89 → Satisfactory (Merit threshold)
        (2.0, 85.0),    # 84-86 → Fair
        (2.25, 82.0),   # 81-83 → Average
        (2.5, 79.0),    # 78-80 → Below Average
        (2.75, 76.0),   # 75-77 → Passing
        (3.0, 72.0),    # 70-74 → Minimum Passing
        (5.0, 40.0),    # Below 70 → Failing
    ]

    @staticmethod
    def convert_point_to_percentage(gwa_value: float) -> float:
        """
        Convert GWA from point scale (1.0-5.0) to percentage scale (0-100)
        """
        if gwa_value >= 60:
            return float(gwa_value)  # Already in percentage scale

        # Linear interpolation between points
        for i in range(len(GWACalculationService.GRADING_SCALE) - 1):
            point1, percent1 = GWACalculationService.GRADING_SCALE[i]
            point2, percent2 = GWACalculationService.GRADING_SCALE[i + 1]

            if point1 <= gwa_value <= point2:
                ratio = (gwa_value - point1) / (point2 - point1)
                return round(percent1 + ratio * (percent2 - percent1), 2)

        # Edge cases
        if gwa_value < 1.0:
            return 98.0  # Excellent
        return 40.0  # Failing

    @staticmethod
    def determine_merit_level(gwa: float) -> str:
        """
        Determine merit level based on GWA
        """
        if gwa <= 1.50:
            return 'HIGH_HONORS'
        elif gwa <= 2.00:
            return 'HONORS'
        elif gwa <= 2.50:
            return 'MERIT'
        elif gwa <= 3.00:
            return 'REGULAR'
        else:
            return 'BELOW_PASSING'

    @staticmethod
    def check_eligibility(gwa: float, total_units: int) -> Dict[str, bool]:
        """
        Check basic and merit eligibility based on updated rules:
        - GWA < 2.00: Basic allowance only (₱5,000)
        - GWA ≥ 2.00: Both basic and merit allowances (₱10,000 total)
        
        Also considers subject count as part of eligibility validation.
        """
        # Updated eligibility logic: GWA threshold is now 2.00
        basic_eligible = gwa <= 2.5 and total_units >= 15  # Basic eligibility still requires GWA ≤ 2.5
        merit_eligible = gwa < 2.00 and total_units >= 15   # Merit eligibility now requires GWA < 2.00
        
        return {
            'basic_eligible': basic_eligible,
            'merit_eligible': merit_eligible
        }
    
    def calculate_semester_gwa_with_subject_count(self, student: CustomUser, academic_year: str,
                                                   semester: str) -> Optional[Dict]:
        """
        Calculate GWA for a specific student, academic year, and semester.
        Emphasizes subject count in the calculation and ensures proper weighting.
        
        Formula: GWA = Sum(grade * units) / Total Units
        Subject count is included in the response for grouping operations.
        """
        try:
            # Get all approved grades for this semester
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
                return None

            # Calculate weighted GPA with explicit subject count
            total_grade_points = Decimal('0')
            total_units = 0
            grades_list = []
            subject_count = 0

            for grade in approved_grades:
                grade_value = Decimal(str(grade.grade_received))
                units = int(grade.units)
                grade_points = grade_value * units

                total_grade_points += grade_points
                total_units += units
                subject_count += 1

                grades_list.append({
                    'subject_code': grade.subject_code,
                    'subject_name': grade.subject_name,
                    'grade': float(grade_value),
                    'units': units
                })

            if total_units == 0:
                return None

            gwa = float(total_grade_points / total_units)
            merit_level = self.determine_merit_level(gwa)
            eligibility = self.check_eligibility(gwa, total_units)

            return {
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}",
                'academic_year': academic_year,
                'semester': semester,
                'gwa': round(gwa, 2),
                'total_units': total_units,
                'total_subjects': subject_count,  # Explicitly included
                'merit_level': merit_level,
                'basic_eligible': eligibility['basic_eligible'],
                'merit_eligible': eligibility['merit_eligible'],
                'grades': grades_list
            }

        except Exception as e:
            logger.error(f"Error calculating semester GWA with subject count for {student.id}: {str(e)}")
            return None

    def calculate_semester_gwa(self, student: CustomUser, academic_year: str,
                              semester: str) -> Optional[Dict]:
        """
        Calculate GWA for a specific student, academic year, and semester.
        Groups all approved grades for that period.
        """
        try:
            # Get all approved grades for this semester
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
                return None

            # Calculate weighted GPA
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

            if total_units == 0:
                return None

            gwa = float(total_grade_points / total_units)
            merit_level = self.determine_merit_level(gwa)
            eligibility = self.check_eligibility(gwa, total_units)

            return {
                'student_id': student.id,
                'academic_year': academic_year,
                'semester': semester,
                'gwa': round(gwa, 2),
                'total_units': total_units,
                'total_subjects': len(grades_list),
                'merit_level': merit_level,
                'basic_eligible': eligibility['basic_eligible'],
                'merit_eligible': eligibility['merit_eligible'],
                'grades': grades_list
            }

        except Exception as e:
            logger.error(f"Error calculating semester GWA for {student.id}: {str(e)}")
            return None

    def update_grade_submissions_with_gwa(self, student: CustomUser, academic_year: str,
                                        semester: str, gwa_data: Dict) -> int:
        """
        Update all grade submissions for a semester with GWA calculation results
        """
        try:
            updated_count = GradeSubmission.objects.filter(
                student=student,
                academic_year=academic_year,
                semester=semester
            ).update(
                qualifies_for_basic_allowance=gwa_data['basic_eligible'],
                qualifies_for_merit_incentive=gwa_data['merit_eligible'],
                ai_gwa_calculated=gwa_data['gwa'],
                ai_merit_level=gwa_data['merit_level']
            )

            logger.info(f"Updated {updated_count} grade submissions with GWA data for {student.username}")
            return updated_count

        except Exception as e:
            logger.error(f"Error updating grade submissions with GWA: {str(e)}")
            return 0

    def check_semester_completion(self, student: CustomUser, academic_year: str,
                                semester: str) -> Dict:
        """
        Check if all subjects for a semester are submitted and determine if GWA calculation should trigger
        """
        try:
            # Get COE document to determine total subjects
            from .models import DocumentSubmission
            coe_document = DocumentSubmission.objects.filter(
                student=student,
                document_type='certificate_of_enrollment',
                status='approved'
            ).order_by('-submitted_at').first()

            if not coe_document or not coe_document.extracted_subjects:
                return {
                    'complete': False,
                    'reason': 'No approved COE with extracted subjects found'
                }

            total_subjects = coe_document.subject_count

            # Count submitted grades for this semester
            submitted_grades = GradeSubmission.objects.filter(
                student=student,
                academic_year=academic_year,
                semester=semester,
                subject_code__isnull=False
            )

            submitted_count = submitted_grades.count()

            return {
                'complete': submitted_count >= total_subjects,
                'total_subjects': total_subjects,
                'submitted_count': submitted_count,
                'coe_document_id': coe_document.id
            }

        except Exception as e:
            logger.error(f"Error checking semester completion: {str(e)}")
            return {
                'complete': False,
                'reason': str(e)
            }

    def trigger_automated_gwa_calculation(self, student: CustomUser, academic_year: str,
                                        semester: str) -> Optional[Dict]:
        """
        Main method to trigger automated GWA calculation when semester is complete
        """
        try:
            # Check if semester is complete
            completion_check = self.check_semester_completion(student, academic_year, semester)

            if not completion_check['complete']:
                logger.info(f"Semester not complete for {student.username}: {completion_check}")
                return None

            # Calculate GWA
            gwa_data = self.calculate_semester_gwa(student, academic_year, semester)

            if not gwa_data:
                logger.warning(f"No GWA data calculated for {student.username}")
                return None

            # Update grade submissions
            updated_count = self.update_grade_submissions_with_gwa(
                student, academic_year, semester, gwa_data
            )

            result = {
                **gwa_data,
                'updated_submissions': updated_count,
                'calculation_triggered': True
            }

            logger.info(f"Automated GWA calculation completed for {student.username}: GWA {gwa_data['gwa']}")
            return result

        except Exception as e:
            logger.error(f"Error in automated GWA calculation: {str(e)}")
            return None


# Global instance for easy access
gwa_calculation_service = GWACalculationService()