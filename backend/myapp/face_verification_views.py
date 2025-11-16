"""
Views for face verification and liveness detection
"""

import json
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .face_comparison_service import FaceComparisonService
from .models import GradeSubmission, DocumentSubmission

logger = logging.getLogger(__name__)

face_service = FaceComparisonService()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_face_with_id(request):
    """
    Verify a live selfie against an ID document.
    
    Expected POST data:
    - id_document: File (ID image with face)
    - selfie: File (Live selfie)
    - liveness_data: JSON string (optional, liveness verification data)
    
    Returns:
    - match: Boolean indicating if faces match
    - similarity_score: Float (0.0 to 1.0)
    - confidence: String (very_low, low, medium, high, very_high)
    - liveness_passed: Boolean
    """
    try:
        # Get files from request
        id_document = request.FILES.get('id_document')
        selfie = request.FILES.get('selfie')
        liveness_data_str = request.POST.get('liveness_data')
        
        # Validate inputs
        if not id_document:
            return Response(
                {'error': 'ID document is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selfie:
            return Response(
                {'error': 'Selfie is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse liveness data if provided
        liveness_data = None
        if liveness_data_str:
            try:
                liveness_data = json.loads(liveness_data_str)
            except json.JSONDecodeError:
                logger.warning("Invalid liveness data JSON")
        
        # Save uploaded files temporarily
        id_path = default_storage.save(f'temp/id_{request.user.id}.jpg', ContentFile(id_document.read()))
        selfie_path = default_storage.save(f'temp/selfie_{request.user.id}.jpg', ContentFile(selfie.read()))
        
        try:
            # Get full paths
            id_full_path = default_storage.path(id_path)
            selfie_full_path = default_storage.path(selfie_path)
            
            # Perform face verification
            result = face_service.verify_id_with_selfie(
                id_full_path,
                selfie_full_path,
                liveness_data
            )
            
            # Clean up temporary files
            default_storage.delete(id_path)
            default_storage.delete(selfie_path)
            
            # Log verification attempt
            logger.info(
                f"Face verification for user {request.user.id}: "
                f"Match={result.get('match')}, "
                f"Similarity={result.get('similarity_score'):.4f}"
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as processing_error:
            # Clean up on error
            default_storage.delete(id_path)
            default_storage.delete(selfie_path)
            raise processing_error
            
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        return Response(
            {
                'error': 'Face verification failed',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_id_face(request):
    """
    Extract face from ID document and save for later verification.
    
    Expected POST data:
    - id_document: File (ID image with face)
    
    Returns:
    - success: Boolean
    - face_extracted: Boolean
    - message: String
    """
    try:
        id_document = request.FILES.get('id_document')
        
        if not id_document:
            return Response(
                {'error': 'ID document is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save uploaded file temporarily
        id_path = default_storage.save(
            f'temp/id_{request.user.id}_extract.jpg',
            ContentFile(id_document.read())
        )
        
        try:
            id_full_path = default_storage.path(id_path)
            
            # Extract face
            output_path = default_storage.path(f'id_faces/user_{request.user.id}_face.jpg')
            success = face_service.extract_and_save_id_face(id_full_path, output_path)
            
            # Clean up temporary file
            default_storage.delete(id_path)
            
            if success:
                return Response({
                    'success': True,
                    'face_extracted': True,
                    'message': 'Face extracted and saved successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'face_extracted': False,
                    'message': 'No face detected in ID document'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as processing_error:
            default_storage.delete(id_path)
            raise processing_error
            
    except Exception as e:
        logger.error(f"Face extraction error: {str(e)}")
        return Response(
            {
                'error': 'Face extraction failed',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_liveness_only(request):
    """
    Verify liveness data from frontend without face matching.
    
    Expected POST data:
    - liveness_data: JSON string with challenge results
    
    Returns:
    - liveness_passed: Boolean
    - checks: Dict with individual check results
    """
    try:
        liveness_data_str = request.POST.get('liveness_data') or request.body.decode('utf-8')
        
        if not liveness_data_str:
            return Response(
                {'error': 'Liveness data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            liveness_data = json.loads(liveness_data_str)
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON in liveness data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify liveness
        liveness_passed = face_service._verify_liveness_data(liveness_data)
        
        return Response({
            'liveness_passed': liveness_passed,
            'checks': {
                'color_flash': liveness_data.get('colorFlash', {}).get('passed', False),
                'blink': liveness_data.get('blink', {}).get('passed', False),
                'movement': liveness_data.get('movement', {}).get('passed', False)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Liveness verification error: {str(e)}")
        return Response(
            {
                'error': 'Liveness verification failed',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_grade_submission_identity(request):
    """
    Verify identity for grade submission using liveness detection and face verification.
    This is the final step after grade submission to confirm the student's identity.
    
    Expected POST data:
    - photo: File (Live selfie with liveness verification)
    - liveness_data: JSON string (liveness challenge results)
    - grade_submission_id: Integer (optional, ID of the grade submission to link)
    
    Returns:
    - success: Boolean
    - liveness_passed: Boolean
    - face_verified: Boolean
    - message: String
    """
    try:
        # Get uploaded photo
        photo = request.FILES.get('photo')
        liveness_data_str = request.POST.get('liveness_data')
        grade_submission_id = request.POST.get('grade_submission_id')
        
        # Validate inputs
        if not photo:
            return Response(
                {'error': 'Photo is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not liveness_data_str:
            return Response(
                {'error': 'Liveness data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse liveness data
        try:
            liveness_data = json.loads(liveness_data_str)
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid liveness data format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify liveness first
        liveness_passed = face_service._verify_liveness_data(liveness_data)
        
        if not liveness_passed:
            logger.warning(f"Liveness verification failed for user {request.user.id}")
            return Response({
                'success': False,
                'liveness_passed': False,
                'face_verified': False,
                'message': 'Liveness verification failed. Please ensure you complete all challenges (color flash, blink, movement).'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the user's ID document for face comparison
        # Look for approved ID documents (school_id, birth_certificate, or voters_certificate)
        id_document = DocumentSubmission.objects.filter(
            student=request.user,
            status='approved',
            document_type__in=['school_id', 'birth_certificate', 'voters_certificate']
        ).first()
        
        if not id_document or not id_document.file:
            return Response({
                'success': False,
                'liveness_passed': True,
                'face_verified': False,
                'message': 'No approved ID document found. Please upload and get your School ID, Birth Certificate, or Voter\'s Certificate approved first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save selfie temporarily
        selfie_path = default_storage.save(
            f'temp/grade_selfie_{request.user.id}.jpg',
            ContentFile(photo.read())
        )
        
        try:
            # Get full paths
            id_full_path = default_storage.path(id_document.file.name)
            selfie_full_path = default_storage.path(selfie_path)
            
            # Perform face verification
            verification_result = face_service.verify_id_with_selfie(
                id_full_path,
                selfie_full_path,
                liveness_data
            )
            
            # Clean up temporary file
            default_storage.delete(selfie_path)
            
            face_verified = verification_result.get('match', False)
            similarity_score = verification_result.get('similarity_score', 0.0)
            confidence = verification_result.get('confidence', 'very_low')
            
            # Log verification attempt
            logger.info(
                f"Grade submission identity verification for user {request.user.id}: "
                f"Liveness={liveness_passed}, Face Match={face_verified}, "
                f"Similarity={similarity_score:.4f}, Confidence={confidence}"
            )
            
            # If grade_submission_id provided, update the grade submission
            if grade_submission_id:
                try:
                    grade_submission = GradeSubmission.objects.get(
                        id=grade_submission_id,
                        student=request.user
                    )
                    # Update grade submission with verification results
                    # Note: These fields would need to be added to the GradeSubmission model
                    # For now, we'll just log it
                    logger.info(f"Grade submission {grade_submission_id} linked to identity verification")
                except GradeSubmission.DoesNotExist:
                    logger.warning(f"Grade submission {grade_submission_id} not found for user {request.user.id}")
            
            if face_verified:
                return Response({
                    'success': True,
                    'liveness_passed': True,
                    'face_verified': True,
                    'similarity_score': similarity_score,
                    'confidence': confidence,
                    'message': 'Identity verification successful! Your face matches your ID document.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'liveness_passed': True,
                    'face_verified': False,
                    'similarity_score': similarity_score,
                    'confidence': confidence,
                    'message': f'Face verification failed. Your face does not sufficiently match your ID document (Similarity: {similarity_score:.2%}, Confidence: {confidence}). This may indicate identity fraud.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as processing_error:
            # Clean up on error
            default_storage.delete(selfie_path)
            raise processing_error
            
    except Exception as e:
        logger.error(f"Grade submission identity verification error: {str(e)}")
        return Response(
            {
                'error': 'Identity verification failed',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
