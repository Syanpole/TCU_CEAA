"""
🔍 Comprehensive Audit Logging System
Tracks all student, admin, and AI activities in the TCU-CEAA system
"""

from django.utils import timezone
from .models import AuditLog, CustomUser
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging utility for comprehensive activity tracking
    """
    
    @staticmethod
    def _get_client_info(request):
        """Extract client IP and user agent from request"""
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return ip_address, user_agent
    
    @staticmethod
    def log(
        user,
        action_type,
        action_description,
        severity='info',
        target_model=None,
        target_object_id=None,
        target_user=None,
        metadata=None,
        request=None
    ):
        """
        Generic audit log creation
        
        Args:
            user: User who performed the action
            action_type: Type of action (from AuditLog.ACTION_TYPES)
            action_description: Human-readable description
            severity: Log severity (info, warning, critical, success)
            target_model: Name of affected model
            target_object_id: ID of affected object
            target_user: User affected by the action
            metadata: Additional data as dictionary
            request: HTTP request object (for IP and user agent)
        """
        try:
            ip_address, user_agent = '', ''
            if request:
                ip_address, user_agent = AuditLogger._get_client_info(request)
            
            AuditLog.objects.create(
                user=user,
                action_type=action_type,
                action_description=action_description,
                severity=severity,
                target_model=target_model,
                target_object_id=target_object_id,
                target_user=target_user,
                metadata=metadata or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
    
    # ==================== USER ACTIONS ====================
    
    @staticmethod
    def log_user_login(user, request, success=True):
        """Log user login attempt"""
        AuditLogger.log(
            user=user if success else None,
            action_type='user_login',
            action_description=f"{'Successful' if success else 'Failed'} login attempt for {user.username if user else 'unknown user'}",
            severity='success' if success else 'warning',
            metadata={
                'username': user.username if user else 'unknown',
                'role': user.role if user else 'unknown',
                'success': success
            },
            request=request
        )
    
    @staticmethod
    def log_user_logout(user, request):
        """Log user logout"""
        AuditLogger.log(
            user=user,
            action_type='user_logout',
            action_description=f"User {user.username} logged out",
            severity='info',
            metadata={'username': user.username, 'role': user.role},
            request=request
        )
    
    @staticmethod
    def log_user_registration(user, request):
        """Log new user registration"""
        AuditLogger.log(
            user=user,
            action_type='user_registered',
            action_description=f"New user registered: {user.username} ({user.role})",
            severity='success',
            metadata={
                'username': user.username,
                'role': user.role,
                'student_id': user.student_id,
                'email': user.email
            },
            request=request
        )
    
    @staticmethod
    def log_profile_update(user, request, fields_updated):
        """Log user profile update"""
        AuditLogger.log(
            user=user,
            action_type='user_updated',
            action_description=f"User {user.username} updated their profile",
            severity='info',
            metadata={
                'fields_updated': fields_updated,
                'username': user.username
            },
            request=request
        )
    
    @staticmethod
    def log_password_change(user, request):
        """Log password change"""
        AuditLogger.log(
            user=user,
            action_type='password_changed',
            action_description=f"User {user.username} changed their password",
            severity='info',
            metadata={'username': user.username},
            request=request
        )
    
    # ==================== DOCUMENT ACTIONS ====================
    
    @staticmethod
    def log_document_submitted(user, document, request):
        """Log document submission"""
        AuditLogger.log(
            user=user,
            action_type='document_submitted',
            action_description=f"Student {user.username} submitted {document.get_document_type_display()}",
            severity='info',
            target_model='DocumentSubmission',
            target_object_id=document.id,
            target_user=user,
            metadata={
                'document_id': document.id,
                'document_type': document.document_type,
                'document_type_display': document.get_document_type_display(),
                'student_id': user.student_id,
                'student_name': user.get_full_name()
            },
            request=request
        )
    
    @staticmethod
    def log_document_approved(admin_user, document, request=None, auto_approved=False):
        """Log document approval"""
        action_desc = (
            f"Document {document.get_document_type_display()} {'auto-' if auto_approved else ''}approved "
            f"for student {document.student.username}"
        )
        
        AuditLogger.log(
            user=admin_user,
            action_type='ai_auto_approve' if auto_approved else 'document_approved',
            action_description=action_desc,
            severity='success',
            target_model='DocumentSubmission',
            target_object_id=document.id,
            target_user=document.student,
            metadata={
                'document_id': document.id,
                'document_type': document.document_type,
                'document_type_display': document.get_document_type_display(),
                'student_id': document.student.student_id,
                'student_name': document.student.get_full_name(),
                'auto_approved': auto_approved,
                'confidence_score': float(document.ai_confidence_score) if document.ai_confidence_score else None
            },
            request=request
        )
    
    @staticmethod
    def log_document_rejected(admin_user, document, reason=None, request=None, auto_rejected=False):
        """Log document rejection"""
        action_desc = (
            f"Document {document.get_document_type_display()} {'auto-' if auto_rejected else ''}rejected "
            f"for student {document.student.username}"
        )
        
        AuditLogger.log(
            user=admin_user,
            action_type='document_rejected',
            action_description=action_desc,
            severity='warning',
            target_model='DocumentSubmission',
            target_object_id=document.id,
            target_user=document.student,
            metadata={
                'document_id': document.id,
                'document_type': document.document_type,
                'document_type_display': document.get_document_type_display(),
                'student_id': document.student.student_id,
                'student_name': document.student.get_full_name(),
                'reason': reason,
                'auto_rejected': auto_rejected,
                'confidence_score': float(document.ai_confidence_score) if document.ai_confidence_score else None
            },
            request=request
        )
    
    @staticmethod
    def log_document_revision_requested(admin_user, document, reason, request=None):
        """Log document revision request"""
        AuditLogger.log(
            user=admin_user,
            action_type='document_revised',
            action_description=f"Revision requested for {document.get_document_type_display()} from student {document.student.username}",
            severity='info',
            target_model='DocumentSubmission',
            target_object_id=document.id,
            target_user=document.student,
            metadata={
                'document_id': document.id,
                'document_type': document.document_type,
                'document_type_display': document.get_document_type_display(),
                'student_id': document.student.student_id,
                'student_name': document.student.get_full_name(),
                'reason': reason
            },
            request=request
        )
    
    # ==================== GRADE ACTIONS ====================
    
    @staticmethod
    def log_grade_submitted(user, grade_submission, request):
        """Log grade submission"""
        AuditLogger.log(
            user=user,
            action_type='grade_submitted',
            action_description=f"Student {user.username} submitted grades for {grade_submission.academic_year} {grade_submission.get_semester_display()}",
            severity='info',
            target_model='GradeSubmission',
            target_object_id=grade_submission.id,
            target_user=user,
            metadata={
                'grade_id': grade_submission.id,
                'academic_year': grade_submission.academic_year,
                'semester': grade_submission.semester,
                'gwa': float(grade_submission.general_weighted_average),
                'swa': float(grade_submission.semestral_weighted_average),
                'student_id': user.student_id,
                'student_name': user.get_full_name()
            },
            request=request
        )
    
    @staticmethod
    def log_grade_approved(admin_user, grade_submission, request=None, auto_approved=False):
        """Log grade approval"""
        action_desc = (
            f"Grades {'auto-' if auto_approved else ''}approved for student {grade_submission.student.username} "
            f"({grade_submission.academic_year} {grade_submission.get_semester_display()})"
        )
        
        AuditLogger.log(
            user=admin_user,
            action_type='grade_approved',
            action_description=action_desc,
            severity='success',
            target_model='GradeSubmission',
            target_object_id=grade_submission.id,
            target_user=grade_submission.student,
            metadata={
                'grade_id': grade_submission.id,
                'academic_year': grade_submission.academic_year,
                'semester': grade_submission.semester,
                'gwa': float(grade_submission.general_weighted_average),
                'student_id': grade_submission.student.student_id,
                'student_name': grade_submission.student.get_full_name(),
                'auto_approved': auto_approved,
                'qualifies_basic': grade_submission.qualifies_for_basic_allowance,
                'qualifies_merit': grade_submission.qualifies_for_merit_incentive
            },
            request=request
        )
    
    @staticmethod
    def log_grade_rejected(admin_user, grade_submission, reason=None, request=None):
        """Log grade rejection"""
        AuditLogger.log(
            user=admin_user,
            action_type='grade_rejected',
            action_description=f"Grades rejected for student {grade_submission.student.username} ({grade_submission.academic_year} {grade_submission.get_semester_display()})",
            severity='warning',
            target_model='GradeSubmission',
            target_object_id=grade_submission.id,
            target_user=grade_submission.student,
            metadata={
                'grade_id': grade_submission.id,
                'academic_year': grade_submission.academic_year,
                'semester': grade_submission.semester,
                'student_id': grade_submission.student.student_id,
                'student_name': grade_submission.student.get_full_name(),
                'reason': reason
            },
            request=request
        )
    
    @staticmethod
    def log_grade_processed(admin_user, grade_submission, request=None):
        """Log grade processing completion"""
        AuditLogger.log(
            user=admin_user,
            action_type='grade_processed',
            action_description=f"Grades processed for student {grade_submission.student.username}",
            severity='success',
            target_model='GradeSubmission',
            target_object_id=grade_submission.id,
            target_user=grade_submission.student,
            metadata={
                'grade_id': grade_submission.id,
                'academic_year': grade_submission.academic_year,
                'semester': grade_submission.semester,
                'student_id': grade_submission.student.student_id,
                'student_name': grade_submission.student.get_full_name()
            },
            request=request
        )
    
    # ==================== APPLICATION ACTIONS ====================
    
    @staticmethod
    def log_application_submitted(user, application, request):
        """Log allowance application submission"""
        AuditLogger.log(
            user=user,
            action_type='application_submitted',
            action_description=f"Student {user.username} applied for {application.get_application_type_display()} (₱{application.amount:,.2f})",
            severity='info',
            target_model='AllowanceApplication',
            target_object_id=application.id,
            target_user=user,
            metadata={
                'application_id': application.id,
                'application_type': application.application_type,
                'amount': float(application.amount),
                'student_id': user.student_id,
                'student_name': user.get_full_name()
            },
            request=request
        )
    
    @staticmethod
    def log_application_approved(admin_user, application, request=None):
        """Log application approval"""
        AuditLogger.log(
            user=admin_user,
            action_type='application_approved',
            action_description=f"Allowance application approved for {application.student.username} - {application.get_application_type_display()} (₱{application.amount:,.2f})",
            severity='success',
            target_model='AllowanceApplication',
            target_object_id=application.id,
            target_user=application.student,
            metadata={
                'application_id': application.id,
                'application_type': application.application_type,
                'amount': float(application.amount),
                'student_id': application.student.student_id,
                'student_name': application.student.get_full_name()
            },
            request=request
        )
    
    @staticmethod
    def log_application_rejected(admin_user, application, reason=None, request=None):
        """Log application rejection"""
        AuditLogger.log(
            user=admin_user,
            action_type='application_rejected',
            action_description=f"Allowance application rejected for {application.student.username} - {application.get_application_type_display()}",
            severity='warning',
            target_model='AllowanceApplication',
            target_object_id=application.id,
            target_user=application.student,
            metadata={
                'application_id': application.id,
                'application_type': application.application_type,
                'amount': float(application.amount),
                'student_id': application.student.student_id,
                'student_name': application.student.get_full_name(),
                'reason': reason
            },
            request=request
        )
    
    @staticmethod
    def log_application_disbursed(admin_user, application, request=None):
        """Log allowance disbursement"""
        AuditLogger.log(
            user=admin_user,
            action_type='application_disbursed',
            action_description=f"Allowance disbursed to {application.student.username} - ₱{application.amount:,.2f}",
            severity='success',
            target_model='AllowanceApplication',
            target_object_id=application.id,
            target_user=application.student,
            metadata={
                'application_id': application.id,
                'application_type': application.application_type,
                'amount': float(application.amount),
                'student_id': application.student.student_id,
                'student_name': application.student.get_full_name()
            },
            request=request
        )
    
    # ==================== AI ACTIONS ====================
    
    @staticmethod
    def log_ai_analysis(user, target_model, target_id, analysis_type, results, request=None):
        """Log AI analysis completion"""
        confidence = results.get('confidence_score', 0.0)
        status = results.get('status', 'unknown')
        
        AuditLogger.log(
            user=user,
            action_type='ai_analysis',
            action_description=f"AI {analysis_type} analysis completed for {target_model} ID:{target_id} (Confidence: {confidence:.1%})",
            severity='info',
            target_model=target_model,
            target_object_id=target_id,
            target_user=user,
            metadata={
                'analysis_type': analysis_type,
                'confidence_score': float(confidence),
                'status': status,
                'algorithms_used': results.get('algorithms_used', []),
                'processing_time': results.get('processing_time', 0),
                **results.get('additional_metadata', {})
            },
            request=request
        )
    
    @staticmethod
    def log_ai_auto_approval(user, target_model, target_id, confidence, request=None):
        """Log AI auto-approval decision"""
        AuditLogger.log(
            user=user,
            action_type='ai_auto_approve',
            action_description=f"AI auto-approved {target_model} ID:{target_id} (Confidence: {confidence:.1%})",
            severity='success',
            target_model=target_model,
            target_object_id=target_id,
            target_user=user,
            metadata={
                'confidence_score': float(confidence),
                'auto_decision': True,
                'decision_type': 'auto_approve'
            },
            request=request
        )
    
    # ==================== ADMIN ACTIONS ====================
    
    @staticmethod
    def log_admin_review(admin_user, target_model, target_id, decision, notes=None, request=None):
        """Log admin review action"""
        AuditLogger.log(
            user=admin_user,
            action_type='admin_review',
            action_description=f"Admin {admin_user.username} reviewed {target_model} ID:{target_id} - Decision: {decision}",
            severity='info',
            target_model=target_model,
            target_object_id=target_id,
            metadata={
                'decision': decision,
                'admin_notes': notes,
                'admin_name': admin_user.get_full_name()
            },
            request=request
        )
    
    @staticmethod
    def log_admin_action(admin_user, action_description, severity='info', metadata=None, request=None):
        """Log general admin action"""
        AuditLogger.log(
            user=admin_user,
            action_type='admin_action',
            action_description=f"Admin {admin_user.username}: {action_description}",
            severity=severity,
            metadata=metadata or {},
            request=request
        )
    
    @staticmethod
    def log_system_config_change(admin_user, setting_name, old_value, new_value, request=None):
        """Log system configuration change"""
        AuditLogger.log(
            user=admin_user,
            action_type='system_config',
            action_description=f"Admin {admin_user.username} changed system setting: {setting_name}",
            severity='warning',
            metadata={
                'setting_name': setting_name,
                'old_value': str(old_value),
                'new_value': str(new_value),
                'admin_name': admin_user.get_full_name()
            },
            request=request
        )
    
    # ==================== BULK OPERATIONS ====================
    
    @staticmethod
    def log_bulk_action(admin_user, action_type, count, target_model, details, request=None):
        """Log bulk operations"""
        AuditLogger.log(
            user=admin_user,
            action_type='admin_action',
            action_description=f"Admin {admin_user.username} performed bulk {action_type} on {count} {target_model} records",
            severity='warning',
            target_model=target_model,
            metadata={
                'bulk_action': True,
                'action_type': action_type,
                'records_affected': count,
                'details': details,
                'admin_name': admin_user.get_full_name()
            },
            request=request
        )

    @staticmethod
    def log_admin_notification(document_or_grade, notification_message, ocr_verification_details=None, request=None):
        """
        🔔 Log admin notification for manual review required
        
        Args:
            document_or_grade: DocumentSubmission or GradeSubmission object
            notification_message: Admin notification message
            ocr_verification_details: OCR verification details dictionary
            request: HTTP request object
        """
        try:
            # Determine object type and get user
            if hasattr(document_or_grade, 'user'):
                target_user = document_or_grade.user
                target_model = 'DocumentSubmission' if hasattr(document_or_grade, 'document_type') else 'GradeSubmission'
            else:
                target_user = None
                target_model = 'Unknown'
            
            # Prepare metadata
            metadata = {
                'notification_message': notification_message,
                'requires_manual_review': True,
                'notification_timestamp': timezone.now().isoformat()
            }
            
            if ocr_verification_details:
                metadata.update({
                    'ocr_verification_status': ocr_verification_details.get('verification_status'),
                    'confidence_level': ocr_verification_details.get('confidence_level'),
                    'ocr_similarity_score': ocr_verification_details.get('similarity_score'),
                    'easyocr_text_length': len(ocr_verification_details.get('easyocr_text', '')),
                    'tesseract_text_length': len(ocr_verification_details.get('tesseract_text', '')),
                    'verification_reasons': ocr_verification_details.get('reasons', [])
                })
            
            AuditLogger.log(
                user=None,  # System-generated notification
                action_type='ai_analysis',
                action_description=f'🔔 Admin notification: {notification_message}',
                severity='warning',
                target_model=target_model,
                target_object_id=document_or_grade.id if document_or_grade else None,
                target_user=target_user,
                metadata=metadata,
                request=request
            )
            
        except Exception as e:
            # Don't let logging errors break the main process
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log admin notification: {str(e)}")


# Convenience singleton instance
audit_logger = AuditLogger()
