"""
Integrated AI Verification System
Combines all 6 core algorithms + advanced features into a unified service
"""

import os
import logging
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile
import tempfile

from .advanced_algorithms import (
    DocumentValidator,
    CrossDocumentMatcher,
    GradeVerifier,
    FaceVerifier,
    FraudDetector,
    AIVerificationManager,
    CosineSimilarityAnalyzer
)
from .ai_generated_detector import AIGeneratedDetector

logger = logging.getLogger(__name__)


class IntegratedVerificationService:
    """
    Unified service that integrates all AI verification algorithms
    Provides a single interface for document and grade verification
    """
    
    def __init__(self):
        # Initialize all algorithms
        self.document_validator = DocumentValidator()
        self.cross_matcher = CrossDocumentMatcher()
        self.grade_verifier = GradeVerifier()
        self.face_verifier = FaceVerifier()
        self.fraud_detector = FraudDetector()
        self.verification_manager = AIVerificationManager()
        self.cosine_analyzer = CosineSimilarityAnalyzer()
        self.ai_generated_detector = AIGeneratedDetector()
        
        logger.info("✅ Integrated AI Verification Service initialized with all 6 algorithms")
    
    def verify_document_submission(self, document_submission, user_profile: Dict = None) -> Dict[str, Any]:
        """
        Complete document verification using all algorithms
        """
        result = {
            'verification_id': f"VER-{document_submission.id}-{timezone.now().timestamp()}",
            'timestamp': timezone.now().isoformat(),
            'document_id': document_submission.id,
            'document_type': document_submission.document_type,
            'overall_status': 'pending',
            'confidence_score': 0.0,
            'algorithms_executed': [],
            'algorithm_results': {},
            'recommendations': [],
            'auto_decision': False,
            'decision': 'manual_review'
        }
        
        try:
            # Save uploaded file to temporary location
            temp_path = self._save_temp_file(document_submission.document_file)
            
            if not temp_path:
                result['overall_status'] = 'error'
                result['error'] = 'Could not process uploaded file'
                return result
            
            # Get user profile data for cross-matching
            user_data = self._extract_user_profile_data(document_submission.student, user_profile)
            
            # Execute comprehensive verification
            logger.info(f"Starting comprehensive verification for document {document_submission.id}")
            
            verification_results = self.verification_manager.comprehensive_verification(
                file_path=temp_path,
                document_type=document_submission.document_type,
                user_data=user_data,
                grade_data=None  # For documents, not grades
            )
            
            result['algorithm_results'] = verification_results.get('algorithm_results', {})
            result['confidence_score'] = verification_results.get('overall_confidence', 0.0)
            result['decision'] = verification_results.get('recommendation', 'manual_review')
            
            # Track which algorithms were executed
            result['algorithms_executed'] = list(verification_results.get('algorithm_results', {}).keys())
            
            # Additional cosine similarity analysis if we have user data
            if user_data and verification_results.get('algorithm_results', {}).get('document_validation'):
                extracted_text = verification_results['algorithm_results']['document_validation'].get('extracted_text', '')
                if extracted_text:
                    document_data = self._extract_document_data(extracted_text)
                    cosine_result = self.cosine_analyzer.compare_multi_field(user_data, document_data)
                    result['algorithm_results']['cosine_similarity'] = cosine_result
                    result['algorithms_executed'].append('cosine_similarity')
            
            # AI-Generated Content Detection
            try:
                ai_detection_result = self.ai_generated_detector.detect_ai_generated(
                    temp_path, 
                    'auto'
                )
                result['algorithm_results']['ai_generated_detection'] = ai_detection_result
                result['algorithms_executed'].append('ai_generated_detection')
                
                # If high probability of AI generation, flag for review
                if ai_detection_result.get('ai_probability', 0.0) >= 0.7:
                    result['recommendations'].append("⚠️ HIGH RISK: Document may be AI-generated")
                    result['decision'] = 'manual_review'
                    
            except Exception as e:
                logger.warning(f"AI generation detection failed: {e}")
                result['algorithm_results']['ai_generated_detection'] = {
                    'error': str(e),
                    'ai_probability': 0.0
                }
            
            # Generate comprehensive recommendations
            recommendations = self._generate_recommendations(verification_results, document_submission)
            result['recommendations'] = recommendations
            
            # Determine auto-decision
            result['auto_decision'] = self._should_auto_decide(verification_results)
            
            # Set overall status
            if result['decision'] == 'auto_approve':
                result['overall_status'] = 'approved'
            elif result['decision'] == 'reject':
                result['overall_status'] = 'rejected'
            else:
                result['overall_status'] = 'pending'
            
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            logger.info(f"Verification complete: {result['overall_status']} (confidence: {result['confidence_score']:.2%})")
            
        except Exception as e:
            logger.error(f"Integrated verification error: {e}")
            result['overall_status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def verify_grade_submission(self, grade_submission) -> Dict[str, Any]:
        """
        Complete grade verification using relevant algorithms
        """
        result = {
            'verification_id': f"GRADE-VER-{grade_submission.id}-{timezone.now().timestamp()}",
            'timestamp': timezone.now().isoformat(),
            'grade_id': grade_submission.id,
            'overall_status': 'pending',
            'confidence_score': 0.0,
            'algorithms_executed': [],
            'algorithm_results': {},
            'qualifies_basic': False,
            'qualifies_merit': False,
            'total_allowance': 0,
            'recommendations': []
        }
        
        try:
            # Prepare grade data
            grade_data = {
                'gwa': float(grade_submission.general_weighted_average),
                'swa': float(grade_submission.semestral_weighted_average),
                'total_units': grade_submission.total_units,
                'grades': [],  # Will be extracted from grade sheet if available
                'units': []
            }
            
            # Extract grades from grade sheet if available
            if grade_submission.grade_sheet:
                temp_path = self._save_temp_file(grade_submission.grade_sheet)
                if temp_path:
                    # Document validation on grade sheet
                    sheet_validation = self.document_validator.validate_document(
                        temp_path, 
                        'report_card'
                    )
                    result['algorithm_results']['grade_sheet_validation'] = sheet_validation
                    result['algorithms_executed'].append('grade_sheet_validation')
                    
                    # Extract grades from text
                    if sheet_validation.get('extracted_text'):
                        extracted_grades = self._extract_grades_from_text(
                            sheet_validation['extracted_text']
                        )
                        if extracted_grades['grades']:
                            grade_data['grades'] = extracted_grades['grades']
                            grade_data['units'] = extracted_grades['units']
                    
                    # Fraud detection on grade sheet
                    fraud_result = self.fraud_detector.detect_fraud(temp_path)
                    result['algorithm_results']['fraud_detection'] = fraud_result
                    result['algorithms_executed'].append('fraud_detection')
                    
                    # Cleanup
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
            
            # Grade verification
            grade_verification = self.grade_verifier.verify_grades(grade_data)
            result['algorithm_results']['grade_verification'] = grade_verification
            result['algorithms_executed'].append('grade_verification')
            
            # Extract eligibility results
            basic_analysis = grade_verification.get('basic_allowance_analysis', {})
            merit_analysis = grade_verification.get('merit_incentive_analysis', {})
            
            result['qualifies_basic'] = basic_analysis.get('eligible', False)
            result['qualifies_merit'] = merit_analysis.get('eligible', False)
            
            # Calculate total allowance
            total_allowance = 0
            if result['qualifies_basic']:
                total_allowance += 5000
            if result['qualifies_merit']:
                total_allowance += 5000
            result['total_allowance'] = total_allowance
            
            # Calculate confidence
            confidence = 1.0 - grade_verification.get('fraud_probability', 0.0)
            if result['algorithm_results'].get('fraud_detection'):
                fraud_prob = result['algorithm_results']['fraud_detection'].get('fraud_probability', 0.0)
                confidence = confidence * (1.0 - fraud_prob)
            result['confidence_score'] = confidence
            
            # Generate recommendations
            recommendations = grade_verification.get('recommendations', [])
            if grade_verification.get('suspicious_patterns'):
                for pattern in grade_verification['suspicious_patterns']:
                    recommendations.append(f"⚠️ {pattern['description']}")
            result['recommendations'] = recommendations
            
            # Determine status
            if confidence >= 0.8:
                result['overall_status'] = 'verified'
            elif confidence >= 0.5:
                result['overall_status'] = 'review_needed'
            else:
                result['overall_status'] = 'suspicious'
            
            logger.info(f"Grade verification complete: {result['overall_status']} (allowance: ₱{total_allowance})")
            
        except Exception as e:
            logger.error(f"Grade verification error: {e}")
            result['overall_status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _save_temp_file(self, uploaded_file) -> Optional[str]:
        """Save uploaded file to temporary location"""
        try:
            # Determine file extension
            filename = uploaded_file.name
            _, ext = os.path.splitext(filename)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                # Handle both UploadedFile and FieldFile
                if hasattr(uploaded_file, 'chunks'):
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                elif hasattr(uploaded_file, 'read'):
                    uploaded_file.seek(0)
                    temp_file.write(uploaded_file.read())
                else:
                    # Try to open and read the file
                    with open(uploaded_file.path, 'rb') as f:
                        temp_file.write(f.read())
                
                return temp_file.name
        except Exception as e:
            logger.error(f"Error saving temp file: {e}")
            return None
    
    def _extract_user_profile_data(self, user, additional_profile: Dict = None) -> Dict[str, Any]:
        """Extract user profile data for cross-matching"""
        data = {
            'name': f"{user.first_name} {user.last_name}".strip(),
            'username': user.username,
            'email': user.email,
            'student_id': user.student_id or '',
        }
        
        # Add additional profile data if provided
        if additional_profile:
            data.update(additional_profile)
        
        return data
    
    def _extract_document_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from document text"""
        import re
        
        data = {
            'full_text': text
        }
        
        # Extract name
        name_pattern = r'name[:\s]*([a-zA-Z\s,\.]+?)(?:\n|birth|address|$)'
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            data['name'] = name_match.group(1).strip()
        
        # Extract address
        address_pattern = r'address[:\s]*([a-zA-Z0-9\s,\.]+?)(?:\n\n|date|$)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            data['address'] = address_match.group(1).strip()
        
        # Extract guardian/parent info
        guardian_pattern = r'(?:mother|father|parent|guardian)[:\s]*([a-zA-Z\s,\.]+?)(?:\n|$)'
        guardian_matches = re.findall(guardian_pattern, text, re.IGNORECASE)
        if guardian_matches:
            data['guardian'] = ', '.join(guardian_matches)
        
        return data
    
    def _extract_grades_from_text(self, text: str) -> Dict[str, List]:
        """Extract individual grades from text"""
        import re
        
        result = {
            'grades': [],
            'units': []
        }
        
        # Pattern for grade entries (subject code, grade, units)
        # Example: "MATH 101 - 85.5 - 3 units"
        grade_pattern = r'(\d{1,2}\.?\d{0,2})\s*(?:units?|credits?)?[\s:]*(\d{1,2})'
        matches = re.findall(grade_pattern, text)
        
        for grade, units in matches:
            try:
                grade_val = float(grade)
                units_val = int(units)
                if 65.0 <= grade_val <= 100.0 and 1 <= units_val <= 6:
                    result['grades'].append(grade_val)
                    result['units'].append(units_val)
            except ValueError:
                continue
        
        return result
    
    def _generate_recommendations(self, verification_results: Dict, document_submission) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        # Document validation recommendations
        doc_val = verification_results.get('algorithm_results', {}).get('document_validation', {})
        if doc_val:
            confidence = doc_val.get('confidence_score', 0.0)
            if confidence < 0.5:
                recommendations.append("Document quality is low - consider re-uploading a clearer image")
            
            ocr_conf = doc_val.get('ocr_confidence', 0.0)
            if ocr_conf < 0.6:
                recommendations.append("Text extraction quality is poor - ensure document is clearly scanned")
        
        # Fraud detection recommendations
        fraud = verification_results.get('algorithm_results', {}).get('fraud_detection', {})
        if fraud and fraud.get('is_likely_fraud'):
            for indicator in fraud.get('fraud_indicators', []):
                recommendations.append(f"⚠️ Fraud alert: {indicator}")
        
        # Cross-matching recommendations
        cross = verification_results.get('algorithm_results', {}).get('cross_matching', {})
        if cross:
            for discrepancy in cross.get('discrepancies', []):
                field = discrepancy.get('field', 'unknown')
                recommendations.append(f"Information mismatch in {field} - please verify")
        
        # Face verification recommendations
        face = verification_results.get('algorithm_results', {}).get('face_verification', {})
        if face:
            if not face.get('has_face'):
                recommendations.append("No face detected - ID document should contain a photo")
            elif face.get('face_count', 0) > 1:
                recommendations.append("Multiple faces detected - ensure only one person in ID photo")
        
        return recommendations
    
    def _should_auto_decide(self, verification_results: Dict) -> bool:
        """Determine if automatic decision should be made"""
        confidence = verification_results.get('overall_confidence', 0.0)
        recommendation = verification_results.get('recommendation', 'manual_review')
        
        # Auto-decide for high confidence approvals or clear rejections
        if confidence >= 0.85 and recommendation == 'auto_approve':
            return True
        
        fraud = verification_results.get('algorithm_results', {}).get('fraud_detection', {})
        if fraud and fraud.get('is_likely_fraud'):
            return True  # Auto-reject fraud
        
        return False
    
    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get statistics about verification performance"""
        stats = {
            'algorithms_available': {
                'document_validator': True,
                'cross_matcher': True,
                'grade_verifier': True,
                'face_verifier': True,
                'fraud_detector': True,
                'verification_manager': True,
                'cosine_analyzer': True
            },
            'total_algorithms': 7,
            'system_status': 'operational'
        }
        
        return stats


# Global service instance
integrated_verification_service = IntegratedVerificationService()
