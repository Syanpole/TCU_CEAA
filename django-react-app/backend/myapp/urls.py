from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
