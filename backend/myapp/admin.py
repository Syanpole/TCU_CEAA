from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Task, Student, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication, AuditLog, SystemAnalytics

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'student_id', 'is_staff', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'student_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'student_id')}),
    )

@admin.register(CustomUser)
class CustomUserAdminRegistered(CustomUserAdmin):
    pass

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

