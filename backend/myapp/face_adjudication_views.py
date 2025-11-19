"""
Face Verification Adjudication Views
Admin endpoints for reviewing and approving/rejecting face verifications
Implements human-in-the-loop verification workflow
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
import logging

from myapp.models import VerificationAdjudication, CustomUser, AuditLog
from myapp.serializers import VerificationAdjudicationSerializer

logger = logging.getLogger(__name__)


class VerificationAdjudicationSerializer(serializers.ModelSerializer):
    """Serializer for VerificationAdjudication model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_student_id = serializers.CharField(source='user.student_id', read_only=True)
    admin_reviewer_name = serializers.CharField(source='admin_reviewer.get_full_name', read_only=True, allow_null=True)
    application_type = serializers.CharField(source='application.application_type', read_only=True, allow_null=True)
    grade_submission_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = VerificationAdjudication
        fields = [
            'id', 'user', 'user_name', 'user_student_id',
            'application', 'application_type',
            'document_submission',
            'school_id_image_path', 'selfie_image_path',
            'verification_backend',
            'automated_liveness_score', 'automated_match_result',
            'automated_similarity_score', 'automated_confidence_level',
            'status', 'admin_decision',
            'admin_decision_score', 'admin_notes',
            'admin_reviewer', 'admin_reviewer_name',
            'admin_device_info', 'admin_ip_address',
            'created_at', 'reviewed_at',
            'grade_submission_info'
        ]
        read_only_fields = [
            'id', 'user', 'application', 'document_submission',
            'school_id_image_path', 'selfie_image_path',
            'verification_backend',
            'automated_liveness_score', 'automated_match_result',
            'automated_similarity_score', 'automated_confidence_level',
            'created_at'
        ]
    
    def get_grade_submission_info(self, obj):
        """Get information about the related grade submission"""
        if obj.application and obj.application.grade_submission:
            gs = obj.application.grade_submission
            return {
                'academic_year': gs.academic_year,
                'semester': gs.semester,
                'gwa': str(gs.general_weighted_average),
                'status': gs.status
            }
        return None


class VerificationAdjudicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing face verification adjudications
    Admins review pending verifications and make final approval/rejection decisions
    """
    serializer_class = VerificationAdjudicationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Get adjudications with filtering and ordering"""
        queryset = VerificationAdjudication.objects.select_related(
            'user', 'admin_reviewer', 'application', 'document_submission'
        ).order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter in ['pending_review', 'under_review', 'completed', 'error']:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by admin decision
        decision_filter = self.request.query_params.get('decision')
        if decision_filter in ['pending', 'approved', 'rejected', 'escalated']:
            queryset = queryset.filter(admin_decision=decision_filter)
        
        # Filter by confidence level (flag low-confidence for review)
        confidence_filter = self.request.query_params.get('confidence')
        if confidence_filter:
            queryset = queryset.filter(automated_confidence_level=confidence_filter)
        
        # Filter by user
        user_filter = self.request.query_params.get('user_id')
        if user_filter:
            queryset = queryset.filter(user_id=user_filter)
        
        # Filter by reviewer
        reviewer_filter = self.request.query_params.get('reviewer_id')
        if reviewer_filter:
            queryset = queryset.filter(admin_reviewer_id=reviewer_filter)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific adjudication with full details"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """List all adjudications with pagination and filtering"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def decide(self, request, pk=None):
        """
        Admin makes a decision on a verification (approve/reject/escalate)
        
        Request body:
        {
            'decision': 'approved|rejected|escalated',
            'decision_score': 0.95 (optional, for overriding automated score),
            'notes': 'Admin comments...'
        }
        """
        adjudication = self.get_object()
        
        # Validate admin decision
        decision = request.data.get('decision')
        if decision not in ['approved', 'rejected', 'escalated']:
            return Response(
                {'error': 'Invalid decision. Must be: approved, rejected, or escalated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        decision_score = request.data.get('decision_score')
        notes = request.data.get('notes', '')
        
        try:
            # Update adjudication with admin decision
            adjudication.admin_reviewer = request.user
            adjudication.admin_decision = decision
            adjudication.admin_decision_score = decision_score
            adjudication.admin_notes = notes
            adjudication.status = 'completed'
            adjudication.reviewed_at = timezone.now()
            
            # Capture admin context
            adjudication.admin_ip_address = self._get_client_ip(request)
            adjudication.admin_device_info = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            adjudication.save()
            
            # Log audit trail
            self._log_adjudication_action(request.user, adjudication, decision, notes)
            
            # If approved, update the related application status if needed
            if decision == 'approved' and adjudication.application:
                self._handle_approval(adjudication.application, request.user)
            
            # If rejected, notify user
            if decision == 'rejected':
                self._handle_rejection(adjudication, request.user)
            
            serializer = self.get_serializer(adjudication)
            return Response(
                {
                    'success': True,
                    'message': f'Face verification {decision} successfully',
                    'adjudication': serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error in adjudication decision: {str(e)}")
            return Response(
                {'error': f'Failed to process decision: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics for admin review queue"""
        try:
            queryset = self.get_queryset()
            
            stats = {
                'total_pending': queryset.filter(status='pending_review').count(),
                'total_under_review': queryset.filter(status='under_review').count(),
                'total_completed': queryset.filter(status='completed').count(),
                'total_errors': queryset.filter(status='error').count(),
                'total_approved': queryset.filter(admin_decision='approved').count(),
                'total_rejected': queryset.filter(admin_decision='rejected').count(),
                'total_escalated': queryset.filter(admin_decision='escalated').count(),
                'low_confidence_count': queryset.filter(
                    automated_confidence_level__in=['low', 'very_low']
                ).count(),
                'high_confidence_count': queryset.filter(
                    automated_confidence_level__in=['high', 'very_high']
                ).count(),
            }
            
            # Recent pending verifications (last 10)
            recent_pending = queryset.filter(
                status='pending_review'
            )[:10]
            recent_serializer = VerificationAdjudicationSerializer(recent_pending, many=True)
            
            # Low confidence verifications requiring attention
            low_confidence = queryset.filter(
                status='pending_review',
                automated_confidence_level__in=['low', 'very_low']
            )[:10]
            low_confidence_serializer = VerificationAdjudicationSerializer(low_confidence, many=True)
            
            return Response({
                'success': True,
                'stats': stats,
                'recent_pending': recent_serializer.data,
                'low_confidence': low_confidence_serializer.data
            })
        
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return Response(
                {'error': f'Failed to retrieve statistics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """
        Escalate a verification for investigation
        Can add escalation reason/notes
        """
        adjudication = self.get_object()
        escalation_reason = request.data.get('reason', 'No reason provided')
        
        try:
            adjudication.admin_decision = 'escalated'
            adjudication.admin_notes = f"Escalated: {escalation_reason}\n\nOriginal notes: {adjudication.admin_notes or 'None'}"
            adjudication.admin_reviewer = request.user
            adjudication.reviewed_at = timezone.now()
            adjudication.save()
            
            # Log escalation
            self._log_adjudication_action(
                request.user, 
                adjudication, 
                'escalated', 
                escalation_reason
            )
            
            serializer = self.get_serializer(adjudication)
            return Response({
                'success': True,
                'message': 'Verification escalated for investigation',
                'adjudication': serializer.data
            })
        
        except Exception as e:
            logger.error(f"Error escalating verification: {str(e)}")
            return Response(
                {'error': f'Failed to escalate: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _log_adjudication_action(admin_user, adjudication, decision, notes):
        """Log admin adjudication action to audit trail"""
        try:
            AuditLog.objects.create(
                user=admin_user,
                action_type='admin_action',
                action_description=f'Face Verification {decision.upper()}: {adjudication.user.username}',
                severity='critical' if decision == 'rejected' else 'info',
                target_model='VerificationAdjudication',
                target_object_id=adjudication.id,
                target_user=adjudication.user,
                metadata={
                    'decision': decision,
                    'similarity_score': float(adjudication.automated_similarity_score or 0),
                    'confidence_level': adjudication.automated_confidence_level,
                    'notes': notes[:500],  # Truncate long notes
                },
                ip_address=adjudication.admin_ip_address,
                user_agent=adjudication.admin_device_info
            )
        except Exception as e:
            logger.error(f"Failed to log adjudication action: {str(e)}")
    
    @staticmethod
    def _handle_approval(application, admin_user):
        """Handle logic when admin approves a verification"""
        try:
            # Update application with approval status if needed
            # This might trigger disbursement workflow, etc.
            logger.info(f"Processing approval for application {application.id}")
            
            # Log approval
            AuditLog.objects.create(
                user=admin_user,
                action_type='application_approved',
                action_description=f'Application approved after face verification: {application.student.username}',
                severity='success',
                target_model='AllowanceApplication',
                target_object_id=application.id,
                target_user=application.student
            )
        except Exception as e:
            logger.error(f"Error handling approval: {str(e)}")
    
    @staticmethod
    def _handle_rejection(adjudication, admin_user):
        """Handle logic when admin rejects a verification"""
        try:
            # Notify user of rejection
            logger.info(f"Processing rejection for user {adjudication.user.username}")
            
            # Log rejection
            AuditLog.objects.create(
                user=admin_user,
                action_type='admin_action',
                action_description=f'Face verification rejected: {adjudication.user.username}',
                severity='warning',
                target_model='VerificationAdjudication',
                target_object_id=adjudication.id,
                target_user=adjudication.user,
                metadata={'reason': adjudication.admin_notes}
            )
        except Exception as e:
            logger.error(f"Error handling rejection: {str(e)}")
