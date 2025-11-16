from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from PIL import Image
import os
from .validators import profile_image_validators, document_validators, grade_sheet_validators

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
    profile_image = models.ImageField(upload_to=profile_image_upload_path, null=True, blank=True, validators=profile_image_validators)
    is_email_verified = models.BooleanField(default=False, help_text="Email verification status")
    created_at = models.DateTimeField(auto_now_add=True)
    ai_verification_score = models.FloatField(default=0.0, help_text="AI verification confidence score (0.0-1.0)")
    
    # Email verification
    is_email_verified = models.BooleanField(default=False, help_text="Email address has been verified")
    email_verified_at = models.DateTimeField(null=True, blank=True, help_text="When email was verified")
    
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

class VerifiedStudent(models.Model):
    """
    Official list of students verified for registration.
    Only students in this list can create accounts in the system.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    COURSE_CHOICES = [
        ('BSCS', 'Bachelor of Science in Computer Science'),
        ('BSIT', 'Bachelor of Science in Information Technology'),
        ('BSIS', 'Bachelor of Science in Information Systems'),
        # Add more courses as needed
    ]
    
    student_id = models.CharField(max_length=20, unique=True, db_index=True, 
                                  help_text="Format: YY-XXXXX (e.g., 22-00001)")
    first_name = models.CharField(max_length=100, db_index=True,
                                  help_text="Student's legal first name")
    last_name = models.CharField(max_length=100, db_index=True,
                                 help_text="Student's legal last name")
    middle_initial = models.CharField(max_length=10, blank=True, null=True,
                                     help_text="Middle initial or 'N/A' if none")
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    year_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)],
                                     help_text="Current year level (1-6)")
    
    # Metadata
    is_active = models.BooleanField(default=True, help_text="Can this student register?")
    has_registered = models.BooleanField(default=False, help_text="Has this student completed registration?")
    registered_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='verified_student_record',
                                       help_text="Linked user account after registration")
    
    # Audit fields
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='verified_students_added',
                                 help_text="Admin who added this verified student")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about this student")
    
    class Meta:
        ordering = ['student_id']
        verbose_name = "Verified Student"
        verbose_name_plural = "Verified Students"
        indexes = [
            models.Index(fields=['student_id', 'is_active']),
            models.Index(fields=['last_name', 'first_name']),
        ]
    
    def __str__(self):
        mi = f" {self.middle_initial}." if self.middle_initial and self.middle_initial != 'N/A' else ""
        return f"{self.first_name}{mi} {self.last_name} ({self.student_id})"
    
    def verify_identity(self, first_name: str, last_name: str, middle_initial: str = '') -> dict:
        """
        Verify if provided information matches this verified student record.
        
        Args:
            first_name: First name to verify (case-insensitive)
            last_name: Last name to verify (case-insensitive)
            middle_initial: Middle initial to verify (optional)
        
        Returns:
            dict with 'verified' boolean and 'message' string
        """
        # Normalize inputs
        first_name = first_name.strip().lower()
        last_name = last_name.strip().lower()
        middle_initial = middle_initial.strip().upper().replace('.', '')
        
        # Check first name
        if self.first_name.lower() != first_name:
            return {
                'verified': False,
                'message': 'First name does not match our records for this Student ID.'
            }
        
        # Check last name
        if self.last_name.lower() != last_name:
            return {
                'verified': False,
                'message': 'Last name does not match our records for this Student ID.'
            }
        
        # Check middle initial
        record_mi = (self.middle_initial or '').upper().replace('.', '')
        
        if record_mi in ['N/A', '']:
            # Record has no middle initial
            if middle_initial and middle_initial not in ['N/A', '']:
                return {
                    'verified': False,
                    'message': 'Middle initial does not match our records. Our records show no middle initial for this student.'
                }
        else:
            # Record has a middle initial
            if middle_initial and middle_initial not in ['N/A', ''] and record_mi != middle_initial:
                return {
                    'verified': False,
                    'message': f'Middle initial does not match our records. Expected: {record_mi}'
                }
        
        # All checks passed
        return {
            'verified': True,
            'message': 'Student information verified successfully.',
            'student_data': {
                'student_id': self.student_id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'middle_initial': self.middle_initial,
                'sex': self.sex,
                'course': self.course,
                'year': self.year_level
            }
        }

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
    document_file = models.FileField(upload_to='documents/%Y/%m/', validators=document_validators)
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
    
    # Face Verification and Liveness Detection Fields
    liveness_verification_completed = models.BooleanField(default=False, help_text="Whether liveness verification was performed")
    liveness_verification_passed = models.BooleanField(default=False, help_text="Whether liveness checks passed")
    liveness_data = models.JSONField(default=dict, blank=True, help_text="Liveness challenge results (color flash, blink, movement)")
    face_detected_in_document = models.BooleanField(default=False, help_text="Whether a face was detected in the document")
    face_embedding = models.JSONField(default=dict, blank=True, help_text="Face embedding vector for comparison")
    face_verification_completed = models.BooleanField(default=False, help_text="Whether face verification with selfie was done")
    face_match_score = models.FloatField(default=0.0, help_text="Face similarity score (0.0-1.0)")
    face_match_confidence = models.CharField(max_length=20, blank=True, null=True, help_text="Confidence level: very_low, low, medium, high, very_high")
    selfie_captured = models.BooleanField(default=False, help_text="Whether a live selfie was captured for verification")
    
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
    grade_sheet = models.FileField(upload_to='grades/%Y/%m/', validators=grade_sheet_validators)
    
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
    
    # AI Grades Detection fields (for OCR-based grade extraction)
    ai_grades_detected = models.BooleanField(default=False, help_text="Whether AI detected grades from document")
    ai_gwa_calculated = models.FloatField(null=True, blank=True, help_text="AI-calculated GWA from OCR")
    ai_merit_level = models.CharField(max_length=50, blank=True, null=True, help_text="AI-determined merit level")
    ai_grades_confidence = models.FloatField(default=0.0, help_text="Confidence in OCR grade detection (0.0-1.0)")
    ai_grades_recommendations = models.JSONField(default=list, blank=True, help_text="Merit-based recommendations")
    
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
        1.75 = 87% (87-89)     → Satisfactory (Merit threshold)
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
            (1.75, 87.0),   # 87-89 → Satisfactory (Merit threshold)
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
        gwa_value = float(self.general_weighted_average)
        
        # OFFICIAL TCU-CEAA GRADING ELIGIBILITY CRITERIA:
        # ==================================================
        # GWA 1.0 to 1.75  → Basic (₱5,000) + Merit (₱5,000) = ₱10,000
        # GWA 1.76 to 2.5  → Basic (₱5,000) ONLY
        # GWA 2.51 and above → NOT ELIGIBLE
        #
        # If name verification (AI) passes, auto-approve for basic allowance (₱5,000)
        #
        # Basic Educational Assistance (₱5,000): GWA ≤ 2.5 (80%), no fails/inc/drops, ≥15 units
        # GWA 2.5 = 80% is the cutoff - anything 2.5 or better (lower number) qualifies
        #
        # If AI name verification is enabled and passed, override to auto-approve basic_eligible
        # Otherwise, use the strict rule
        basic_eligible = (
            gwa_value <= 2.5 and
            self.total_units >= 15 and
            not self.has_failing_grades and
            not self.has_incomplete_grades and
            not self.has_dropped_subjects
        )
        # If AI name verification is enabled and passed, override:
        if getattr(self, 'ai_verification_score', 0.0) >= 0.75:
            basic_eligible = True
        #
        # Merit Incentive (₱5,000): GWA ≤ 1.75 (87%) on 10-point scale
        merit_eligible = (
            gwa_value <= 1.75 and
            self.total_units >= 15 and
            not self.has_failing_grades and
            not self.has_incomplete_grades and
            not self.has_dropped_subjects
        )
        merit_eligible = (
            gwa_value <= 1.75 and
            self.total_units >= 15 and
            not self.has_failing_grades and
            not self.has_incomplete_grades and
            not self.has_dropped_subjects
        )
        
        self.qualifies_for_basic_allowance = basic_eligible
        self.qualifies_for_merit_incentive = merit_eligible
        self.ai_evaluation_completed = True
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        notes = []
        notes.append("🤖 Autonomous AI Processing - Auto-Approved")
        notes.append("=" * 40)
        if getattr(self, 'ai_verification_score', 0.0) >= 0.75:
            notes.append("✅ NAME VERIFIED: Your identity has been confirmed on the grade sheet")
            notes.append("🎉 AUTO-APPROVED: ₱5,000 Basic Allowance automatically granted")
            notes.append("")
        if basic_eligible:
            notes.append("✅ Qualifies for Basic Educational Assistance (₱5,000)")
        else:
            reasons = []
            if gwa_value > 2.5:
                reasons.append(f"GWA {self.general_weighted_average} > 2.5 ({gwa_percent:.2f}% < 80%)")
            if self.total_units < 15:
                reasons.append(f"Units {self.total_units} < 15")
            if self.has_failing_grades:
                reasons.append("Has failing grades")
            if self.has_incomplete_grades:
                reasons.append("Has incomplete grades")
            if self.has_dropped_subjects:
                reasons.append("Has dropped subjects")
            notes.append(f"❌ Does not qualify for Basic Allowance: {', '.join(reasons)}")
        
        if merit_eligible:
            notes.append("✅ Qualifies for Merit Incentive (₱5,000)")
        else:
            reasons = []
            if gwa_value > 1.75:
                reasons.append(f"GWA {self.general_weighted_average} > 1.75 ({gwa_percent:.2f}%)")
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



class EmailVerificationCode(models.Model):
    """
    Model to store email verification codes for new user registration.
    Codes expire after 10 minutes for security.
    """
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)  # 6-digit verification code
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)  # Track verification attempts
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def is_valid(self):
        """Check if code is still valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def is_expired(self):
        """Check if code has expired"""
        return timezone.now() >= self.expires_at
    
    def increment_attempts(self):
        """Increment verification attempts"""
        self.attempts += 1
        self.save()
    
    def mark_as_used(self):
        """Mark verification code as used"""
        self.is_used = True
        self.save()
    
    @staticmethod
    def generate_code():
        """Generate a random 6-digit verification code"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    @classmethod
    def create_verification_code(cls, email):
        """Create a new verification code for an email, only mark expired codes as used"""
        from datetime import timedelta
        now = timezone.now()
        # Only mark expired codes as used
        cls.objects.filter(email=email, is_used=False, expires_at__lt=now).update(is_used=True)
        # Generate new code
        code = cls.generate_code()
        expires_at = now + timedelta(minutes=10)
        return cls.objects.create(
            email=email,
            code=code,
            expires_at=expires_at
        )
    
    def __str__(self):
        return f"Verification code for {self.email} - {'Used' if self.is_used else 'Active'}"


class BasicQualification(models.Model):
    """
    Stores the basic qualification criteria responses for students.
    This must be completed before students can access documents and grades pages.
    """
    APPLICANT_TYPE_CHOICES = [
        ('new', 'New Applicant'),
        ('renewing', 'Renewing Applicant'),
    ]
    
    student = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'},
        related_name='basic_qualification'
    )
    
    # Basic Qualification Questions
    is_enrolled = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Currently enrolled at Taguig City University"
    )
    is_resident = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Bona fide resident of Taguig City for at least 3 years"
    )
    is_eighteen_or_older = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="18 years old or older"
    )
    is_registered_voter = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Registered voter of the City"
    )
    parent_is_voter = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="One parent is an active voter of Taguig City"
    )
    has_good_moral_character = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Possesses good moral character"
    )
    is_committed = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Committed to love and serve Taguig City"
    )
    
    # Applicant Type
    applicant_type = models.CharField(
        max_length=10,
        choices=APPLICANT_TYPE_CHOICES,
        default='new'
    )
    
    # Status and timestamps
    is_qualified = models.BooleanField(
        default=False,
        help_text="Automatically set to True if all criteria are met"
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Basic Qualification"
        verbose_name_plural = "Basic Qualifications"
        ordering = ['-completed_at']
    
    def save(self, *args, **kwargs):
        # Automatically determine if qualified based on all answers being True
        self.is_qualified = all([
            self.is_enrolled,
            self.is_resident,
            self.is_eighteen_or_older,
            self.is_registered_voter,
            self.parent_is_voter,
            self.has_good_moral_character,
            self.is_committed
        ])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Qualification for {self.student.username} - {'Qualified' if self.is_qualified else 'Not Qualified'}"


class FullApplication(models.Model):
    """
    Complete application form submitted by students.
    Contains all personal, contact, academic, and family information.
    """
    SEMESTER_CHOICES = [
        ('1st', 'First Semester'),
        ('2nd', 'Second Semester'),
        ('summer', 'Summer'),
    ]
    
    APPLICATION_TYPE_CHOICES = [
        ('new', 'New Application'),
        ('renewal', 'Renewal'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='full_applications',
        limit_choices_to={'role': 'student'}
    )
    
    # Application Details
    facebook_link = models.URLField(max_length=500, blank=True, null=True)
    application_type = models.CharField(max_length=10, choices=APPLICATION_TYPE_CHOICES, default='new')
    scholarship_type = models.CharField(max_length=100, default='TCU-CEAA')
    school_year = models.CharField(max_length=20, help_text="School year (e.g., 2024-2025)")
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='1st')
    applying_for_merit = models.CharField(max_length=10, blank=True, null=True)
    
    # Personal Information
    first_name = models.CharField(max_length=100, default='')
    middle_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, default='')
    house_no = models.CharField(max_length=50, default='')
    street = models.CharField(max_length=200, default='')
    zip_code = models.CharField(max_length=10, default='')
    barangay = models.CharField(max_length=100, help_text='Barangay of residence', default='')
    district = models.CharField(max_length=50, blank=True, default='')
    mobile_no = models.CharField(max_length=15, help_text='Contact number', default='')
    other_contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(help_text="Student's email address", default='')
    date_of_birth = models.DateField(help_text='Date of birth', null=True, blank=True)
    age = models.IntegerField(blank=True, null=True)
    citizenship = models.CharField(max_length=50, default='Filipino')
    sex = models.CharField(max_length=10, default='')
    marital_status = models.CharField(max_length=20, default='')
    religion = models.CharField(max_length=100, default='')
    place_of_birth = models.CharField(max_length=200, default='')
    years_of_residency = models.CharField(max_length=50, default='')
    
    # School Information
    course_name = models.CharField(max_length=200, default='')
    ladderized = models.CharField(max_length=10, default='NO')
    year_level = models.CharField(max_length=50, default='')
    swa_input = models.CharField(max_length=100, blank=True, null=True)
    units_enrolled = models.CharField(max_length=50, default='')
    course_duration = models.CharField(max_length=50, default='')
    school_name = models.CharField(max_length=200, default='TAGUIG CITY UNIVERSITY (TCU)')
    school_address = models.CharField(max_length=500, default='Gen. Santos Ave., Central Bicutan, Taguig City')
    graduating_this_term = models.CharField(max_length=10, default='')
    semesters_to_graduate = models.CharField(max_length=50, blank=True, null=True)
    with_honors = models.CharField(max_length=50, blank=True, null=True)
    transferee = models.CharField(max_length=10, default='')
    shiftee = models.CharField(max_length=10, default='')
    status = models.CharField(max_length=50, default='')
    
    # Educational Background - Senior High School
    shs_attended = models.CharField(max_length=200, blank=True)
    shs_type = models.CharField(max_length=50, blank=True)
    shs_address = models.CharField(max_length=500, blank=True)
    shs_years = models.CharField(max_length=50, blank=True)
    shs_honors = models.CharField(max_length=200, blank=True)
    
    # Educational Background - Junior High School
    jhs_attended = models.CharField(max_length=200, blank=True)
    jhs_type = models.CharField(max_length=50, blank=True)
    jhs_address = models.CharField(max_length=500, blank=True)
    jhs_years = models.CharField(max_length=50, blank=True)
    jhs_honors = models.CharField(max_length=200, blank=True)
    
    # Educational Background - Elementary
    elem_attended = models.CharField(max_length=200, blank=True)
    elem_type = models.CharField(max_length=50, blank=True)
    elem_address = models.CharField(max_length=500, blank=True)
    elem_years = models.CharField(max_length=50, blank=True)
    elem_honors = models.CharField(max_length=200, blank=True)
    
    # Parents Information - Father
    father_name = models.CharField(max_length=200, blank=True)
    father_address = models.CharField(max_length=500, blank=True)
    father_contact = models.CharField(max_length=15, blank=True)
    father_occupation = models.CharField(max_length=200, blank=True)
    father_place_of_work = models.CharField(max_length=200, blank=True)
    father_education = models.CharField(max_length=200, blank=True)
    father_deceased = models.BooleanField(default=False)
    
    # Parents Information - Mother
    mother_name = models.CharField(max_length=200, blank=True)
    mother_address = models.CharField(max_length=500, blank=True)
    mother_contact = models.CharField(max_length=15, blank=True)
    mother_occupation = models.CharField(max_length=200, blank=True)
    mother_place_of_work = models.CharField(max_length=200, blank=True)
    mother_education = models.CharField(max_length=200, blank=True)
    mother_deceased = models.BooleanField(default=False)
    
    # Status Fields
    is_submitted = models.BooleanField(default=False, help_text='Whether the application has been submitted')
    is_locked = models.BooleanField(default=False, help_text='Whether the application is locked for editing')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True, help_text='When the application was submitted')
    
    class Meta:
        verbose_name = "Full Application"
        verbose_name_plural = "Full Applications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Application for {self.user.username} - {self.school_year} {self.semester}"


# Import fraud detection models at the end to avoid circular import
from .fraud_detection_models import FraudReport, FraudNotification, UserAccountAction


