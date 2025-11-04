from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_verification_code_email(email, code):
    """
    Send email verification code to user during registration.
    
    Args:
        email: Email address to send to
        code: 6-digit verification code
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        subject = "TCU-CEAA Email Verification Code"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #8b0000; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code-box {{ background: #fff; border: 3px dashed #8b0000; padding: 20px; text-align: center; margin: 20px 0; border-radius: 10px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #8b0000; letter-spacing: 5px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #777; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🎓 TCU-CEAA Email Verification</h2>
                </div>
                <div class="content">
                    <h3>Verify Your Email Address</h3>
                    <p>Thank you for registering with the Taguig City University – City Educational Assistance Allowance (TCU-CEAA) system!</p>
                    
                    <p>To complete your registration, please use the verification code below:</p>
                    
                    <div class="code-box">
                        <div class="code">{code}</div>
                        <p style="margin: 10px 0 0 0; color: #666;">This code expires in 10 minutes</p>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important Security Information:</strong>
                        <ul style="margin: 10px 0;">
                            <li>This code is valid for <strong>10 minutes only</strong></li>
                            <li>Do not share this code with anyone</li>
                            <li>TCU-CEAA staff will never ask for your verification code</li>
                            <li>If you didn't request this code, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>After entering your code, you can complete your registration and access the TCU-CEAA application system.</p>
                    
                    <p>If you have any questions, please contact us at <a href="mailto:ceaainfo@tcu.edu.ph">ceaainfo@tcu.edu.ph</a></p>
                    
                    <p>
                        Best regards,<br>
                        <strong>TCU-CEAA System Team</strong><br>
                        Taguig City University
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 Taguig City University – City Educational Assistance Allowance</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
TCU-CEAA Email Verification

Thank you for registering with the Taguig City University – City Educational Assistance Allowance (TCU-CEAA) system!

Your Verification Code: {code}

This code expires in 10 minutes.

IMPORTANT SECURITY INFORMATION:
- This code is valid for 10 minutes only
- Do not share this code with anyone
- TCU-CEAA staff will never ask for your verification code
- If you didn't request this code, please ignore this email

After entering your code, you can complete your registration and access the TCU-CEAA application system.

If you have any questions, please contact us at ceaainfo@tcu.edu.ph

Best regards,
TCU-CEAA System Team
Taguig City University

---
© 2025 Taguig City University – City Educational Assistance Allowance
This is an automated message. Please do not reply to this email.
        """
        
        # Create email
        email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email_message.attach_alternative(html_content, "text/html")
        
        # Send email
        email_message.send(fail_silently=False)
        
        logger.info(f"Verification code email sent successfully to {email}")
        return True, None
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to send verification email to {email}: {error_message}")
        return False, error_message


def send_approval_email(application):
    """
    Send email notification when an allowance application is approved.
    
    Args:
        application: AllowanceApplication instance
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        student = application.student
        student_email = student.email
        student_name = f"{student.first_name} {student.last_name}"
        
        # Format the amount
        amount = f"₱{application.amount:,.2f}"
        
        # Get application type display name
        application_type = application.get_application_type_display()
        
        # Email subject
        subject = "Congratulations! Your TCU-CEAA Application Has Been Approved!"
        
        # Email from
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Email to
        to_email = [student_email]
        
        # Render HTML content from template
        html_content = render_to_string('approved_email.html', {
            'student_name': student_name,
            'application_type': application_type,
            'amount': amount,
        })
        
        # Plain text version for email clients that don't support HTML
        text_content = f"""
Dear {student_name},

Congratulations! Your application for the Taguig City University – City Educational Assistance Allowance (TCU-CEAA)
has been approved.

Application Details:
- Status: APPROVED
- Application Type: {application_type}
- Amount: {amount}

Next Steps:
- Wait for further instructions regarding the release schedule of your allowance.
- Make sure your student information is updated in the university portal.
- Check your dashboard regularly for updates on the disbursement status.

For questions or assistance, you may contact ceaainfo@tcu.edu.ph or visit the Student Affairs Office during office hours.

Once again, congratulations, and we wish you continued success in your studies!

Best regards,
Scholarship and Financial Assistance Office
Taguig City University (TCU-CEAA)
📧 ceaainfo@tcu.edu.ph | 🌐 www.tcu.edu.ph

---
© 2025 Taguig City University – City Educational Assistance Allowance
This is an automated message. Please do not reply to this email.
        """
        
        # Create the email
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        
        # Send the email
        email.send(fail_silently=False)
        
        # Update the application to mark email as sent
        application.email_sent = True
        application.email_sent_at = timezone.now()
        application.notification_error = None  # Clear any previous errors
        application.save()
        
        logger.info(f"Approval email sent successfully to {student_email} for application {application.id}")
        return True, None
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to send approval email for application {application.id}: {error_message}")
        
        # Store the error in the application
        try:
            application.notification_error = error_message
            application.save()
        except:
            pass
        
        return False, error_message


def send_password_reset_email(email, code, username):
    """
    Send password reset code to user.
    
    Args:
        email: Email address to send to
        code: 6-digit verification code
        username: Username of the account
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        subject = "TCU-CEAA Password Reset Code"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #8b0000; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code-box {{ background: #fff; border: 3px dashed #8b0000; padding: 20px; text-align: center; margin: 20px 0; border-radius: 10px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #8b0000; letter-spacing: 5px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .info {{ background: #d1ecf1; border-left: 4px solid #0c5460; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #777; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔐 TCU-CEAA Password Reset</h2>
                </div>
                <div class="content">
                    <h3>Password Reset Request</h3>
                    <p>Hello <strong>{username}</strong>,</p>
                    
                    <p>We received a request to reset the password for your TCU-CEAA account associated with this email address.</p>
                    
                    <p>Use the verification code below to reset your password:</p>
                    
                    <div class="code-box">
                        <div class="code">{code}</div>
                        <p style="margin: 10px 0 0 0; color: #666;">This code expires in 10 minutes</p>
                    </div>
                    
                    <div class="info">
                        <strong>📋 How to reset your password:</strong>
                        <ol style="margin: 10px 0;">
                            <li>Enter the verification code above in the password reset form</li>
                            <li>Create a new strong password (minimum 8 characters)</li>
                            <li>Confirm your new password</li>
                            <li>Log in with your new password</li>
                        </ol>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important Security Information:</strong>
                        <ul style="margin: 10px 0;">
                            <li>This code is valid for <strong>10 minutes only</strong></li>
                            <li>Do not share this code with anyone</li>
                            <li>TCU-CEAA staff will never ask for your verification code</li>
                            <li><strong>If you didn't request this password reset, please ignore this email and your password will remain unchanged</strong></li>
                            <li>Consider changing your password if you suspect unauthorized access</li>
                        </ul>
                    </div>
                    
                    <p>If you continue to have problems accessing your account, please contact us at <a href="mailto:ceaainfo@tcu.edu.ph">ceaainfo@tcu.edu.ph</a></p>
                    
                    <p>
                        Best regards,<br>
                        <strong>TCU-CEAA System Team</strong><br>
                        Taguig City University
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 Taguig City University – City Educational Assistance Allowance</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
TCU-CEAA Password Reset

Hello {username},

We received a request to reset the password for your TCU-CEAA account associated with this email address.

Your Password Reset Code: {code}

This code expires in 10 minutes.

HOW TO RESET YOUR PASSWORD:
1. Enter the verification code above in the password reset form
2. Create a new strong password (minimum 8 characters)
3. Confirm your new password
4. Log in with your new password

IMPORTANT SECURITY INFORMATION:
- This code is valid for 10 minutes only
- Do not share this code with anyone
- TCU-CEAA staff will never ask for your verification code
- If you didn't request this password reset, please ignore this email and your password will remain unchanged
- Consider changing your password if you suspect unauthorized access

If you continue to have problems accessing your account, please contact us at ceaainfo@tcu.edu.ph

Best regards,
TCU-CEAA System Team
Taguig City University

---
© 2025 Taguig City University – City Educational Assistance Allowance
This is an automated message. Please do not reply to this email.
        """
        
        # Create email
        email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email_message.attach_alternative(html_content, "text/html")
        
        # Send email
        email_message.send(fail_silently=False)
        
        logger.info(f"Password reset email sent successfully to {email}")
        return True, None
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to send password reset email to {email}: {error_message}")
        return False, error_message


def retry_failed_emails():
    """
    Retry sending emails for approved applications that haven't been sent yet.
    This can be called from a management command or admin action.
    
    Returns:
        dict: Statistics about the retry operation
    """
    from .models import AllowanceApplication
    
    # Get approved applications without sent emails
    pending_emails = AllowanceApplication.objects.filter(
        status='approved',
        email_sent=False
    )
    
    stats = {
        'total': pending_emails.count(),
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for application in pending_emails:
        success, error = send_approval_email(application)
        if success:
            stats['success'] += 1
        else:
            stats['failed'] += 1
            stats['errors'].append({
                'application_id': application.id,
                'student_email': application.student.email,
                'error': error
            })
    
    return stats
