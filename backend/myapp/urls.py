from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, UserViewSet,
    login_view, logout_view, register_view, user_profile, check_admin, students_list
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/students/', students_list, name='students-list'),
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/register/', register_view, name='register'),
    path('api/auth/profile/', user_profile, name='profile'),
    path('api/auth/check-admin/', check_admin, name='check_admin'),
]
