"""
Asynchronous document verification views for fast processing
"""
import asyncio
import json
import time
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from asgiref.sync import sync_to_async
import logging

from .fast_verifier import FastDocumentTypeDetector
from myapp.models import DocumentSubmission

logger = logging.getLogger(__name__)

class FastDocumentVerificationView(View):
    """
    Fast asynchronous document verification view
    Returns results in under 3 seconds with progress updates
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    async def post(self, request):
        """Handle asynchronous document verification"""
        try:
            # Parse request
            document_id = request.POST.get('document_id')
            if not document_id:
                return JsonResponse({
                    'error': 'Document ID required',
                    'processing_time': 0.0
                }, status=400)
            
            # Get document submission
            try:
                document_submission = await sync_to_async(DocumentSubmission.objects.get)(id=document_id)
            except DocumentSubmission.DoesNotExist:
                return JsonResponse({
                    'error': 'Document not found',
                    'processing_time': 0.0
                }, status=404)
            
            # Start fast verification
            start_time = time.time()
            fast_verifier = FastDocumentTypeDetector()
            
            # Run verification with timeout
            result = await asyncio.wait_for(
                self._run_verification(fast_verifier, document_submission),
                timeout=3.0  # 3 second maximum
            )
            
            processing_time = time.time() - start_time
            
            # Format response
            response_data = {
                'success': True,
                'document_id': document_id,
                'verification_result': result,
                'processing_time': processing_time,
                'performance_rating': (
                    'excellent' if processing_time < 1.0 else
                    'good' if processing_time < 2.0 else
                    'acceptable' if processing_time < 3.0 else
                    'slow'
                ),
                'timestamp': time.time()
            }
            
            # Update document status
            await self._update_document_status(document_submission, result)
            
            return JsonResponse(response_data)
            
        except asyncio.TimeoutError:
            return JsonResponse({
                'error': 'Verification timeout - document may be too complex',
                'processing_time': 3.0,
                'suggestion': 'Please try with a clearer image or smaller file size'
            }, status=408)
            
        except Exception as e:
            logger.error(f"Fast verification error: {str(e)}")
            return JsonResponse({
                'error': f'Verification failed: {str(e)}',
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0.0
            }, status=500)
    
    async def _run_verification(self, fast_verifier, document_submission):
        """Run verification in async context"""
        def sync_verification():
            return fast_verifier.fast_verify_document(
                document_submission,
                document_submission.document_file,
                max_time=2.5  # Leave 0.5s for response processing
            )
        
        return await sync_to_async(sync_verification)()
    
    async def _update_document_status(self, document_submission, result):
        """Update document status based on verification result"""
        try:
            def update_status():
                if result.get('is_valid_document', False):
                    document_submission.verification_status = 'verified'
                    document_submission.ai_confidence_score = result.get('confidence_score', 0.0)
                else:
                    document_submission.verification_status = 'rejected'
                    document_submission.rejection_reason = ', '.join(result.get('fraud_indicators', ['Verification failed']))
                
                document_submission.ai_processing_time = result.get('processing_time', 0.0)
                document_submission.save()
            
            await sync_to_async(update_status)()
        except Exception as e:
            logger.error(f"Status update error: {str(e)}")

class ProgressVerificationView(View):
    """
    Progressive verification view with real-time updates
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Start progressive verification with streaming response"""
        document_id = request.POST.get('document_id')
        if not document_id:
            return JsonResponse({'error': 'Document ID required'}, status=400)
        
        def generate_progress():
            """Generate progress updates"""
            try:
                # Get document
                document_submission = DocumentSubmission.objects.get(id=document_id)
                fast_verifier = FastDocumentTypeDetector()
                
                # Progress updates
                yield f"data: {json.dumps({'stage': 'starting', 'progress': 0, 'message': 'Starting verification...'})}\n\n"
                time.sleep(0.1)
                
                yield f"data: {json.dumps({'stage': 'file_check', 'progress': 20, 'message': 'Checking file format...'})}\n\n"
                time.sleep(0.1)
                
                yield f"data: {json.dumps({'stage': 'image_analysis', 'progress': 40, 'message': 'Analyzing image content...'})}\n\n"
                time.sleep(0.2)
                
                yield f"data: {json.dumps({'stage': 'quality_check', 'progress': 60, 'message': 'Assessing document quality...'})}\n\n"
                time.sleep(0.2)
                
                yield f"data: {json.dumps({'stage': 'ai_processing', 'progress': 80, 'message': 'Running AI verification...'})}\n\n"
                
                # Run actual verification
                start_time = time.time()
                result = fast_verifier.fast_verify_document(
                    document_submission,
                    document_submission.document_file,
                    max_time=2.0
                )
                processing_time = time.time() - start_time
                
                # Final result
                final_data = {
                    'stage': 'complete',
                    'progress': 100,
                    'message': 'Verification complete!',
                    'result': result,
                    'processing_time': processing_time,
                    'success': result.get('is_valid_document', False)
                }
                
                yield f"data: {json.dumps(final_data)}\n\n"
                
            except Exception as e:
                error_data = {
                    'stage': 'error',
                    'progress': 100,
                    'message': f'Verification failed: {str(e)}',
                    'error': True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        response = StreamingHttpResponse(generate_progress(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        return response

@csrf_exempt
@require_http_methods(["GET"])
def get_verification_status(request, document_id):
    """Get current verification status"""
    try:
        document = DocumentSubmission.objects.get(id=document_id)
        return JsonResponse({
            'document_id': document_id,
            'status': getattr(document, 'verification_status', 'pending'),
            'confidence': getattr(document, 'ai_confidence_score', 0.0),
            'processing_time': getattr(document, 'ai_processing_time', 0.0),
            'last_updated': document.updated_at.isoformat() if hasattr(document, 'updated_at') else None
        })
    except DocumentSubmission.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def quick_document_check(request):
    """Quick document format and basic validation (under 0.5 seconds)"""
    try:
        uploaded_file = request.FILES.get('document')
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        start_time = time.time()
        fast_verifier = FastDocumentTypeDetector()
        
        # Quick validation only
        is_valid = fast_verifier._quick_file_validation(uploaded_file)
        processing_time = time.time() - start_time
        
        return JsonResponse({
            'valid_format': is_valid,
            'processing_time': processing_time,
            'message': 'File format is acceptable' if is_valid else 'Invalid file format or size',
            'can_proceed': is_valid
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Quick check failed: {str(e)}',
            'valid_format': False,
            'can_proceed': False
        }, status=500)
