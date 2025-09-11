"""
Lightning-fast URL patterns for ultra-fast document verification
Optimized for impatient students
"""
from django.urls import path
from . import lightning_views

urlpatterns = [
    # Lightning-fast verification (< 0.5 seconds)
    path('lightning-verify/', lightning_views.LightningFastVerificationView.as_view(), name='lightning_verify'),
    
    # Instant file check (< 0.1 seconds)  
    path('instant-check/', lightning_views.instant_file_check, name='instant_file_check'),
    
    # Performance statistics
    path('performance-stats/', lightning_views.performance_stats, name='performance_stats'),
    
    # Batch verification for multiple documents
    path('batch-verify/', lightning_views.batch_verify, name='batch_verify'),
]
