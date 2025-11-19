"""
Grade Validation Service
=======================

Service for validating grade submissions against Certificate of Enrollment (COE) data.
Ensures that submitted grades match the subjects extracted from the COE document.

Features:
- Subject count validation
- Subject code matching
- Subject name verification
- Comprehensive validation reporting

Author: TCU CEAA Development Team
Date: November 17, 2025
"""

import logging
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class GradeValidationService:
    """
    Service for validating grade submissions against COE subject data.
    
    This service ensures that:
    1. Number of grade submissions matches number of subjects in COE
    2. Subject codes in submissions match COE subject codes
    3. Subject names in submissions match COE subject names
    """
    
    # Threshold for fuzzy string matching (0.0-1.0)
    # 0.85 means 85% similarity is required for a match
    NAME_MATCH_THRESHOLD = 0.85
    
    def __init__(self):
        """Initialize the grade validation service."""
        logger.info("✅ Grade Validation Service initialized")
    
    def validate_grade_submissions(
        self,
        coe_subjects: List[Dict[str, str]],
        grade_submissions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate grade submissions against COE subject list.
        
        Args:
            coe_subjects: List of subjects from COE [{'subject_code': 'GE101', 'subject_name': 'Technopreneurship'}, ...]
            grade_submissions: List of grade submission data [{'subject_code': '...', 'subject_name': '...', ...}, ...]
        
        Returns:
            Dictionary containing:
                - is_valid: Boolean indicating if all validations passed
                - validation_results: Dictionary of individual validation results
                - errors: List of validation errors
                - warnings: List of warnings
                - missing_subjects: List of subjects in COE but not in submissions
                - extra_subjects: List of subjects in submissions but not in COE
                - matched_subjects: List of successfully matched subjects
        """
        result = {
            'is_valid': False,
            'validation_results': {
                'subject_count_match': False,
                'all_codes_match': False,
                'all_names_match': False
            },
            'errors': [],
            'warnings': [],
            'missing_subjects': [],
            'extra_subjects': [],
            'matched_subjects': []
        }
        
        try:
            logger.info(f"🔍 Validating {len(grade_submissions)} grade submissions against {len(coe_subjects)} COE subjects")
            
            # Validate subject count
            count_valid, count_errors = self._validate_subject_count(
                len(coe_subjects),
                len(grade_submissions)
            )
            result['validation_results']['subject_count_match'] = count_valid
            result['errors'].extend(count_errors)
            
            # Validate subject codes and names
            codes_valid, names_valid, matched, missing, extra, validation_errors = self._validate_subjects(
                coe_subjects,
                grade_submissions
            )
            
            result['validation_results']['all_codes_match'] = codes_valid
            result['validation_results']['all_names_match'] = names_valid
            result['matched_subjects'] = matched
            result['missing_subjects'] = missing
            result['extra_subjects'] = extra
            result['errors'].extend(validation_errors)
            
            # Generate warnings for partial matches
            if len(missing) > 0:
                result['warnings'].append(f"{len(missing)} subject(s) from COE not found in submissions")
            if len(extra) > 0:
                result['warnings'].append(f"{len(extra)} submission(s) do not match any COE subject")
            
            # Overall validation
            result['is_valid'] = (
                count_valid and
                codes_valid and
                names_valid and
                len(missing) == 0 and
                len(extra) == 0
            )
            
            if result['is_valid']:
                logger.info("✅ Grade submissions validation PASSED")
            else:
                logger.warning(f"⚠️ Grade submissions validation FAILED: {len(result['errors'])} error(s)")
            
        except Exception as e:
            logger.error(f"❌ Validation error: {str(e)}")
            result['errors'].append(f"Validation error: {str(e)}")
        
        return result
    
    def _validate_subject_count(
        self,
        coe_count: int,
        submission_count: int
    ) -> Tuple[bool, List[str]]:
        """
        Validate that the number of submissions matches the number of COE subjects.
        
        Args:
            coe_count: Number of subjects in COE
            submission_count: Number of grade submissions
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        if coe_count == 0:
            errors.append("No subjects found in COE document")
            return False, errors
        
        if submission_count == 0:
            errors.append("No grade submissions provided")
            return False, errors
        
        if coe_count != submission_count:
            errors.append(
                f"Subject count mismatch: COE has {coe_count} subject(s), "
                f"but {submission_count} grade(s) submitted"
            )
            return False, errors
        
        logger.info(f"✅ Subject count matches: {coe_count} subject(s)")
        return True, errors
    
    def _validate_subjects(
        self,
        coe_subjects: List[Dict[str, str]],
        submissions: List[Dict[str, Any]]
    ) -> Tuple[bool, bool, List[Dict], List[Dict], List[Dict], List[str]]:
        """
        Validate individual subjects against COE data.
        
        Args:
            coe_subjects: List of COE subjects
            submissions: List of grade submissions
        
        Returns:
            Tuple of (codes_valid, names_valid, matched, missing, extra, errors)
        """
        errors = []
        matched_subjects = []
        missing_subjects = []
        extra_submissions = []
        
        # Normalize COE subjects for comparison
        coe_map = {}
        for subject in coe_subjects:
            code = self._normalize_code(subject.get('subject_code', ''))
            coe_map[code] = {
                'code': subject.get('subject_code', ''),
                'name': subject.get('subject_name', ''),
                'matched': False
            }
        
        # Check each submission
        for submission in submissions:
            sub_code = self._normalize_code(submission.get('subject_code', ''))
            sub_name = submission.get('subject_name', '')
            
            if sub_code in coe_map:
                # Code matches - check name
                coe_subject = coe_map[sub_code]
                coe_name = coe_subject['name']
                
                name_similarity = self._calculate_similarity(sub_name, coe_name)
                
                if name_similarity >= self.NAME_MATCH_THRESHOLD:
                    # Both code and name match
                    matched_subjects.append({
                        'subject_code': sub_code,
                        'subject_name': sub_name,
                        'coe_name': coe_name,
                        'name_similarity': name_similarity
                    })
                    coe_map[sub_code]['matched'] = True
                    logger.info(f"✅ Matched: {sub_code} - {sub_name} (similarity: {name_similarity:.2%})")
                else:
                    # Code matches but name doesn't
                    errors.append(
                        f"Subject name mismatch for {sub_code}: "
                        f"Expected '{coe_name}', got '{sub_name}' "
                        f"(similarity: {name_similarity:.2%})"
                    )
                    logger.warning(f"⚠️ Name mismatch for {sub_code}: {name_similarity:.2%} similarity")
            else:
                # Code not found in COE
                extra_submissions.append({
                    'subject_code': sub_code,
                    'subject_name': sub_name
                })
                errors.append(f"Subject code '{sub_code}' not found in COE")
                logger.warning(f"⚠️ Extra submission: {sub_code} not in COE")
        
        # Find missing subjects (in COE but not submitted)
        for code, subject in coe_map.items():
            if not subject['matched']:
                missing_subjects.append({
                    'subject_code': subject['code'],
                    'subject_name': subject['name']
                })
                errors.append(f"Missing grade submission for {subject['code']} - {subject['name']}")
                logger.warning(f"⚠️ Missing: {subject['code']} - {subject['name']}")
        
        codes_valid = len(extra_submissions) == 0
        names_valid = all(m['name_similarity'] >= self.NAME_MATCH_THRESHOLD for m in matched_subjects)
        
        return codes_valid, names_valid, matched_subjects, missing_subjects, extra_submissions, errors
    
    def _normalize_code(self, code: str) -> str:
        """
        Normalize subject code for comparison (remove spaces, convert to uppercase).
        
        Args:
            code: Subject code
        
        Returns:
            Normalized subject code
        """
        return code.strip().upper().replace(' ', '').replace('-', '')
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score (0.0-1.0)
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        s1 = str1.strip().lower()
        s2 = str2.strip().lower()
        
        return SequenceMatcher(None, s1, s2).ratio()
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """
        Generate a human-readable validation summary.
        
        Args:
            validation_result: Result from validate_grade_submissions()
        
        Returns:
            Formatted validation summary string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("GRADE VALIDATION SUMMARY")
        lines.append("=" * 60)
        
        if validation_result['is_valid']:
            lines.append("✅ Status: VALID")
            lines.append(f"✅ All {len(validation_result['matched_subjects'])} subjects matched successfully")
        else:
            lines.append("❌ Status: INVALID")
            lines.append(f"❌ {len(validation_result['errors'])} validation error(s) found")
        
        lines.append("")
        lines.append("Validation Checks:")
        checks = validation_result['validation_results']
        lines.append(f"  {'✅' if checks['subject_count_match'] else '❌'} Subject Count Match")
        lines.append(f"  {'✅' if checks['all_codes_match'] else '❌'} All Subject Codes Match")
        lines.append(f"  {'✅' if checks['all_names_match'] else '❌'} All Subject Names Match")
        
        if validation_result['matched_subjects']:
            lines.append("")
            lines.append(f"Matched Subjects ({len(validation_result['matched_subjects'])}):")
            for match in validation_result['matched_subjects']:
                lines.append(f"  ✅ {match['subject_code']} - {match['subject_name']}")
        
        if validation_result['missing_subjects']:
            lines.append("")
            lines.append(f"Missing Submissions ({len(validation_result['missing_subjects'])}):")
            for subject in validation_result['missing_subjects']:
                lines.append(f"  ❌ {subject['subject_code']} - {subject['subject_name']}")
        
        if validation_result['extra_subjects']:
            lines.append("")
            lines.append(f"Extra Submissions ({len(validation_result['extra_subjects'])}):")
            for subject in validation_result['extra_subjects']:
                lines.append(f"  ⚠️ {subject['subject_code']} - {subject['subject_name']}")
        
        if validation_result['errors']:
            lines.append("")
            lines.append("Errors:")
            for error in validation_result['errors']:
                lines.append(f"  • {error}")
        
        if validation_result['warnings']:
            lines.append("")
            lines.append("Warnings:")
            for warning in validation_result['warnings']:
                lines.append(f"  • {warning}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Singleton instance
_grade_validation_service = None

def get_grade_validation_service() -> GradeValidationService:
    """Get or create the singleton grade validation service instance."""
    global _grade_validation_service
    if _grade_validation_service is None:
        _grade_validation_service = GradeValidationService()
    return _grade_validation_service
