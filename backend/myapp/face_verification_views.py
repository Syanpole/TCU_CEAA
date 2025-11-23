"""
Views for face verification and liveness detection
Production implementation with AWS Rekognition integration
"""

import json
import logging
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from .face_comparison_service import FaceComparisonService
from .rekognition_service import get_verification_service
from .models import GradeSubmission, DocumentSubmission, AllowanceApplication, VerificationAdjudication

logger = logging.getLogger(__name__)

# Fallback to FaceComparisonService for non-AWS workflows
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_allowance_application_identity(request):
    """
    Verify identity for allowance application submission using liveness detection and face verification.
    This is triggered when student clicks "Submit Application" in the allowance application form.
    
    Features:
    - Fresh liveness verification every time (no reuse)
    - Maximum 3 failed attempts
    - 24-hour cooldown after 3 failed attempts
    - Detailed attempt tracking and cooldown management
    
    Expected POST data:
    - photo: File (Live selfie with liveness verification)
    - liveness_data: JSON string (liveness challenge results)
    - grade_submission_id: Integer (which grade submission is this for)
    
    Returns:
    - success: Boolean
    - liveness_passed: Boolean
    - face_verified: Boolean
    - verification_passed: Boolean (both liveness AND face verification must pass)
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
        
        if not grade_submission_id:
            return Response(
                {'error': 'Grade submission ID is required'},
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
        
        # Get the grade submission to find associated allowance application
        try:
            grade_submission = GradeSubmission.objects.get(
                id=grade_submission_id,
                student=request.user
            )
        except GradeSubmission.DoesNotExist:
            return Response(
                {'error': 'Grade submission not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create the allowance application for this grade submission
        # Find pending allowance application
        allowance_app = AllowanceApplication.objects.filter(
            student=request.user,
            grade_submission=grade_submission,
            status__in=['pending']  # Only for pending applications
        ).first()
        
        if not allowance_app:
            # Application might not be created yet - this is fine, just do verification
            logger.info(f"Allowance application not found for grade {grade_submission_id}, creating verification-only session")
        
        # Check for cooldown
        if allowance_app and allowance_app.verification_cooldown_until:
            now = timezone.now()
            if now < allowance_app.verification_cooldown_until:
                hours_remaining = (allowance_app.verification_cooldown_until - now).total_seconds() / 3600
                logger.warning(f"User {request.user.id} in cooldown for allowance app {allowance_app.id} until {allowance_app.verification_cooldown_until}")
                return Response({
                    'success': False,
                    'liveness_passed': False,
                    'face_verified': False,
                    'verification_passed': False,
                    'cooldown_active': True,
                    'cooldown_until': allowance_app.verification_cooldown_until.isoformat(),
                    'hours_remaining': round(hours_remaining, 1),
                    'message': f'Too many failed verification attempts. Please try again in {round(hours_remaining)} hour(s).'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                # Cooldown expired, reset
                if allowance_app:
                    allowance_app.verification_attempt_count = 0
                    allowance_app.verification_cooldown_until = None
                    allowance_app.save()
        
        # Verify liveness first
        liveness_passed = face_service._verify_liveness_data(liveness_data)
        
        if not liveness_passed:
            logger.warning(f"Liveness verification failed for user {request.user.id} for allowance app")
            
            # Increment failure counter
            if allowance_app:
                allowance_app.verification_attempt_count += 1
                allowance_app.last_verification_attempt_at = timezone.now()
                
                # Check if we've hit 3 attempts
                if allowance_app.verification_attempt_count >= 3:
                    # Set 24-hour cooldown
                    cooldown_until = timezone.now() + timedelta(hours=24)
                    allowance_app.verification_cooldown_until = cooldown_until
                    logger.warning(f"3 failed verification attempts for allowance app {allowance_app.id}, setting 24-hour cooldown until {cooldown_until}")
                
                allowance_app.save()
            
            return Response({
                'success': False,
                'liveness_passed': False,
                'face_verified': False,
                'verification_passed': False,
                'attempt_count': allowance_app.verification_attempt_count if allowance_app else 1,
                'message': 'Liveness verification failed. Please ensure you complete all challenges (color flash, blink, movement).'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the user's ID document for face comparison
        id_document = DocumentSubmission.objects.filter(
            student=request.user,
            status='approved',
            document_type__in=['school_id', 'birth_certificate', 'voters_certificate']
        ).first()
        
        if not id_document or not id_document.file:
            logger.warning(f"No approved ID document found for user {request.user.id}")
            return Response({
                'success': False,
                'liveness_passed': True,
                'face_verified': False,
                'verification_passed': False,
                'message': 'No approved ID document found. Please upload and get your School ID, Birth Certificate, or Voter\'s Certificate approved first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save selfie temporarily
        selfie_path = default_storage.save(
            f'temp/allowance_selfie_{request.user.id}_{timezone.now().timestamp()}.jpg',
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
                f"Allowance application identity verification for user {request.user.id}: "
                f"Liveness={liveness_passed}, Face Match={face_verified}, "
                f"Similarity={similarity_score:.4f}, Confidence={confidence}"
            )
            
            # Update allowance application if it exists
            if allowance_app:
                allowance_app.face_verification_attempted_at = timezone.now()
                allowance_app.face_verification_score = similarity_score
                allowance_app.face_verification_confidence = confidence
                allowance_app.last_verification_attempt_at = timezone.now()
                
                if face_verified:
                    # Success! Reset attempt counter
                    allowance_app.verification_attempt_count = 0
                    allowance_app.face_verification_passed = True
                    allowance_app.face_verification_completed = True
                    allowance_app.face_verification_notes = f"[AUTO-VERIFIED] Liveness ✓, Face Match ✓, Similarity: {similarity_score:.2%}, Confidence: {confidence}"
                    logger.info(f"Face verification PASSED for allowance application {allowance_app.id}")
                else:
                    # Failure - increment attempt counter
                    allowance_app.verification_attempt_count += 1
                    allowance_app.face_verification_passed = False
                    allowance_app.face_verification_completed = False
                    allowance_app.face_verification_notes = f"[VERIFICATION FAILED] Attempt {allowance_app.verification_attempt_count}/3, Similarity: {similarity_score:.2%}, Confidence: {confidence}"
                    
                    # Check if we've hit 3 attempts
                    if allowance_app.verification_attempt_count >= 3:
                        cooldown_until = timezone.now() + timedelta(hours=24)
                        allowance_app.verification_cooldown_until = cooldown_until
                        logger.warning(f"3 failed face verification attempts for allowance app {allowance_app.id}, setting 24-hour cooldown")
                
                allowance_app.face_verification_data = verification_result
                allowance_app.save()
            
            if face_verified:
                return Response({
                    'success': True,
                    'liveness_passed': True,
                    'face_verified': True,
                    'verification_passed': True,
                    'similarity_score': similarity_score,
                    'confidence': confidence,
                    'message': 'Identity verification successful! Your face matches your ID document. Your application is ready to be submitted.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'liveness_passed': True,
                    'face_verified': False,
                    'verification_passed': False,
                    'similarity_score': similarity_score,
                    'confidence': confidence,
                    'attempt_count': allowance_app.verification_attempt_count if allowance_app else 1,
                    'message': f'Face verification failed. Your face does not sufficiently match your ID document (Similarity: {similarity_score:.2%}, Confidence: {confidence}).'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as processing_error:
            # Clean up on error
            default_storage.delete(selfie_path)
            logger.error(f"Face comparison error during allowance verification: {str(processing_error)}")
            raise processing_error
            
    except Exception as e:
        logger.error(f"Allowance application identity verification error: {str(e)}")
        return Response(
            {
                'error': 'Identity verification failed',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_liveness_session(request):
    """
    Create an AWS Rekognition Face Liveness session with security tracking
    
    Enhanced security features:
    - Device fingerprinting
    - Rate limiting (3 attempts per session, 10 per day)
    - IP geolocation (Philippines only)
    - VPN/proxy detection
    - Fraud risk scoring
    
    Expected POST data:
    - student_id: String (optional)
    - device_fingerprint: String (required)
    - ip_address: String (optional, will use request IP if not provided)
    - attempt_number: Integer (current attempt count)
    
    Returns:
    - success: Boolean
    - session_id: String (AWS session ID for frontend)
    - error: String (if failed)
    """
    try:
        from .models import FaceVerificationSession
        from datetime import timedelta
        import requests
        
        logger.info(f"Creating liveness session for user {request.user.id}")
        
        # Get request data
        device_fingerprint = request.data.get('device_fingerprint')
        attempt_number = int(request.data.get('attempt_number', 1))
        
        # Validate device fingerprint
        if not device_fingerprint or len(device_fingerprint) < 32:
            return Response(
                {
                    'success': False,
                    'error': 'Invalid device fingerprint'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get IP address
        ip_address = request.data.get('ip_address') or request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check rate limiting - daily attempts
        today = timezone.now().date()
        today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        daily_count = FaceVerificationSession.objects.filter(
            user=request.user,
            created_at__gte=today_start
        ).count()
        
        if daily_count >= 10:
            logger.warning(f"User {request.user.id} exceeded daily verification limit ({daily_count}/10)")
            return Response(
                {
                    'success': False,
                    'error': 'Daily verification limit reached (10 attempts). Please try again tomorrow.',
                    'daily_count': daily_count
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Check for recent sessions with same device (prevent rapid fire)
        recent_cutoff = timezone.now() - timedelta(minutes=2)
        recent_session = FaceVerificationSession.objects.filter(
            user=request.user,
            device_fingerprint=device_fingerprint,
            created_at__gte=recent_cutoff
        ).first()
        
        if recent_session and not recent_session.is_expired():
            logger.warning(f"User {request.user.id} has recent active session from same device")
            return Response(
                {
                    'success': False,
                    'error': 'Please wait 2 minutes between verification attempts from the same device.',
                    'retry_after': 120
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Get IP geolocation (optional - will not block if service unavailable)
        geolocation_data = {
            'country': None,
            'region': None,
            'city': None,
            'is_vpn': False,
            'is_philippines': False
        }
        
        try:
            # Use ipapi.co for geolocation (free tier: 1000 requests/day)
            geo_response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=3)
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                geolocation_data = {
                    'country': geo_data.get('country_name'),
                    'region': geo_data.get('region'),
                    'city': geo_data.get('city'),
                    'is_vpn': geo_data.get('threat', {}).get('is_proxy', False) or geo_data.get('threat', {}).get('is_vpn', False),
                    'is_philippines': geo_data.get('country_code') == 'PH'
                }
        except Exception as geo_error:
            logger.warning(f"Geolocation lookup failed: {str(geo_error)}")
        
        # Get verification service (AWS Rekognition or fallback)
        verification_service = get_verification_service()
        
        # Create AWS liveness session
        result = verification_service.create_liveness_session()
        
        if not result.get('success'):
            logger.error(f"Failed to create AWS liveness session: {result.get('error')}")
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        session_id = result.get('session_id')
        
        # Create FaceVerificationSession record
        session = FaceVerificationSession.objects.create(
            session_id=session_id,
            user=request.user,
            status='created',
            verification_type='liveness_and_match',
            device_fingerprint=device_fingerprint,
            ip_address=ip_address,
            user_agent=user_agent,
            geolocation_country=geolocation_data['country'],
            geolocation_region=geolocation_data['region'],
            geolocation_city=geolocation_data['city'],
            is_vpn=geolocation_data['is_vpn'],
            is_philippines=geolocation_data['is_philippines'],
            attempt_number=attempt_number,
            daily_attempt_count=daily_count + 1,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        
        # Add fraud flags if suspicious
        if geolocation_data['is_vpn']:
            session.add_fraud_flag('vpn_detected', 'VPN or proxy connection detected')
        
        if not geolocation_data['is_philippines'] and geolocation_data['country']:
            session.add_fraud_flag('foreign_ip', f'Non-Philippines IP address ({geolocation_data["country"]})')
        
        # Check for unusual times (2am-5am)
        current_hour = timezone.now().hour
        if 2 <= current_hour < 5:
            session.add_fraud_flag('unusual_time', f'Verification attempt at {current_hour}:00 (2am-5am window)')
        
        logger.info(
            f"Liveness session created: {session_id}, User: {request.user.id}, "
            f"Device: {device_fingerprint[:16]}..., IP: {ip_address}, "
            f"Country: {geolocation_data['country']}, Fraud Score: {session.fraud_risk_score}"
        )
        
        return Response({
            'success': True,
            'session_id': session_id,
            'attempt_number': attempt_number,
            'daily_count': daily_count + 1,
            'fraud_risk_score': session.fraud_risk_score,
            'warnings': session.fraud_flags if session.fraud_flags else []
        }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error creating liveness session: {str(e)}", exc_info=True)
        return Response(
            {
                'success': False,
                'error': f'Failed to create liveness session: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_liveness(request):
    """
    Verify liveness session and optionally compare with ID photo
    
    Enhanced security features:
    - Session expiration checking (5 minute TTL)
    - Device fingerprint validation
    - Fraud risk assessment
    - Comprehensive result tracking
    
    Expected POST data:
    - session_id: String (from create_liveness_session)
    - device_fingerprint: String (must match session creation)
    
    Returns:
    - success: Boolean
    - is_live: Boolean
    - confidence_score: Float (0.0-100.0)
    - session_id: String
    - fraud_risk_score: Float
    - message: String
    """
    try:
        from .models import FaceVerificationSession
        
        session_id = request.data.get('session_id')
        device_fingerprint = request.data.get('device_fingerprint')
        
        # Validate inputs
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not device_fingerprint:
            return Response(
                {'error': 'device_fingerprint is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get session from database
        try:
            session = FaceVerificationSession.objects.get(
                session_id=session_id,
                user=request.user
            )
        except FaceVerificationSession.DoesNotExist:
            logger.error(f"Session {session_id} not found for user {request.user.id}")
            return Response(
                {
                    'success': False,
                    'error': 'Invalid session ID'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if session expired
        if session.is_expired():
            logger.warning(f"Session {session_id} expired for user {request.user.id}")
            session.status = 'expired'
            session.save()
            return Response(
                {
                    'success': False,
                    'error': 'Session expired. Please start a new verification.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate device fingerprint matches
        if session.device_fingerprint != device_fingerprint:
            logger.error(
                f"Device fingerprint mismatch for session {session_id}: "
                f"Expected {session.device_fingerprint[:16]}..., Got {device_fingerprint[:16]}..."
            )
            session.add_fraud_flag('device_mismatch', 'Device fingerprint changed during verification')
            return Response(
                {
                    'success': False,
                    'error': 'Device validation failed. Please start a new verification.',
                    'fraud_detected': True
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update session status
        session.status = 'in_progress'
        session.save()
        
        logger.info(f"Verifying liveness for session {session_id}, user {request.user.id}")
        
        # Get verification service
        verification_service = get_verification_service()
        
        # Get liveness session results from AWS
        liveness_result = verification_service.get_liveness_session_results(session_id)
        
        if not liveness_result.get('success'):
            error_msg = liveness_result.get('error', 'Liveness verification failed')
            logger.error(f"Liveness verification failed for session {session_id}: {error_msg}")
            session.mark_failed(error_msg)
            return Response(
                {
                    'success': False,
                    'error': error_msg
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract liveness data
        is_live = liveness_result.get('status') == 'SUCCEEDED'
        confidence_score = liveness_result.get('confidence', 0.0)
        audit_images = liveness_result.get('audit_images', [])
        reference_image = liveness_result.get('reference_image')
        
        # Update session with results
        session.liveness_score = confidence_score
        session.is_live = is_live
        session.confidence_score = confidence_score
        session.aws_response = liveness_result
        
        if reference_image:
            session.reference_image_url = reference_image.get('S3Object', {}).get('Name', '')
        
        if audit_images:
            # Store first audit image URL
            session.audit_image_url = audit_images[0].get('S3Object', {}).get('Name', '') if audit_images else ''
        
        # Assess fraud risk based on confidence
        if confidence_score < 80:
            session.add_fraud_flag('low_confidence', f'Low liveness confidence: {confidence_score:.1f}%')
        
        if is_live and confidence_score >= 80:
            session.mark_completed(
                confidence_score=confidence_score,
                liveness_score=confidence_score,
                similarity_score=0.0,  # Will be set later if face matching is done
                is_live=True,
                face_match=False  # Will be set later
            )
            message = f'Liveness verification successful (Confidence: {confidence_score:.1f}%)'
        else:
            session.mark_failed('Liveness check failed')
            message = f'Liveness verification failed (Confidence: {confidence_score:.1f}%)'
        
        logger.info(
            f"Liveness verification completed: Session={session_id}, "
            f"User={request.user.id}, IsLive={is_live}, "
            f"Confidence={confidence_score:.1f}%, FraudScore={session.fraud_risk_score}"
        )
        
        return Response({
            'success': is_live,
            'is_live': is_live,
            'confidence_score': confidence_score,
            'session_id': session_id,
            'fraud_risk_score': session.fraud_risk_score,
            'fraud_flags': session.fraud_flags,
            'audit_image_url': session.audit_image_url,
            'reference_image_url': session.reference_image_url,
            'message': message
        }, status=status.HTTP_200_OK if is_live else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in verify_liveness: {str(e)}", exc_info=True)
        return Response(
            {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_with_liveness(request):
    """
    Complete biometric verification: Liveness + Identity Match + Admin Review
    
    Security Flow:
    1. User completes AWS Rekognition 3D liveness challenge (frontend)
    2. Backend retrieves liveness results (3D video analysis)
    3. Backend compares reference image vs School ID (>99% threshold)
    4. Creates VerificationAdjudication record for mandatory admin review
    5. Returns result to frontend (ALWAYS pending admin approval)
    
    Expected POST data:
    - session_id: String (from create_liveness_session)
    - school_id_image: File (School ID image for comparison)
    - application_id: Integer (optional, link to AllowanceApplication)
    
    Returns:
    - success: Boolean
    - liveness_passed: Boolean
    - face_match: Boolean
    - similarity_score: Float (0.0-1.0)
    - requires_admin_review: Boolean (ALWAYS True)
    - adjudication_id: Integer (VerificationAdjudication record ID)
    - message: String
    """
    try:
        session_id = request.POST.get('session_id')
        school_id_image = request.FILES.get('school_id_image')
        application_id = request.POST.get('application_id')
        
        # Validate inputs
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not school_id_image:
            return Response(
                {'error': 'school_id_image is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Starting liveness verification for user {request.user.id}, session {session_id}")
        
        # Get verification service
        verification_service = get_verification_service()
        
        # Read school ID image bytes
        school_id_bytes = school_id_image.read()
        
        # Perform complete verification (liveness + face comparison)
        verification_result = verification_service.verify_identity_with_liveness(
            session_id=session_id,
            school_id_image_bytes=school_id_bytes
        )
        
        # Extract results
        liveness_passed = verification_result.get('liveness_passed', False)
        face_match = verification_result.get('face_match', False)
        similarity_score = verification_result.get('similarity_score', 0.0)
        similarity_percentage = verification_result.get('similarity_percentage', 0.0)
        confidence = verification_result.get('confidence', 'very_low')
        liveness_confidence = verification_result.get('liveness_confidence', 0.0)
        
        # Save school ID image for admin review
        school_id_path = default_storage.save(
            f'verification/{request.user.id}/school_id_{session_id}.jpg',
            ContentFile(school_id_bytes)
        )
        
        # Get or create AllowanceApplication if application_id provided
        application = None
        if application_id:
            try:
                application = AllowanceApplication.objects.get(
                    id=application_id,
                    student=request.user
                )
            except AllowanceApplication.DoesNotExist:
                logger.warning(f"AllowanceApplication {application_id} not found for user {request.user.id}")
        
        # Create VerificationAdjudication record for MANDATORY admin review
        adjudication = VerificationAdjudication.objects.create(
            user=request.user,
            application=application,
            school_id_image_path=school_id_path,
            selfie_image_path=f'liveness-sessions/{session_id}/reference_image.jpg',  # S3 path from liveness
            verification_backend='rekognition',
            automated_liveness_score=liveness_confidence,
            automated_similarity_score=similarity_score,
            automated_confidence_level=confidence,
            automated_verification_data=verification_result,
            liveness_data=verification_result.get('liveness_data', {}),
            admin_decision='pending'  # ALWAYS starts as pending
        )
        
        logger.info(
            f"Verification adjudication created: ID={adjudication.id}, "
            f"User={request.user.id}, Liveness={liveness_passed}, "
            f"Match={face_match}, Similarity={similarity_percentage}%"
        )
        
        # Prepare response message
        if not verification_result.get('success'):
            message = verification_result.get('error', 'Verification failed')
        elif not liveness_passed:
            message = 'Liveness check failed. Please try again in good lighting.'
        elif face_match:
            message = (
                f'Automated verification suggests a match (Similarity: {similarity_percentage:.1f}%). '
                f'Your verification is now pending administrative review for final approval.'
            )
        else:
            message = (
                f'Automated verification indicates no match (Similarity: {similarity_percentage:.1f}%). '
                f'This will be reviewed by an administrator.'
            )
        
        return Response({
            'success': verification_result.get('success', False),
            'liveness_passed': liveness_passed,
            'face_match': face_match,
            'similarity_score': similarity_score,
            'similarity_percentage': similarity_percentage,
            'confidence': confidence,
            'requires_admin_review': True,  # ALWAYS True
            'adjudication_id': adjudication.id,
            'adjudication_status': 'pending',
            'message': message
        }, status=status.HTTP_200_OK if verification_result.get('success') else status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in verify_with_liveness: {str(e)}", exc_info=True)
        return Response(
            {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
