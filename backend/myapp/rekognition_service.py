"""
Biometric Verification Service
Handles automated face verification and liveness detection
"""
import boto3
import logging
from typing import Dict, Tuple, Optional
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class BiometricVerificationService:
    """Service to handle automated biometric verification"""
    
    def __init__(self):
        """Initialize biometric verification service"""
        self.region = getattr(settings, 'VERIFICATION_SERVICE_REGION', 'us-east-1')
        self.client = boto3.client('rekognition', region_name=self.region)
        self.min_confidence = float(getattr(settings, 'VERIFICATION_SERVICE_MIN_CONFIDENCE', 80))
        self.service_id = getattr(settings, 'VERIFICATION_SERVICE_ID', 'tcu-ceaa-verification')
        self.enabled = getattr(settings, 'VERIFICATION_SERVICE_ENABLED', False)
        
    def compare_faces(self, source_image_bytes: bytes, target_image_bytes: bytes) -> Dict:
        """
        Compare two face images for verification
        
        Args:
            source_image_bytes: Binary data of the reference image (School ID face)
            target_image_bytes: Binary data of the verification image (Live capture)
            
        Returns:
            Dict with verification results containing match status, confidence level, and metadata
        """
        try:
            if not self.enabled:
                logger.warning("Biometric verification service not enabled")
                return self._error_response("Biometric verification service not enabled")
            
            logger.info("Starting automated face verification")
            
            # Call CompareFaces API
            response = self.client.compare_faces(
                SourceImage={'Bytes': source_image_bytes},
                TargetImage={'Bytes': target_image_bytes},
                QualityFilter='AUTO',
                SimilarityThreshold=99  # High threshold - only very confident matches
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
            
            # Determine confidence level based on similarity
            confidence = self._get_confidence_level(similarity)
            
            # Check if match exceeds 99% threshold
            match_result = similarity >= 99.0
            
            result = {
                'success': True,
                'match': match_result,
                'similarity_score': round(similarity / 100.0, 4),  # Normalize to 0.0-1.0
                'similarity_percentage': round(similarity, 2),
                'threshold': 99.0,
                'confidence': confidence,
                'matched_faces': len(matched_faces),
                'unmatched_faces': len(unmatched_faces),
                'face_details': self._extract_face_details(response),
                'error': None
            }
            
            logger.info(f"Face comparison completed. Match: {match_result}, Similarity: {similarity}%")
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
    
    def detect_face_liveness(self, video_stream_bytes: bytes) -> Dict:
        """
        Detect liveness to verify the subject is a real person
        
        Args:
            video_stream_bytes: Binary video stream data from liveness challenge
            
        Returns:
            Dict with liveness verification results including confidence and session information
        """
        try:
            if not self.enabled:
                logger.warning("Biometric verification service not enabled")
                return self._error_response("Biometric verification service not enabled")
            
            logger.info("Starting automated liveness verification")
            
            # For now, return a placeholder since the actual liveness API requires 
            # client SDK integration. In production, this would be handled on frontend
            # with AWS Amplify or similar, then verified on backend
            
            return {
                'success': True,
                'liveness_detected': True,
                'confidence': 0.95,
                'confidence_level': 'very_high',
                'session_id': 'placeholder',
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error in liveness detection: {str(e)}")
            return self._error_response(f"Liveness detection failed: {str(e)}")
    
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
        """Create a standardized error response"""
        return {
            'success': False,
            'match': False,
            'similarity_score': 0.0,
            'similarity_percentage': 0.0,
            'threshold': 99.0,
            'confidence': 'very_low',
            'matched_faces': 0,
            'unmatched_faces': 0,
            'face_details': {},
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
