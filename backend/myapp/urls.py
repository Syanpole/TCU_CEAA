from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TaskViewSet, UserViewSet, DocumentSubmissionViewSet, GradeSubmissionViewSet, AllowanceApplicationViewSet,
    BasicQualificationViewSet, FullApplicationViewSet,
    login_view, logout_view, register_view, verify_student_view, user_profile, check_admin, students_list,
    student_dashboard_data, admin_dashboard_data, profile_image, audit_logs_list, analytics_overview, ai_stats,
    send_verification_code, verify_email_code, resend_verification_code,
    request_password_reset, verify_reset_code, reset_password,
    ai_document_analysis, ai_analysis_status, ai_dashboard_stats, ai_batch_process, admin_document_dashboard,
    # New grade submission endpoints
    check_grade_submission_eligibility, get_coe_subjects, submit_subject_grade, validate_grade_submissions, get_grade_submission_status
)

# Face verification views
from .face_verification_views import (
    verify_face_with_id, extract_id_face, verify_liveness_only,
    verify_grade_submission_identity
)

# Fraud management views
from .fraud_management_views import (
    get_fraud_reports, get_fraud_report_detail, update_fraud_report,
    resolve_fraud_report, contact_real_owner, get_fraud_notifications,
    mark_notification_read
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'users', UserViewSet)
router.register(r'documents', DocumentSubmissionViewSet, basename='documents')
router.register(r'grades', GradeSubmissionViewSet, basename='grades')
router.register(r'applications', AllowanceApplicationViewSet, basename='applications')
router.register(r'basic-qualification', BasicQualificationViewSet, basename='basic-qualification')
router.register(r'full-application', FullApplicationViewSet, basename='full-application')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/students/', students_list, name='students-list'),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/register/', register_view, name='register'),
    path('api/auth/verify-student/', verify_student_view, name='verify-student'),
    path('api/auth/send-verification-code/', send_verification_code, name='send-verification-code'),
    path('api/auth/verify-email-code/', verify_email_code, name='verify-email-code'),
    path('api/auth/resend-verification-code/', resend_verification_code, name='resend-verification-code'),
    path('api/auth/profile/', user_profile, name='profile'),
    path('api/auth/profile/image/', profile_image, name='profile-image'),
    path('api/auth/check-admin/', check_admin, name='check_admin'),
    path('api/auth/request-password-reset/', request_password_reset, name='request-password-reset'),
    path('api/auth/verify-reset-code/', verify_reset_code, name='verify-reset-code'),
    path('api/auth/reset-password/', reset_password, name='reset-password'),
    path('api/dashboard/student/', student_dashboard_data, name='student-dashboard'),
    path('api/dashboard/admin/', admin_dashboard_data, name='admin-dashboard'),
    path('api/audit-logs/', audit_logs_list, name='audit-logs'),
    path('api/analytics/', analytics_overview, name='analytics'),
    path('api/ai-stats/', ai_stats, name='ai-stats'),
    # 🤖 Comprehensive AI System Endpoints
    path('api/ai/analyze-document/', ai_document_analysis, name='ai-document-analysis'),
    path('api/ai/status/<int:document_id>/', ai_analysis_status, name='ai-analysis-status'),
    path('api/ai/dashboard-stats/', ai_dashboard_stats, name='ai-dashboard-stats'),
    path('api/ai/batch-process/', ai_batch_process, name='ai-batch-process'),
    # 📊 Admin Document Management
    path('api/admin/documents/dashboard/', admin_document_dashboard, name='admin-document-dashboard'),
    
    # 🔒 Face Verification Endpoints
    path('api/face-verification/verify/', verify_face_with_id, name='verify-face-with-id'),
    path('api/face-verification/extract-face/', extract_id_face, name='extract-id-face'),
    path('api/face-verification/liveness/', verify_liveness_only, name='verify-liveness-only'),
    path('api/face-verification/grade-submission/', verify_grade_submission_identity, name='verify-grade-submission-identity'),
    
    # 📚 New Grade Submission Workflow Endpoints (Per-Subject)
    path('api/grade-workflow/check-eligibility/', check_grade_submission_eligibility, name='check-grade-submission-eligibility'),
    path('api/grade-workflow/coe-subjects/', get_coe_subjects, name='get-coe-subjects'),
    path('api/grade-workflow/submit-subject/', submit_subject_grade, name='submit-subject-grade'),
    path('api/grade-workflow/validate/', validate_grade_submissions, name='validate-grade-submissions'),
    path('api/grade-workflow/status/', get_grade_submission_status, name='get-grade-submission-status'),
    
    # 🚨 Fraud Management Endpoints
    path('api/fraud-reports/', get_fraud_reports, name='fraud-reports-list'),
    path('api/fraud-reports/<int:report_id>/', get_fraud_report_detail, name='fraud-report-detail'),
    path('api/fraud-reports/<int:report_id>/update/', update_fraud_report, name='fraud-report-update'),
    path('api/fraud-reports/<int:report_id>/resolve/', resolve_fraud_report, name='fraud-report-resolve'),
    path('api/fraud-reports/<int:report_id>/contact-real-owner/', contact_real_owner, name='fraud-contact-owner'),
    path('api/fraud-notifications/', get_fraud_notifications, name='fraud-notifications'),
    path('api/fraud-notifications/<int:notification_id>/mark-read/', mark_notification_read, name='fraud-notification-read'),
]

