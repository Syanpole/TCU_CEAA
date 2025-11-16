"""
Fraud Detection and Reporting System
Handles fraud cases when face verification fails during application confirmation
"""

from django.db import models
from django.utils import timezone
from .models import CustomUser, DocumentSubmission, FullApplication, AllowanceApplication


class FraudReport(models.Model):
    """
    Records fraud attempts when face verification fails during final application confirmation.
    """
    
    FRAUD_TYPE_CHOICES = [
        ('face_mismatch', 'Face Verification Failed'),
        ('liveness_failed', 'Liveness Detection Failed'),
        ('stolen_identity', 'Suspected Stolen Identity'),
        ('document_tampering', 'Document Tampering Detected'),
        ('multiple_attempts', 'Multiple Failed Verification Attempts'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Investigation'),
        ('investigating', 'Under Investigation'),
        ('confirmed_fraud', 'Confirmed Fraud'),
        ('resolved', 'Resolved - Real Owner Verified'),
        ('dismissed', 'Dismissed - False Positive'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical - Immediate Action Required'),
    ]
    
    # Fraud Report Details
    report_id = models.CharField(max_length=50, unique=True, editable=False)
    suspected_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='fraud_reports_as_suspect',
        help_text="User account that attempted fraud"
    )
    fraud_type = models.CharField(max_length=30, choices=FRAUD_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='high')
    
    # Context Information
    application = models.ForeignKey(
        FullApplication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fraud_reports',
        help_text="Related full application if applicable"
    )
    allowance_application = models.ForeignKey(
        AllowanceApplication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fraud_reports',
        help_text="Related allowance application if applicable"
    )
    document_submission = models.ForeignKey(
        DocumentSubmission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fraud_reports',
        help_text="Document that failed verification"
    )
    
    # Verification Failure Details
    face_match_score = models.FloatField(
        default=0.0,
        help_text="Face similarity score (0.0-1.0) from failed verification"
    )
    liveness_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Liveness verification data from failed attempt"
    )
    verification_attempts = models.IntegerField(
        default=1,
        help_text="Number of verification attempts before flagging as fraud"
    )
    
    # Evidence and Details
    description = models.TextField(
        help_text="Detailed description of the fraud attempt"
    )
    evidence_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional evidence (timestamps, IP addresses, device info, etc.)"
    )
    suspected_real_identity = models.TextField(
        blank=True,
        null=True,
        help_text="Details of the real identity owner if discovered"
    )
    
    # Admin Actions
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin investigation notes"
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_fraud_cases',
        limit_choices_to={'role': 'admin'}
    )
    actions_taken = models.JSONField(
        default=list,
        blank=True,
        help_text="List of actions taken (account suspension, notification sent, etc.)"
    )
    
    # Real Owner Contact
    real_owner_contacted = models.BooleanField(
        default=False,
        help_text="Whether the real identity owner has been contacted"
    )
    real_owner_verified = models.BooleanField(
        default=False,
        help_text="Whether the real owner has been verified and guided"
    )
    real_owner_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about real owner contact and verification"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['suspected_user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            # Generate unique report ID
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.report_id = f"FR-{timestamp}-{self.suspected_user.id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.report_id} - {self.suspected_user.get_full_name()} ({self.get_fraud_type_display()})"
    
    def mark_as_resolved(self, resolved_by, notes=""):
        """Mark fraud report as resolved."""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.admin_notes = f"{self.admin_notes or ''}\n\n[Resolved by {resolved_by}] {notes}"
        self.save()
    
    def mark_as_confirmed_fraud(self, confirmed_by, notes=""):
        """Confirm this is actual fraud."""
        self.status = 'confirmed_fraud'
        self.severity = 'critical'
        self.admin_notes = f"{self.admin_notes or ''}\n\n[Confirmed by {confirmed_by}] {notes}"
        self.save()
    
    def contact_real_owner(self, contact_method, contact_details):
        """Record that real owner has been contacted."""
        self.real_owner_contacted = True
        self.real_owner_notes = f"Contacted via {contact_method}: {contact_details}"
        self.save()


class FraudNotification(models.Model):
    """
    Notifications sent to admins about fraud attempts.
    """
    
    NOTIFICATION_TYPE_CHOICES = [
        ('new_fraud_report', 'New Fraud Report'),
        ('high_severity_alert', 'High Severity Alert'),
        ('multiple_attempts', 'Multiple Failed Attempts'),
        ('real_owner_contacted', 'Real Owner Contacted'),
        ('fraud_resolved', 'Fraud Case Resolved'),
    ]
    
    fraud_report = models.ForeignKey(
        FraudReport,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    admin = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='fraud_notifications',
        limit_choices_to={'role': 'admin'}
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='high'
    )
    
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.read = True
        self.read_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.fraud_report.report_id}"


class UserAccountAction(models.Model):
    """
    Tracks actions taken on user accounts related to fraud.
    """
    
    ACTION_TYPE_CHOICES = [
        ('suspended', 'Account Suspended'),
        ('flagged', 'Account Flagged'),
        ('investigation', 'Under Investigation'),
        ('reinstated', 'Account Reinstated'),
        ('permanently_banned', 'Permanently Banned'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='account_actions'
    )
    fraud_report = models.ForeignKey(
        FraudReport,
        on_delete=models.CASCADE,
        related_name='account_actions',
        null=True,
        blank=True
    )
    
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    reason = models.TextField()
    performed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_account_actions',
        limit_choices_to={'role': 'admin'}
    )
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When temporary suspension expires"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_action_type_display()}"
