"""
Application Email Service
Handles sending email notifications for application status changes
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from .models import AllowanceApplication
import logging

logger = logging.getLogger(__name__)


class ApplicationEmailService:
    """Service for handling application-related email notifications"""
    
    @staticmethod
    def send_confirmation_email(application: AllowanceApplication) -> bool:
        """
        Send confirmation email when a student submits a new application
        
        Args:
            application: The AllowanceApplication instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            student = application.student
            subject = f'TCU-CEAA: Application Received - {application.get_application_type_display()}'
            
            # Render HTML email template
            html_message = render_to_string('emails/application_received.html', {
                'student_name': f"{student.first_name} {student.last_name}",
                'application': application,
                'support_email': settings.DEFAULT_FROM_EMAIL,
            })
            
            # Create plain text version
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Update email tracking
            application.email_sent = True
            application.email_sent_at = timezone.now()
            application.save(update_fields=['email_sent', 'email_sent_at'])
            
            logger.info(f"Application confirmation email sent to {student.email} for application #{application.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send application confirmation email for #{application.id}: {str(e)}")
            
            # Track error
            application.notification_error = str(e)
            application.save(update_fields=['notification_error'])
            
            return False
    
    @staticmethod
    def send_status_update_email(application: AllowanceApplication, previous_status: str = None) -> bool:
        """
        Send email notification when application status changes
        
        Args:
            application: The AllowanceApplication instance
            previous_status: Previous status before change (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            student = application.student
            status_display = application.get_status_display()
            
            # Determine email subject based on status
            status_subjects = {
                'approved': 'TCU-CEAA: Your Application Has Been Approved! 🎉',
                'rejected': 'TCU-CEAA: Application Status Update',
                'disbursed': 'TCU-CEAA: Allowance Disbursed Successfully! 💰',
            }
            
            subject = status_subjects.get(application.status, f'TCU-CEAA: Application Status Update - {status_display}')
            
            # Render HTML email template
            html_message = render_to_string('emails/application_status_update.html', {
                'student_name': f"{student.first_name} {student.last_name}",
                'application': application,
                'previous_status': previous_status,
                'support_email': settings.DEFAULT_FROM_EMAIL,
            })
            
            # Create plain text version
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Status update email sent to {student.email} for application #{application.id} (status: {application.status})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send status update email for application #{application.id}: {str(e)}")
            
            # Track error
            application.notification_error = str(e)
            application.save(update_fields=['notification_error'])
            
            return False
    
    @classmethod
    def notify_application_submission(cls, application: AllowanceApplication) -> dict:
        """
        Convenience method to send confirmation email on application submission
        
        Args:
            application: The AllowanceApplication instance
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        success = cls.send_confirmation_email(application)
        
        if success:
            return {
                'success': True,
                'message': 'Application confirmation email sent successfully'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to send application confirmation email'
            }
    
    @classmethod
    def notify_status_change(cls, application: AllowanceApplication, previous_status: str = None) -> dict:
        """
        Convenience method to send status update email
        
        Args:
            application: The AllowanceApplication instance
            previous_status: Previous status before change
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        success = cls.send_status_update_email(application, previous_status)
        
        if success:
            return {
                'success': True,
                'message': f'Status update email sent successfully (new status: {application.status})'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to send status update email'
            }


# Convenience functions
def send_application_confirmation(application: AllowanceApplication) -> bool:
    """Send confirmation email for new application"""
    return ApplicationEmailService.send_confirmation_email(application)


def send_application_status_update(application: AllowanceApplication, previous_status: str = None) -> bool:
    """Send status update email for application"""
    return ApplicationEmailService.send_status_update_email(application, previous_status)
