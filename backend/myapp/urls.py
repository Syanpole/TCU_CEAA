from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, UserViewSet, DocumentSubmissionViewSet, GradeSubmissionViewSet, AllowanceApplicationViewSet,
    login_view, logout_view, register_view, user_profile, check_admin, students_list,
    student_dashboard_data, admin_dashboard_data, profile_image,
    student_ai_analysis, program_analytics, predict_eligibility, eligibility_summary
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
    path('api/auth/profile/', user_profile, name='profile'),
    path('api/auth/profile/image/', profile_image, name='profile-image'),
    path('api/auth/check-admin/', check_admin, name='check_admin'),
    path('api/dashboard/student/', student_dashboard_data, name='student-dashboard'),
    path('api/dashboard/admin/', admin_dashboard_data, name='admin-dashboard'),
    
    # AI Analytics endpoints (Ready for real sample data)
    path('api/ai/student-analysis/', student_ai_analysis, name='student-ai-analysis'),
    path('api/ai/student-analysis/<str:student_id>/', student_ai_analysis, name='student-ai-analysis-by-id'),
    path('api/ai/program-analytics/', program_analytics, name='program-analytics'),
    path('api/ai/predict-eligibility/', predict_eligibility, name='predict-eligibility'),
    path('api/ai/eligibility-summary/', eligibility_summary, name='eligibility-summary'),
]
