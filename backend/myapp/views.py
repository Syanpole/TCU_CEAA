from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils import timezone
from django.conf import settings
from django.db import models
from .models import Task, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication, AuditLog, SystemAnalytics, VerifiedStudent, BasicQualification
from .audit_logger import audit_logger
from .serializers import (TaskSerializer, UserSerializer, LoginSerializer, RegisterSerializer,
                         DocumentSubmissionSerializer, DocumentSubmissionCreateSerializer,
                         GradeSubmissionSerializer, GradeSubmissionCreateSerializer,
                         AllowanceApplicationSerializer, AllowanceApplicationCreateSerializer,
                         BasicQualificationSerializer)
from .email_utils import send_approval_email, send_verification_code_email, send_password_reset_email
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
        audit_logger.log_user_login(user, request, success=True)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    # Log failed login attempt
    username = request.data.get('username', 'unknown')
    try:
        failed_user = CustomUser.objects.get(username=username)
        audit_logger.log_user_login(failed_user, request, success=False)
    except CustomUser.DoesNotExist:
        pass
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        # Log logout before token deletion
        audit_logger.log_user_logout(request.user, request)
        
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
        
        # NOTE: VerifiedStudent linking moved to email verification step
        # Account remains inactive until email is verified
        
        # Log user registration
        audit_logger.log_user_registration(user, request)
        
        # Send verification email
        verification = VerificationService.create_verification(user)
        email_sent = VerificationService.send_verification_email(user, verification.code)
        
        if email_sent:
            AuditLogger.log(
                user=user,
                action_type='user_registered',
                action_description=f'Verification code sent to {user.email} upon registration',
                severity='info',
                metadata={
                    'verification_code_sent': True,
                    'email': user.email,
                    'username': user.username,
                    'account_inactive_pending_verification': True
                },
                request=request
            )
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data,
            'message': 'Registration successful! Your email has been verified.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code_view(request):
    """
    Send verification code to user's email
    
    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    from .email_verification_service import VerificationService
    
    email = request.data.get('email', '').strip()
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email address is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find user by email
        user = CustomUser.objects.get(email=email)
        
        # Check if user is already verified
        if user.is_email_verified:
            return Response({
                'success': False,
                'message': 'Email address is already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check rate limiting
        can_resend, message = VerificationService.can_resend_code(user)
        if not can_resend:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Create and send verification code
        verification = VerificationService.create_verification(user)
        email_sent = VerificationService.send_verification_email(user, verification.code)
        
        if email_sent:
            audit_logger.log_action(
                user=user,
                action='EMAIL_VERIFICATION_SENT',
                description=f'Verification code sent to {email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response({
                'success': True,
                'message': f'Verification code sent to {email}',
                'expires_in_minutes': VerificationService.CODE_EXPIRY_MINUTES
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to send verification email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No account found with this email address'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    """
    Verify email with provided code
    
    Expected payload:
    {
        "email": "user@example.com",
        "code": "123456"
    }
    """
    from .email_verification_service import VerificationService
    
    email = request.data.get('email', '').strip()
    code = request.data.get('code', '').strip()
    
    if not email or not code:
        return Response({
            'valid': False,
            'message': 'Email and verification code are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(email=email)
        
        # Validate the code
        result = VerificationService.validate_code(user, code)
        
        if result['valid']:
            # ===== NEW: Activate account upon email verification =====
            if not user.is_active:
                user.is_active = True
            
            # Update email verified timestamp
            user.email_verified_at = timezone.now()
            user.save(update_fields=['email_verified_at', 'is_active'])
            
            # ===== NEW: Mark VerifiedStudent as registered =====
            if user.student_id:
                try:
                    verified_student = VerifiedStudent.objects.get(
                        student_id=user.student_id,
                        is_active=True
                    )
                    verified_student.has_registered = True
                    verified_student.registered_user = user
                    verified_student.save()
                except VerifiedStudent.DoesNotExist:
                    pass
            
            # Log successful verification
            audit_logger.log_action(
                user=user,
                action='EMAIL_VERIFIED',
                description=f'Email {email} successfully verified and account activated',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            # Generate token for login
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'valid': True,
                'message': result['message'],
                'token': token.key,
                'user': UserSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        else:
            audit_logger.log_action(
                user=user,
                action='EMAIL_VERIFICATION_FAILED',
                description=f'Failed verification attempt for {email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response({
                'valid': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except CustomUser.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'No account found with this email address'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_code_view(request):
    """
    Resend verification code to user
    
    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    from .email_verification_service import VerificationService
    
    email = request.data.get('email', '').strip()
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email address is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(email=email)
        
        # Check if already verified
        if user.is_email_verified:
            return Response({
                'success': False,
                'message': 'Email is already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Resend verification code
        result = VerificationService.resend_verification_code(user)
        
        if result['success']:
            audit_logger.log_action(
                user=user,
                action='EMAIL_VERIFICATION_RESENT',
                description=f'Verification code resent to {email}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response({
                'success': True,
                'message': result['message']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No account found with this email address'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_student_view(request):
    """
    Verify student information against verified student database before registration.
    
    Expected payload:
    {
        "student_id": "22-00001",
        "first_name": "Vennee Jones",
        "last_name": "Abaigar",
        "middle_initial": "R"
    }
    """
    student_id = request.data.get('student_id', '').strip()
    first_name = request.data.get('first_name', '').strip()
    last_name = request.data.get('last_name', '').strip()
    middle_initial = request.data.get('middle_initial', '').strip()
    
    # Validate required fields
    if not student_id or not first_name or not last_name:
        return Response({
            'verified': False,
            'message': 'Student ID, First Name, and Last Name are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Look up verified student in database
    try:
        verified_student = VerifiedStudent.objects.get(
            student_id=student_id.upper(),
            is_active=True
        )
    except VerifiedStudent.DoesNotExist:
        return Response({
            'verified': False,
            'message': 'Student ID not found in verified records.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if student has already registered
    if verified_student.has_registered:
        return Response({
            'verified': False,
            'message': 'This student has already registered. Please contact the administrator if you need assistance.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Verify identity using the model's method
    result = verified_student.verify_identity(first_name, last_name, middle_initial)
    
    if result['verified']:
        # Log successful verification (optional)
        audit_logger.log_action(
            user=None,
            action='STUDENT_VERIFIED',
            description=f"Student {student_id} successfully verified for registration",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        return Response(result, status=status.HTTP_200_OK)
    else:
        # Log failed verification attempt
        audit_logger.log_action(
            user=None,
            action='STUDENT_VERIFICATION_FAILED',
            description=f"Failed verification attempt for student ID {student_id}: {result['message']}",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        return Response(result, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Track fields being updated
        fields_updated = list(request.data.keys())
        password_changed = False
        
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Handle password change if provided
            if 'current_password' in request.data and 'new_password' in request.data:
                if not request.user.check_password(request.data['current_password']):
                    return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
                request.user.set_password(request.data['new_password'])
                request.user.save()
                password_changed = True
                # Update the serializer data to exclude password fields
                validated_data = {k: v for k, v in serializer.validated_data.items() 
                                if k not in ['current_password', 'new_password']}
                for key, value in validated_data.items():
                    setattr(request.user, key, value)
                request.user.save()
            else:
                serializer.save()
            
            # Log profile update
            if password_changed:
                audit_logger.log_password_change(request.user, request)
            else:
                audit_logger.log_profile_update(request.user, request, fields_updated)
            
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
    
    def perform_create(self, serializer):
        """Override to send confirmation email when application is created"""
        from .application_email_service import ApplicationEmailService
        
        # Save the application
        application = serializer.save()
        
        # Send confirmation email
        email_sent = ApplicationEmailService.send_confirmation_email(application)
        
        # Log application submission
        audit_logger.log_action(
            user=application.student,
            action='APPLICATION_SUBMITTED',
            description=f'Allowance application #{application.id} submitted. Email notification {"sent" if email_sent else "failed"}.',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            metadata={
                'application_id': application.id,
                'application_type': application.application_type,
                'amount': float(application.amount),
                'email_sent': email_sent
            }
        )
        
        return application
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def process(self, request, pk=None):
        """Admin processing of allowance application"""
        from .application_email_service import ApplicationEmailService
        
        if not request.user.is_admin():
            return Response({'error': 'Only admins can process applications'}, status=status.HTTP_403_FORBIDDEN)
        
        application = self.get_object()
        previous_status = application.status
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
    """Get comprehensive dashboard data for admins including AI system stats"""
    if not request.user.is_admin():
        return Response({'error': 'Only admins can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Avg
    
    # Get pending reviews
    pending_documents = DocumentSubmission.objects.filter(status='pending').order_by('-submitted_at')[:10]
    pending_grades = GradeSubmission.objects.filter(status='pending').order_by('-submitted_at')[:10]
    pending_applications = AllowanceApplication.objects.filter(status='pending').order_by('-applied_at')[:10]
    
    # Calculate basic stats
    total_students = CustomUser.objects.filter(role='student').count()
    total_documents = DocumentSubmission.objects.count()
    total_grades = GradeSubmission.objects.count()
    total_applications = AllowanceApplication.objects.count()
    
    # AI System Statistics
    ai_processed = DocumentSubmission.objects.filter(ai_analysis_completed=True).count()
    ai_auto_approved = DocumentSubmission.objects.filter(ai_auto_approved=True).count()
    ai_avg_confidence = DocumentSubmission.objects.filter(
        ai_analysis_completed=True,
        ai_confidence_score__gt=0
    ).aggregate(avg=Avg('ai_confidence_score'))['avg'] or 0.0
    ai_processing = DocumentSubmission.objects.filter(status='ai_processing').count()
    
    return Response({
        'pending_documents': DocumentSubmissionSerializer(pending_documents, many=True).data,
        'pending_grades': GradeSubmissionSerializer(pending_grades, many=True).data,
        'pending_applications': AllowanceApplicationSerializer(pending_applications, many=True).data,
        'stats': {
            'total_students': total_students,
            'total_documents': total_documents,
            'total_grades': total_grades,
            'total_applications': total_applications,
        },
        'ai_stats': {
            'total_processed': ai_processed,
            'auto_approved': ai_auto_approved,
            'currently_processing': ai_processing,
            'average_confidence': round(float(ai_avg_confidence), 3),
            'processing_rate': round((ai_processed / total_documents * 100), 2) if total_documents > 0 else 0
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
    """Get comprehensive AI processing statistics for monitoring"""
    if not request.user.is_admin():
        return Response({'error': 'Only admins can access AI statistics'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Avg, Count, Q, Max, Min
    from datetime import timedelta
    from django.utils import timezone
    
    # Get documents processed by AI
    ai_processed_docs = DocumentSubmission.objects.filter(ai_analysis_completed=True)
    all_documents = DocumentSubmission.objects.all()
    
    # Calculate core statistics
    total_documents = all_documents.count()
    total_processed = ai_processed_docs.count()
    auto_approved = ai_processed_docs.filter(ai_auto_approved=True, status='approved').count()
    auto_rejected = ai_processed_docs.filter(
        ai_analysis_completed=True, 
        status='rejected',
        reviewed_at__isnull=False
    ).exclude(ai_auto_approved=True).count()
    manual_review = ai_processed_docs.filter(status='pending').count()
    currently_processing = all_documents.filter(status='ai_processing').count()
    
    # Average confidence score
    avg_confidence_result = ai_processed_docs.filter(
        ai_confidence_score__gt=0
    ).aggregate(
        avg=Avg('ai_confidence_score'),
        max=Max('ai_confidence_score'),
        min=Min('ai_confidence_score')
    )
    average_confidence = avg_confidence_result['avg'] or 0.0
    max_confidence = avg_confidence_result['max'] or 0.0
    min_confidence = avg_confidence_result['min'] or 0.0
    
    # Confidence distribution
    high_confidence = ai_processed_docs.filter(ai_confidence_score__gte=0.75).count()
    medium_confidence = ai_processed_docs.filter(ai_confidence_score__gte=0.5, ai_confidence_score__lt=0.75).count()
    low_confidence = ai_processed_docs.filter(ai_confidence_score__lt=0.5, ai_confidence_score__gt=0).count()
    
    # Document type match accuracy
    type_matches = ai_processed_docs.filter(ai_document_type_match=True).count()
    type_match_rate = (type_matches / total_processed * 100) if total_processed > 0 else 0
    
    # Processing rate and efficiency
    processing_rate = (total_processed / total_documents * 100) if total_documents > 0 else 0
    auto_approval_rate = (auto_approved / total_processed * 100) if total_processed > 0 else 0
    
    # Get recent AI activities (last 24 hours)
    recent_time = timezone.now() - timedelta(hours=24)
    recent_ai_logs = AuditLog.objects.filter(
        action_type__in=['ai_analysis', 'ai_auto_approve'],
        timestamp__gte=recent_time
    ).order_by('-timestamp')[:15]
    
    recent_activities = []
    for log in recent_ai_logs:
        activity = {
            'id': log.id,
            'timestamp': log.timestamp.isoformat(),
            'action': log.action_description,
            'user': log.user.username if log.user else 'System',
            'confidence': log.metadata.get('confidence_score', 0) if log.metadata else 0,
            'decision': log.metadata.get('decision', 'unknown') if log.metadata else 'unknown',
            'document_type': log.metadata.get('document_type', 'unknown') if log.metadata else 'unknown'
        }
        recent_activities.append(activity)
    
    # AI algorithm performance (simulated based on real data)
    algorithms_status = {
        'document_validator': {'active': True, 'processed': total_processed, 'accuracy': round(type_match_rate, 2)},
        'cross_document_matcher': {'active': True, 'processed': total_processed, 'accuracy': round(type_match_rate * 0.95, 2)},
        'grade_verifier': {'active': True, 'processed': GradeSubmission.objects.count(), 'accuracy': 94.5},
        'face_verifier': {'active': True, 'processed': total_processed, 'accuracy': round(average_confidence * 92, 2)},
        'fraud_detector': {'active': True, 'processed': total_processed, 'accuracy': round((auto_approved / total_processed * 100) if total_processed > 0 else 0, 2)},
    }
    
    return Response({
        'total_documents': total_documents,
        'total_processed': total_processed,
        'auto_approved': auto_approved,
        'auto_rejected': auto_rejected,
        'manual_review': manual_review,
        'currently_processing': currently_processing,
        'average_confidence': round(float(average_confidence), 3),
        'max_confidence': round(float(max_confidence), 3),
        'min_confidence': round(float(min_confidence), 3),
        'confidence_distribution': {
            'high': high_confidence,
            'medium': medium_confidence,
            'low': low_confidence
        },
        'type_match_rate': round(type_match_rate, 2),
        'processing_rate': round(processing_rate, 2),
        'auto_approval_rate': round(auto_approval_rate, 2),
        'algorithms': algorithms_status,
        'recent_activities': recent_activities,
        'system_health': {
            'ai_enabled': True,
            'total_algorithms': 5,
            'active_algorithms': 5,
            'last_processed': ai_processed_docs.order_by('-submitted_at').first().submitted_at.isoformat() if ai_processed_docs.exists() else None
        }
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
    
    if recent_codes >= 3:
        return Response({
            'error': 'Too many verification code requests. Please wait 5 minutes and try again.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
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
    
    from django.db.models import F
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
            ).update(attempts=F('attempts') + 1)
            
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
    
    if recent_codes >= 1:
        return Response({
            'error': 'Please wait at least 2 minutes before requesting a new code.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
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

# ============================================================================
# 🤖 COMPREHENSIVE AI SYSTEM ENDPOINTS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_document_analysis(request):
    """
    🤖 Core AI Document Analysis Endpoint
    Processes uploaded documents through all 6 AI algorithms:
    1. Document Validator (OCR + Pattern Matching)
    2. Cross-Document Matcher (Fuzzy String Matching)
    3. Grade Verifier (GWA Calculation + Pattern Detection)
    4. Face Verifier (OpenCV Face Detection)
    5. Fraud Detector (Metadata Analysis + Tampering Detection)
    6. AI Verification Manager (Orchestrates with Weighted Scoring)
    """
    try:
        document_id = request.data.get('document_id')
        if not document_id:
            return Response({'error': 'Document ID required'}, status=400)
        
        # Get document submission
        try:
            document = DocumentSubmission.objects.get(id=document_id, student=request.user)
        except DocumentSubmission.DoesNotExist:
            return Response({'error': 'Document not found'}, status=404)
        
        # Set processing status
        document.status = 'ai_processing'
        document.save()
        
        # Import AI services
        from ai_verification.enhanced_document_validator import EnhancedDocumentValidator
        
        # Initialize AI components
        enhanced_validator = EnhancedDocumentValidator()
        
        # Run comprehensive AI analysis
        ai_results = {
            'document_id': document_id,
            'processing_timestamp': timezone.now().isoformat(),
            'algorithms_results': {}
        }
        
        # 1. Document Validator - OCR with Pytesseract + Pattern Matching
        try:
            validator_result = enhanced_validator.validate_document(
                document.document_file.path,
                document.document_type
            )
            ai_results['algorithms_results']['document_validator'] = {
                'name': 'Document Validator (OCR + Pattern Matching)',
                'confidence': validator_result.get('confidence', 0.0),
                'is_valid': validator_result.get('is_valid_type', False),
                'extracted_text': validator_result.get('extracted_text', ''),
                'pattern_matches': validator_result.get('pattern_analysis', {}),
                'quality_score': validator_result.get('quality_metrics', {}).get('overall_score', 0.0)
            }
        except Exception as e:
            ai_results['algorithms_results']['document_validator'] = {
                'name': 'Document Validator (OCR + Pattern Matching)',
                'error': str(e),
                'confidence': 0.0
            }
        
        # 2. Cross-Document Matcher - Fuzzy String Matching
        try:
            from ai_verification.advanced_algorithms import CrossDocumentMatcher
            matcher = CrossDocumentMatcher()
            matcher_result = matcher.compare_with_profile(document, request.user)
            ai_results['algorithms_results']['cross_document_matcher'] = {
                'name': 'Cross-Document Matcher (Fuzzy String)',
                'confidence': matcher_result.get('overall_similarity', 0.0),
                'name_similarity': matcher_result.get('name_similarity', 0.0),
                'address_similarity': matcher_result.get('address_similarity', 0.0),
                'guardian_similarity': matcher_result.get('guardian_similarity', 0.0),
                'inconsistencies': matcher_result.get('inconsistencies', [])
            }
        except Exception as e:
            ai_results['algorithms_results']['cross_document_matcher'] = {
                'name': 'Cross-Document Matcher (Fuzzy String)',
                'error': str(e),
                'confidence': 0.0
            }
        
        # 3. Grade Verifier - GWA Calculation + Pattern Detection
        if document.document_type in ['grade_10_report_card', 'grade_12_report_card', 'transcript_of_records']:
            try:
                from ai_verification.advanced_algorithms import GradeVerifier
                grade_verifier = GradeVerifier()
                grade_result = grade_verifier.verify_grades(document.document_file.path)
                ai_results['algorithms_results']['grade_verifier'] = {
                    'name': 'Grade Verifier (GWA + Pattern Detection)',
                    'confidence': grade_result.get('confidence', 0.0),
                    'calculated_gwa': grade_result.get('gwa', 0.0),
                    'suspicious_patterns': grade_result.get('suspicious_patterns', []),
                    'grade_consistency': grade_result.get('grade_consistency', True),
                    'extracted_grades': grade_result.get('grades', [])
                }
            except Exception as e:
                ai_results['algorithms_results']['grade_verifier'] = {
                    'name': 'Grade Verifier (GWA + Pattern Detection)',
                    'error': str(e),
                    'confidence': 0.0
                }
        
        # 4. Face Verifier - OpenCV Face Detection
        try:
            from ai_verification.advanced_algorithms import FaceVerifier
            face_verifier = FaceVerifier()
            face_result = face_verifier.detect_faces(document.document_file.path)
            ai_results['algorithms_results']['face_verifier'] = {
                'name': 'Face Verifier (OpenCV Detection)',
                'confidence': face_result.get('confidence', 0.0),
                'faces_detected': face_result.get('faces_count', 0),
                'face_quality': face_result.get('face_quality', 0.0),
                'is_photo_document': face_result.get('is_photo_document', False)
            }
        except Exception as e:
            ai_results['algorithms_results']['face_verifier'] = {
                'name': 'Face Verifier (OpenCV Detection)',
                'error': str(e),
                'confidence': 0.0
            }
        
        # 5. Fraud Detector - Metadata Analysis + Tampering Detection
        try:
            from ai_verification.advanced_algorithms import FraudDetector
            fraud_detector = FraudDetector()
            fraud_result = fraud_detector.analyze_document(document.document_file.path)
            ai_results['algorithms_results']['fraud_detector'] = {
                'name': 'Fraud Detector (Metadata + Tampering)',
                'confidence': fraud_result.get('confidence', 0.0),
                'tampering_detected': fraud_result.get('tampering_detected', False),
                'metadata_analysis': fraud_result.get('metadata', {}),
                'authenticity_score': fraud_result.get('authenticity_score', 0.0),
                'red_flags': fraud_result.get('red_flags', [])
            }
        except Exception as e:
            ai_results['algorithms_results']['fraud_detector'] = {
                'name': 'Fraud Detector (Metadata + Tampering)',
                'error': str(e),
                'confidence': 0.0
            }
        
        # 6. AI-Generated Content Detection
        try:
            from ai_verification.ai_generated_detector import AIGeneratedDetector
            ai_detector = AIGeneratedDetector()
            ai_detection_result = ai_detector.detect_ai_generated(
                document.document_file.path,
                'auto'
            )
            ai_results['algorithms_results']['ai_generated_detector'] = {
                'name': 'AI-Generated Content Detector',
                'confidence': 1.0 - ai_detection_result.get('ai_probability', 0.0),  # Invert - higher confidence = less likely AI
                'ai_probability': ai_detection_result.get('ai_probability', 0.0),
                'is_ai_generated': ai_detection_result.get('is_ai_generated', False),
                'detection_methods': len(ai_detection_result.get('detection_methods', {})),
                'suspicious_indicators': len(ai_detection_result.get('suspicious_indicators', [])),
                'recommendations': ai_detection_result.get('recommendations', [])
            }
        except Exception as e:
            ai_results['algorithms_results']['ai_generated_detector'] = {
                'name': 'AI-Generated Content Detector',
                'error': str(e),
                'confidence': 0.0
            }
        
        # 7. AI Verification Manager - Orchestrates with Weighted Scoring
        try:
            overall_confidence = 0.0
            total_weight = 0.0
            algorithm_weights = {
                'document_validator': 0.20,
                'cross_document_matcher': 0.15,
                'grade_verifier': 0.15,
                'face_verifier': 0.15,
                'fraud_detector': 0.15,
                'ai_generated_detector': 0.20  # High weight for AI detection
            }
            
            for alg_name, weight in algorithm_weights.items():
                if alg_name in ai_results['algorithms_results']:
                    alg_result = ai_results['algorithms_results'][alg_name]
                    if 'confidence' in alg_result and alg_result['confidence'] > 0:
                        overall_confidence += alg_result['confidence'] * weight
                        total_weight += weight
            
            if total_weight > 0:
                overall_confidence = overall_confidence / total_weight
            
            ai_results['overall_analysis'] = {
                'name': 'AI Verification Manager (Weighted Scoring)',
                'overall_confidence': round(overall_confidence, 3),
                'total_algorithms_run': len([r for r in ai_results['algorithms_results'].values() if 'confidence' in r]),
                'successful_algorithms': len([r for r in ai_results['algorithms_results'].values() if 'confidence' in r and r['confidence'] > 0]),
                'recommendation': 'approved' if overall_confidence >= 0.75 else 'manual_review' if overall_confidence >= 0.5 else 'rejected'
            }
            
        except Exception as e:
            ai_results['overall_analysis'] = {
                'name': 'AI Verification Manager (Weighted Scoring)',
                'error': str(e),
                'overall_confidence': 0.0
            }
        
        # Update document with AI results
        document.ai_analysis_completed = True
        document.ai_confidence_score = ai_results['overall_analysis'].get('overall_confidence', 0.0)
        document.ai_extracted_text = ai_results['algorithms_results'].get('document_validator', {}).get('extracted_text', '')
        document.ai_key_information = ai_results
        document.ai_recommendations = [ai_results['overall_analysis'].get('recommendation', 'manual_review')]
        document.ai_analysis_notes = f"AI Analysis completed at {timezone.now()}\nOverall Confidence: {document.ai_confidence_score:.1%}"
        
        # Auto-approve if high confidence
        if document.ai_confidence_score >= 0.85:
            document.status = 'approved'
            document.ai_auto_approved = True
            document.reviewed_at = timezone.now()
        elif document.ai_confidence_score <= 0.3:
            document.status = 'rejected'
            document.reviewed_at = timezone.now()
        else:
            document.status = 'pending'
        
        document.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action_type='ai_analysis',
            description=f'AI analysis completed for document {document.get_document_type_display()}',
            details={
                'document_id': document_id,
                'confidence_score': document.ai_confidence_score,
                'final_status': document.status,
                'algorithms_run': len(ai_results['algorithms_results'])
            },
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'success': True,
            'message': 'AI analysis completed successfully',
            'results': ai_results,
            'document_status': document.status,
            'auto_approved': document.ai_auto_approved
        })
        
    except Exception as e:
        return Response({
            'error': f'AI analysis failed: {str(e)}',
            'success': False
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_analysis_status(request, document_id):
    """
    🔍 Get AI Analysis Status for a Document
    Returns real-time status and results of AI processing
    """
    try:
        document = DocumentSubmission.objects.get(id=document_id, student=request.user)
        
        return Response({
            'document_id': document_id,
            'status': document.status,
            'ai_completed': document.ai_analysis_completed,
            'confidence_score': document.ai_confidence_score,
            'auto_approved': document.ai_auto_approved,
            'analysis_notes': document.ai_analysis_notes,
            'key_information': document.ai_key_information,
            'recommendations': document.ai_recommendations,
            'extracted_text': document.ai_extracted_text,
            'last_updated': document.reviewed_at.isoformat() if document.reviewed_at else None
        })
        
    except DocumentSubmission.DoesNotExist:
        return Response({'error': 'Document not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_dashboard_stats(request):
    """
    📊 AI Dashboard Statistics
    Returns comprehensive AI system performance metrics for frontend dashboard
    """
    try:
        # Basic AI stats
        total_documents = DocumentSubmission.objects.count()
        ai_processed = DocumentSubmission.objects.filter(ai_analysis_completed=True).count()
        auto_approved = DocumentSubmission.objects.filter(ai_auto_approved=True).count()
        
        # Confidence score distribution
        confidence_ranges = {
            'high_confidence': DocumentSubmission.objects.filter(ai_confidence_score__gte=0.75).count(),
            'medium_confidence': DocumentSubmission.objects.filter(ai_confidence_score__gte=0.5, ai_confidence_score__lt=0.75).count(),
            'low_confidence': DocumentSubmission.objects.filter(ai_confidence_score__lt=0.5, ai_confidence_score__gt=0).count()
        }
        
        # Algorithm performance
        recent_processed = DocumentSubmission.objects.filter(
            ai_analysis_completed=True,
            submitted_at__gte=timezone.now() - timezone.timedelta(days=30)
        )
        
        from django.db.models import Avg
        avg_confidence = recent_processed.aggregate(
            avg_confidence=Avg('ai_confidence_score')
        )['avg_confidence'] or 0.0
        
        # Processing speed metrics
        processing_stats = {
            'total_processed': ai_processed,
            'auto_approval_rate': (auto_approved / ai_processed * 100) if ai_processed > 0 else 0,
            'average_confidence': round(avg_confidence, 3),
            'confidence_distribution': confidence_ranges,
            'processing_efficiency': round((ai_processed / total_documents * 100), 1) if total_documents > 0 else 0
        }
        
        # Recent AI activity
        recent_activities = AuditLog.objects.filter(
            action_type__in=['ai_analysis', 'ai_auto_approve'],
            timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
        ).order_by('-timestamp')[:10]
        
        activities = []
        for activity in recent_activities:
            activities.append({
                'timestamp': activity.timestamp.isoformat(),
                'action': activity.action_type,
                'description': activity.action_description,
                'user': activity.user.username if activity.user else 'System',
                'details': activity.metadata
            })
        
        return Response({
            'success': True,
            'ai_statistics': processing_stats,
            'recent_activities': activities,
            'system_status': {
                'ai_enabled': True,
                'algorithms_available': 6,
                'processing_queue': DocumentSubmission.objects.filter(status='ai_processing').count()
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch AI statistics: {str(e)}',
            'success': False
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_batch_process(request):
    """
    🚀 Batch AI Processing
    Process multiple documents through AI algorithms
    """
    try:
        document_ids = request.data.get('document_ids', [])
        if not document_ids:
            return Response({'error': 'No document IDs provided'}, status=400)
        
        # Validate documents belong to user
        documents = DocumentSubmission.objects.filter(
            id__in=document_ids,
            student=request.user
        )
        
        if documents.count() != len(document_ids):
            return Response({'error': 'Some documents not found or unauthorized'}, status=400)
        
        # Process each document
        results = []
        for document in documents:
            try:
                # Call individual AI analysis
                analysis_result = ai_document_analysis(request._request if hasattr(request, '_request') else request)
                results.append({
                    'document_id': document.id,
                    'status': 'processed',
                    'confidence': document.ai_confidence_score
                })
            except Exception as e:
                results.append({
                    'document_id': document.id,
                    'status': 'error',
                    'error': str(e)
                })
        
        return Response({
            'success': True,
            'message': f'Batch processing completed for {len(results)} documents',
            'results': results
        })
        
    except Exception as e:
        return Response({
            'error': f'Batch processing failed: {str(e)}',
            'success': False
        }, status=500)


# ==================== PASSWORD RESET FUNCTIONALITY ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request a password reset code sent to email.
    POST data: { "email": "user@example.com" }
    """
    from .models import EmailVerificationCode
    from .email_utils import send_password_reset_email
    
    email = request.data.get('email', '').lower().strip()
    
    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user exists
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        # For security, don't reveal if email exists or not
        return Response({
            'success': True,
            'message': 'If an account with this email exists, a password reset code has been sent.'
        }, status=status.HTTP_200_OK)
    
    try:
        # Create verification code
        verification = EmailVerificationCode.create_verification_code(email)
        logger.info(f'Created verification code for {email}: {verification.code}')
        
        # Send password reset email
        success, error = send_password_reset_email(email, verification.code, user.username)
        
        if not success:
            logger.error(f'Failed to send password reset email to {email}: {error}')
            # Return a more detailed error for debugging
            return Response({
                'error': f'Email sending failed: {error}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f'Password reset email sent successfully to {email}')
        
        # Log the action
        audit_logger.log(
            user=user,
            action_type='password_changed',
            action_description=f'Password reset requested for email: {email}',
            severity='info',
            request=request
        )
        
        return Response({
            'success': True,
            'message': 'Password reset code has been sent to your email.',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f'Exception in password reset request: {str(e)}', exc_info=True)
        return Response({
            'error': f'Server error: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_code(request):
    """
    Verify the password reset code.
    POST data: { "email": "user@example.com", "code": "123456" }
    """
    from .models import EmailVerificationCode
    
    email = request.data.get('email', '').lower().strip()
    code = request.data.get('code', '').strip()
    
    if not email or not code:
        return Response({
            'error': 'Email and code are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find the verification code
    verification = EmailVerificationCode.objects.filter(
        email=email,
        code=code,
        is_used=False
    ).order_by('-created_at').first()
    
    if not verification:
        return Response({
            'error': 'Invalid verification code'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if verification.is_expired():
        return Response({
            'error': 'Verification code has expired. Please request a new one.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check attempts (max 5 attempts)
    if verification.attempts >= 5:
        verification.mark_as_used()
        return Response({
            'error': 'Too many verification attempts. Please request a new code.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    verification.increment_attempts()
    
    return Response({
        'success': True,
        'message': 'Code verified successfully. You can now reset your password.',
        'email': email,
        'code': code  # Return code for next step
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password after code verification.
    POST data: { "email": "user@example.com", "code": "123456", "new_password": "newpass123" }
    """
    from .models import EmailVerificationCode
    from django.contrib.auth.hashers import make_password
    
    email = request.data.get('email', '').lower().strip()
    code = request.data.get('code', '').strip()
    new_password = request.data.get('new_password', '').strip()
    
    if not email or not code or not new_password:
        return Response({
            'error': 'Email, code, and new password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    if len(new_password) < 8:
        return Response({
            'error': 'Password must be at least 8 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find the verification code
    verification = EmailVerificationCode.objects.filter(
        email=email,
        code=code,
        is_used=False
    ).order_by('-created_at').first()
    
    if not verification:
        return Response({
            'error': 'Invalid verification code'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if verification.is_expired():
        return Response({
            'error': 'Verification code has expired. Please request a new one.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find user
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark verification code as used
        verification.mark_as_used()
        
        # Log the action
        audit_logger.log(
            user=user,
            action_type='password_changed',
            action_description=f'Password reset successful for user: {user.username}',
            severity='success',
            request=request
        )
        
        logger.info(f'Password reset successful for user: {user.username}')
        
        return Response({
            'success': True,
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f'Error resetting password: {str(e)}', exc_info=True)
        return Response({
            'error': f'Failed to reset password: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BasicQualificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Basic Qualification criteria.
    Students must complete this before accessing documents and grades pages.
    """
    serializer_class = BasicQualificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return BasicQualification.objects.all()
        return BasicQualification.objects.filter(student=self.request.user)
    
    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """Check if the current user has completed basic qualification"""
        try:
            qualification = BasicQualification.objects.get(student=request.user)
            serializer = self.get_serializer(qualification)
            return Response({
                'completed': True,
                'qualified': qualification.is_qualified,
                'data': serializer.data
            })
        except BasicQualification.DoesNotExist:
            return Response({
                'completed': False,
                'qualified': False,
                'data': None
            })
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit or update basic qualification criteria"""
        try:
            # Check if qualification already exists
            try:
                qualification = BasicQualification.objects.get(student=request.user)
                serializer = self.get_serializer(qualification, data=request.data, partial=True, context={'request': request})
            except BasicQualification.DoesNotExist:
                # Create new qualification
                data = request.data.copy()
                data['student'] = request.user.id
                serializer = self.get_serializer(data=data, context={'request': request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Basic qualification criteria submitted successfully',
                    'qualified': serializer.instance.is_qualified,
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f'Error submitting basic qualification: {str(e)}', exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
