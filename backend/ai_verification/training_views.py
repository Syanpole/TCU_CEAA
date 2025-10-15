"""
🎯 ADMIN TRAINING INTERFACE
Allows admins to train the AI system by providing feedback on document verification results
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_ai_feedback(request):
    """
    📚 Train AI with admin feedback
    
    Endpoint: POST /api/ai/train-feedback/
    
    Payload:
    {
        "document_id": 123,
        "admin_decision": "approved|rejected",
        "admin_notes": "Optional feedback",
        "correct_document_type": "birth_certificate" (if type was wrong)
    }
    """
    try:
        from myapp.models import DocumentSubmission
        from ai_verification.learning_system import learning_system
        
        # Validate admin permission
        if not request.user.role == 'admin':
            return Response({
                'error': 'Only administrators can provide AI training feedback'
            }, status=403)
        
        data = request.data
        document_id = data.get('document_id')
        admin_decision = data.get('admin_decision')
        admin_notes = data.get('admin_notes', '')
        correct_type = data.get('correct_document_type')
        
        # Validate input
        if not document_id or admin_decision not in ['approved', 'rejected']:
            return Response({
                'error': 'Invalid input. Required: document_id, admin_decision (approved/rejected)'
            }, status=400)
        
        # Get document
        document = get_object_or_404(DocumentSubmission, id=document_id)
        
        # Get the original OCR results from the document's AI analysis
        ocr_results = {
            'extracted_text': getattr(document, 'ai_analysis_notes', ''),
            'confidence_score': getattr(document, 'ai_confidence_score', 0.0),
            'verification_method': 'dual_ocr',
            'similarity_score': 0.85 if admin_decision == 'approved' else 0.45,  # Estimated
            'confidence_level': 'high' if admin_decision == 'approved' else 'low'
        }
        
        # Record admin feedback for training
        learning_system.record_admin_decision(
            document_id=document_id,
            document_type=correct_type or document.document_type,
            ocr_results=ocr_results,
            admin_decision=admin_decision,
            admin_notes=admin_notes
        )
        
        # Update document status based on admin decision
        document.status = admin_decision
        document.admin_notes = admin_notes
        document.save()
        
        # Get updated learning progress
        progress = learning_system.analyze_learning_progress()
        
        logger.info(f"📚 AI trained with admin feedback: Doc {document_id} -> {admin_decision}")
        
        return Response({
            'success': True,
            'message': f'AI training updated with {admin_decision} decision',
            'learning_progress': {
                'overall_accuracy': progress['overall_accuracy'],
                'training_samples': progress['training_samples'],
                'document_type_accuracy': progress['document_types'].get(document.document_type, {})
            }
        })
        
    except Exception as e:
        logger.error(f"AI training feedback error: {str(e)}")
        return Response({
            'error': f'Failed to record training feedback: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_learning_stats(request):
    """
    📊 Get AI learning statistics
    
    Endpoint: GET /api/ai/learning-stats/
    """
    try:
        from ai_verification.learning_system import learning_system
        
        if not request.user.role == 'admin':
            return Response({
                'error': 'Only administrators can view AI learning statistics'
            }, status=403)
        
        # Get comprehensive learning progress
        progress = learning_system.analyze_learning_progress()
        
        # Generate training report
        training_report = learning_system.export_training_report()
        
        return Response({
            'learning_progress': progress,
            'training_report': training_report,
            'recommendations': progress.get('recommendations', []),
            'status': 'learning' if progress['training_samples'] < 100 else 'autonomous'
        })
        
    except Exception as e:
        logger.error(f"AI learning stats error: {str(e)}")
        return Response({
            'error': f'Failed to get learning statistics: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retrain_ai_model(request):
    """
    🔄 Retrain AI model with accumulated data
    
    Endpoint: POST /api/ai/retrain/
    """
    try:
        from ai_verification.learning_system import learning_system
        
        if not request.user.role == 'admin':
            return Response({
                'error': 'Only administrators can retrain AI models'
            }, status=403)
        
        # Get current progress
        progress = learning_system.analyze_learning_progress()
        
        if progress['training_samples'] < 20:
            return Response({
                'error': f'Insufficient training data. Need at least 20 samples, have {progress["training_samples"]}'
            }, status=400)
        
        # Force recalculation of all thresholds
        for doc_type in progress['document_types'].keys():
            learning_system._recalculate_thresholds(doc_type)
        
        # Save updated patterns
        learning_system._save_learning_patterns()
        
        logger.info(f"🔄 AI model retrained with {progress['training_samples']} samples")
        
        return Response({
            'success': True,
            'message': f'AI model retrained with {progress["training_samples"]} samples',
            'updated_accuracy': progress['overall_accuracy'],
            'document_types': progress['document_types']
        })
        
    except Exception as e:
        logger.error(f"AI retraining error: {str(e)}")
        return Response({
            'error': f'Failed to retrain AI model: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_ai_reviews(request):
    """
    📋 Get documents pending AI review (for training)
    
    Endpoint: GET /api/ai/pending-reviews/
    """
    try:
        from myapp.models import DocumentSubmission
        
        if not request.user.role == 'admin':
            return Response({
                'error': 'Only administrators can view pending AI reviews'
            }, status=403)
        
        # Get documents that need admin review
        pending_docs = DocumentSubmission.objects.filter(
            status='pending'
        ).select_related('student').order_by('-submitted_at')[:50]
        
        pending_list = []
        for doc in pending_docs:
            pending_list.append({
                'id': doc.id,
                'student_name': f"{doc.student.first_name} {doc.student.last_name}",
                'document_type': doc.get_document_type_display(),
                'submitted_at': doc.submitted_at,
                'ai_confidence': getattr(doc, 'ai_confidence_score', 0.0),
                'requires_training': True,
                'document_url': doc.document_file.url if doc.document_file else None
            })
        
        return Response({
            'pending_reviews': pending_list,
            'total_count': len(pending_list),
            'message': f'Found {len(pending_list)} documents needing AI training feedback'
        })
        
    except Exception as e:
        logger.error(f"Pending AI reviews error: {str(e)}")
        return Response({
            'error': f'Failed to get pending reviews: {str(e)}'
        }, status=500)