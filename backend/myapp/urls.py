from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, UserViewSet, DocumentSubmissionViewSet, GradeSubmissionViewSet, AllowanceApplicationViewSet,
    login_view, logout_view, register_view, verify_student_view, user_profile, check_admin, students_list,
    student_dashboard_data, admin_dashboard_data, profile_image, audit_logs_list, analytics_overview, ai_stats,
    # 🤖 AI System Views
    ai_document_analysis, ai_analysis_status, ai_dashboard_stats, ai_batch_process
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'users', UserViewSet)
router.register(r'documents', DocumentSubmissionViewSet, basename='documents')
router.register(r'grades', GradeSubmissionViewSet, basename='grades')
router.register(r'applications', AllowanceApplicationViewSet, basename='applications')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/students/', students_list, name='students-list'),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/register/', register_view, name='register'),
    path('api/auth/verify-student/', verify_student_view, name='verify-student'),
    path('api/auth/profile/', user_profile, name='profile'),
    path('api/auth/profile/image/', profile_image, name='profile-image'),
    path('api/auth/check-admin/', check_admin, name='check_admin'),
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
]

