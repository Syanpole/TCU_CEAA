"""
Semester Grouping Service
=========================

Service for grouping grade submissions by (student, academic_year, semester)
with comprehensive GWA calculation and semester aggregation.

Features:
- Group grades by semester and academic year
- Calculate GWA per semester group
- Calculate subject count per semester
- Generate hierarchical semester summaries
- Support for bulk semester operations

Author: TCU CEAA Development Team
Date: November 18, 2025
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict

from django.db.models import Q, Sum, Count, F, DecimalField
from django.db.models.functions import Coalesce

from .models import GradeSubmission, CustomUser

logger = logging.getLogger(__name__)


class SemesterGroupingService:
    """
    Service for grouping and aggregating grade submissions by semester.
    
    This service handles:
    1. Grouping grades by (student, academic_year, semester)
    2. Calculating GWA for each semester group
    3. Calculating total subjects per semester
    4. Generating hierarchical data for UI rendering
    """
    
    def __init__(self):
        """Initialize the semester grouping service."""
        logger.info("✅ Semester Grouping Service initialized")
    
    def group_student_grades_by_semester(
        self,
        student: CustomUser,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Group all grades for a student by (academic_year, semester).
        
        Args:
            student: The student whose grades should be grouped
            filters: Optional additional filters (e.g., {'status': 'approved'})
        
        Returns:
            List of semester groups, each containing:
                - academic_year: e.g., '2024-2025'
                - semester: e.g., '1st', '2nd', 'summer'
                - semester_label: e.g., '2024-2025 1st Semester'
                - subjects: List of grade submissions for this semester
                - gwa: Calculated GWA for this semester
                - subject_count: Total subjects in this semester
                - total_units: Total units in this semester
                - status_breakdown: Count of each status (pending, approved, etc.)
                - all_approved: Boolean indicating if all subjects are approved
                - merit_level: Merit level based on GWA
                - qualifies_basic: Boolean for basic allowance
                - qualifies_merit: Boolean for merit allowance
        """
        try:
            # Build base query - include all submissions (drafts and final)
            query = GradeSubmission.objects.filter(student=student)
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.filter(**{key: value})
            
            if not query.exists():
                logger.info(f"No grades found for student {student.id}")
                return []
            
            # Group by academic_year and semester
            semester_groups = defaultdict(list)
            
            for grade in query.order_by('academic_year', 'semester', 'subject_code'):
                key = (grade.academic_year, grade.semester)
                semester_groups[key].append(grade)
            
            # Convert to sorted list of dicts
            result = []
            for (academic_year, semester), grades in sorted(semester_groups.items()):
                group_data = self._aggregate_semester_group(academic_year, semester, grades)
                result.append(group_data)
            
            logger.info(f"✅ Grouped {len(result)} semester(s) for student {student.username}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Error grouping grades: {str(e)}")
            return []
    
    def get_grouped_grades_for_admin(
        self,
        students: Optional[List[CustomUser]] = None,
        academic_year: Optional[str] = None,
        semester: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get grouped grades for admin dashboard.
        Groups by student, then by (academic_year, semester).
        
        Args:
            students: List of students to filter (if None, gets all)
            academic_year: Optional academic year filter
            semester: Optional semester filter
            status: Optional status filter (pending, approved, etc.)
        
        Returns:
            Dictionary: {student_id: [semester_group1, semester_group2, ...]}
        """
        try:
            # Build query - include all submissions (drafts and final)
            query = GradeSubmission.objects.all()
            
            if students:
                query = query.filter(student__in=students)
            if academic_year:
                query = query.filter(academic_year=academic_year)
            if semester:
                query = query.filter(semester=semester)
            if status:
                query = query.filter(status=status)
            
            # Group by student first
            result = defaultdict(list)
            
            for grade in query.order_by('student', 'academic_year', 'semester', 'subject_code'):
                student_id = grade.student.id
                key = (grade.academic_year, grade.semester)
                
                # Check if this semester group already exists for this student
                existing = next(
                    (group for group in result[student_id] if 
                     group['academic_year'] == grade.academic_year and 
                     group['semester'] == grade.semester),
                    None
                )
                
                if existing:
                    existing['subjects'].append(self._serialize_grade(grade))
                else:
                    # Create new semester group
                    group = {
                        'academic_year': grade.academic_year,
                        'semester': grade.semester,
                        'semester_label': self._get_semester_label(grade.academic_year, grade.semester),
                        'subjects': [self._serialize_grade(grade)],
                        'student_id': grade.student.id,
                        'student_name': f"{grade.student.first_name} {grade.student.last_name}"
                    }
                    result[student_id].append(group)
            
            # Calculate aggregates for each semester group
            for student_id in result:
                for group in result[student_id]:
                    self._calculate_semester_aggregates(group)
            
            logger.info(f"✅ Retrieved grouped grades for {len(result)} student(s)")
            return dict(result)
        
        except Exception as e:
            logger.error(f"❌ Error getting grouped grades for admin: {str(e)}")
            return {}
    
    def _aggregate_semester_group(
        self,
        academic_year: str,
        semester: str,
        grades: List[GradeSubmission]
    ) -> Dict[str, Any]:
        """
        Aggregate data for a single semester group.
        
        Args:
            academic_year: e.g., '2024-2025'
            semester: e.g., '1st', '2nd', 'summer'
            grades: List of GradeSubmission objects for this semester
        
        Returns:
            Aggregated semester group data
        """
        # Serialize grades
        subject_list = [self._serialize_grade(grade) for grade in grades]
        
        # Calculate GWA from approved grades only
        approved_grades = [g for g in grades if g.status == 'approved']
        gwa, merit_level, qualifies_basic, qualifies_merit = self._calculate_semester_gwa(approved_grades)
        
        # Calculate status breakdown
        status_breakdown = defaultdict(int)
        for grade in grades:
            status_breakdown[grade.status] += 1
        
        # Count total units
        total_units = sum(g.units or 0 for g in grades if g.units)
        
        # Check if all approved
        all_approved = all(g.status == 'approved' for g in grades)
        
        return {
            'academic_year': academic_year,
            'semester': semester,
            'semester_label': self._get_semester_label(academic_year, semester),
            'subjects': subject_list,
            'gwa': round(gwa, 2) if gwa else None,
            'subject_count': len(subject_list),
            'total_units': total_units,
            'status_breakdown': dict(status_breakdown),
            'all_approved': all_approved,
            'merit_level': merit_level,
            'qualifies_basic': qualifies_basic,
            'qualifies_merit': qualifies_merit,
            'pending_count': sum(1 for g in grades if g.status == 'pending'),
            'approved_count': sum(1 for g in grades if g.status == 'approved'),
            'rejected_count': sum(1 for g in grades if g.status == 'rejected')
        }
    
    def _calculate_semester_gwa(self, approved_grades: List[GradeSubmission]) -> Tuple[float, str, bool, bool]:
        """
        Calculate GWA for a set of approved grades.
        
        Args:
            approved_grades: List of approved GradeSubmission objects
        
        Returns:
            Tuple of (gwa, merit_level, qualifies_basic, qualifies_merit)
        """
        if not approved_grades:
            return 0.0, 'BELOW_PASSING', False, False
        
        try:
            total_grade_points = Decimal('0')
            total_units = 0
            
            for grade in approved_grades:
                if grade.grade_received and grade.units:
                    grade_value = Decimal(str(grade.grade_received))
                    units = int(grade.units)
                    grade_points = grade_value * units
                    
                    total_grade_points += grade_points
                    total_units += units
            
            if total_units == 0:
                return 0.0, 'BELOW_PASSING', False, False
            
            gwa = float(total_grade_points / total_units)
            merit_level = self._determine_merit_level(gwa)
            
            # Eligibility rules (official TCU-CEAA criteria)
            qualifies_basic = gwa <= 2.5 and total_units >= 15   # Basic: GWA ≤ 2.5 (80%)
            qualifies_merit = gwa <= 1.75 and total_units >= 15  # Merit: GWA ≤ 1.75 (87%)
            
            return gwa, merit_level, qualifies_basic, qualifies_merit
        
        except Exception as e:
            logger.error(f"Error calculating semester GWA: {str(e)}")
            return 0.0, 'BELOW_PASSING', False, False
    
    def _determine_merit_level(self, gwa: float) -> str:
        """
        Determine merit level based on GWA.
        
        Args:
            gwa: Grade weighted average
        
        Returns:
            Merit level string
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
    
    def _calculate_semester_aggregates(self, semester_group: Dict[str, Any]) -> None:
        """
        Calculate aggregate values for a semester group (modifies in-place).
        
        Args:
            semester_group: The semester group dict to aggregate
        """
        if not semester_group['subjects']:
            semester_group['gwa'] = None
            semester_group['merit_level'] = 'BELOW_PASSING'
            semester_group['total_units'] = 0
            semester_group['subject_count'] = 0
            semester_group['approved_count'] = 0
            semester_group['pending_count'] = 0
            semester_group['rejected_count'] = 0
            semester_group['qualifies_basic'] = False
            semester_group['qualifies_merit'] = False
            return
        
        # Calculate subject counts
        semester_group['subject_count'] = len(semester_group['subjects'])
        semester_group['approved_count'] = sum(1 for s in semester_group['subjects'] if s['status'] == 'approved')
        semester_group['pending_count'] = sum(1 for s in semester_group['subjects'] if s['status'] == 'pending')
        semester_group['rejected_count'] = sum(1 for s in semester_group['subjects'] if s['status'] == 'rejected')
        
        # Calculate from approved subjects only
        approved_subjects = [s for s in semester_group['subjects'] if s['status'] == 'approved']
        
        if not approved_subjects:
            semester_group['gwa'] = None
            semester_group['merit_level'] = 'BELOW_PASSING'
            semester_group['total_units'] = sum(s.get('units', 0) or 0 for s in semester_group['subjects'])
            semester_group['qualifies_basic'] = False
            semester_group['qualifies_merit'] = False
            return
        
        total_grade_points = 0.0
        total_units = 0
        
        for subject in approved_subjects:
            if subject.get('grade_received') and subject.get('units'):
                grade_value = float(subject['grade_received'])
                units = int(subject['units'])
                total_grade_points += grade_value * units
                total_units += units
        
        if total_units > 0:
            gwa = total_grade_points / total_units
            semester_group['gwa'] = round(gwa, 2)
            semester_group['merit_level'] = self._determine_merit_level(gwa)
            semester_group['qualifies_basic'] = gwa <= 2.5 and total_units >= 15   # Basic: GWA ≤ 2.5 (80%)
            semester_group['qualifies_merit'] = gwa <= 1.75 and total_units >= 15  # Merit: GWA ≤ 1.75 (87%)
        else:
            semester_group['gwa'] = None
            semester_group['merit_level'] = 'BELOW_PASSING'
            semester_group['qualifies_basic'] = False
            semester_group['qualifies_merit'] = False
        
        semester_group['total_units'] = total_units
    
    def _serialize_grade(self, grade: GradeSubmission) -> Dict[str, Any]:
        """
        Serialize a GradeSubmission object to a dictionary.
        
        Args:
            grade: GradeSubmission object
        
        Returns:
            Dictionary representation of the grade
        """
        return {
            'id': grade.id,
            'subject_code': grade.subject_code,
            'subject_name': grade.subject_name,
            'units': grade.units,
            'grade_received': float(grade.grade_received) if grade.grade_received else None,
            'status': grade.status,
            'ai_confidence_score': grade.ai_confidence_score,
            'ai_merit_level': grade.ai_merit_level,
            'submitted_at': grade.submitted_at.isoformat() if grade.submitted_at else None,
            'reviewed_at': grade.reviewed_at.isoformat() if grade.reviewed_at else None,
            'admin_notes': grade.admin_notes
        }
    
    def _get_semester_label(self, academic_year: str, semester: str) -> str:
        """
        Generate a user-friendly semester label.
        
        Args:
            academic_year: e.g., '2024-2025'
            semester: e.g., '1st', '2nd', 'summer'
        
        Returns:
            Formatted label, e.g., '2024-2025 1st Semester'
        """
        semester_names = {
            '1st': '1st Semester',
            '2nd': '2nd Semester',
            'summer': 'Summer',
            'midyear': 'Midyear'
        }
        return f"{academic_year} {semester_names.get(semester, semester)}"
    
    def get_semester_detail(
        self,
        student: CustomUser,
        academic_year: str,
        semester: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed breakdown for a specific semester.
        
        Args:
            student: The student
            academic_year: e.g., '2024-2025'
            semester: e.g., '1st', '2nd'
        
        Returns:
            Detailed semester breakdown or None
        """
        try:
            grades = GradeSubmission.objects.filter(
                student=student,
                academic_year=academic_year,
                semester=semester
            ).order_by('subject_code')
            
            if not grades.exists():
                return None
            
            return self._aggregate_semester_group(academic_year, semester, list(grades))
        
        except Exception as e:
            logger.error(f"Error getting semester detail: {str(e)}")
            return None


# Singleton instance
_semester_grouping_service = None


def get_semester_grouping_service() -> SemesterGroupingService:
    """Get or create the singleton semester grouping service instance."""
    global _semester_grouping_service
    if _semester_grouping_service is None:
        _semester_grouping_service = SemesterGroupingService()
    return _semester_grouping_service
