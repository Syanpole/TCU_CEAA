"""
Enhanced URLs with fast verification endpoints
"""
from django.urls import path
from . import views, fast_views

urlpatterns = [
    # Original AI verification endpoints
    path('verify/', views.verify_document_ai, name='verify_document_ai'),
    
    # Fast verification endpoints (NEW - for impatient students!)
    path('fast-verify/', fast_views.FastDocumentVerificationView.as_view(), name='fast_verify_document'),
    path('progress-verify/', fast_views.ProgressVerificationView.as_view(), name='progress_verify_document'),
    path('quick-check/', fast_views.quick_document_check, name='quick_document_check'),
    path('status/<int:document_id>/', fast_views.get_verification_status, name='verification_status'),
    
    # Face verification endpoints
    path('verify-face/', views.verify_face, name='verify_face'),
    path('train-face/', views.train_face_model, name='train_face_model'),
]
