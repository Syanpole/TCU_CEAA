from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from PIL import Image
import os

def profile_image_upload_path(instance, filename):
    return f'profile_images/{instance.id}/{filename}'

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    student_id = models.CharField(max_length=8, unique=True, null=True, blank=True, help_text="Format: YY-XXXXX (e.g., 22-00001)")
    middle_initial = models.CharField(max_length=5, blank=True, null=True, help_text="Middle initial (e.g., A. or M.)")
    profile_image = models.ImageField(upload_to=profile_image_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ai_verification_score = models.FloatField(default=0.0, help_text="AI verification confidence score (0.0-1.0)")
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_student(self):
        return self.role == 'student'
    
    def save(self, *args, **kwargs):
        # Check if profile_image field is being cleared/changed
        try:
            old_instance = CustomUser.objects.get(pk=self.pk) if self.pk else None
            if old_instance and old_instance.profile_image and old_instance.profile_image != self.profile_image:
                # Delete old image file if it exists
                import os
                if os.path.exists(old_instance.profile_image.path):
                    try:
                        os.remove(old_instance.profile_image.path)
                    except OSError:
                        pass
        except CustomUser.DoesNotExist:
            pass
        
        super().save(*args, **kwargs)
        
        # Resize profile image if it exists and has a valid path
        if self.profile_image and hasattr(self.profile_image, 'path'):
            try:
                import os
                if os.path.exists(self.profile_image.path):
                    img = Image.open(self.profile_image.path)
                    if img.height > 300 or img.width > 300:
                        img.thumbnail((300, 300))
                        img.save(self.profile_image.path)
            except (IOError, OSError) as e:
                # Log the error or handle it gracefully
                print(f"Error processing profile image: {e}")
                pass
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

class DocumentSubmission(models.Model):
    DOCUMENT_TYPES = [
        # Simplified Required Documents (New System)
        ('academic_records', 'Academic Records (Grade 10/12 Report Card, Certificate, or Diploma)'),
        ('valid_id', 'Valid ID (School ID, Birth Certificate, or Government-issued ID)'),
        ('certificate_of_enrollment', 'Certificate of Enrollment'),
        ('transcript_of_records', 'Transcript of Records'),
        
        # Required Documents (New Applicants)
        ('junior_hs_certificate', 'Junior High School Certificate/Grade 10 Report Card/Certification from Principal'),
        ('senior_hs_diploma', 'Senior High School Diploma/Grade 12 Report Card/Certification from Principal'),
        ('school_id', 'School ID or Valid Government-issued ID'),
        ('birth_certificate', 'Birth Certificate (issued by PSA/NSO/Civil Registry Office)'),
        ('grade_10_report_card', 'Grade 10 Report Card'),
        ('grade_12_report_card', 'Grade 12 Report Card'),
        ('diploma', 'Diploma'),
        
        # Other Necessary Documents
        ('form_137', 'Certified True Copy of Elementary and/or High School Form 137'),
        ('als_certificate', 'ALS Certificate (if ALS Graduate)'),
        ('death_certificate', 'Death Certificate (Parents, if claimed to be deceased, issued by PSA/NSO/Civil Registry Office)'),
        ('work_contract_visa', 'Work Contract/VISA/Passport (if any of both parents are OFWs)'),
        ('comelec_stub', 'Original copy and one (1) photocopy of Comelec Stub (issued after May 2022 Elections)'),
        
        # Valid Government-issued IDs
        ('umid_card', 'UMID Card'),
        ('drivers_license', 'Driver\'s License'),
        ('passport', 'Passport'),
        ('sss_id', 'SSS ID'),
        ('voters_id', 'Voter\'s ID'),
        ('bir_tin_id', 'BIR (TIN) ID'),
        ('pag_ibig_id', 'Pag-IBIG ID'),
        ('company_id', 'Company ID'),
        ('postal_id', 'Postal ID'),
        ('philhealth_id', 'PhilHealth ID'),
        ('philsys_id', 'Philippine Identification (PhilID/PhilSys) National ID'),
        ('afp_beneficiary_id', 'AFP Beneficiary/Dependent\'s ID'),
        
        # Legacy and Other
        ('report_card', 'Report Card/Grades'),
        ('enrollment_certificate', 'Certificate of Enrollment'),
        ('barangay_clearance', 'Barangay Clearance'),
        ('parents_id', 'Parent\'s Valid ID'),
        ('voter_certification', 'Voter\'s Certification'),
        ('other', 'Other Document'),
        ('others', 'Others'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision_needed', 'Revision Needed'),
        ('ai_processing', 'AI Processing'),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='documents/%Y/%m/')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    # AI Analysis Fields
    ai_analysis_completed = models.BooleanField(default=False)
    ai_confidence_score = models.FloatField(default=0.0, help_text="AI confidence score (0.0-1.0)")
    ai_document_type_match = models.BooleanField(default=False)
    ai_extracted_text = models.TextField(blank=True, null=True)
    ai_key_information = models.JSONField(default=dict, blank=True)
    ai_quality_assessment = models.JSONField(default=dict, blank=True)
    ai_recommendations = models.JSONField(default=list, blank=True)
    ai_auto_approved = models.BooleanField(default=False)
    ai_analysis_notes = models.TextField(blank=True, null=True)
    address_match_score = models.FloatField(default=0.0, help_text="Address matching confidence score (0.0-1.0)")
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='reviewed_documents', limit_choices_to={'role': 'admin'})
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.get_document_type_display()} ({self.status})"

class GradeSubmission(models.Model):
    SEMESTER_CHOICES = [
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('summer', 'Summer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    academic_year = models.CharField(max_length=9, help_text="Format: YYYY-YYYY (e.g., 2024-2025)")
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    
    # Grade details
    total_units = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    # GWA in point scale: 1.00-5.00 (1.00 is highest, 5.00 is failing)
    # Note: Backend validation will accept both percentage (65-100) and point scale (1.00-5.00)
    general_weighted_average = models.DecimalField(max_digits=5, decimal_places=2, 
                                                 validators=[MinValueValidator(1.0), MaxValueValidator(100.0)])
    # DEPRECATED: SWA field kept for backward compatibility but not used in frontend
    semestral_weighted_average = models.DecimalField(max_digits=5, decimal_places=2, 
                                                   validators=[MinValueValidator(1.0), MaxValueValidator(100.0)],
                                                   null=True, blank=True, default=None)
    
    # Grade sheet upload
    grade_sheet = models.FileField(upload_to='grades/%Y/%m/')
    
    # Validation flags
    has_failing_grades = models.BooleanField(default=False)
    has_incomplete_grades = models.BooleanField(default=False)
    has_dropped_subjects = models.BooleanField(default=False)
    
    # AI evaluation results
    ai_evaluation_completed = models.BooleanField(default=False)
    ai_evaluation_notes = models.TextField(blank=True, null=True)
    ai_confidence_score = models.FloatField(default=0.0, help_text="AI analysis confidence (0.0-1.0)")
    ai_extracted_grades = models.JSONField(default=dict, blank=True, help_text="AI extracted grade data")
    ai_grade_validation = models.JSONField(default=dict, blank=True, help_text="AI grade validation results")
    ai_recommendations = models.JSONField(default=list, blank=True, help_text="AI recommendations")
    qualifies_for_basic_allowance = models.BooleanField(default=False)
    qualifies_for_merit_incentive = models.BooleanField(default=False)
    
    # Admin review
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='reviewed_grades', limit_choices_to={'role': 'admin'})
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['student', 'academic_year', 'semester']
    
    def _convert_to_percentage(self, gwa_value):
        """
        Convert GWA from point scale (1.0-5.0) to percentage scale (0-100)
        Uses official university grading scale with linear interpolation.
        
        Official Grading Scale (Midpoint of Ranges):
        1.0 = 98% (96-100)     → Excellent
        1.25 = 94% (93-95)     → Very Good
        1.5 = 91% (90-92)      → Good
        1.75 = 88% (87-89)     → Satisfactory
        2.0 = 85% (84-86)      → Fair
        2.25 = 82% (81-83)     → Average
        2.5 = 79% (78-80)      → Below Average
        2.75 = 76% (75-77)     → Passing
        3.0 = 72% (70-74)      → Minimum Passing
        5.0 = 40% (Below 70)   → Failing
        
        Accepts any decimal format (1, 1.0, 1.00, 1.75, 1.91, etc.)
        If value is already in percentage (60-100), return as-is
        """
        if gwa_value >= 60:
            # Already in percentage scale
            return float(gwa_value)
        
        # Official university grading scale conversion table (using midpoint of ranges)
        conversion_table = [
            (1.0, 98.0),    # 96-100 → Excellent
            (1.25, 94.0),   # 93-95 → Very Good
            (1.5, 91.0),    # 90-92 → Good
            (1.75, 88.0),   # 87-89 → Satisfactory
            (2.0, 85.0),    # 84-86 → Fair
            (2.25, 82.0),   # 81-83 → Average
            (2.5, 79.0),    # 78-80 → Below Average
            (2.75, 76.0),   # 75-77 → Passing
            (3.0, 72.0),    # 70-74 → Minimum Passing
            (5.0, 40.0),    # Below 70 → Failing
        ]
        
        # Check for exact match (with floating point tolerance)
        for point, percent in conversion_table:
            if abs(gwa_value - point) < 0.01:
                return percent
        
        # Linear interpolation between two nearest points
        for i in range(len(conversion_table) - 1):
            point1, percent1 = conversion_table[i]
            point2, percent2 = conversion_table[i + 1]
            
            if point1 <= gwa_value <= point2:
                # Linear interpolation formula
                ratio = (gwa_value - point1) / (point2 - point1)
                interpolated = percent1 + ratio * (percent2 - percent1)
                return round(interpolated, 2)
        
        # If below 1.0, treat as 98% (excellent)
        if gwa_value < 1.0:
            return 98.0
        
        # If above 5.0, treat as failing (below 40%)
        if gwa_value > 5.0:
            return 0.0
        
        return 40.0
    
    def get_gwa_percentage(self):
        """Get GWA as percentage, converting from point scale if necessary"""
        return self._convert_to_percentage(float(self.general_weighted_average))
    
    def get_swa_percentage(self):
        """Get SWA as percentage, converting from point scale if necessary"""
        if self.semestral_weighted_average:
            return self._convert_to_percentage(float(self.semestral_weighted_average))
        # If no SWA provided, use GWA (since frontend now only collects GWA)
        return self.get_gwa_percentage()
    
    def calculate_allowance_eligibility(self):
        """AI-based calculation of allowance eligibility - Enhanced Autonomous version"""
        try:
            from .ai_service import grade_analyzer
            
            # Use the comprehensive AI analyzer
            analysis_result = grade_analyzer.analyze_grades(self)
            
            # Extract eligibility results
            basic_analysis = analysis_result.get('basic_allowance_analysis', {})
            merit_analysis = analysis_result.get('merit_incentive_analysis', {})
            
            self.qualifies_for_basic_allowance = basic_analysis.get('eligible', False)
            self.qualifies_for_merit_incentive = merit_analysis.get('eligible', False)
            self.ai_evaluation_completed = True
            self.ai_confidence_score = analysis_result.get('confidence_score', 0.0)
            self.ai_extracted_grades = analysis_result.get('extracted_grades', {})
            self.ai_grade_validation = analysis_result.get('grade_validation', {})
            self.ai_recommendations = analysis_result.get('recommendations', [])
            
            # Generate evaluation notes
            evaluation_notes = analysis_result.get('analysis_notes', [])
            self.ai_evaluation_notes = "\n".join(evaluation_notes)
            
            # Autonomous processing - auto-approve all calculations
            self.status = 'approved'
            self.reviewed_at = timezone.now()
            
            return self.qualifies_for_basic_allowance, self.qualifies_for_merit_incentive
            
        except Exception as e:
            # Fallback to basic calculation if AI service fails - still autonomous
            return self._basic_allowance_calculation_autonomous()
    
    def _basic_allowance_calculation_autonomous(self):
        """
        Fallback basic calculation method - Autonomous processing
        NEW RULE: Name verification success = Auto approve = ₱5,000 basic allowance
        """
        # Convert GWA to percentage for calculation
        gwa_percent = self.get_gwa_percentage()
        swa_percent = self.get_swa_percentage()
        
        # ✅ SIMPLE RULE: If we reach this method, name verification passed
        # Automatically qualify for basic allowance (₱5,000)
        basic_eligible = True
        
        # Merit Incentive (₱5,000): Still requires SWA ≥ 88% (GWA ≤1.75), no fails/inc/drops, ≥15 units
        # Note: SWA now uses GWA value if SWA not provided
        # 1.75 GWA = 88% (87-89 range)
        merit_eligible = (
            swa_percent >= 88.0 and
            self.total_units >= 15 and
            not self.has_failing_grades and
            not self.has_incomplete_grades and
            not self.has_dropped_subjects
        )
        
        self.qualifies_for_basic_allowance = basic_eligible
        self.qualifies_for_merit_incentive = merit_eligible
        self.ai_evaluation_completed = True
        
        # Autonomous approval
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        
        # Generate basic evaluation notes
        notes = []
        notes.append("🤖 Autonomous AI Processing - Auto-Approved")
        notes.append("=" * 40)
        notes.append("✅ NAME VERIFIED: Your identity has been confirmed on the grade sheet")
        notes.append("🎉 AUTO-APPROVED: ₱5,000 Basic Allowance automatically granted")
        notes.append("")
        
        if merit_eligible:
            notes.append("✅ Qualifies for Merit Incentive (₱5,000)")
        else:
            reasons = []
            if swa_percent < 88.0:
                reasons.append(f"GWA {swa_percent:.2f}% < 88% (Point: {self.general_weighted_average})")
            if self.total_units < 15:
                reasons.append(f"Units {self.total_units} < 15")
            if self.has_failing_grades:
                reasons.append("Has failing grades")
            if self.has_incomplete_grades:
                reasons.append("Has incomplete grades")
            if self.has_dropped_subjects:
                reasons.append("Has dropped subjects")
            notes.append(f"❌ Does not qualify for Merit Incentive: {', '.join(reasons)}")

        
        total_allowance = 0
        if basic_eligible:
            total_allowance += 5000
        if merit_eligible:
            total_allowance += 5000
        
        if total_allowance > 0:
            notes.append(f"💰 Total Allowance Qualified: ₱{total_allowance:,}")
            notes.append("🎉 Congratulations! You qualify for TCU-CEAA allowance.")
        else:
            notes.append("💰 Total Allowance: ₱0")
            notes.append("📚 Keep working hard! Review the requirements for future eligibility.")
        
        notes.append("\n⚡ Processing Status: Automatically approved by AI system")
        notes.append("📋 Next Step: Allowance application available for final approval")
        
        self.ai_evaluation_notes = "\n".join(notes)
        return basic_eligible, merit_eligible
    
    def __str__(self):
        return f"{self.student.username} - {self.academic_year} {self.semester} ({self.status})"

class AllowanceApplication(models.Model):
    APPLICATION_TYPES = [
        ('basic', 'Basic Educational Assistance (₱5,000)'),
        ('merit', 'Merit Incentive (₱5,000)'),
        ('both', 'Both Allowances (₱10,000)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    grade_submission = models.ForeignKey(GradeSubmission, on_delete=models.CASCADE)
    application_type = models.CharField(max_length=10, choices=APPLICATION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='processed_applications', limit_choices_to={'role': 'admin'})
    
    # Email notification tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    notification_error = models.TextField(blank=True, null=True)
    
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['student', 'grade_submission']
    
    def __str__(self):
        return f"{self.student.username} - {self.get_application_type_display()} - ₱{self.amount}"


# Audit Log Model
class AuditLog(models.Model):
    """Model to track all admin and user actions in the system"""
    
    ACTION_TYPES = [
        # Document Actions
        ('document_submitted', 'Document Submitted'),
        ('document_approved', 'Document Approved'),
        ('document_rejected', 'Document Rejected'),
        ('document_revised', 'Document Revision Requested'),
        
        # Grade Actions
        ('grade_submitted', 'Grade Submitted'),
        ('grade_approved', 'Grade Approved'),
        ('grade_rejected', 'Grade Rejected'),
        ('grade_processed', 'Grade Processed'),
        
        # Application Actions
        ('application_submitted', 'Application Submitted'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('application_disbursed', 'Application Disbursed'),
        
        # User Actions
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('user_registered', 'User Registered'),
        ('user_updated', 'User Profile Updated'),
        ('password_changed', 'Password Changed'),
        
        # Admin Actions
        ('admin_review', 'Admin Review Performed'),
        ('admin_action', 'Admin Action Taken'),
        ('system_config', 'System Configuration Changed'),
        
        # AI Actions
        ('ai_analysis', 'AI Analysis Completed'),
        ('ai_auto_approve', 'AI Auto-Approval'),
        
        # Other
        ('other', 'Other Action'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('success', 'Success'),
    ]
    
    # Who performed the action
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs'
    )
    
    # Action details
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    action_description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='info')
    
    # Affected object details
    target_model = models.CharField(max_length=50, blank=True, null=True, help_text="Model name (e.g., DocumentSubmission)")
    target_object_id = models.IntegerField(blank=True, null=True, help_text="ID of the affected object")
    target_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targeted_audit_logs',
        help_text="User affected by the action (if applicable)"
    )
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional action metadata")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['severity', '-timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{user_str} - {self.get_action_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def log_action(cls, action_type, description, user=None, target_model=None, 
                   target_object_id=None, target_user=None, severity='info', 
                   metadata=None, request=None):
        """Helper method to create audit log entries"""
        ip_address = None
        user_agent = None
        
        if request:
            # Extract IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Extract user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(
            user=user,
            action_type=action_type,
            action_description=description,
            severity=severity,
            target_model=target_model,
            target_object_id=target_object_id,
            target_user=target_user,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )


class SystemAnalytics(models.Model):
    """Model to store daily analytics snapshots"""
    
    date = models.DateField(unique=True, db_index=True)
    
    # User statistics
    total_users = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)
    total_admins = models.IntegerField(default=0)
    new_users_today = models.IntegerField(default=0)
    active_users_today = models.IntegerField(default=0)
    
    # Document statistics
    total_documents = models.IntegerField(default=0)
    documents_pending = models.IntegerField(default=0)
    documents_approved = models.IntegerField(default=0)
    documents_rejected = models.IntegerField(default=0)
    documents_submitted_today = models.IntegerField(default=0)
    
    # Grade statistics
    total_grades = models.IntegerField(default=0)
    grades_pending = models.IntegerField(default=0)
    grades_approved = models.IntegerField(default=0)
    grades_rejected = models.IntegerField(default=0)
    grades_submitted_today = models.IntegerField(default=0)
    
    # Application statistics
    total_applications = models.IntegerField(default=0)
    applications_pending = models.IntegerField(default=0)
    applications_approved = models.IntegerField(default=0)
    applications_rejected = models.IntegerField(default=0)
    applications_disbursed = models.IntegerField(default=0)
    applications_submitted_today = models.IntegerField(default=0)
    total_amount_disbursed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # AI statistics
    ai_analyses_completed = models.IntegerField(default=0)
    ai_auto_approvals = models.IntegerField(default=0)
    avg_ai_confidence_score = models.FloatField(default=0.0)
    
    # Performance metrics
    avg_document_processing_time = models.FloatField(default=0.0, help_text="Average time in hours")
    avg_grade_processing_time = models.FloatField(default=0.0, help_text="Average time in hours")
    avg_application_processing_time = models.FloatField(default=0.0, help_text="Average time in hours")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "System Analytics"
    
    def __str__(self):
        return f"Analytics for {self.date}"
    
    @classmethod
    def generate_today_snapshot(cls):
        """Generate analytics snapshot for today"""
        from django.db.models import Count, Avg, Sum
        from datetime import date
        
        today = date.today()
        
        # Get or create today's analytics
        analytics, created = cls.objects.get_or_create(date=today)
        
        # User statistics
        analytics.total_users = CustomUser.objects.count()
        analytics.total_students = CustomUser.objects.filter(role='student').count()
        analytics.total_admins = CustomUser.objects.filter(role='admin').count()
        analytics.new_users_today = CustomUser.objects.filter(created_at__date=today).count()
        
        # Document statistics
        analytics.total_documents = DocumentSubmission.objects.count()
        analytics.documents_pending = DocumentSubmission.objects.filter(status='pending').count()
        analytics.documents_approved = DocumentSubmission.objects.filter(status='approved').count()
        analytics.documents_rejected = DocumentSubmission.objects.filter(status='rejected').count()
        analytics.documents_submitted_today = DocumentSubmission.objects.filter(submitted_at__date=today).count()
        
        # Grade statistics
        analytics.total_grades = GradeSubmission.objects.count()
        analytics.grades_pending = GradeSubmission.objects.filter(status='pending').count()
        analytics.grades_approved = GradeSubmission.objects.filter(status='approved').count()
        analytics.grades_rejected = GradeSubmission.objects.filter(status='rejected').count()
        analytics.grades_submitted_today = GradeSubmission.objects.filter(submitted_at__date=today).count()
        
        # Application statistics
        analytics.total_applications = AllowanceApplication.objects.count()
        analytics.applications_pending = AllowanceApplication.objects.filter(status='pending').count()
        analytics.applications_approved = AllowanceApplication.objects.filter(status='approved').count()
        analytics.applications_rejected = AllowanceApplication.objects.filter(status='rejected').count()
        analytics.applications_disbursed = AllowanceApplication.objects.filter(status='disbursed').count()
        analytics.applications_submitted_today = AllowanceApplication.objects.filter(applied_at__date=today).count()
        analytics.total_amount_disbursed = AllowanceApplication.objects.filter(
            status='disbursed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # AI statistics
        analytics.ai_analyses_completed = DocumentSubmission.objects.filter(ai_analysis_completed=True).count()
        analytics.ai_auto_approvals = DocumentSubmission.objects.filter(ai_auto_approved=True).count()
        avg_confidence = DocumentSubmission.objects.filter(
            ai_analysis_completed=True
        ).aggregate(avg=Avg('ai_confidence_score'))['avg']
        analytics.avg_ai_confidence_score = avg_confidence or 0.0
        
        analytics.save()
        return analytics

