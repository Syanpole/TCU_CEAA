from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db import models
from django.conf import settings
from .models import Task, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication, AuditLog, SystemAnalytics
from .serializers import (TaskSerializer, UserSerializer, LoginSerializer, RegisterSerializer,
                         DocumentSubmissionSerializer, DocumentSubmissionCreateSerializer,
                         GradeSubmissionSerializer, GradeSubmissionCreateSerializer,
                         AllowanceApplicationSerializer, AllowanceApplicationCreateSerializer)
from .email_utils import send_approval_email, send_verification_code_email
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Check if email is verified (only for students)
        if user.role == 'student' and not user.is_email_verified:
            return Response({
                'error': 'Please verify your email address before logging in. Check your email for the verification code.',
                'email_not_verified': True,
                'email': user.email
            }, status=status.HTTP_403_FORBIDDEN)
        
        token, created = Token.objects.get_or_create(user=user)
        
        # Log successful login
        AuditLog.log_action(
            action_type='user_login',
            description=f'User {user.username} logged in successfully',
            user=user,
            severity='info',
            request=request
        )
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user after email verification.
    Requires: verification_code to confirm email was verified.
    """
    from .models import EmailVerificationCode
    
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email', '').lower()
        verification_code = request.data.get('verification_code', '').strip()
        
        # Verification code is required
        if not verification_code:
            return Response({
                'error': 'Email verification code is required',
                'requires_verification': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the code one more time during registration
        # Check for a recently used valid code (within last 15 minutes)
        recent_verification = EmailVerificationCode.objects.filter(
            email=email,
            code=verification_code,
            is_used=True,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=15)
        ).first()
        
        if not recent_verification:
            return Response({
                'error': 'Invalid or expired verification code. Please verify your email again.',
                'requires_verification': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user with verified email
        user = serializer.save()
        user.is_email_verified = True
        user.save()
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data,
            'message': 'Registration successful! Your email has been verified.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Handle password change if provided
            if 'current_password' in request.data and 'new_password' in request.data:
                if not request.user.check_password(request.data['current_password']):
                    return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
                request.user.set_password(request.data['new_password'])
                request.user.save()
                # Update the serializer data to exclude password fields
                validated_data = {k: v for k, v in serializer.validated_data.items() 
                                if k not in ['current_password', 'new_password']}
                for key, value in validated_data.items():
                    setattr(request.user, key, value)
                request.user.save()
            else:
                serializer.save()
            
            return Response(UserSerializer(request.user, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_admin(request):
    return Response({
        'is_admin': request.user.is_admin(),
        'role': request.user.role
    })

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def profile_image(request):
    if request.method == 'POST':
        if 'profile_image' not in request.FILES:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['profile_image']
        
        # Validate file type
        if not image_file.content_type.startswith('image/'):
            return Response({'error': 'Invalid file type. Please upload an image.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (5MB limit)
        if image_file.size > 5 * 1024 * 1024:
            return Response({'error': 'File size too large. Maximum size is 5MB.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the image
        request.user.profile_image = image_file
        request.user.save()
        
        return Response({
            'message': 'Profile image updated successfully',
            'profile_image': request.build_absolute_uri(request.user.profile_image.url) if request.user.profile_image else None
        })
    
    elif request.method == 'DELETE':
        if request.user.profile_image:
            request.user.profile_image.delete()
            request.user.profile_image = None
            request.user.save()
            return Response({'message': 'Profile image removed successfully'})
        return Response({'message': 'No profile image to remove'})

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can see all users
        if self.request.user.is_admin():
            return CustomUser.objects.all()
        else:
            # Regular users can only see their own profile
            return CustomUser.objects.filter(id=self.request.user.id)

# API endpoint to get students (users with student role)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def students_list(request):
    if not request.user.is_admin():
        return Response({'error': 'Only admins can view students list'}, status=status.HTTP_403_FORBIDDEN)
    
    students = CustomUser.objects.filter(role='student')
    serializer = UserSerializer(students, many=True)
    return Response(serializer.data)

class DocumentSubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentSubmissionCreateSerializer
        return DocumentSubmissionSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return DocumentSubmission.objects.all()
        else:
            # Students can only see their own documents
            return DocumentSubmission.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, pk=None):
        """Admin review of document submission"""
        if not request.user.is_admin():
            return Response({'error': 'Only admins can review documents'}, status=status.HTTP_403_FORBIDDEN)
        
        document = self.get_object()
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', '')
        
        if new_status not in ['approved', 'rejected', 'revision_needed']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        document.status = new_status
        document.admin_notes = admin_notes
        document.reviewed_at = timezone.now()
        document.reviewed_by = request.user
        document.save()
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)

class GradeSubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GradeSubmissionCreateSerializer
        return GradeSubmissionSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return GradeSubmission.objects.all()
        else:
            # Students can only see their own grades
            return GradeSubmission.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, pk=None):
        """Admin review of grade submission"""
        if not request.user.is_admin():
            return Response({'error': 'Only admins can review grades'}, status=status.HTTP_403_FORBIDDEN)
        
        grade_submission = self.get_object()
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', '')
        
        if new_status not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        grade_submission.status = new_status
        grade_submission.admin_notes = admin_notes
        grade_submission.reviewed_at = timezone.now()
        grade_submission.reviewed_by = request.user
        grade_submission.save()
        
        serializer = self.get_serializer(grade_submission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def recalculate(self, request, pk=None):
        """Recalculate AI evaluation for grade submission"""
        if not request.user.is_admin():
            return Response({'error': 'Only admins can recalculate evaluations'}, status=status.HTTP_403_FORBIDDEN)
        
        grade_submission = self.get_object()
        grade_submission.calculate_allowance_eligibility()
        grade_submission.save()
        
        serializer = self.get_serializer(grade_submission)
        return Response(serializer.data)

class AllowanceApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AllowanceApplicationCreateSerializer
        return AllowanceApplicationSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return AllowanceApplication.objects.all()
        else:
            # Students can only see their own applications
            return AllowanceApplication.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def process(self, request, pk=None):
        """Admin processing of allowance application"""
        if not request.user.is_admin():
            return Response({'error': 'Only admins can process applications'}, status=status.HTTP_403_FORBIDDEN)
        
        application = self.get_object()
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', '')
        
        if new_status not in ['approved', 'rejected', 'disbursed']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = application.status
        application.status = new_status
        application.admin_notes = admin_notes
        application.processed_at = timezone.now()
        application.processed_by = request.user
        application.save()
        
        # Send approval email if status changed to approved
        email_sent = False
        email_error = None
        if new_status == 'approved' and old_status != 'approved':
            try:
                success, error = send_approval_email(application)
                email_sent = success
                if not success:
                    email_error = error
                    logger.warning(f"Failed to send approval email for application {application.id}: {error}")
            except Exception as e:
                email_error = str(e)
                logger.error(f"Exception while sending approval email for application {application.id}: {e}")
        
        serializer = self.get_serializer(application)
        response_data = serializer.data
        
        # Add email status to response
        if new_status == 'approved':
            response_data['email_sent'] = email_sent
            if email_error:
                response_data['email_error'] = email_error
        
        return Response(response_data)

# Dashboard endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_data(request):
    """Get dashboard data for students"""
    if not request.user.is_student():
        return Response({'error': 'Only students can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get recent document submissions
    documents = DocumentSubmission.objects.filter(student=request.user).order_by('-submitted_at')[:5]
    
    # Get recent grade submissions
    grades = GradeSubmission.objects.filter(student=request.user).order_by('-submitted_at')[:5]
    
    # Get recent allowance applications
    applications = AllowanceApplication.objects.filter(student=request.user).order_by('-applied_at')[:5]
    
    # Calculate stats
    total_documents = DocumentSubmission.objects.filter(student=request.user).count()
    approved_documents = DocumentSubmission.objects.filter(student=request.user, status='approved').count()
    total_applications = AllowanceApplication.objects.filter(student=request.user).count()
    approved_applications = AllowanceApplication.objects.filter(student=request.user, status='approved').count()
    
    return Response({
        'documents': DocumentSubmissionSerializer(documents, many=True).data,
        'grades': GradeSubmissionSerializer(grades, many=True).data,
        'applications': AllowanceApplicationSerializer(applications, many=True).data,
        'stats': {
            'total_documents': total_documents,
            'approved_documents': approved_documents,
            'total_applications': total_applications,
            'approved_applications': approved_applications,
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_data(request):
    """Get dashboard data for admins"""
    if not request.user.is_admin():
        return Response({'error': 'Only admins can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get pending reviews
    pending_documents = DocumentSubmission.objects.filter(status='pending').order_by('-submitted_at')[:10]
    pending_grades = GradeSubmission.objects.filter(status='pending').order_by('-submitted_at')[:10]
    pending_applications = AllowanceApplication.objects.filter(status='pending').order_by('-applied_at')[:10]
    
    # Calculate stats
    total_students = CustomUser.objects.filter(role='student').count()
    total_documents = DocumentSubmission.objects.count()
    total_grades = GradeSubmission.objects.count()
    total_applications = AllowanceApplication.objects.count()
    
    return Response({
        'pending_documents': DocumentSubmissionSerializer(pending_documents, many=True).data,
        'pending_grades': GradeSubmissionSerializer(pending_grades, many=True).data,
        'pending_applications': AllowanceApplicationSerializer(pending_applications, many=True).data,
        'stats': {
            'total_students': total_students,
            'total_documents': total_documents,
            'total_grades': total_grades,
            'total_applications': total_applications,
        }
    })

# Audit Logs and Analytics Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs_list(request):
    """Get audit logs for admins"""
    if not request.user.is_admin():
        return Response({'error': 'Only admins can access audit logs'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get query parameters
    limit = int(request.GET.get('limit', 50))
    action_type = request.GET.get('action_type', None)
    severity = request.GET.get('severity', None)
    user_id = request.GET.get('user_id', None)
    
    # Build query
    logs = AuditLog.objects.all()
    
    if action_type:
        logs = logs.filter(action_type=action_type)
    if severity:
        logs = logs.filter(severity=severity)
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Limit results
    logs = logs[:limit]
    
    # Serialize data manually
    logs_data = []
    for log in logs:
        logs_data.append({
            'id': log.id,
            'user': {
                'id': log.user.id if log.user else None,
                'username': log.user.username if log.user else 'System',
                'full_name': f"{log.user.first_name} {log.user.last_name}" if log.user else 'System'
            },
            'action_type': log.action_type,
            'action_type_display': log.get_action_type_display(),
            'action_description': log.action_description,
            'severity': log.severity,
            'severity_display': log.get_severity_display(),
            'target_model': log.target_model,
            'target_object_id': log.target_object_id,
            'target_user': {
                'id': log.target_user.id if log.target_user else None,
                'username': log.target_user.username if log.target_user else None,
                'full_name': f"{log.target_user.first_name} {log.target_user.last_name}" if log.target_user else None
            } if log.target_user else None,
            'metadata': log.metadata,
            'ip_address': log.ip_address,
            'timestamp': log.timestamp.isoformat()
        })
    
    return Response({
        'logs': logs_data,
        'count': len(logs_data)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """Get system analytics overview for admins"""
    if not request.user.is_admin():
        return Response({'error': 'Only admins can access analytics'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Count, Avg, Sum, Q
    from datetime import date, timedelta
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Generate today's snapshot
    try:
        today_analytics = SystemAnalytics.generate_today_snapshot()
    except Exception as e:
        today_analytics = None
    
    # Get recent analytics
    recent_analytics = SystemAnalytics.objects.filter(date__gte=week_ago).order_by('-date')[:7]
    
    # Calculate trends
    documents_trend = list(DocumentSubmission.objects.filter(
        submitted_at__date__gte=week_ago
    ).values('submitted_at__date').annotate(count=Count('id')).order_by('submitted_at__date'))
    
    grades_trend = list(GradeSubmission.objects.filter(
        submitted_at__date__gte=week_ago
    ).values('submitted_at__date').annotate(count=Count('id')).order_by('submitted_at__date'))
    
    applications_trend = list(AllowanceApplication.objects.filter(
        applied_at__date__gte=week_ago
    ).values('applied_at__date').annotate(count=Count('id')).order_by('applied_at__date'))
    
    # Status distribution
    document_status_dist = DocumentSubmission.objects.values('status').annotate(count=Count('id'))
    grade_status_dist = GradeSubmission.objects.values('status').annotate(count=Count('id'))
    application_status_dist = AllowanceApplication.objects.values('status').annotate(count=Count('id'))
    
    # Top performing students
    top_students = GradeSubmission.objects.filter(
        status='approved',
        qualifies_for_merit_incentive=True
    ).order_by('-semestral_weighted_average')[:10]
    
    top_students_data = []
    for grade in top_students:
        top_students_data.append({
            'student_name': f"{grade.student.first_name} {grade.student.last_name}",
            'student_id': grade.student.student_id,
            'gwa': float(grade.general_weighted_average),
            'swa': float(grade.semestral_weighted_average),
            'academic_year': grade.academic_year,
            'semester': grade.get_semester_display()
        })
    
    # Financial summary
    total_disbursed = AllowanceApplication.objects.filter(
        status='disbursed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_pending_amount = AllowanceApplication.objects.filter(
        status__in=['pending', 'approved']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return Response({
        'today_snapshot': {
            'total_users': today_analytics.total_users if today_analytics else 0,
            'total_students': today_analytics.total_students if today_analytics else 0,
            'total_documents': today_analytics.total_documents if today_analytics else 0,
            'total_grades': today_analytics.total_grades if today_analytics else 0,
            'total_applications': today_analytics.total_applications if today_analytics else 0,
            'documents_pending': today_analytics.documents_pending if today_analytics else 0,
            'grades_pending': today_analytics.grades_pending if today_analytics else 0,
            'applications_pending': today_analytics.applications_pending if today_analytics else 0,
        },
        'trends': {
            'documents': [{'date': str(item['submitted_at__date']), 'count': item['count']} for item in documents_trend],
            'grades': [{'date': str(item['submitted_at__date']), 'count': item['count']} for item in grades_trend],
            'applications': [{'date': str(item['applied_at__date']), 'count': item['count']} for item in applications_trend],
        },
        'status_distribution': {
            'documents': list(document_status_dist),
            'grades': list(grade_status_dist),
            'applications': list(application_status_dist),
        },
        'top_students': top_students_data,
        'financial_summary': {
            'total_disbursed': float(total_disbursed),
            'total_pending': float(total_pending_amount),
            'total_committed': float(total_disbursed + total_pending_amount)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_stats(request):
    """Get AI processing statistics for monitoring"""
    if not request.user.is_admin():
        return Response({'error': 'Only admins can access AI statistics'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Avg, Count, Q
    from datetime import timedelta
    from django.utils import timezone
    
    # Get documents processed by AI
    ai_processed_docs = DocumentSubmission.objects.filter(ai_analysis_completed=True)
    
    # Calculate statistics
    total_processed = ai_processed_docs.count()
    auto_approved = ai_processed_docs.filter(ai_auto_approved=True, status='approved').count()
    auto_rejected = ai_processed_docs.filter(
        ai_analysis_completed=True, 
        status='rejected',
        reviewed_at__isnull=False
    ).exclude(ai_auto_approved=True).count()
    manual_review = ai_processed_docs.filter(status='pending').count()
    
    # Average confidence score
    avg_confidence_result = ai_processed_docs.filter(
        ai_confidence_score__gt=0
    ).aggregate(avg=Avg('ai_confidence_score'))
    average_confidence = avg_confidence_result['avg'] or 0.0
    
    # Get recent AI activities (last 24 hours)
    recent_time = timezone.now() - timedelta(hours=24)
    recent_ai_logs = AuditLog.objects.filter(
        action_type__in=['ai_analysis', 'ai_auto_approve'],
        timestamp__gte=recent_time
    ).order_by('-timestamp')[:10]
    
    recent_activities = []
    for log in recent_ai_logs:
        activity = {
            'timestamp': log.timestamp.isoformat(),
            'action': log.action_description,
            'confidence': log.metadata.get('confidence_score', 0) if log.metadata else 0,
            'decision': log.metadata.get('decision', 'unknown') if log.metadata else 'unknown'
        }
        recent_activities.append(activity)
    
    return Response({
        'total_processed': total_processed,
        'auto_approved': auto_approved,
        'auto_rejected': auto_rejected,
        'manual_review': manual_review,
        'average_confidence': float(average_confidence),
        'recent_activities': recent_activities
    })


# Email Verification Endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
    """
    Send email verification code to user's email.
    This is called during registration before account creation.
    """
    from .models import EmailVerificationCode
    from .email_utils import send_verification_code_email
    
    email = request.data.get('email', '').lower().strip()
    
    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate email format
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return Response({
            'error': 'Invalid email format'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if email already registered
    if CustomUser.objects.filter(email=email).exists():
        return Response({
            'error': 'This email is already registered. Please login instead.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Rate limiting: Check if user has requested too many codes recently
    from datetime import timedelta
    recent_codes = EmailVerificationCode.objects.filter(
        email=email,
        created_at__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    # TEMPORARILY DISABLED FOR TESTING - Re-enable in production
    # if recent_codes >= 3:
    #     return Response({
    #         'error': 'Too many verification code requests. Please wait 5 minutes and try again.'
    #     }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        # Create verification code
        verification = EmailVerificationCode.create_verification_code(email)
        
        # Send email with verification code (SECURE: code never exposed to frontend)
        success, error = send_verification_code_email(email, verification.code)
        
        if not success:
            logger.error(f"Failed to send verification email to {email}: {error}")
            return Response({
                'error': 'Failed to send verification email. Please try again or contact support.',
                'technical_error': error if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Verification code sent successfully to {email}")
        
        # For security: DO NOT return the actual code to frontend
        return Response({
            'message': 'Verification code sent to your email! Please check your inbox.',
            'email': email,
            'expires_in_minutes': 10,
            'code_sent': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating verification code for {email}: {str(e)}")
        return Response({
            'error': 'Failed to generate verification code. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_code(request):
    """
    Verify the email verification code entered by user.
    Returns success if code is valid.
    """
    from .models import EmailVerificationCode
    
    email = request.data.get('email', '').lower().strip()
    code = request.data.get('code', '').strip()
    
    if not email or not code:
        return Response({
            'error': 'Email and verification code are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find the most recent unused code for this email
        verification = EmailVerificationCode.objects.filter(
            email=email,
            code=code,
            is_used=False
        ).order_by('-created_at').first()
        
        if not verification:
            # Check if code exists but was already used
            used_code = EmailVerificationCode.objects.filter(
                email=email,
                code=code,
                is_used=True
            ).exists()
            
            if used_code:
                return Response({
                    'error': 'This verification code has already been used. Please request a new code.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Increment failed attempts for all codes of this email
            EmailVerificationCode.objects.filter(
                email=email,
                is_used=False
            ).update(attempts=models.F('attempts') + 1)
            
            return Response({
                'error': 'Invalid verification code. Please check and try again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if code is expired
        if not verification.is_valid():
            return Response({
                'error': 'This verification code has expired. Please request a new code.',
                'expired': True
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark code as used
        verification.mark_as_used()
        
        logger.info(f"Email verified successfully for {email}")
        
        return Response({
            'message': 'Email verified successfully! You can now complete your registration.',
            'email': email,
            'verified': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error verifying code for {email}: {str(e)}")
        return Response({
            'error': 'Verification failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_code(request):
    """
    Resend verification code to user's email.
    """
    from .models import EmailVerificationCode
    from .email_utils import send_verification_code_email
    
    email = request.data.get('email', '').lower().strip()
    
    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Rate limiting
    from datetime import timedelta
    recent_codes = EmailVerificationCode.objects.filter(
        email=email,
        created_at__gte=timezone.now() - timedelta(minutes=2)
    ).count()
    
    # TEMPORARILY DISABLED FOR TESTING - Re-enable in production
    # if recent_codes >= 1:
    #     return Response({
    #         'error': 'Please wait at least 2 minutes before requesting a new code.'
    #     }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        # Create new verification code
        verification = EmailVerificationCode.create_verification_code(email)
        
        # Send email with verification code (SECURE: code never exposed to frontend)
        success, error = send_verification_code_email(email, verification.code)
        
        if not success:
            logger.error(f"Failed to resend verification email to {email}: {error}")
            return Response({
                'error': 'Failed to send verification email. Please try again or contact support.',
                'technical_error': error if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Verification code resent successfully to {email}")
        
        # For security: DO NOT return the actual code to frontend
        return Response({
            'message': 'New verification code sent to your email! Please check your inbox.',
            'email': email,
            'expires_in_minutes': 10,
            'code_sent': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error resending verification code for {email}: {str(e)}")
        return Response({
            'error': 'Failed to resend verification code. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

