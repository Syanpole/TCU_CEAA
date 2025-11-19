"""
API Views for Fraud Detection and Management
Admin endpoints for reviewing and resolving fraud reports
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .fraud_detection_models import FraudReport, FraudNotification, UserAccountAction
from .fraud_detection_service import FraudDetectionService
import json

logger = logging.getLogger(__name__)
fraud_service = FraudDetectionService()


def is_admin(user):
    """Check if user is admin."""
    return user.role == 'admin'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fraud_reports(request):
    """
    Get fraud reports (admin only).
    
    Query Parameters:
    - status: Filter by status (pending, investigating, confirmed_fraud, resolved, dismissed)
    - severity: Filter by severity (low, medium, high, critical)
    - limit: Number of results (default 50)
    """
    if not is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Get query parameters
        status_filter = request.GET.get('status')
        severity_filter = request.GET.get('severity')
        limit = int(request.GET.get('limit', 50))
        
        # Build query
        query = Q()
        if status_filter:
            query &= Q(status=status_filter)
        if severity_filter:
            query &= Q(severity=severity_filter)
        
        # Get fraud reports
        fraud_reports = FraudReport.objects.filter(query).select_related(
            'suspected_user',
            'document_submission',
            'assigned_to'
        )[:limit]
        
        # Serialize data
        reports_data = []
        for report in fraud_reports:
            reports_data.append({
                'id': report.id,
                'report_id': report.report_id,
                'suspected_user': {
                    'id': report.suspected_user.id,
                    'name': report.suspected_user.get_full_name(),
                    'email': report.suspected_user.email,
                    'student_id': getattr(report.suspected_user, 'student_id', None),
                },
                'fraud_type': report.fraud_type,
                'fraud_type_display': report.get_fraud_type_display(),
                'status': report.status,
                'status_display': report.get_status_display(),
                'severity': report.severity,
                'severity_display': report.get_severity_display(),
                'face_match_score': report.face_match_score,
                'verification_attempts': report.verification_attempts,
                'liveness_verification': {
                    'color_flash': report.liveness_data.get('colorFlash', {}).get('passed', False),
                    'blink': report.liveness_data.get('blink', {}).get('passed', False),
                    'movement': report.liveness_data.get('movement', {}).get('passed', False),
                },
                'real_owner_contacted': report.real_owner_contacted,
                'real_owner_verified': report.real_owner_verified,
                'assigned_to': report.assigned_to.get_full_name() if report.assigned_to else None,
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat(),
                'resolved_at': report.resolved_at.isoformat() if report.resolved_at else None,
            })
        
        # Get statistics
        stats = {
            'total': FraudReport.objects.count(),
            'pending': FraudReport.objects.filter(status='pending').count(),
            'investigating': FraudReport.objects.filter(status='investigating').count(),
            'confirmed': FraudReport.objects.filter(status='confirmed_fraud').count(),
            'resolved': FraudReport.objects.filter(status='resolved').count(),
            'critical_severity': FraudReport.objects.filter(severity='critical').count(),
        }
        
        return Response({
            'reports': reports_data,
            'count': len(reports_data),
            'statistics': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching fraud reports: {str(e)}")
        return Response(
            {'error': 'Failed to fetch fraud reports', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fraud_report_detail(request, report_id):
    """
    Get detailed fraud report (admin only).
    """
    if not is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        report = get_object_or_404(FraudReport, id=report_id)
        
        # Get account actions
        account_actions = UserAccountAction.objects.filter(
            fraud_report=report
        ).select_related('performed_by')
        
        actions_data = [{
            'action_type': action.get_action_type_display(),
            'reason': action.reason,
            'performed_by': action.performed_by.get_full_name() if action.performed_by else 'System',
            'created_at': action.created_at.isoformat(),
        } for action in account_actions]
        
        # Detailed data
        detail = {
            'id': report.id,
            'report_id': report.report_id,
            'suspected_user': {
                'id': report.suspected_user.id,
                'name': report.suspected_user.get_full_name(),
                'email': report.suspected_user.email,
                'student_id': getattr(report.suspected_user, 'student_id', None),
                'date_joined': report.suspected_user.date_joined.isoformat(),
                'is_active': report.suspected_user.is_active,
            },
            'fraud_details': {
                'fraud_type': report.get_fraud_type_display(),
                'status': report.get_status_display(),
                'severity': report.get_severity_display(),
                'face_match_score': report.face_match_score,
                'verification_attempts': report.verification_attempts,
                'description': report.description,
            },
            'liveness_data': report.liveness_data,
            'evidence_data': report.evidence_data,
            'document_id': report.document_submission.id if report.document_submission else None,
            'application_id': report.application.id if report.application else None,
            'real_owner': {
                'contacted': report.real_owner_contacted,
                'verified': report.real_owner_verified,
                'notes': report.real_owner_notes,
                'suspected_identity': report.suspected_real_identity,
            },
            'admin_info': {
                'assigned_to': report.assigned_to.get_full_name() if report.assigned_to else None,
                'admin_notes': report.admin_notes,
            },
            'account_actions': actions_data,
            'timestamps': {
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat(),
                'resolved_at': report.resolved_at.isoformat() if report.resolved_at else None,
            }
        }
        
        return Response(detail, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching fraud report detail: {str(e)}")
        return Response(
            {'error': 'Failed to fetch fraud report detail', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fraud_report(request, report_id):
    """
    Update fraud report status or assign to admin.
    
    POST data:
    - assigned_to: Admin user ID (optional)
    - status: New status (optional)
    - admin_notes: Additional notes (optional)
    """
    if not is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        report = get_object_or_404(FraudReport, id=report_id)
        
        # Update fields
        if 'assigned_to' in request.data:
            assigned_to_id = request.data['assigned_to']
            if assigned_to_id:
                from .models import CustomUser
                assigned_to = CustomUser.objects.get(id=assigned_to_id, role='admin')
                report.assigned_to = assigned_to
        
        if 'status' in request.data:
            report.status = request.data['status']
        
        if 'admin_notes' in request.data:
            notes = request.data['admin_notes']
            report.admin_notes = f"{report.admin_notes or ''}\n\n[{request.user.get_full_name()}] {notes}"
        
        report.save()
        
        logger.info(f"Fraud report {report.report_id} updated by {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Fraud report updated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating fraud report: {str(e)}")
        return Response(
            {'error': 'Failed to update fraud report', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_fraud_report(request, report_id):
    """
    Resolve a fraud report.
    
    POST data:
    - resolution: 'confirmed' | 'dismissed' | 'real_owner_verified'
    - notes: Resolution notes
    """
    if not is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        report = get_object_or_404(FraudReport, id=report_id)
        
        resolution = request.data.get('resolution')
        notes = request.data.get('notes', '')
        
        if not resolution:
            return Response(
                {'error': 'Resolution type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if resolution not in ['confirmed', 'dismissed', 'real_owner_verified']:
            return Response(
                {'error': 'Invalid resolution type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Resolve the case
        fraud_service.resolve_fraud_case(report, resolution, request.user, notes)
        
        return Response({
            'success': True,
            'message': f'Fraud report resolved as: {resolution}',
            'report_id': report.report_id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error resolving fraud report: {str(e)}")
        return Response(
            {'error': 'Failed to resolve fraud report', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_real_owner(request, report_id):
    """
    Record that real owner has been contacted.
    
    POST data:
    - method: Contact method (email, phone, etc.)
    - details: Contact details
    - verified: Boolean (optional)
    """
    if not is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        report = get_object_or_404(FraudReport, id=report_id)
        
        contact_info = {
            'method': request.data.get('method', 'Unknown'),
            'details': request.data.get('details', ''),
            'verified': request.data.get('verified', False)
        }
        
        fraud_service.handle_real_owner_contact(report, contact_info, request.user)
        
        return Response({
            'success': True,
            'message': 'Real owner contact recorded'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error recording real owner contact: {str(e)}")
        return Response(
            {'error': 'Failed to record contact', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fraud_notifications(request):
    """
    Get fraud notifications for current admin.
    """
    if not is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        notifications = FraudNotification.objects.filter(
            admin=request.user
        ).select_related('fraud_report').order_by('-created_at')[:50]
        
        notifications_data = [{
            'id': notif.id,
            'notification_type': notif.get_notification_type_display(),
            'title': notif.title,
            'message': notif.message,
            'priority': notif.priority,
            'read': notif.read,
            'fraud_report_id': notif.fraud_report.id,
            'report_id': notif.fraud_report.report_id,
            'created_at': notif.created_at.isoformat(),
            'read_at': notif.read_at.isoformat() if notif.read_at else None,
        } for notif in notifications]
        
        unread_count = notifications.filter(read=False).count()
        
        return Response({
            'notifications': notifications_data,
            'unread_count': unread_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching fraud notifications: {str(e)}")
        return Response(
            {'error': 'Failed to fetch notifications', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a fraud notification as read.
    """
    if not is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        notification = get_object_or_404(
            FraudNotification,
            id=notification_id,
            admin=request.user
        )
        
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return Response(
            {'error': 'Failed to mark notification', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
