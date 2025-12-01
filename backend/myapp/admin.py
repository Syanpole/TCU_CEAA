from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.db import transaction
from rest_framework.authtoken.models import Token
from .models import Task, Student, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication, AuditLog, SystemAnalytics, VerifiedStudent, EmailVerificationCode, BasicQualification, FullApplication
import logging

logger = logging.getLogger(__name__)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'student_id', 'is_staff', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'student_id', 'middle_initial')}),
        ('Email Verification', {'fields': ('is_email_verified', 'email_verified_at')}),
        ('AI Verification', {'fields': ('ai_verification_score',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'student_id', 'middle_initial')}),
    )
    
    actions = ['delete_users_with_records']
    
    def delete_users_with_records(self, request, queryset):
        """
        Custom deletion action that safely removes users and all related records
        """
        if not request.user.is_superuser:
            self.message_user(request, 'Only superusers can delete user accounts.', level=messages.ERROR)
            return
        
        total_deleted = 0
        total_records_deleted = 0
        
        for user in queryset:
            try:
                with transaction.atomic():
                    # Count related records before deletion
                    documents = DocumentSubmission.objects.filter(student=user).count()
                    grades = GradeSubmission.objects.filter(student=user).count()
                    applications = AllowanceApplication.objects.filter(student=user).count()
                    verifications = EmailVerificationCode.objects.filter(user=user).count()
                    
                    # Delete auth token
                    Token.objects.filter(user=user).delete()
                    
                    # Reset VerifiedStudent if exists
                    try:
                        verified_student = VerifiedStudent.objects.get(registered_user=user)
                        verified_student.has_registered = False
                        verified_student.registered_user = None
                        verified_student.save()
                    except VerifiedStudent.DoesNotExist:
                        pass
                    
                    # Delete user (CASCADE will handle related records)
                    user.delete()
                    
                    records_deleted = documents + grades + applications + verifications + 1
                    total_deleted += 1
                    total_records_deleted += records_deleted
                    
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error deleting user {user.username}: {str(e)}', 
                    level=messages.ERROR
                )
        
        self.message_user(
            request,
            f'Successfully deleted {total_deleted} user(s) and {total_records_deleted} related record(s).',
            level=messages.SUCCESS
        )
    
    delete_users_with_records.short_description = '🗑️ Delete selected users and ALL their records'

# Register CustomUser with CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'completed', 'created_at']
    list_filter = ['completed', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'email', 'enrollment_date']
    list_filter = ['enrollment_date']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']

@admin.register(VerifiedStudent)
class VerifiedStudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'get_full_name', 'course', 'year_level', 'is_active', 'has_registered', 'added_at']
    list_filter = ['is_active', 'has_registered', 'course', 'year_level', 'sex', 'added_at']
    search_fields = ['student_id', 'first_name', 'last_name']
    readonly_fields = ['added_at', 'updated_at', 'added_by']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'middle_initial', 'sex')
        }),
        ('Academic Information', {
            'fields': ('course', 'year_level')
        }),
        ('Registration Status', {
            'fields': ('is_active', 'has_registered', 'registered_user')
        }),
        ('Audit Information', {
            'fields': ('added_by', 'added_at', 'updated_at', 'notes'),
            'classes': ('collapse',)
        })
    )
    
    def get_full_name(self, obj):
        mi = f" {obj.middle_initial}." if obj.middle_initial and obj.middle_initial != 'N/A' else ""
        return f"{obj.first_name}{mi} {obj.last_name}"
    get_full_name.short_description = 'Full Name'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set added_by on creation
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['activate_students', 'deactivate_students', 'reset_registration_status']
    
    def activate_students(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {updated} student(s).')
    activate_students.short_description = 'Activate selected students'
    
    def deactivate_students(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {updated} student(s).')
    deactivate_students.short_description = 'Deactivate selected students'
    
    def reset_registration_status(self, request, queryset):
        updated = queryset.update(has_registered=False, registered_user=None)
        self.message_user(request, f'Successfully reset registration status for {updated} student(s).')
    reset_registration_status.short_description = 'Reset registration status'

@admin.register(DocumentSubmission)
class DocumentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'document_type', 'status', 'submitted_at', 'reviewed_by']
    list_filter = ['document_type', 'status', 'submitted_at']
    search_fields = ['student__username', 'student__student_id', 'document_type']
    readonly_fields = ['submitted_at', 'reviewed_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['student', 'document_type', 'document_file']
        return self.readonly_fields

@admin.register(GradeSubmission)
class GradeSubmissionAdmin(admin.ModelAdmin):
    # Group and display grades by student and semester
    list_display = ['student_info', 'subject_display', 'grade_display', 'automated_gwa_display', 
                   'eligibility_display', 'ai_status', 'verification_badge', 'status_badge', 'submitted_at']
    list_filter = ['academic_year', 'semester', 'status', 'ai_merit_level', 'qualifies_for_merit_incentive', 'submitted_at']
    search_fields = ['student__username', 'student__student_id', 'student__first_name', 'student__last_name', 
                    'subject_code', 'subject_name', 'academic_year']
    readonly_fields = ['submitted_at', 'reviewed_at', 'ai_evaluation_completed', 'ai_evaluation_notes', 
                      'ai_extracted_grades', 'ai_confidence_score', 'grade_sheet_preview', 'student_all_grades',
                      'automated_gwa_details', 'detection_validation_status']
    ordering = ['-academic_year', 'semester', 'student__student_id', 'subject_code']
    list_per_page = 50
    
    fieldsets = (
        ('📚 Student & Subject Information', {
            'fields': ('student', 'academic_year', 'semester', 'subject_code', 'subject_name')
        }),
        ('📊 Grade Details (Per-Subject)', {
            'fields': ('units', 'grade_received', 'grade_sheet', 'grade_sheet_preview')
        }),
        ('🤖 AI Detection & Validation Status', {
            'fields': ('detection_validation_status',),
            'classes': ('collapse',)
        }),
        ('🎓 Automated GWA Calculation Results', {
            'fields': ('automated_gwa_details',),
            'classes': ('collapse',)
        }),
        ('🎓 Student All Grades Summary', {
            'fields': ('student_all_grades',),
            'description': 'View all grades submitted by this student for this semester'
        }),
        ('🤖 AI Verification Results', {
            'fields': ('ai_evaluation_completed', 'ai_confidence_score', 'ai_evaluation_notes', 
                      'ai_extracted_grades', 'ai_gwa_calculated', 'ai_merit_level'),
            'classes': ('collapse',)
        }),
        ('🏆 Merit & Qualification', {
            'fields': ('qualifies_for_merit_incentive', 'qualifies_for_basic_allowance'),
        }),
        ('✅ Admin Review', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('🕐 Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        })
    )
    
    def student_info(self, obj):
        """Display student info with semester grouping"""
        from django.utils.html import format_html
        count = GradeSubmission.objects.filter(
            student=obj.student,
            academic_year=obj.academic_year,
            semester=obj.semester
        ).count()
        
        # Get semester display name
        semester_display = {
            '1st': '1st Semester',
            '2nd': '2nd Semester',
            'summer': 'Summer',
            'midyear': 'Midyear'
        }.get(obj.semester, obj.semester)
        
        return format_html(
            '<strong>{}</strong><br>'
            '<small>ID: {}</small><br>'
            '<span style="color: #007bff; font-weight: 600;">{} - {}</span><br>'
            '<span style="color: #666; font-size: 11px;">{} subject{}</span>',
            obj.student.get_full_name() or obj.student.username,
            obj.student.student_id,
            obj.academic_year,
            semester_display,
            count,
            's' if count != 1 else ''
        )
    student_info.short_description = 'Student & Semester'
    
    def subject_display(self, obj):
        """Display subject code and name"""
        from django.utils.html import format_html
        return format_html(
            '<strong>{}</strong><br><small>{}</small><br><span style="color: #888;">{} units</span>',
            obj.subject_code or 'N/A',
            obj.subject_name or 'N/A',
            obj.units or 0
        )
    subject_display.short_description = 'Subject'
    
    def grade_display(self, obj):
        """Display grade with visual indicator"""
        from django.utils.html import format_html
        if obj.grade_received:
            grade = float(obj.grade_received)
            # Color code: <= 1.5 (green), <= 2.5 (blue), <= 3.0 (orange), > 3.0 (red)
            if grade <= 1.5:
                color = '#28a745'  # green
            elif grade <= 2.5:
                color = '#007bff'  # blue
            elif grade <= 3.0:
                color = '#fd7e14'  # orange
            else:
                color = '#dc3545'  # red
            
            return format_html(
                '<div style="font-size: 24px; font-weight: bold; color: {};">{:.2f}</div>',
                color, grade
            )
        return format_html('<span style="color: #999;">Not set</span>')
    grade_display.short_description = 'Grade'
    
    def automated_gwa_display(self, obj):
        """Display automated GWA calculation results"""
        from django.utils.html import format_html
        
        # Get the latest GWA calculation for this student's semester
        from myapp.services import gwa_calculation_service
        gwa_data = gwa_calculation_service.calculate_semester_gwa(
            obj.student, obj.academic_year, obj.semester
        )
        
        if gwa_data:
            gwa = gwa_data['gwa']
            merit_level = gwa_data['merit_level']
            
            # Color coding based on merit level
            color_map = {
                'HIGH_HONORS': '#d4af37',
                'HONORS': '#007bff', 
                'MERIT': '#28a745',
                'REGULAR': '#6c757d',
                'BELOW_PASSING': '#dc3545'
            }
            color = color_map.get(merit_level, '#6c757d')
            
            # Merit level emoji
            emoji_map = {
                'HIGH_HONORS': '🥇',
                'HONORS': '🥈',
                'MERIT': '🥉',
                'REGULAR': '📋',
                'BELOW_PASSING': '⚠️'
            }
            emoji = emoji_map.get(merit_level, '📊')
            
            return format_html(
                '<div style="text-align: center;">'
                '<div style="font-size: 20px; font-weight: bold; color: {};">{:.2f}</div>'
                '<div style="font-size: 12px; color: {}; margin-top: 2px;">{} {}</div>'
                '<div style="font-size: 10px; color: #666;">{} units</div>'
                '</div>',
                color, gwa, color, emoji, merit_level.replace('_', ' ').title(), gwa_data['total_units']
            )
        return format_html('<span style="color: #999; font-style: italic;">Pending</span>')
    automated_gwa_display.short_description = 'Auto GWA'
    
    def eligibility_display(self, obj):
        """Display allowance eligibility based on automated GWA"""
        from django.utils.html import format_html
        
        # Get the latest GWA calculation for this student's semester
        from myapp.services import gwa_calculation_service
        gwa_data = gwa_calculation_service.calculate_semester_gwa(
            obj.student, obj.academic_year, obj.semester
        )
        
        if gwa_data:
            gwa = gwa_data['gwa']
            
            # Updated eligibility logic: GWA < 2.00 = basic only ₱5,000, GWA ≥ 2.00 = both ₱10,000
            if gwa < 2.00:
                # Basic only
                return format_html(
                    '<div style="text-align: center;">'
                    '<div style="font-size: 16px; font-weight: bold; color: #28a745;">₱5,000</div>'
                    '<div style="font-size: 11px; color: #666;">Basic Only</div>'
                    '</div>'
                )
            else:
                # Both basic and merit
                return format_html(
                    '<div style="text-align: center;">'
                    '<div style="font-size: 16px; font-weight: bold; color: #007bff;">₱10,000</div>'
                    '<div style="font-size: 11px; color: #666;">Basic + Merit</div>'
                    '</div>'
                )
        return format_html('<span style="color: #999; font-style: italic;">Pending</span>')
    eligibility_display.short_description = 'Allowance'
    
    def detection_validation_status(self, obj):
        """Display AI detection and validation service integration status"""
        from django.utils.html import format_html
        from myapp.grades_detection_service import get_grades_detection_service
        from myapp.grade_validation_service import get_grade_validation_service
        
        status_parts = []
        
        # Detection Service Status
        detection_service = get_grades_detection_service()
        if obj.grade_sheet:
            try:
                # Attempt to run detection on this grade sheet
                detection_result = detection_service.detect_grades_from_image(obj.grade_sheet.path)
                if detection_result.get('success'):
                    detected_count = len(detection_result.get('detected_grades', []))
                    status_parts.append(f'<span style="color: #28a745;">✓ Detection: {detected_count} grades found</span>')
                else:
                    status_parts.append('<span style="color: #dc3545;">✗ Detection: Failed</span>')
            except Exception as e:
                status_parts.append('<span style="color: #ffc107;">⚠️ Detection: Error</span>')
        else:
            status_parts.append('<span style="color: #999;">No grade sheet</span>')
        
        # Validation Service Status
        validation_service = get_grade_validation_service()
        
        # Get COE subjects for this student
        from myapp.models import DocumentSubmission
        coe_doc = DocumentSubmission.objects.filter(
            student=obj.student,
            document_type='certificate_of_enrollment',
            status='approved'
        ).order_by('-submitted_at').first()
        
        if coe_doc and coe_doc.extracted_subjects:
            # Get all grades for this semester to validate
            semester_grades = GradeSubmission.objects.filter(
                student=obj.student,
                academic_year=obj.academic_year,
                semester=obj.semester,
                subject_code__isnull=False
            )
            
            grade_data = []
            for grade in semester_grades:
                grade_data.append({
                    'subject_code': grade.subject_code,
                    'subject_name': grade.subject_name,
                    'grade_received': float(grade.grade_received) if grade.grade_received else None
                })
            
            validation_result = validation_service.validate_grade_submissions(
                coe_doc.extracted_subjects,
                grade_data
            )
            
            if validation_result.get('is_valid'):
                status_parts.append('<span style="color: #28a745;">✓ Validation: Passed</span>')
            else:
                error_count = len(validation_result.get('errors', []))
                status_parts.append(f'<span style="color: #dc3545;">✗ Validation: {error_count} errors</span>')
        else:
            status_parts.append('<span style="color: #ffc107;">⚠️ Validation: No COE</span>')
        
        return format_html('<br>'.join(status_parts))
    detection_validation_status.short_description = 'AI Services Status'
    
    def automated_gwa_details(self, obj):
        """Display detailed automated GWA calculation with service integration"""
        from django.utils.html import format_html
        from myapp.services import gwa_calculation_service
        
        # Get automated GWA calculation
        gwa_data = gwa_calculation_service.calculate_semester_gwa(
            obj.student, obj.academic_year, obj.semester
        )
        
        if not gwa_data:
            return format_html('<p style="color: #999; font-style: italic;">No automated GWA calculation available</p>')
        
        gwa = gwa_data['gwa']
        merit_level = gwa_data['merit_level']
        total_units = gwa_data['total_units']
        total_subjects = gwa_data['total_subjects']
        
        # Determine allowance amount based on updated logic
        if gwa < 2.00:
            allowance_amount = 5000
            allowance_type = "Basic Allowance Only"
            allowance_color = "#28a745"
        else:
            allowance_amount = 10000
            allowance_type = "Basic + Merit Allowance"
            allowance_color = "#007bff"
        
        # Build detailed display
        html_parts = []
        html_parts.append('<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">')
        html_parts.append('<h4 style="margin: 0 0 10px 0; color: #007bff;">🤖 Automated GWA Calculation</h4>')
        
        # GWA Display
        html_parts.append('<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">')
        html_parts.append('<div>')
        html_parts.append(f'<div style="font-size: 24px; font-weight: bold; color: #007bff;">{gwa:.2f}</div>')
        html_parts.append(f'<div style="font-size: 12px; color: #666;">General Weighted Average</div>')
        html_parts.append('</div>')
        html_parts.append('<div style="text-align: right;">')
        html_parts.append(f'<div style="font-size: 18px; font-weight: bold;">{merit_level.replace("_", " ").title()}</div>')
        html_parts.append(f'<div style="font-size: 12px; color: #666;">{total_subjects} subjects, {total_units} units</div>')
        html_parts.append('</div>')
        html_parts.append('</div>')
        
        # Allowance Eligibility
        html_parts.append('<div style="background: white; padding: 10px; border-radius: 4px; margin-bottom: 10px;">')
        html_parts.append(f'<div style="font-size: 16px; font-weight: bold; color: {allowance_color};">₱{allowance_amount:,}</div>')
        html_parts.append(f'<div style="font-size: 12px; color: #666;">{allowance_type}</div>')
        html_parts.append('</div>')
        
        # Service Integration Status
        html_parts.append('<div style="font-size: 11px; color: #666;">')
        html_parts.append('<strong>Services Used:</strong> GWACalculationService, GradesDetectionService, GradeValidationService<br>')
        html_parts.append('<strong>Eligibility Rule:</strong> GWA < 2.00 = ₱5,000 basic only, GWA ≥ 2.00 = ₱10,000 both<br>')
        html_parts.append('<strong>Calculation:</strong> Weighted average of all approved semester grades')
        html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return format_html(''.join(html_parts))
    automated_gwa_details.short_description = 'Automated GWA Details'
    
    def ai_status(self, obj):
        """Display AI verification status"""
        from django.utils.html import format_html
        if obj.ai_evaluation_completed:
            confidence = obj.ai_confidence_score * 100 if obj.ai_confidence_score else 0
            if confidence >= 85:
                badge_color = 'success'
                icon = '✓'
            elif confidence >= 70:
                badge_color = 'warning'
                icon = '⚠'
            else:
                badge_color = 'danger'
                icon = '✗'
            
            return format_html(
                '<span class="badge badge-{}">{} AI {:.0f}%</span>',
                badge_color, icon, confidence
            )
        return format_html('<span class="badge badge-secondary">⏳ Pending</span>')
    ai_status.short_description = 'AI Status'
    
    def verification_badge(self, obj):
        """Show verification badges"""
        from django.utils.html import format_html
        badges = []
        
        if obj.ai_extracted_grades:
            data = obj.ai_extracted_grades
            
            # Document type badge (informational)
            doc_type = data.get('document_type', 'GRADE_SHEET')
            if doc_type == 'CLASS_CARD':
                badges.append('<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">📋 CLASS CARD</span>')
            
            # Authenticity with count
            detected_count = data.get('detected_count', 0)
            if data.get('is_authentic'):
                badges.append(f'<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">🔒 AUTHENTIC ({detected_count}/3)</span>')
            elif detected_count > 0:
                badges.append(f'<span style="background: #ffc107; color: #000; padding: 2px 6px; border-radius: 3px; font-size: 11px;">⚠️ PARTIAL ({detected_count}/3)</span>')
            else:
                badges.append('<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">✗ NO LOGOS</span>')
            
            if data.get('subject_in_coe'):
                badges.append('<span style="background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">📋 IN COE</span>')
            
            if data.get('grade_matches'):
                badges.append('<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">✓ MATCH</span>')
            elif data.get('extracted_grade'):
                badges.append('<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">✗ MISMATCH</span>')
            else:
                badges.append('<span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">? NO GRADE</span>')
        
        return format_html('<br>'.join(badges)) if badges else format_html('<span style="color: #999;">-</span>')
    verification_badge.short_description = 'Verification'
    
    def status_badge(self, obj):
        """Display status with color"""
        from django.utils.html import format_html
        status_colors = {
            'approved': ('#28a745', '✓ Approved'),
            'pending': ('#ffc107', '⏳ Pending'),
            'rejected': ('#dc3545', '✗ Rejected'),
            'processing': ('#17a2b8', '🔄 Processing')
        }
        color, label = status_colors.get(obj.status, ('#6c757d', obj.status))
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Status'
    
    def grade_sheet_preview(self, obj):
        """Show grade sheet image preview"""
        from django.utils.html import format_html
        if obj.grade_sheet:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px;"></a>',
                obj.grade_sheet.url, obj.grade_sheet.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    grade_sheet_preview.short_description = 'Grade Sheet Preview'
    
    def student_all_grades(self, obj):
        """Display all grades for this student in this semester with GWA calculation"""
        from django.utils.html import format_html
        
        all_grades = GradeSubmission.objects.filter(
            student=obj.student,
            academic_year=obj.academic_year,
            semester=obj.semester,
            subject_code__isnull=False
        ).order_by('subject_code')
        
        if not all_grades.exists():
            return format_html('<p>No grades found</p>')
        
        # Get semester display name
        semester_display = {
            '1st': '1st Semester',
            '2nd': '2nd Semester',
            'summer': 'Summer',
            'midyear': 'Midyear'
        }.get(obj.semester, obj.semester)
        
        rows = []
        # Add header with semester info
        rows.append('<div style="background: #007bff; color: white; padding: 12px; border-radius: 8px 8px 0 0; margin-bottom: 0;">')
        rows.append(f'<h3 style="margin: 0; font-size: 16px;">📚 {obj.academic_year} - {semester_display}</h3>')
        rows.append(f'<p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{obj.student.get_full_name()} (ID: {obj.student.student_id})</p>')
        rows.append('</div>')
        
        rows.append('<table style="width: 100%; border-collapse: collapse; margin-top: 0;">')
        rows.append('<tr style="background: #f8f9fa; font-weight: bold;">')
        rows.append('<th style="padding: 10px; border: 1px solid #dee2e6; text-align: left;">Subject Code</th>')
        rows.append('<th style="padding: 10px; border: 1px solid #dee2e6; text-align: left;">Subject Name</th>')
        rows.append('<th style="padding: 10px; border: 1px solid #dee2e6; text-align: center;">Units</th>')
        rows.append('<th style="padding: 10px; border: 1px solid #dee2e6; text-align: center;">Grade</th>')
        rows.append('<th style="padding: 10px; border: 1px solid #dee2e6; text-align: center;">Status</th>')
        rows.append('</tr>')
        
        total_units = 0
        total_grade_points = 0
        
        for grade in all_grades:
            status_color = {
                'approved': '#28a745',
                'pending': '#ffc107',
                'rejected': '#dc3545',
                'processing': '#17a2b8'
            }.get(grade.status, '#6c757d')
            
            rows.append('<tr>')
            rows.append(f'<td style="padding: 8px; border: 1px solid #dee2e6;">{grade.subject_code}</td>')
            rows.append(f'<td style="padding: 8px; border: 1px solid #dee2e6;">{grade.subject_name}</td>')
            rows.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{grade.units}</td>')
            rows.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center; font-weight: bold;">{grade.grade_received}</td>')
            rows.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;"><span style="color: {status_color};">{grade.status}</span></td>')
            rows.append('</tr>')
            
            if grade.status == 'approved' and grade.units and grade.grade_received:
                total_units += grade.units
                total_grade_points += float(grade.grade_received) * grade.units
        
        rows.append('</table>')
        
        # Show GPA and semester summary
        approved_count = all_grades.filter(status='approved').count()
        total_count = all_grades.count()
        completion_percentage = (approved_count / total_count * 100) if total_count > 0 else 0
        
        if total_units > 0:
            gpa = total_grade_points / total_units
            merit_level = ''
            if gpa <= 1.50:
                merit_level = '🥇 HIGH HONORS'
                merit_color = '#d4af37'
                merit_bg = '#fff8e1'
            elif gpa <= 2.00:
                merit_level = '🥈 HONORS'
                merit_color = '#007bff'
                merit_bg = '#e3f2fd'
            elif gpa <= 2.50:
                merit_level = '🥉 MERIT'
                merit_color = '#28a745'
                merit_bg = '#e8f5e9'
            elif gpa <= 3.00:
                merit_level = '📋 REGULAR'
                merit_color = '#6c757d'
                merit_bg = '#f5f5f5'
            else:
                merit_level = '⚠️ BELOW PASSING'
                merit_color = '#dc3545'
                merit_bg = '#ffebee'
            
            rows.append(f'<div style="margin-top: 20px; padding: 20px; background: {merit_bg}; border-radius: 8px; border-left: 4px solid {merit_color};">')
            rows.append(f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">')
            rows.append(f'<div style="flex: 1;">')
            rows.append(f'<div style="font-size: 13px; color: #666; margin-bottom: 5px;">GENERAL WEIGHTED AVERAGE</div>')
            rows.append(f'<div style="font-size: 36px; font-weight: bold; color: {merit_color}; line-height: 1;">{gpa:.2f}</div>')
            rows.append(f'</div>')
            rows.append(f'<div style="flex: 1; text-align: right;">')
            rows.append(f'<div style="font-size: 24px; font-weight: bold; color: {merit_color};">{merit_level}</div>')
            rows.append(f'<div style="font-size: 13px; color: #666; margin-top: 5px;">{total_units} total units</div>')
            rows.append(f'</div>')
            rows.append(f'</div>')
            rows.append(f'<div style="background: white; padding: 10px; border-radius: 4px;">')
            rows.append(f'<div style="display: flex; justify-content: space-between; font-size: 13px;">')
            rows.append(f'<span><strong>Completion:</strong> {approved_count}/{total_count} subjects approved ({completion_percentage:.0f}%)</span>')
            rows.append(f'<span><strong>Merit Eligible:</strong> {"✅ YES" if gpa <= 2.50 and approved_count == total_count else "⏳ Pending" if approved_count < total_count else "❌ NO"}</span>')
            rows.append(f'</div>')
            rows.append(f'</div>')
            rows.append('</div>')
        else:
            rows.append(f'<div style="margin-top: 20px; padding: 20px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">')
            rows.append(f'<div style="color: #856404;">⚠️ <strong>No approved grades yet.</strong> Approve subjects to calculate GWA.</div>')
            rows.append(f'<div style="margin-top: 10px; font-size: 13px;">Progress: {approved_count}/{total_count} subjects approved</div>')
            rows.append('</div>')
        
        return format_html(''.join(rows))
    student_all_grades.short_description = 'All Grades This Semester'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['student', 'academic_year', 'semester', 'subject_code', 'subject_name']
        return self.readonly_fields
    
    def semester_grouping_summary(self, obj):
        """Display a hierarchical summary of all grades grouped by semester"""
        from django.utils.html import format_html
        from myapp.semester_grouping_service import get_semester_grouping_service
        
        grouping_service = get_semester_grouping_service()
        
        try:
            # Get all semester groups for this student
            semester_groups = grouping_service.group_student_grades_by_semester(obj.student)
            
            if not semester_groups:
                return format_html('<span style="color: #999;">No grades found</span>')
            
            rows = []
            rows.append('<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">')
            rows.append('<h4 style="margin: 0 0 15px 0; color: #007bff;">📅 Semester Groups Overview</h4>')
            
            for group in semester_groups:
                academic_year = group['academic_year']
                semester_label = group['semester_label']
                gwa = group['gwa']
                subject_count = group['subject_count']
                total_units = group['total_units']
                merit_level = group.get('merit_level', 'BELOW_PASSING')
                all_approved = group['all_approved']
                pending_count = group.get('pending_count', 0)
                approved_count = group.get('approved_count', 0)
                
                # Determine color based on merit level
                color_map = {
                    'HIGH_HONORS': '#d4af37',
                    'HONORS': '#007bff',
                    'MERIT': '#28a745',
                    'REGULAR': '#6c757d',
                    'BELOW_PASSING': '#dc3545'
                }
                merit_color = color_map.get(merit_level, '#6c757d')
                
                # Emoji map
                emoji_map = {
                    'HIGH_HONORS': '🥇',
                    'HONORS': '🥈',
                    'MERIT': '🥉',
                    'REGULAR': '📋',
                    'BELOW_PASSING': '⚠️'
                }
                emoji = emoji_map.get(merit_level, '📊')
                
                # Completion status
                completion_color = '#28a745' if all_approved else '#ffc107'
                completion_text = '✅ All Approved' if all_approved else f'⏳ {pending_count} Pending'
                
                rows.append('<div style="background: white; padding: 12px; margin-bottom: 10px; border-radius: 6px; border-left: 3px solid ' + merit_color + ';">')
                rows.append(f'<div style="display: flex; justify-content: space-between; align-items: center;">')
                rows.append(f'<div style="flex: 2;">')
                rows.append(f'<div style="font-weight: bold; font-size: 14px;">{semester_label}</div>')
                rows.append(f'<div style="font-size: 12px; color: #666; margin-top: 4px;">{subject_count} subjects • {total_units} units</div>')
                rows.append(f'</div>')
                rows.append(f'<div style="flex: 1; text-align: right;">')
                rows.append(f'<div style="font-size: 20px; font-weight: bold; color: {merit_color};">{gwa:.2f}</div>')
                rows.append(f'<div style="font-size: 11px; color: {merit_color};">{emoji} {merit_level.replace("_", " ")}</div>')
                rows.append(f'</div>')
                rows.append(f'<div style="flex: 0.5; text-align: right;">')
                rows.append(f'<span style="background: {completion_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{completion_text}</span>')
                rows.append(f'</div>')
                rows.append(f'</div>')
                rows.append('</div>')
            
            rows.append('</div>')
            return format_html(''.join(rows))
        
        except Exception as e:
            logger.error(f"Error generating semester grouping summary: {str(e)}")
            return format_html(f'<span style="color: #999;">Error loading summary: {str(e)}</span>')
    
    semester_grouping_summary.short_description = 'Semester Groups'
    
    actions = ['approve_all_by_student', 'approve_selected', 'reject_selected', 'recalculate_gpa',
               'run_detection_validation', 'auto_approve_with_services', 'bulk_approve_semester_groups']
    
    def approve_all_by_student(self, request, queryset):
        """Approve ALL grades for the students in the selection"""
        from myapp.services import gwa_calculation_service
        from decimal import Decimal
        from myapp.models import GradeSubmission
        
        # Get unique student/academic_year/semester combinations
        students_periods = set()
        for grade in queryset:
            students_periods.add((grade.student_id, grade.academic_year, grade.semester))
        
        total_approved = 0
        messages = []
        
        for student_id, academic_year, semester in students_periods:
            # Get ALL grades for this student/period (not just selected ones)
            student_grades = GradeSubmission.objects.filter(
                student_id=student_id,
                academic_year=academic_year,
                semester=semester
            )
            
            # Approve all grades
            count = student_grades.update(status='approved', reviewed_by=request.user)
            total_approved += count
            
            # Calculate GPA using centralized service
            student = student_grades.first().student
            gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(student, academic_year, semester)
            
            if gwa_result:
                gpa = gwa_result.get('gwa', 0)
                merit = gwa_result.get('merit_level', 'N/A')
                
                # Determine merit emoji
                gpa_decimal = Decimal(str(gpa))
                if gpa_decimal <= Decimal('1.50'):
                    emoji = '🥇'
                elif gpa_decimal <= Decimal('2.00'):
                    emoji = '🥈'
                elif gpa_decimal <= Decimal('2.50'):
                    emoji = '🥉'
                else:
                    emoji = '📋'
                
                msg = f"{emoji} {student.username} ({academic_year} {semester}): {count} grades approved | GWA: {gpa:.2f} - {merit}"
                messages.append(msg)
        
        self.message_user(request, f'✅ Approved {total_approved} grade submission(s) for {len(students_periods)} student(s).')
        for msg in messages:
            self.message_user(request, msg)
    approve_all_by_student.short_description = '✅ Approve ALL grades for selected students'
    
    def approve_selected(self, request, queryset):
        """Approve selected grade submissions"""
        count = queryset.update(status='approved', reviewed_by=request.user)
        
        # Calculate GWA for affected semesters
        from myapp.services import gwa_calculation_service
        semester_groups = set()
        for grade in queryset:
            semester_groups.add((grade.student, grade.academic_year, grade.semester))
        
        for student, academic_year, semester in semester_groups:
            try:
                gwa_calculation_service.trigger_automated_gwa_calculation(student, academic_year, semester)
            except Exception as e:
                pass  # Don't fail approval if GWA calc fails
        
        self.message_user(request, f'✓ Approved {count} grade submission(s).')
    approve_selected.short_description = '✓ Approve selected grades'
    
    def reject_selected(self, request, queryset):
        """Reject selected grade submissions"""
        count = queryset.update(status='rejected', reviewed_by=request.user)
        self.message_user(request, f'✗ Rejected {count} grade submission(s).')
    reject_selected.short_description = '✗ Reject selected grades'
    
    def recalculate_gpa(self, request, queryset):
        """Recalculate GPA for selected students"""
        from myapp.services import gwa_calculation_service
        students_processed = set()
        
        for grade in queryset:
            key = (grade.student.id, grade.academic_year, grade.semester)
            if key not in students_processed:
                gwa_calculation_service.trigger_automated_gwa_calculation(grade.student, grade.academic_year, grade.semester)
                students_processed.add(key)
        
        self.message_user(request, f'📊 Recalculated GPA for {len(students_processed)} student(s).')
    recalculate_gpa.short_description = '📊 Recalculate GPA and merit'
    
    def run_detection_validation(self, request, queryset):
        """Run AI detection and validation services on selected grade submissions"""
        from myapp.grades_detection_service import get_grades_detection_service
        from myapp.grade_validation_service import get_grade_validation_service
        from myapp.services import gwa_calculation_service
        
        detection_service = get_grades_detection_service()
        validation_service = get_grade_validation_service()
        
        processed_count = 0
        success_count = 0
        messages = []
        
        # Group by student/semester for batch processing
        student_semesters = {}
        for grade in queryset:
            key = (grade.student_id, grade.academic_year, grade.semester)
            if key not in student_semesters:
                student_semesters[key] = []
            student_semesters[key].append(grade)
        
        for (student_id, academic_year, semester), grades in student_semesters.items():
            student = grades[0].student
            
            try:
                # Step 1: Run detection service on all grade sheets
                detected_grades = []
                for grade in grades:
                    if grade.grade_sheet:
                        try:
                            detection_result = detection_service.detect_grades_from_image(grade.grade_sheet.path)
                            if detection_result.get('success'):
                                detected_grades.extend(detection_result.get('detected_grades', []))
                        except Exception as e:
                            messages.append(f"⚠️ Detection failed for {grade.subject_code}: {str(e)}")
                
                # Step 2: Get COE subjects for validation
                from myapp.models import DocumentSubmission
                coe_doc = DocumentSubmission.objects.filter(
                    student=student,
                    document_type='certificate_of_enrollment',
                    status='approved'
                ).order_by('-submitted_at').first()
                
                if coe_doc and coe_doc.extracted_subjects:
                    # Step 3: Run validation
                    validation_result = validation_service.validate_grade_submissions(
                        coe_doc.extracted_subjects,
                        detected_grades
                    )
                    
                    if validation_result.get('is_valid'):
                        # Step 4: If validation passes, trigger automated GWA calculation
                        gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(
                            student, academic_year, semester
                        )
                        
                        if gwa_result:
                            success_count += 1
                            messages.append(f"✅ {student.username}: Detection → Validation → GWA {gwa_result['gwa']:.2f} calculated")
                        else:
                            messages.append(f"⚠️ {student.username}: Validation passed but GWA calculation failed")
                    else:
                        error_count = len(validation_result.get('errors', []))
                        messages.append(f"❌ {student.username}: Validation failed ({error_count} errors)")
                else:
                    messages.append(f"⚠️ {student.username}: No approved COE document found")
                
                processed_count += 1
                
            except Exception as e:
                messages.append(f"❌ Error processing {student.username}: {str(e)}")
        
        self.message_user(request, f'🤖 Processed {processed_count} student(s), {success_count} successful detections/validations.')
        for msg in messages:
            self.message_user(request, msg)
    run_detection_validation.short_description = '🤖 Run AI Detection & Validation'
    
    def auto_approve_with_services(self, request, queryset):
        """Auto-approve grades using integrated detection and validation services"""
        from myapp.grades_detection_service import get_grades_detection_service
        from myapp.grade_validation_service import get_grade_validation_service
        from myapp.services import gwa_calculation_service
        
        detection_service = get_grades_detection_service()
        validation_service = get_grade_validation_service()
        
        approved_count = 0
        messages = []
        
        # Group by student/semester for batch processing
        student_semesters = {}
        for grade in queryset:
            key = (grade.student_id, grade.academic_year, grade.semester)
            if key not in student_semesters:
                student_semesters[key] = []
            student_semesters[key].append(grade)
        
        for (student_id, academic_year, semester), grades in student_semesters.items():
            student = grades[0].student
            
            try:
                # Step 1: Run detection service
                detected_grades = []
                for grade in grades:
                    if grade.grade_sheet:
                        detection_result = detection_service.detect_grades_from_image(grade.grade_sheet.path)
                        if detection_result.get('success'):
                            detected_grades.extend(detection_result.get('detected_grades', []))
                
                # Step 2: Get COE and validate
                from myapp.models import DocumentSubmission
                coe_doc = DocumentSubmission.objects.filter(
                    student=student,
                    document_type='certificate_of_enrollment',
                    status='approved'
                ).order_by('-submitted_at').first()
                
                if coe_doc and coe_doc.extracted_subjects:
                    validation_result = validation_service.validate_grade_submissions(
                        coe_doc.extracted_subjects,
                        detected_grades
                    )
                    
                    if validation_result.get('is_valid'):
                        # Step 3: Auto-approve all grades for this semester
                        count = GradeSubmission.objects.filter(
                            student=student,
                            academic_year=academic_year,
                            semester=semester
                        ).update(status='approved', reviewed_by=request.user)
                        
                        # Step 4: Trigger GWA calculation
                        gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(
                            student, academic_year, semester
                        )
                        
                        if gwa_result:
                            gwa = gwa_result['gwa']
                            allowance = "₱5,000" if gwa < 2.00 else "₱10,000"
                            messages.append(f"✅ {student.username}: {count} grades auto-approved | GWA {gwa:.2f} | {allowance}")
                            approved_count += count
                        else:
                            messages.append(f"⚠️ {student.username}: Grades approved but GWA calculation failed")
                    else:
                        messages.append(f"❌ {student.username}: Validation failed - cannot auto-approve")
                else:
                    messages.append(f"⚠️ {student.username}: No COE document - cannot validate")
                    
            except Exception as e:
                messages.append(f"❌ Error auto-approving {student.username}: {str(e)}")
        
        self.message_user(request, f'✅ Auto-approved {approved_count} grade submission(s) using integrated AI services.')
        for msg in messages:
            self.message_user(request, msg)
    auto_approve_with_services.short_description = '🚀 Auto-Approve with AI Services'
    
    def bulk_approve_semester_groups(self, request, queryset):
        """
        Bulk approve entire semester groups for selected grades.
        Automatically groups by (student, academic_year, semester) and approves all grades in each group.
        Then calculates GWA and merit level for each group.
        """
        from myapp.services import gwa_calculation_service
        
        # Get unique semester groups from selected grades
        semester_groups = {}
        for grade in queryset:
            key = (grade.student_id, grade.academic_year, grade.semester)
            if key not in semester_groups:
                semester_groups[key] = grade.student
        
        total_approved = 0
        messages_list = []
        
        for (student_id, academic_year, semester), student in semester_groups.items():
            try:
                # Get all grades in this semester group
                semester_grades = GradeSubmission.objects.filter(
                    student_id=student_id,
                    academic_year=academic_year,
                    semester=semester
                )
                
                subject_count = semester_grades.count()
                
                # Approve all grades in this semester group
                count = semester_grades.update(
                    status='approved',
                    reviewed_by=request.user
                )
                
                total_approved += count
                
                # Trigger automated GWA calculation
                gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(
                    student, academic_year, semester
                )
                
                if gwa_result:
                    gwa = gwa_result['gwa']
                    merit_level = gwa_result['merit_level']
                    total_units = gwa_result['total_units']
                    
                    # Determine emoji and allowance amount
                    if gwa <= 1.50:
                        emoji = '🥇'
                    elif gwa <= 2.00:
                        emoji = '🥈'
                    elif gwa <= 2.50:
                        emoji = '🥉'
                    else:
                        emoji = '📋'
                    
                    allowance_amount = "₱5,000" if gwa < 2.00 else "₱10,000"
                    
                    msg = f"{emoji} {student.username} ({academic_year} {semester}): {subject_count} subjects ({total_units} units) approved | GWA: {gwa:.2f} ({merit_level.replace('_', ' ')}) | {allowance_amount}"
                    messages_list.append(msg)
                else:
                    msg = f"⚠️ {student.username} ({academic_year} {semester}): {subject_count} subjects approved, but GWA calculation failed"
                    messages_list.append(msg)
            
            except Exception as e:
                msg = f"❌ Error processing {student.username}: {str(e)}"
                messages_list.append(msg)
        
        # Send main message
        self.message_user(
            request,
            f'✅ Bulk approved {total_approved} grades in {len(semester_groups)} semester group(s). Semester data grouped and GWA calculated.'
        )
        
        # Send individual semester group messages
        for msg in messages_list:
            self.message_user(request, msg)
    
    bulk_approve_semester_groups.short_description = '📅 Bulk Approve Semester Groups (with GWA)'

@admin.register(AllowanceApplication)
class AllowanceApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'application_type', 'amount', 'status', 'applied_at', 'processed_by']
    list_filter = ['application_type', 'status', 'applied_at']
    search_fields = ['student__username', 'student__student_id']
    readonly_fields = ['applied_at', 'processed_at', 'amount']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('student', 'grade_submission', 'application_type', 'amount')
        }),
        ('Processing', {
            'fields': ('status', 'admin_notes', 'processed_by', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('applied_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['student', 'grade_submission', 'application_type']
        return self.readonly_fields


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'severity', 'target_model', 'timestamp']
    list_filter = ['action_type', 'severity', 'timestamp']
    search_fields = ['user__username', 'action_description', 'target_model']
    readonly_fields = ['user', 'action_type', 'action_description', 'severity', 'target_model', 
                      'target_object_id', 'target_user', 'metadata', 'ip_address', 'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        return False  # Audit logs should only be created programmatically
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can delete audit logs


@admin.register(SystemAnalytics)
class SystemAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_users', 'total_students', 'total_documents', 
                   'total_grades', 'total_applications', 'total_amount_disbursed']
    list_filter = ['date']
    readonly_fields = ['date', 'total_users', 'total_students', 'total_admins', 'new_users_today',
                      'total_documents', 'documents_pending', 'documents_approved', 'documents_rejected',
                      'total_grades', 'grades_pending', 'grades_approved', 'grades_rejected',
                      'total_applications', 'applications_pending', 'applications_approved',
                      'applications_rejected', 'applications_disbursed', 'total_amount_disbursed',
                      'ai_analyses_completed', 'ai_auto_approvals', 'avg_ai_confidence_score',
                      'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False  # Analytics should only be created programmatically
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(BasicQualification)
class BasicQualificationAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'get_student_id', 'applicant_type', 'is_qualified', 'completed_at', 'updated_at']
    list_filter = ['applicant_type', 'is_qualified', 'is_enrolled', 'is_resident', 
                   'is_eighteen_or_older', 'is_registered_voter', 'completed_at']
    search_fields = ['student__username', 'student__student_id', 'student__email', 'student__first_name', 'student__last_name']
    readonly_fields = ['completed_at', 'updated_at', 'is_qualified']
    
    def get_student_name(self, obj):
        """Display the student's full name"""
        return obj.student.get_full_name() if obj.student else 'N/A'
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'student__last_name'
    
    def get_student_id(self, obj):
        """Display the student ID"""
        return obj.student.student_id if obj.student and obj.student.student_id else 'N/A'
    get_student_id.short_description = 'Student ID'
    get_student_id.admin_order_field = 'student__student_id'
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Qualification Criteria', {
            'fields': (
                'is_enrolled',
                'is_resident',
                'is_eighteen_or_older',
                'is_registered_voter',
                'parent_is_voter',
                'has_good_moral_character',
                'is_committed'
            )
        }),
        ('Application Details', {
            'fields': ('applicant_type',)
        }),
        ('Status', {
            'fields': ('is_qualified', 'completed_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # Only allow creation through the student interface
        return False


@admin.register(FullApplication)
class FullApplicationAdmin(admin.ModelAdmin):
    list_display = ['get_student_name', 'get_student_id', 'school_year', 'semester', 'application_type', 
                    'is_submitted', 'is_locked', 'submitted_at', 'created_at']
    list_filter = ['semester', 'application_type', 'is_submitted', 'is_locked', 
                   'school_year', 'submitted_at', 'created_at']
    search_fields = ['user__username', 'user__student_id', 'user__first_name', 
                     'user__last_name', 'first_name', 'last_name', 'email', 'barangay']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at']
    
    def get_student_name(self, obj):
        """Display the full name from the form or user profile"""
        if obj.first_name and obj.last_name:
            name_parts = [obj.first_name]
            if obj.middle_name:
                name_parts.append(obj.middle_name)
            name_parts.append(obj.last_name)
            return ' '.join(name_parts)
        return obj.user.get_full_name() if obj.user else 'N/A'
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'last_name'
    
    def get_student_id(self, obj):
        """Display the student ID"""
        return obj.user.student_id if obj.user and obj.user.student_id else 'N/A'
    get_student_id.short_description = 'Student ID'
    get_student_id.admin_order_field = 'user__student_id'
    
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'first_name', 'middle_name', 'last_name')
        }),
        ('Academic Information', {
            'fields': ('school_year', 'semester', 'application_type', 'course_name', 'year_level')
        }),
        ('Contact Information', {
            'fields': ('email', 'mobile_no', 'other_contact')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'age', 'sex', 'barangay', 'house_no', 'street', 'zip_code')
        }),
        ('Status', {
            'fields': ('is_submitted', 'is_locked', 'submitted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_locked:
            # If locked, make most fields readonly
            return self.readonly_fields + ['user', 'first_name', 'last_name', 'school_year', 'semester', 
                                          'application_type', 'email', 'mobile_no',
                                          'date_of_birth', 'barangay']
        return self.readonly_fields
    
    actions = ['lock_applications', 'unlock_applications']
    
    def lock_applications(self, request, queryset):
        updated = queryset.update(is_locked=True)
        self.message_user(request, f'Successfully locked {updated} application(s).')
    lock_applications.short_description = 'Lock selected applications'
    
    def unlock_applications(self, request, queryset):
        updated = queryset.update(is_locked=False)
        self.message_user(request, f'Successfully unlocked {updated} application(s).')
    unlock_applications.short_description = 'Unlock selected applications'


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ['email', 'code', 'is_used', 'attempts', 'created_at', 'expires_at', 'is_code_valid']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['email', 'code']
    readonly_fields = ['created_at', 'expires_at']
    
    def is_code_valid(self, obj):
        """Display if the code is still valid"""
        return obj.is_valid()
    is_code_valid.short_description = 'Valid'
    is_code_valid.boolean = True
    
    def has_add_permission(self, request):
        # Verification codes should only be created programmatically
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete verification codes
        return request.user.is_superuser
