"""
🛤️ AI Training URLs
Endpoints for admin AI training and learning system management
"""

from django.urls import path
from . import training_views

urlpatterns = [
    # AI Training endpoints
    path('ai/train-feedback/', training_views.train_ai_feedback, name='train_ai_feedback'),
    path('ai/learning-stats/', training_views.ai_learning_stats, name='ai_learning_stats'),
    path('ai/retrain/', training_views.retrain_ai_model, name='retrain_ai_model'),
    path('ai/pending-reviews/', training_views.pending_ai_reviews, name='pending_ai_reviews'),
]