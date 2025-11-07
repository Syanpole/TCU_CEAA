"""
Email Verification Service
Handles email verification code generation, validation, and email sending
"""
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import EmailVerificationCode, CustomUser
import logging

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for handling email verification operations"""
    
    # Code validity period (15 minutes)
    CODE_EXPIRY_MINUTES = 15
    
    # Code length
    CODE_LENGTH = 6
    
    # Maximum resend attempts per hour
    MAX_RESEND_PER_HOUR = 3
    
    @staticmethod
    def generate_verification_code() -> str:
        """
        Generate a random 6-digit verification code
        
        Returns:
            str: 6-digit numeric code
        """
        return ''.join(random.choices(string.digits, k=VerificationService.CODE_LENGTH))
    
    @classmethod
    def create_verification(cls, user: CustomUser) -> 'EmailVerificationCode':
        """
        Create a new email verification record for a user
        
        Args:
            user: The CustomUser instance
            
        Returns:
            EmailVerificationCode: The created verification record
        """
        # Invalidate any existing active verifications for this user
        EmailVerificationCode.objects.filter(
            email=user.email,
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        # Generate new code
        code = cls.generate_verification_code()
        expires_at = timezone.now() + timedelta(minutes=cls.CODE_EXPIRY_MINUTES)
        
        # Create verification record
        verification = EmailVerificationCode.objects.create(
            email=user.email,
            code=code,
            expires_at=expires_at
        )
        
        logger.info(f"Created verification code for user {user.username} (expires: {expires_at})")
        
        return verification
    
    @classmethod
    def send_verification_email(cls, user: CustomUser, code: str) -> bool:
        """
        Send verification email to user
        
        Args:
            user: The CustomUser instance
            code: The verification code to send
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = 'TCU-CEAA: Verify Your Email Address'
            
            # Render HTML email template
            html_message = render_to_string('emails/verification_code.html', {
                'user': user,
                'code': code,
                'expiry_minutes': cls.CODE_EXPIRY_MINUTES,
                'site_name': 'TCU-CEAA Portal',
                'support_email': settings.DEFAULT_FROM_EMAIL
            })
            
            # Create plain text version
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Verification email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            return False
    
    @classmethod
    def validate_code(cls, user: CustomUser, code: str) -> dict:
        """
        Validate a verification code for a user
        
        Args:
            user: The CustomUser instance
            code: The verification code to validate
            
        Returns:
            dict: {'valid': bool, 'message': str, 'verification': EmailVerificationCode or None}
        """
        try:
            # Find the verification record
            verification = EmailVerificationCode.objects.filter(
                email=user.email,
                code=code,
                is_used=False
            ).first()
            
            if not verification:
                return {
                    'valid': False,
                    'message': 'Invalid verification code. Please check and try again.',
                    'verification': None
                }
            
            # Check if code has expired
            if verification.is_expired():
                return {
                    'valid': False,
                    'message': f'Verification code has expired. Please request a new code.',
                    'verification': None
                }
            
            # Mark as used
            verification.mark_as_used()
            
            # Update user email verification status
            user.is_email_verified = True
            user.email_verified_at = timezone.now()
            user.save()
            
            logger.info(f"Email verified successfully for user {user.username}")
            
            return {
                'valid': True,
                'message': 'Email verified successfully!',
                'verification': verification
            }
            
        except Exception as e:
            logger.error(f"Error validating verification code for {user.username}: {str(e)}")
            return {
                'valid': False,
                'message': 'An error occurred during verification. Please try again.',
                'verification': None
            }
    
    @classmethod
    def can_resend_code(cls, user: CustomUser) -> tuple[bool, str]:
        """
        Check if user can request another verification code
        
        Args:
            user: The CustomUser instance
            
        Returns:
            tuple: (can_resend: bool, message: str)
        """
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        # Count verification codes sent in the last hour
        recent_codes = EmailVerificationCode.objects.filter(
            email=user.email,
            created_at__gte=one_hour_ago
        ).count()
        
        if recent_codes >= cls.MAX_RESEND_PER_HOUR:
            return False, f'Maximum {cls.MAX_RESEND_PER_HOUR} verification codes per hour. Please try again later.'
        
        # Check if there's a recent code (within 1 minute)
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        very_recent_code = EmailVerificationCode.objects.filter(
            email=user.email,
            created_at__gte=one_minute_ago
        ).exists()
        
        if very_recent_code:
            return False, 'Please wait at least 1 minute before requesting another code.'
        
        return True, 'OK'
    
    @classmethod
    def resend_verification_code(cls, user: CustomUser) -> dict:
        """
        Resend verification code to user
        
        Args:
            user: The CustomUser instance
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Check if user can resend
        can_resend, message = cls.can_resend_code(user)
        if not can_resend:
            return {'success': False, 'message': message}
        
        # Create new verification
        verification = cls.create_verification(user)
        
        # Send email
        email_sent = cls.send_verification_email(user, verification.code)
        
        if email_sent:
            return {
                'success': True,
                'message': f'Verification code sent to {user.email}. Please check your inbox.'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to send verification email. Please try again later.'
            }


# Convenience function for creating and sending verification
def send_verification_code_to_user(user: CustomUser) -> dict:
    """
    Create and send verification code to user
    
    Args:
        user: The CustomUser instance
        
    Returns:
        dict: {'success': bool, 'message': str}
    """
    verification = VerificationService.create_verification(user)
    email_sent = VerificationService.send_verification_email(user, verification.code)
    
    if email_sent:
        return {
            'success': True,
            'message': f'Verification code sent to {user.email}'
        }
    else:
        return {
            'success': False,
            'message': 'Failed to send verification email'
        }
