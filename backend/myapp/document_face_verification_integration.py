"""
Example integration of face verification into document upload flow
with automatic fraud detection and reporting
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from .models import DocumentSubmission
from .face_comparison_service import FaceComparisonService
from .fraud_detection_service import FraudDetectionService
import json
import logging

logger = logging.getLogger(__name__)
face_service = FaceComparisonService()
fraud_service = FraudDetectionService()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_document_with_face_verification(request):
    """
    Enhanced document submission with automatic face verification for IDs.
    
    Expected POST data:
    - document_type: String
    - description: String (optional)
    - file: File (document)
    - selfie: File (optional, for face verification)
    - liveness_data: JSON string (optional, liveness verification data)
    
    Flow:
    1. Upload document
    2. If document has face → extract face and embedding
    3. If selfie provided → verify face match
    4. Save document with verification results
    """
    try:
        # Get form data
        document_type = request.POST.get('document_type')
        description = request.POST.get('description', '')
        document_file = request.FILES.get('file')
        selfie_file = request.FILES.get('selfie')
        liveness_data_str = request.POST.get('liveness_data')
        
        # Validate required fields
        if not document_type or not document_file:
            return Response(
                {'error': 'Document type and file are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse liveness data
        liveness_data = None
        if liveness_data_str:
            try:
                liveness_data = json.loads(liveness_data_str)
            except json.JSONDecodeError:
                logger.warning("Invalid liveness data JSON")
        
        # Create document submission
        document = DocumentSubmission.objects.create(
            student=request.user,
            document_type=document_type,
            description=description,
            document_file=document_file,
            status='ai_processing'
        )
        
        # Check if document type requires face verification
        face_required_types = [
            'school_id', 
            'birth_certificate', 
            'voters_id',
            'drivers_license',
            'passport',
            'valid_id'
        ]
        
        if document_type in face_required_types:
            logger.info(f"Face verification required for document type: {document_type}")
            
            # Save uploaded files to S3 - NO LOCAL STORAGE
            from myapp.storage_backends import get_storage_backend
            from django.core.files.base import ContentFile
            
            s3_storage = get_storage_backend('private')
            document_path = s3_storage.save(
                f'temp/doc_{request.user.id}.jpg',
                ContentFile(document_file.read())
            )
            
            try:
                # For S3, we need to use the URL, not a local path
                document_full_path = s3_storage.url(document_path) if hasattr(s3_storage, 'url') else document_path
                
                # Step 1: Detect face in document
                face, bbox = face_service._detect_face_yolo(document_full_path)
                
                if face is not None:
                    document.face_detected_in_document = True
                    logger.info(f"Face detected in document at bbox: {bbox}")
                    
                    # Step 2: Extract embedding from document face
                    id_embedding = face_service._extract_face_embedding(face)
                    
                    if id_embedding is not None:
                        # Store embedding (convert to list for JSON)
                        document.face_embedding = {
                            'vector': id_embedding.tolist(),
                            'bbox': bbox
                        }
                        logger.info("Face embedding extracted from document")
                        
                        # Step 3: If selfie provided, verify face match
                        if selfie_file:
                            selfie_path = s3_storage.save(
                                f'temp/selfie_{request.user.id}.jpg',
                                ContentFile(selfie_file.read())
                            )
                            
                            try:
                                # For S3, use URL instead of local path
                                selfie_full_path = s3_storage.url(selfie_path) if hasattr(s3_storage, 'url') else selfie_path
                                
                                # Perform complete verification
                                verification_result = face_service.verify_id_with_selfie(
                                    document_full_path,
                                    selfie_full_path,
                                    liveness_data
                                )
                                
                                # Update document with verification results
                                document.face_verification_completed = True
                                document.selfie_captured = True
                                document.face_match_score = verification_result.get('similarity_score', 0.0)
                                document.face_match_confidence = verification_result.get('confidence', 'low')
                                document.liveness_verification_completed = liveness_data is not None
                                document.liveness_verification_passed = verification_result.get('liveness_passed', False)
                                
                                if liveness_data:
                                    document.liveness_data = liveness_data
                                
                                # Auto-approve if verification passed
                                if verification_result.get('match') and verification_result.get('liveness_passed'):
                                    document.status = 'approved'
                                    document.ai_auto_approved = True
                                    document.ai_analysis_notes = f"Face verification passed with {verification_result.get('confidence')} confidence (score: {verification_result.get('similarity_score'):.2f})"
                                else:
                                    # FRAUD DETECTION: Verification failed
                                    document.status = 'rejected'
                                    document.ai_analysis_notes = f"Face verification failed - Potential fraud detected"
                                    
                                    # Create fraud report
                                    try:
                                        fraud_report = fraud_service.report_fraud_attempt(
                                            user=request.user,
                                            verification_data=verification_result,
                                            document=document,
                                            application_type='document_verification',
                                            application_id=None
                                        )
                                        logger.warning(
                                            f"FRAUD DETECTED: User {request.user.email} failed face verification. "
                                            f"Fraud report {fraud_report.report_id} created."
                                        )
                                    except Exception as fraud_error:
                                        logger.error(f"Error creating fraud report: {fraud_error}")
                                
                                logger.info(
                                    f"Face verification completed: "
                                    f"Match={verification_result.get('match')}, "
                                    f"Score={verification_result.get('similarity_score'):.2f}, "
                                    f"Liveness={verification_result.get('liveness_passed')}"
                                )
                                
                            finally:
                                default_storage.delete(selfie_path)
                        else:
                            # No selfie provided - mark as pending for manual selfie
                            document.status = 'pending'
                            document.ai_analysis_notes = "Face detected in document. Awaiting live selfie for verification."
                    else:
                        document.ai_analysis_notes = "Face detected but embedding extraction failed"
                        document.status = 'pending'
                else:
                    # No face detected in document
                    document.face_detected_in_document = False
                    document.ai_analysis_notes = "No face detected in document (may not be required for this document type)"
                    document.status = 'pending'
                
            finally:
                # Clean up temporary document file
                default_storage.delete(document_path)
        else:
            # Document type doesn't require face verification
            document.status = 'pending'
            logger.info(f"Face verification not required for document type: {document_type}")
        
        # Save document with all updates
        document.ai_analysis_completed = True
        document.save()
        
        # Prepare response
        response_data = {
            'success': True,
            'document_id': document.id,
            'status': document.status,
            'face_verification': {
                'required': document_type in face_required_types,
                'face_detected': document.face_detected_in_document,
                'verification_completed': document.face_verification_completed,
                'match_score': document.face_match_score if document.face_verification_completed else None,
                'confidence': document.face_match_confidence if document.face_verification_completed else None,
                'liveness_passed': document.liveness_verification_passed if document.liveness_verification_completed else None,
            },
            'message': 'Document submitted successfully'
        }
        
        if document.ai_auto_approved:
            response_data['message'] = '🎉 Document verified and auto-approved! Face verification passed with high confidence.'
        elif document.face_verification_completed and not document.ai_auto_approved:
            response_data['message'] = '⚠️ Face verification completed but did not pass. Manual review required.'
        elif document.face_detected_in_document and not document.face_verification_completed:
            response_data['message'] = '📸 Face detected in document. Please capture a live selfie for verification.'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Document submission error: {str(e)}")
        return Response(
            {
                'error': 'Document submission failed',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_selfie_for_document(request, document_id):
    """
    Submit a live selfie for an existing document that requires face verification.
    
    Expected POST data:
    - selfie: File
    - liveness_data: JSON string
    """
    try:
        # Get document
        try:
            document = DocumentSubmission.objects.get(
                id=document_id,
                student=request.user
            )
        except DocumentSubmission.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if document has face detected
        if not document.face_detected_in_document:
            return Response(
                {'error': 'No face detected in document. Face verification not required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get selfie and liveness data
        selfie_file = request.FILES.get('selfie')
        liveness_data_str = request.POST.get('liveness_data')
        
        if not selfie_file:
            return Response(
                {'error': 'Selfie is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse liveness data
        liveness_data = None
        if liveness_data_str:
            try:
                liveness_data = json.loads(liveness_data_str)
            except json.JSONDecodeError:
                return Response(
                    {'error': 'Invalid liveness data'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get document face embedding
        if not document.face_embedding or 'vector' not in document.face_embedding:
            return Response(
                {'error': 'Document face embedding not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save selfie to S3 and verify - NO LOCAL STORAGE
        from myapp.storage_backends import get_storage_backend
        from django.core.files.base import ContentFile
        import numpy as np
        
        s3_storage = get_storage_backend('private')
        selfie_path = s3_storage.save(
            f'temp/selfie_{request.user.id}_{document_id}.jpg',
            ContentFile(selfie_file.read())
        )
        
        try:
            # For S3, use URL instead of local path
            selfie_full_path = s3_storage.url(selfie_path) if hasattr(s3_storage, 'url') else selfie_path
            
            # Detect face in selfie
            selfie_face, selfie_bbox = face_service._detect_face_yolo(selfie_full_path)
            
            if selfie_face is None:
                return Response(
                    {'error': 'No face detected in selfie. Please try again with better lighting.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract embedding from selfie
            selfie_embedding = face_service._extract_face_embedding(selfie_face)
            
            if selfie_embedding is None:
                return Response(
                    {'error': 'Failed to extract face features from selfie'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get ID embedding from document
            id_embedding = np.array(document.face_embedding['vector'])
            
            # Verify liveness if data provided
            liveness_passed = True
            if liveness_data:
                liveness_passed = face_service._verify_liveness_data(liveness_data)
            
            # Compare embeddings
            similarity = face_service._calculate_cosine_similarity(id_embedding, selfie_embedding)
            confidence = face_service._calculate_confidence(similarity)
            is_match = similarity >= face_service.SIMILARITY_THRESHOLD
            
            # Update document
            document.face_verification_completed = True
            document.selfie_captured = True
            document.face_match_score = float(similarity)
            document.face_match_confidence = confidence
            document.liveness_verification_completed = liveness_data is not None
            document.liveness_verification_passed = liveness_passed
            
            if liveness_data:
                document.liveness_data = liveness_data
            
            # Update status based on verification
            if is_match and liveness_passed:
                document.status = 'approved'
                document.ai_auto_approved = True
                document.ai_analysis_notes = f"Face verification passed with {confidence} confidence (score: {similarity:.2f}). Liveness verified."
                message = '🎉 Face verification successful! Your document has been approved.'
            else:
                # FRAUD DETECTION: Verification failed after document submission
                document.status = 'rejected'
                
                if not is_match:
                    document.ai_analysis_notes = f"FRAUD ALERT: Face verification failed - similarity score {similarity:.2f} below threshold {face_service.SIMILARITY_THRESHOLD}"
                    message = '🚨 Face verification failed. Your account has been suspended for security review. If you are the real owner of this ID, please contact the admin immediately.'
                else:
                    document.ai_analysis_notes = "FRAUD ALERT: Liveness verification failed - possible use of static photo"
                    message = '🚨 Liveness verification failed. Your account has been suspended. If you are the real owner of this ID, please contact the admin.'
                
                # Create fraud report
                try:
                    verification_result = {
                        'match': is_match,
                        'similarity_score': float(similarity),
                        'confidence': confidence,
                        'liveness_passed': liveness_passed,
                        'liveness_data': liveness_data
                    }
                    
                    fraud_report = fraud_service.report_fraud_attempt(
                        user=request.user,
                        verification_data=verification_result,
                        document=document,
                        application_type='selfie_verification',
                        application_id=document_id
                    )
                    
                    logger.critical(
                        f"🚨 FRAUD DETECTED: User {request.user.email} (ID: {request.user.id}) "
                        f"failed face verification after document submission. "
                        f"Fraud Report: {fraud_report.report_id}. Account SUSPENDED."
                    )
                    
                    # Add fraud report ID to message
                    message += f" Reference ID: {fraud_report.report_id}"
                    
                except Exception as fraud_error:
                    logger.error(f"Error creating fraud report: {fraud_error}")
                    # Still reject the document even if fraud report fails
                    message = '🚨 Face verification failed. Account suspended pending review.'
            
            document.save()
            
            return Response({
                'success': True,
                'match': is_match,
                'similarity_score': float(similarity),
                'confidence': confidence,
                'liveness_passed': liveness_passed,
                'status': document.status,
                'message': message
            }, status=status.HTTP_200_OK)
            
        finally:
            default_storage.delete(selfie_path)
            
    except Exception as e:
        logger.error(f"Selfie submission error: {str(e)}")
        return Response(
            {
                'error': 'Selfie verification failed',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
