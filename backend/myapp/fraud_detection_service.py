"""
Fraud Detection Service
Handles fraud detection, reporting, and notification when face verification fails
"""

import logging
from typing import Dict, Optional
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .fraud_detection_models import FraudReport, FraudNotification, UserAccountAction
from .models import CustomUser, DocumentSubmission

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """
    Service for detecting, reporting, and handling fraud cases.
    
    Accounts for natural facial changes:
    - Weight gain/loss can affect facial structure
    - Facial hair growth changes appearance significantly
    - Aging affects skin and features
    - Different angles, lighting, and expressions
    
    Thresholds are more lenient to avoid false positives from natural changes.
    """
    
    # Thresholds for fraud detection (adjusted for natural changes)
    FACE_MATCH_FRAUD_THRESHOLD = 0.35  # Below this = likely fraud (very low similarity)
    UNCERTAIN_THRESHOLD = 0.45          # 0.35-0.45 = uncertain, needs manual review
    ACCEPTABLE_MATCH = 0.50             # Above this = acceptable match with natural changes
    MAX_VERIFICATION_ATTEMPTS = 3       # Max attempts before flagging
    
    def __init__(self):
        """Initialize fraud detection service."""
        pass
    
    @transaction.atomic
    def report_fraud_attempt(
        self,
        user: CustomUser,
        verification_data: Dict,
        document: Optional[DocumentSubmission] = None,
        application_type: str = 'full_application',
        application_id: Optional[int] = None
    ) -> FraudReport:
        """
        Create a fraud report when face verification fails.
        
        Args:
            user: User who failed verification
            verification_data: Face verification results
            document: Related document submission
            application_type: 'full_application' or 'allowance_application'
            application_id: ID of the related application
            
        Returns:
            Created FraudReport instance
        """
        try:
            # Determine fraud type and severity
            fraud_type, severity = self._analyze_fraud_type(verification_data)
            
            # Check previous attempts
            previous_attempts = FraudReport.objects.filter(
                suspected_user=user,
                status__in=['pending', 'investigating']
            ).count()
            
            # Adjust severity based on attempts
            if previous_attempts >= 2:
                severity = 'critical'
                fraud_type = 'multiple_attempts'
            
            # Create fraud report
            fraud_report = FraudReport.objects.create(
                suspected_user=user,
                fraud_type=fraud_type,
                severity=severity,
                status='pending',
                document_submission=document,
                face_match_score=verification_data.get('similarity_score', 0.0),
                liveness_data=verification_data.get('liveness_data', {}),
                verification_attempts=previous_attempts + 1,
                description=self._generate_fraud_description(user, verification_data, previous_attempts),
                evidence_data={
                    'verification_result': verification_data,
                    'timestamp': timezone.now().isoformat(),
                    'previous_attempts': previous_attempts,
                    'application_type': application_type,
                    'application_id': application_id,
                    'user_email': user.email,
                    'user_student_id': getattr(user, 'student_id', None),
                }
            )
            
            # Link to application if provided
            if application_type == 'full_application' and application_id:
                from .models import FullApplication
                try:
                    app = FullApplication.objects.get(id=application_id)
                    fraud_report.application = app
                    fraud_report.save()
                except FullApplication.DoesNotExist:
                    pass
            elif application_type == 'allowance_application' and application_id:
                from .models import AllowanceApplication
                try:
                    app = AllowanceApplication.objects.get(id=application_id)
                    fraud_report.allowance_application = app
                    fraud_report.save()
                except AllowanceApplication.DoesNotExist:
                    pass
            
            # Suspend user account
            self._suspend_user_account(user, fraud_report, severity)
            
            # Notify admins
            self._notify_admins(fraud_report)
            
            # Send email to admins
            self._send_fraud_alert_email(fraud_report)
            
            logger.warning(
                f"Fraud report created: {fraud_report.report_id} for user {user.email} "
                f"(Score: {verification_data.get('similarity_score', 0.0):.2f})"
            )
            
            return fraud_report
            
        except Exception as e:
            logger.error(f"Error creating fraud report: {str(e)}")
            raise
    
    def _analyze_fraud_type(self, verification_data: Dict) -> tuple:
        """
        Analyze verification data to determine fraud type and severity.
        Considers natural facial changes to avoid false positives.
        
        Returns:
            Tuple of (fraud_type, severity)
        """
        similarity_score = verification_data.get('similarity_score', 0.0)
        liveness_passed = verification_data.get('liveness_passed', False)
        confidence = verification_data.get('confidence', 'unknown')
        
        # Very low similarity = likely stolen identity
        if similarity_score < self.FACE_MATCH_FRAUD_THRESHOLD:
            return ('stolen_identity', 'critical')
        
        # Uncertain range (0.35-0.45) = possible natural changes or fraud
        # If liveness passed, more likely natural changes than fraud
        if similarity_score < self.UNCERTAIN_THRESHOLD:
            if liveness_passed:
                return ('face_mismatch', 'medium')  # Natural changes possible, needs review
            else:
                return ('stolen_identity', 'high')  # No liveness + low match = fraud
        
        # Liveness failed = using photo instead of live selfie
        if not liveness_passed:
            return ('liveness_failed', 'high')
        
        # Acceptable range (0.45-0.50) but below auto-approve threshold
        # Likely natural changes (weight gain, facial hair, aging)
        if similarity_score < self.ACCEPTABLE_MATCH and liveness_passed:
            return ('face_mismatch', 'low')  # Natural changes, low risk
        
        # Default
        return ('face_mismatch', 'medium')
    
    def _get_liveness_check(self, verification_data: Dict, check_type: str) -> bool:
        """
        Safely extract liveness check result.
        Handles both nested dict format and simple boolean format.
        
        Args:
            verification_data: Verification data dict
            check_type: 'colorFlash', 'blink', or 'movement'
            
        Returns:
            True if check passed, False otherwise
        """
        liveness_data = verification_data.get('liveness_data', {})
        
        # Handle simple boolean format (e.g., {'colorFlash': True})
        if isinstance(liveness_data.get(check_type), bool):
            return liveness_data.get(check_type, False)
        
        # Handle nested dict format (e.g., {'colorFlash': {'passed': True}})
        if isinstance(liveness_data.get(check_type), dict):
            return liveness_data.get(check_type, {}).get('passed', False)
        
        return False
    
    def _generate_fraud_description(
        self,
        user: CustomUser,
        verification_data: Dict,
        previous_attempts: int
    ) -> str:
        """Generate detailed fraud description."""
        description = f"""
🚨 FRAUD ALERT - Face Verification Failed

User Details:
- Name: {user.get_full_name()}
- Email: {user.email}
- Student ID: {getattr(user, 'student_id', 'N/A')}
- Account Created: {user.date_joined.strftime('%Y-%m-%d %H:%M')}

Verification Failure:
- Face Match Score: {verification_data.get('similarity_score', 0.0):.4f} (Threshold: 0.50)
- Liveness Verification: {'✅ PASSED' if verification_data.get('liveness_passed') else '❌ FAILED'}
- Confidence Level: {verification_data.get('confidence', 'unknown')}

Natural Changes Consideration:
- Score 0.45-0.50: Likely natural changes (weight, facial hair, aging)
- Score 0.35-0.45: Uncertain - may be natural changes or fraud
- Score < 0.35: Likely different person (fraud)

Liveness Checks:
- Color Flash: {'✅' if self._get_liveness_check(verification_data, 'colorFlash') else '❌'}
- Blink Detection: {'✅' if self._get_liveness_check(verification_data, 'blink') else '❌'}
- Movement Detection: {'✅' if self._get_liveness_check(verification_data, 'movement') else '❌'}

Attempt History:
- Previous Failed Attempts: {previous_attempts}
- Current Attempt: {previous_attempts + 1}

⚠️ RECOMMENDED ACTIONS:
1. Review match score and confidence level
2. Consider if natural changes could explain low score (weight gain, facial hair, aging)
3. Check ID document date - older IDs more likely to show natural changes
4. Review all submitted documents for consistency
5. If score < 0.35: Likely fraud - suspend and investigate
6. If score 0.35-0.50 with liveness passed: Possible natural changes - manual review
7. Contact user for updated photo if natural changes suspected
8. Contact real identity owner only if strong fraud indicators

This appears to be an attempt to use someone else's identity for scholarship fraud.
"""
        return description.strip()
    
    def _suspend_user_account(
        self,
        user: CustomUser,
        fraud_report: FraudReport,
        severity: str
    ):
        """
        Suspend user account based on fraud severity.
        """
        try:
            # Determine suspension duration
            if severity == 'critical':
                action_type = 'suspended'
                reason = "Account suspended due to critical fraud detection (face verification failed)"
                expires_at = None  # Indefinite suspension
            elif severity == 'high':
                action_type = 'suspended'
                reason = "Account suspended due to failed face verification"
                expires_at = timezone.now() + timezone.timedelta(days=30)
            else:
                action_type = 'flagged'
                reason = "Account flagged for review due to face verification failure"
                expires_at = None
            
            # Create account action
            UserAccountAction.objects.create(
                user=user,
                fraud_report=fraud_report,
                action_type=action_type,
                reason=reason,
                performed_by=None,  # Automatic system action
                expires_at=expires_at
            )
            
            # Update user status
            user.is_active = False if action_type == 'suspended' else True
            user.save()
            
            logger.info(f"User account {user.email} - Action: {action_type}")
            
        except Exception as e:
            logger.error(f"Error suspending user account: {str(e)}")
    
    def _notify_admins(self, fraud_report: FraudReport):
        """
        Create notifications for all admin users.
        """
        try:
            # Get all admin users
            admins = CustomUser.objects.filter(role='admin', is_active=True)
            
            # Determine notification priority
            priority = 'urgent' if fraud_report.severity == 'critical' else 'high'
            
            # Create notifications
            for admin in admins:
                FraudNotification.objects.create(
                    fraud_report=fraud_report,
                    notification_type='new_fraud_report',
                    admin=admin,
                    title=f"🚨 Fraud Alert: {fraud_report.suspected_user.get_full_name()}",
                    message=f"""
A potential fraud attempt has been detected and requires immediate attention.

Report ID: {fraud_report.report_id}
User: {fraud_report.suspected_user.get_full_name()} ({fraud_report.suspected_user.email})
Fraud Type: {fraud_report.get_fraud_type_display()}
Severity: {fraud_report.get_severity_display()}
Face Match Score: {fraud_report.face_match_score:.2f}
Verification Attempts: {fraud_report.verification_attempts}

The user account has been automatically suspended pending investigation.

Please review the fraud report and take appropriate action:
1. Review submitted documents
2. Contact real identity owner if possible
3. Confirm or dismiss fraud report
4. Update investigation status

Action Required: Immediate Review
                    """.strip(),
                    priority=priority
                )
            
            logger.info(f"Created {admins.count()} admin notifications for fraud report {fraud_report.report_id}")
            
        except Exception as e:
            logger.error(f"Error creating admin notifications: {str(e)}")
    
    def _send_fraud_alert_email(self, fraud_report: FraudReport):
        """
        Send email alert to admin email addresses.
        """
        try:
            subject = f"🚨 FRAUD ALERT - {fraud_report.report_id}"
            
            message = f"""
CRITICAL SECURITY ALERT - POTENTIAL SCHOLARSHIP FRAUD DETECTED

Report ID: {fraud_report.report_id}
Timestamp: {fraud_report.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Severity: {fraud_report.get_severity_display()}

SUSPECTED USER:
- Name: {fraud_report.suspected_user.get_full_name()}
- Email: {fraud_report.suspected_user.email}
- Student ID: {getattr(fraud_report.suspected_user, 'student_id', 'N/A')}

FRAUD DETAILS:
- Type: {fraud_report.get_fraud_type_display()}
- Face Match Score: {fraud_report.face_match_score:.4f} (Threshold: 0.60)
- Verification Attempts: {fraud_report.verification_attempts}
- Account Status: SUSPENDED

IMMEDIATE ACTIONS REQUIRED:
1. Log into admin panel to review fraud report
2. Examine all submitted documents
3. Contact real identity owner if contact information available
4. Coordinate with security team if necessary
5. File formal report if fraud confirmed

The user account has been automatically suspended to prevent further fraudulent activity.

DO NOT REPLY to this email. Log into the admin panel to take action.

System: TCU-CEAA Scholarship Management
Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # Get admin emails from settings
            admin_emails = getattr(settings, 'FRAUD_ALERT_EMAILS', [])
            if not admin_emails:
                admin_emails = [admin[1] for admin in getattr(settings, 'ADMINS', [])]
            
            if admin_emails:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    fail_silently=False,
                )
                logger.info(f"Fraud alert email sent to {len(admin_emails)} admins")
            else:
                logger.warning("No admin emails configured for fraud alerts")
                
        except Exception as e:
            logger.error(f"Error sending fraud alert email: {str(e)}")
    
    def handle_real_owner_contact(
        self,
        fraud_report: FraudReport,
        contact_info: Dict,
        admin: CustomUser
    ):
        """
        Handle when the real identity owner contacts about fraud.
        
        Args:
            fraud_report: The fraud report
            contact_info: Contact information and verification details
            admin: Admin handling the contact
        """
        try:
            # Update fraud report
            fraud_report.real_owner_contacted = True
            fraud_report.real_owner_notes = f"""
Real Owner Contact Information:
- Contact Method: {contact_info.get('method', 'Unknown')}
- Contact Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}
- Verified By: {admin.get_full_name()}

Owner Details:
{contact_info.get('details', 'No details provided')}

Verification Status: {contact_info.get('verified', 'Pending')}
            """.strip()
            
            fraud_report.assigned_to = admin
            fraud_report.status = 'investigating'
            fraud_report.save()
            
            # Create notification
            FraudNotification.objects.create(
                fraud_report=fraud_report,
                notification_type='real_owner_contacted',
                admin=admin,
                title=f"✅ Real Owner Contacted - {fraud_report.report_id}",
                message=f"The real identity owner has been contacted for fraud report {fraud_report.report_id}. Verification in progress.",
                priority='high'
            )
            
            logger.info(f"Real owner contacted for fraud report {fraud_report.report_id}")
            
        except Exception as e:
            logger.error(f"Error handling real owner contact: {str(e)}")
    
    def resolve_fraud_case(
        self,
        fraud_report: FraudReport,
        resolution: str,
        admin: CustomUser,
        notes: str = ""
    ):
        """
        Resolve a fraud case.
        
        Args:
            fraud_report: The fraud report to resolve
            resolution: 'confirmed' or 'dismissed' or 'real_owner_verified'
            admin: Admin resolving the case
            notes: Additional resolution notes
        """
        try:
            if resolution == 'confirmed':
                fraud_report.mark_as_confirmed_fraud(admin.get_full_name(), notes)
                
                # Permanently ban the fraudulent account
                UserAccountAction.objects.create(
                    user=fraud_report.suspected_user,
                    fraud_report=fraud_report,
                    action_type='permanently_banned',
                    reason=f"Confirmed fraud: {notes}",
                    performed_by=admin
                )
                
            elif resolution == 'real_owner_verified':
                fraud_report.real_owner_verified = True
                fraud_report.mark_as_resolved(admin.get_full_name(), f"Real owner verified and guided. {notes}")
                
                # Keep fraudulent account banned but help real owner
                
            elif resolution == 'dismissed':
                fraud_report.status = 'dismissed'
                fraud_report.resolved_at = timezone.now()
                fraud_report.admin_notes = f"{fraud_report.admin_notes or ''}\n\n[Dismissed by {admin.get_full_name()}] {notes}"
                fraud_report.save()
                
                # Reinstate user account if dismissed
                UserAccountAction.objects.create(
                    user=fraud_report.suspected_user,
                    fraud_report=fraud_report,
                    action_type='reinstated',
                    reason=f"Fraud report dismissed: {notes}",
                    performed_by=admin
                )
                
                fraud_report.suspected_user.is_active = True
                fraud_report.suspected_user.save()
            
            # Notify relevant admins
            FraudNotification.objects.create(
                fraud_report=fraud_report,
                notification_type='fraud_resolved',
                admin=admin,
                title=f"Fraud Case Resolved - {fraud_report.report_id}",
                message=f"Fraud report {fraud_report.report_id} has been resolved as: {resolution}. Notes: {notes}",
                priority='medium'
            )
            
            logger.info(f"Fraud report {fraud_report.report_id} resolved as: {resolution}")
            
        except Exception as e:
            logger.error(f"Error resolving fraud case: {str(e)}")
            raise
