from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.db import transaction
from rest_framework.authtoken.models import Token
from .models import Task, Student, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication, AuditLog, SystemAnalytics, VerifiedStudent, EmailVerificationCode, BasicQualification, FullApplication


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
    list_display = ['student', 'academic_year', 'semester', 'general_weighted_average', 
                   'qualifies_for_basic_allowance', 'qualifies_for_merit_incentive', 'status', 'submitted_at']
    list_filter = ['semester', 'status', 'qualifies_for_basic_allowance', 'qualifies_for_merit_incentive', 'submitted_at']
    search_fields = ['student__username', 'student__student_id', 'academic_year']
    readonly_fields = ['submitted_at', 'reviewed_at', 'ai_evaluation_completed', 'ai_evaluation_notes']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'academic_year', 'semester')
        }),
        ('Grade Details', {
            'fields': ('total_units', 'general_weighted_average', 'semestral_weighted_average', 'grade_sheet')
        }),
        ('Grade Validation', {
            'fields': ('has_failing_grades', 'has_incomplete_grades', 'has_dropped_subjects')
        }),
        ('AI Evaluation', {
            'fields': ('ai_evaluation_completed', 'ai_evaluation_notes', 'qualifies_for_basic_allowance', 'qualifies_for_merit_incentive'),
            'classes': ('collapse',)
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['student', 'academic_year', 'semester']
        return self.readonly_fields
    
    actions = ['recalculate_eligibility']
    
    def recalculate_eligibility(self, request, queryset):
        for grade_submission in queryset:
            grade_submission.calculate_allowance_eligibility()
            grade_submission.save()
        self.message_user(request, f'Successfully recalculated eligibility for {queryset.count()} submissions.')
    recalculate_eligibility.short_description = 'Recalculate AI eligibility'

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
