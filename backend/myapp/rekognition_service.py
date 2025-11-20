"""
BiometricVerificationService - Production Implementation
Enforces consistent security flow: Consent → Liveness → Identity Match → Admin Review

This service integrates:
- AWS Rekognition Face Liveness (3D video-based anti-spoofing)
- AWS Rekognition CompareFaces (>99% similarity threshold)
- Mandatory Human-in-the-Loop admin adjudication
- Cross-cloud authentication (Google Cloud ↔ AWS)

Security Flow:
1. Consent: Non-dismissible modal with biometric usage disclaimer
2. Liveness: AWS Rekognition 3D liveness challenge (prevents photo/video spoofing)
3. Identity Match: Compare live reference image vs School ID (>99% threshold)
4. Admin Review: All verifications routed to admin queue regardless of AI score
"""
import boto3
import logging
import json
import uuid
from typing import Dict, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from botocore.config import Config

logger = logging.getLogger(__name__)


class BiometricVerificationService:
    """
    Production-grade biometric verification service
    Integrates AWS Rekognition with mandatory admin oversight
    """
    
    def __init__(self):
        """Initialize biometric verification service with extended timeout configuration"""
        self.region = getattr(settings, 'VERIFICATION_SERVICE_REGION', 'us-east-1')
        
        # Configure boto3 with generous timeouts for cross-cloud latency
        config = Config(
            region_name=self.region,
            connect_timeout=30,  # 30 seconds for connection
            read_timeout=60,     # 60 seconds for read (handles slow mobile networks)
            retries={'max_attempts': 3, 'mode': 'standard'}
        )
        
        self.client = boto3.client('rekognition', region_name=self.region, config=config)
        self.min_confidence = float(getattr(settings, 'VERIFICATION_SERVICE_MIN_CONFIDENCE', 80))
        self.service_id = getattr(settings, 'VERIFICATION_SERVICE_ID', 'tcu-ceaa-verification')
        self.enabled = getattr(settings, 'VERIFICATION_SERVICE_ENABLED', False)
        
        # Strict threshold: >99% for auto-tagging (but always requires admin review)
        self.similarity_threshold = 99.0
        
        logger.info(f"BiometricVerificationService initialized (Enabled: {self.enabled}, Threshold: {self.similarity_threshold}%)")
        
    def create_liveness_session(self) -> Dict:
        """
        Create an AWS Rekognition Face Liveness session
        
        Returns:
            Dict with session_id for client-side liveness challenge
        """
        try:
            if not self.enabled:
                logger.warning("Biometric verification service not enabled")
                return self._error_response("Biometric verification service not enabled")
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            logger.info(f"Creating Face Liveness session: {session_id}")
            
            # Create liveness session (requires AWS Rekognition Face Liveness API)
            response = self.client.create_face_liveness_session(
                Settings={
                    'OutputConfig': {
                        'S3Bucket': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'tcu-ceaa-bucket'),
                        'S3KeyPrefix': f'liveness-sessions/{session_id}/'
                    },
                    'AuditImagesLimit': 4  # Store audit images for admin review
                }
            )
            
            return {
                'success': True,
                'session_id': response['SessionId'],
                'error': None
            }
            
        except self.client.exceptions.AccessDeniedException as e:
            logger.error(f"Access denied for liveness session: {str(e)}")
            return self._error_response("Service access denied. Check IAM permissions.")
        except Exception as e:
            logger.error(f"Error creating liveness session: {str(e)}")
            return self._error_response(f"Liveness session creation failed: {str(e)}")
    
    def get_liveness_session_results(self, session_id: str) -> Dict:
        """
        Retrieve results from a completed liveness session
        
        Args:
            session_id: The session ID from create_liveness_session
            
        Returns:
            Dict with liveness verification results
        """
        try:
            if not self.enabled:
                return self._error_response("Biometric verification service not enabled")
            
            logger.info(f"Retrieving liveness results for session: {session_id}")
            
            response = self.client.get_face_liveness_session_results(
                SessionId=session_id
            )
            
            status = response.get('Status')
            confidence = response.get('Confidence', 0.0)
            
            # Liveness check passed if SUCCEEDED and high confidence
            liveness_passed = (
                status == 'SUCCEEDED' and 
                confidence >= self.min_confidence
            )
            
            result = {
                'success': True,
                'liveness_passed': liveness_passed,
                'liveness_confidence': round(confidence / 100.0, 4),
                'liveness_confidence_percentage': round(confidence, 2),
                'session_id': session_id,
                'status': status,
                'reference_image': response.get('ReferenceImage'),  # Base64 encoded reference image
                'audit_images': response.get('AuditImages', []),
                'error': None
            }
            
            logger.info(f"Liveness check: {status}, Confidence: {confidence}%, Passed: {liveness_passed}")
            return result
            
        except self.client.exceptions.SessionNotFoundException as e:
            logger.error(f"Liveness session not found: {str(e)}")
            return self._error_response("Liveness session not found or expired")
        except Exception as e:
            logger.error(f"Error retrieving liveness results: {str(e)}")
            return self._error_response(f"Liveness verification failed: {str(e)}")
    
    def compare_faces(self, source_image_bytes: bytes, target_image_bytes: bytes) -> Dict:
        """
        Compare two face images with strict >99% threshold
        
        Args:
            source_image_bytes: Binary data of the reference image (School ID face)
            target_image_bytes: Binary data of the verification image (Live capture from liveness)
            
        Returns:
            Dict with verification results (always requires admin review)
        """
        try:
            if not self.enabled:
                logger.warning("Biometric verification service not enabled")
                return self._error_response("Biometric verification service not enabled")
            
            logger.info("Starting face comparison with >99% threshold")
            
            # Call AWS Rekognition CompareFaces API
            response = self.client.compare_faces(
                SourceImage={'Bytes': source_image_bytes},
                TargetImage={'Bytes': target_image_bytes},
                QualityFilter='AUTO',
                SimilarityThreshold=self.similarity_threshold  # 99% threshold
            )
            
            # Process response
            matched_faces = response.get('FaceMatches', [])
            unmatched_faces = response.get('UnmatchedFaces', [])
            
            # Get the best match if available
            best_match = None
            if matched_faces:
                best_match = matched_faces[0]  # Sorted by similarity descending
                similarity = best_match['Similarity']
            else:
                similarity = 0.0
            
            # Determine confidence level
            confidence = self._get_confidence_level(similarity)
            
            # Auto-tag if >99%, but STILL requires admin review
            auto_match = similarity >= self.similarity_threshold
            
            result = {
                'success': True,
                'match': auto_match,
                'similarity_score': round(similarity / 100.0, 4),  # 0.0-1.0
                'similarity_percentage': round(similarity, 2),
                'threshold': self.similarity_threshold,
                'confidence': confidence,
                'matched_faces': len(matched_faces),
                'unmatched_faces': len(unmatched_faces),
                'face_details': self._extract_face_details(response),
                'requires_admin_review': True,  # ALWAYS True
                'admin_review_reason': 'Mandatory human-in-the-loop verification',
                'error': None
            }
            
            logger.info(
                f"Face comparison: Match={auto_match}, Similarity={similarity}%, "
                f"Confidence={confidence}, AdminReviewRequired=True"
            )
            return result
            
        except self.client.exceptions.InvalidParameterException as e:
            logger.error(f"Invalid parameter in face comparison: {str(e)}")
            return self._error_response(f"Invalid image format or parameters: {str(e)}")
        except self.client.exceptions.ImageTooLargeException as e:
            logger.error(f"Image too large: {str(e)}")
            return self._error_response("Image file is too large. Maximum size: 5MB")
        except self.client.exceptions.InvalidImageFormatException as e:
            logger.error(f"Invalid image format: {str(e)}")
            return self._error_response("Invalid image format. Supported: JPEG, PNG, GIF, WebP")
        except self.client.exceptions.ThrottlingException as e:
            logger.error(f"Verification service API throttled: {str(e)}")
            return self._error_response("Service temporarily unavailable. Please try again.")
        except self.client.exceptions.ProvisionedThroughputExceededException as e:
            logger.error(f"Provisioned throughput exceeded: {str(e)}")
            return self._error_response("Service capacity exceeded. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected error in face comparison: {str(e)}")
            return self._error_response(f"Face comparison failed: {str(e)}")
    
    def verify_identity_with_liveness(
        self, 
        session_id: str, 
        school_id_image_bytes: bytes
    ) -> Dict:
        """
        Complete verification: Liveness + Identity Match
        
        Args:
            session_id: Completed liveness session ID
            school_id_image_bytes: School ID image for comparison
            
        Returns:
            Dict with complete verification results + admin review requirement
        """
        try:
            # Step 1: Get liveness results
            liveness_result = self.get_liveness_session_results(session_id)
            
            if not liveness_result['success']:
                return liveness_result
            
            if not liveness_result['liveness_passed']:
                return {
                    'success': False,
                    'error': 'Liveness check failed. Please try again in good lighting.',
                    'liveness_passed': False,
                    'requires_admin_review': True,
                    'admin_review_reason': 'Liveness check failed'
                }
            
            # Step 2: Extract reference image from liveness session
            reference_image_base64 = liveness_result.get('reference_image')
            if not reference_image_base64:
                return {
                    'success': False,
                    'error': 'No reference image from liveness session',
                    'requires_admin_review': True
                }
            
            # Decode base64 reference image
            import base64
            reference_image_bytes = base64.b64decode(reference_image_base64['Bytes'])
            
            # Step 3: Compare faces
            comparison_result = self.compare_faces(school_id_image_bytes, reference_image_bytes)
            
            # Step 4: Combine results
            combined_result = {
                'success': comparison_result['success'],
                'liveness_passed': liveness_result['liveness_passed'],
                'liveness_confidence': liveness_result['liveness_confidence'],
                'face_match': comparison_result['match'],
                'similarity_score': comparison_result['similarity_score'],
                'similarity_percentage': comparison_result['similarity_percentage'],
                'confidence': comparison_result['confidence'],
                'session_id': session_id,
                'requires_admin_review': True,  # MANDATORY
                'admin_review_reason': 'All biometric verifications require human review',
                'liveness_data': liveness_result,
                'comparison_data': comparison_result,
                'error': comparison_result.get('error')
            }
            
            logger.info(
                f"Complete verification: Liveness={liveness_result['liveness_passed']}, "
                f"Match={comparison_result['match']}, AdminReview=REQUIRED"
            )
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Error in complete verification: {str(e)}")
            return self._error_response(f"Verification failed: {str(e)}")
    
    def detect_faces_in_image(self, image_bytes: bytes) -> Dict:
        """
        Detect faces in an image using automated face detection
        
        Args:
            image_bytes: Binary image data
            
        Returns:
            Dict with face detection results
        """
        try:
            if not self.enabled:
                logger.warning("Biometric verification service not enabled")
                return self._error_response("Biometric verification service not enabled")
            
            response = self.client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )
            
            face_details = response.get('FaceDetails', [])
            
            result = {
                'success': True,
                'faces_detected': len(face_details),
                'faces': [
                    {
                        'confidence': face['Confidence'],
                        'bounding_box': face['BoundingBox'],
                        'attributes': {
                            'smile': face.get('Smile', {}).get('Value', False),
                            'eyes_open': face.get('EyesOpen', {}).get('Value', False),
                            'mouth_open': face.get('MouthOpen', {}).get('Value', False),
                        }
                    }
                    for face in face_details
                ],
                'error': None
            }
            
            logger.info(f"Face detection completed. Found {len(face_details)} faces")
            return result
            
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            return self._error_response(f"Face detection failed: {str(e)}")
    
    @staticmethod
    def _get_confidence_level(similarity_percentage: float) -> str:
        """
        Map similarity percentage to confidence level
        
        Args:
            similarity_percentage: Similarity score 0-100
            
        Returns:
            Confidence level string
        """
        if similarity_percentage >= 99.0:
            return 'very_high'
        elif similarity_percentage >= 95.0:
            return 'high'
        elif similarity_percentage >= 90.0:
            return 'medium'
        elif similarity_percentage >= 85.0:
            return 'low'
        else:
            return 'very_low'
    
    @staticmethod
    def _extract_face_details(response: Dict) -> Dict:
        """Extract detailed face information from verification response"""
        face_details = {}
        
        # Source face details
        source_face = response.get('SourceImageFace', {})
        if source_face:
            face_details['source_face'] = {
                'bounding_box': source_face.get('BoundingBox'),
                'confidence': source_face.get('Confidence')
            }
        
        # Target face details (from matched faces)
        matched_faces = response.get('FaceMatches', [])
        if matched_faces:
            best_match = matched_faces[0]
            face_details['target_face'] = {
                'bounding_box': best_match['Face']['BoundingBox'],
                'confidence': best_match['Face']['Confidence'],
                'similarity': best_match['Similarity']
            }
        
        return face_details
    
    @staticmethod
    def _error_response(error_message: str) -> Dict:
        """Standardized error response with admin review flag"""
        return {
            'success': False,
            'match': False,
            'similarity_score': 0.0,
            'similarity_percentage': 0.0,
            'threshold': 99.0,
            'confidence': 'very_low',
            'requires_admin_review': True,
            'admin_review_reason': 'Verification error',
            'error': error_message
        }


def get_verification_service():
    """Factory function to get the biometric verification service"""
    if getattr(settings, 'VERIFICATION_SERVICE_ENABLED', False):
        logger.info("Initializing automated verification service")
        return BiometricVerificationService()
    else:
        logger.info("Initializing fallback verification service")
        from .face_comparison_service import FaceComparisonService
        return FaceComparisonService()
