from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
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
    profile_image = models.ImageField(upload_to=profile_image_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
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
        ('birth_certificate', 'Birth Certificate'),
        ('school_id', 'School ID'),
        ('report_card', 'Report Card/Grades'),
        ('enrollment_certificate', 'Certificate of Enrollment'),
        ('barangay_clearance', 'Barangay Clearance'),
        ('parents_id', 'Parent\'s Valid ID'),
        ('voter_certification', 'Voter\'s Certification'),
        ('other', 'Other Document'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision_needed', 'Revision Needed'),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='documents/%Y/%m/')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
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
    general_weighted_average = models.DecimalField(max_digits=5, decimal_places=2, 
                                                 validators=[MinValueValidator(65.0), MaxValueValidator(100.0)])
    semestral_weighted_average = models.DecimalField(max_digits=5, decimal_places=2, 
                                                   validators=[MinValueValidator(65.0), MaxValueValidator(100.0)])
    
    # Grade sheet upload
    grade_sheet = models.FileField(upload_to='grades/%Y/%m/')
    
    # Validation flags
    has_failing_grades = models.BooleanField(default=False)
    has_incomplete_grades = models.BooleanField(default=False)
    has_dropped_subjects = models.BooleanField(default=False)
    
    # AI evaluation results
    ai_evaluation_completed = models.BooleanField(default=False)
    ai_evaluation_notes = models.TextField(blank=True, null=True)
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
    
    def calculate_allowance_eligibility(self):
        """AI-based calculation of allowance eligibility"""
        # Basic Educational Assistance (₱5,000): GWA ≥ 80%, no fails/inc/drops, ≥15 units
        basic_eligible = (
            self.general_weighted_average >= 80.0 and
            self.total_units >= 15 and
            not self.has_failing_grades and
            not self.has_incomplete_grades and
            not self.has_dropped_subjects
        )
        
        # Merit Incentive (₱5,000): SWA ≥ 88.75%, no fails/inc/drops, ≥15 units
        merit_eligible = (
            self.semestral_weighted_average >= 88.75 and
            self.total_units >= 15 and
            not self.has_failing_grades and
            not self.has_incomplete_grades and
            not self.has_dropped_subjects
        )
        
        self.qualifies_for_basic_allowance = basic_eligible
        self.qualifies_for_merit_incentive = merit_eligible
        self.ai_evaluation_completed = True
        
        # Generate AI evaluation notes
        notes = []
        if basic_eligible:
            notes.append("✅ Qualifies for Basic Educational Assistance (₱5,000)")
        else:
            reasons = []
            if self.general_weighted_average < 80.0:
                reasons.append(f"GWA {self.general_weighted_average}% < 80%")
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
            if self.semestral_weighted_average < 88.75:
                reasons.append(f"SWA {self.semestral_weighted_average}% < 88.75%")
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
            notes.append(f"💰 Total Allowance: ₱{total_allowance:,}")
        else:
            notes.append("💰 Total Allowance: ₱0")
        
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
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['student', 'grade_submission']
    
    def __str__(self):
        return f"{self.student.username} - {self.get_application_type_display()} - ₱{self.amount}"
