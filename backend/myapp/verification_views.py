"""
Email Verification Views for TCU-CEAA System

This module handles:
1. Sending verification codes to new registrants
2. Verifying email codes
3. Resending verification codes
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import EmailVerificationCode, CustomUser
from .email_utils import send_verification_code_email
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
    """
    Send a verification code to the provided email address.
    Used during registration process.
    """
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate email format
    if '@' not in email or '.' not in email:
        return Response({
            'error': 'Invalid email format'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if email is already registered and verified
    if CustomUser.objects.filter(email=email, is_email_verified=True).exists():
        return Response({
            'error': 'This email is already registered and verified'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Rate limiting: Check if user requested code too recently (within 1 minute)
    recent_code = EmailVerificationCode.objects.filter(
        email=email,
        created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
    ).first()
    
    if recent_code:
        return Response({
            'error': 'Please wait 1 minute before requesting another code',
            'retry_after': 60
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        # Create verification code
        verification = EmailVerificationCode.create_verification_code(email)
        
        # Send email with verification code
        success, error_message = send_verification_code_email(
            email=email,
            code=verification.code
        )
        
        if success:
            logger.info(f"Verification code sent to {email}")
            return Response({
                'success': True,
                'message': 'Verification code sent to your email',
                'expires_in': 600  # 10 minutes
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"Failed to send verification email to {email}: {error_message}")
            verification.delete()  # Clean up if email failed
            return Response({
                'error': 'Failed to send verification email. Please try again.',
                'details': error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error sending verification code to {email}: {str(e)}")
        return Response({
            'error': 'An error occurred while sending verification code'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_code(request):
    """
    Verify the email verification code provided by user.
    Returns success if code is valid and not expired.
    """
    email = request.data.get('email', '').strip().lower()
    code = request.data.get('code', '').strip()
    
    if not email or not code:
        return Response({
            'error': 'Email and verification code are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find the most recent unused code for this email
    verification = EmailVerificationCode.objects.filter(
        email=email,
        code=code,
        is_used=False
    ).order_by('-created_at').first()
    
    if not verification:
        return Response({
            'error': 'Invalid verification code',
            'verified': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if code is expired
    if verification.is_expired():
        return Response({
            'error': 'Verification code has expired. Please request a new one.',
            'verified': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for too many attempts (max 5)
    if verification.attempts >= 5:
        verification.is_used = True  # Invalidate after too many attempts
        verification.save()
        return Response({
            'error': 'Too many verification attempts. Please request a new code.',
            'verified': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Increment attempts
    verification.increment_attempts()
    
    # Mark as used
    verification.is_used = True
    verification.save()
    
    logger.info(f"Email verified successfully for {email}")
    
    return Response({
        'success': True,
        'verified': True,
        'message': 'Email verified successfully! You can now complete your registration.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_code(request):
    """
    Resend verification code to the email address.
    Same as send_verification_code but explicitly for resending.
    """
    return send_verification_code(request)
