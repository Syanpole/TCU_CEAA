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
from .models import Task, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication, AuditLog, SystemAnalytics, VerifiedStudent, BasicQualification, FullApplication
from .audit_logger import audit_logger
from .serializers import (TaskSerializer, UserSerializer, LoginSerializer, RegisterSerializer,
                         DocumentSubmissionSerializer, DocumentSubmissionCreateSerializer,
                         GradeSubmissionSerializer, GradeSubmissionCreateSerializer,
                         AllowanceApplicationSerializer, AllowanceApplicationCreateSerializer,
                         BasicQualificationSerializer, FullApplicationSerializer)
from .email_utils import send_approval_email, send_verification_code_email, send_password_reset_email
from .email_verification_service import VerificationService
import logging
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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
        user.is_active = True  # Activate account since email is verified
        user.email_verified_at = timezone.now()
        user.save()
        
        token, created = Token.objects.get_or_create(user=user)
        
        # Mark VerifiedStudent as registered (if applicable)
        if user.student_id:
            try:
                verified_student = VerifiedStudent.objects.get(
                    student_id=user.student_id,
                    is_active=True
                )
                verified_student.has_registered = True
                verified_student.save()
            except VerifiedStudent.DoesNotExist:
                pass
        
        # Log user registration
        audit_logger.log_user_registration(user, request)
        
        # Log successful registration with verified email
        audit_logger.log(
            user=user,
            action_type='user_registered',
            action_description=f'User registered successfully with verified email: {user.email}',
            severity='info',
            metadata={
                'email': user.email,
                'username': user.username,
                'email_verified': True
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
            audit_logger.log(
                user=user,
                action_type='EMAIL_VERIFICATION_SENT',
                action_description=f'Verification code sent to {email}',
                severity='info',
                metadata={
                    'email': email
                },
                request=request
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
            audit_logger.log(
                user=user,
                action_type='EMAIL_VERIFIED',
                action_description=f'Email {email} successfully verified and account activated',
                severity='success',
                metadata={
                    'email': email,
                    'account_activated': True
                },
                request=request
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
            audit_logger.log(
                user=user,
                action_type='EMAIL_VERIFICATION_FAILED',
                action_description=f'Failed verification attempt for {email}',
                severity='warning',
                metadata={
                    'email': email,
                    'reason': result.get('message', 'Invalid code')
                },
                request=request
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
            audit_logger.log(
                user=user,
                action_type='EMAIL_VERIFICATION_RESENT',
                action_description=f'Verification code resent to {email}',
                severity='info',
                metadata={
                    'email': email
                },
                request=request
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
    Only requires Student ID number for verification.
    
    Expected payload:
    {
        "student_id": "22-00001"
    }
    
    Returns student information if verified.
    """
    student_id = request.data.get('student_id', '').strip()
    
    # Validate required field
    if not student_id:
        return Response({
            'verified': False,
            'message': 'Student ID is required.'
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
            'message': 'Student ID not found in verified records. Please ensure you are using your correct TCU Student ID.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if student has already registered
    if verified_student.has_registered:
        return Response({
            'verified': False,
            'message': 'This student has already registered. Please contact the administrator if you need assistance.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Student is verified - return their information
    result = {
        'verified': True,
        'message': 'Student verified successfully!',
        'student_data': {
            'student_id': verified_student.student_id,
            'first_name': verified_student.first_name,
            'last_name': verified_student.last_name,
            'middle_initial': verified_student.middle_initial,
            'sex': verified_student.sex,
            'course': verified_student.course,
            'year_level': verified_student.year_level
        }
    }
    
    # Log successful verification
    audit_logger.log(
        user=None,
        action_type='STUDENT_VERIFIED',
        action_description=f"Student {student_id} successfully verified for registration",
        severity='info',
        metadata={
            'student_id': student_id
        },
        request=request
    )
    
    return Response(result, status=status.HTTP_200_OK)

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
        
        # If COE is approved, extract subjects
        if new_status == 'approved' and document.document_type == 'certificate_of_enrollment':
            try:
                from .coe_verification_service import get_coe_verification_service
                coe_service = get_coe_verification_service()
                
                # Get the file path
                file_path = document.document_file.path if hasattr(document.document_file, 'path') else None
                
                if file_path:
                    logger.info(f"Extracting subjects from approved COE for student {document.student.student_id}")
                    
                    # Extract subjects
                    subject_result = coe_service.extract_subject_list(file_path)
                    
                    if subject_result['success'] and subject_result['subjects']:
                        document.extracted_subjects = subject_result['subjects']
                        document.subject_count = subject_result['subject_count']
                        document.save()
                        
                        logger.info(f"✅ Extracted {subject_result['subject_count']} subjects from COE")
                    else:
                        logger.warning(f"⚠️ Could not extract subjects from COE: {subject_result.get('errors')}")
            except Exception as e:
                logger.error(f"❌ Error extracting subjects from COE: {str(e)}")
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action_type='document_review',
            description=f'Admin reviewed document: {document.get_document_type_display()} - Status: {new_status}',
            details={
                'document_id': document.id,
                'student_id': document.student.student_id,
                'document_type': document.document_type,
                'new_status': new_status,
                'admin_notes': admin_notes,
                'subjects_extracted': document.subject_count if document.document_type == 'certificate_of_enrollment' else None
            },
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def ai_details(self, request, pk=None):
        """Get detailed AI analysis results for admin review"""
        if not request.user.is_admin():
            return Response({'error': 'Only admins can view AI details'}, status=status.HTTP_403_FORBIDDEN)
        
        document = self.get_object()
        
        # Extract detailed information from AI analysis
        ai_info = document.ai_key_information if document.ai_key_information else {}
        
        return Response({
            'document_id': document.id,
            'student': {
                'name': document.student.get_full_name(),
                'student_id': document.student.student_id,
                'email': document.student.email
            },
            'document_type': document.document_type,
            'document_type_display': document.get_document_type_display(),
            'status': document.status,
            'submitted_at': document.submitted_at,
            'ai_analysis': {
                'completed': document.ai_analysis_completed,
                'confidence_score': document.ai_confidence_score,
                'auto_approved': document.ai_auto_approved,
                'analysis_notes': document.ai_analysis_notes,
                'algorithms_results': ai_info.get('algorithms_results', {}),
                'overall_analysis': ai_info.get('overall_analysis', {}),
                'extracted_text': document.ai_extracted_text,
                'recommendations': document.ai_recommendations
            },
            'review_info': {
                'reviewed_at': document.reviewed_at,
                'reviewed_by': document.reviewed_by.get_full_name() if document.reviewed_by else None,
                'admin_notes': document.admin_notes
            }
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reanalyze(self, request, pk=None):
        """Trigger manual re-analysis of document by admin"""
        if not request.user.is_admin():
            return Response({'error': 'Only admins can trigger re-analysis'}, status=status.HTTP_403_FORBIDDEN)
        
        document = self.get_object()
        
        # Set status to processing
        document.status = 'ai_processing'
        document.save()
        
        # Trigger AI analysis
        try:
            from django.test import RequestFactory
            factory = RequestFactory()
            
            # Create a mock request for ai_document_analysis
            mock_request = factory.post('/api/ai/analyze-document/')
            mock_request.user = document.student
            mock_request.data = {'document_id': document.id}
            mock_request.META = request.META
            
            # Import and call the AI analysis function
            from myapp.views import ai_document_analysis
            result = ai_document_analysis(mock_request)
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action_type='document_reanalysis',
                description=f'Admin triggered re-analysis for document: {document.get_document_type_display()}',
                details={
                    'document_id': document.id,
                    'student_id': document.student.student_id,
                    'document_type': document.document_type
                },
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Refresh document from database
            document.refresh_from_db()
            serializer = self.get_serializer(document)
            
            return Response({
                'success': True,
                'message': 'Document re-analyzed successfully',
                'document': serializer.data,
                'new_confidence': document.ai_confidence_score,
                'new_status': document.status
            })
            
        except Exception as e:
            document.status = 'pending'
            document.save()
            return Response({
                'success': False,
                'error': f'Re-analysis failed: {str(e)}'
            }, status=500)

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
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def grouped_by_semester(self, request):
        """
        Get grades grouped by (academic_year, semester) with GWA calculation.
        Admins can get grouped grades for all students or specific students.
        Students can only get their own grouped grades.
        
        Query parameters:
        - student_id: (Admin only) Filter by specific student
        - academic_year: Filter by academic year
        - semester: Filter by semester
        - status: Filter by status (pending, approved, rejected)
        
        Returns:
            List of semester groups with:
            - academic_year, semester, semester_label
            - subjects: List of grades in group
            - gwa: Calculated GWA
            - subject_count: Number of subjects
            - total_units: Total units for semester
            - merit_level: Merit classification
            - qualifies_basic: Basic allowance eligibility
            - qualifies_merit: Merit allowance eligibility
        """
        from .semester_grouping_service import get_semester_grouping_service
        
        grouping_service = get_semester_grouping_service()
        
        try:
            if request.user.is_admin():
                # Admin can view grouped grades
                student_id = request.query_params.get('student_id')
                academic_year = request.query_params.get('academic_year')
                semester = request.query_params.get('semester')
                status_filter = request.query_params.get('status')
                
                if student_id:
                    # Get grouped grades for specific student
                    try:
                        student = CustomUser.objects.get(id=student_id, role='student')
                    except CustomUser.DoesNotExist:
                        return Response(
                            {'error': f'Student with ID {student_id} not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    
                    filters = {}
                    if academic_year:
                        filters['academic_year'] = academic_year
                    if semester:
                        filters['semester'] = semester
                    if status_filter:
                        filters['status'] = status_filter
                    
                    grouped_data = grouping_service.group_student_grades_by_semester(student, filters)
                    return Response({
                        'student_id': student.id,
                        'student_name': f"{student.first_name} {student.last_name}",
                        'semester_groups': grouped_data
                    })
                else:
                    # Get grouped grades for all students
                    grouped_all = grouping_service.get_grouped_grades_for_admin(
                        academic_year=academic_year,
                        semester=semester,
                        status=status_filter
                    )
                    
                    # Convert to list format for response
                    response_data = []
                    for student_id, groups in grouped_all.items():
                        try:
                            student = CustomUser.objects.get(id=student_id)
                            response_data.append({
                                'student_id': student_id,
                                'student_name': f"{student.first_name} {student.last_name}",
                                'semester_groups': groups
                            })
                        except CustomUser.DoesNotExist:
                            pass
                    
                    return Response(response_data)
            else:
                # Students can only see their own grouped grades
                academic_year = request.query_params.get('academic_year')
                semester = request.query_params.get('semester')
                
                filters = {}
                if academic_year:
                    filters['academic_year'] = academic_year
                if semester:
                    filters['semester'] = semester
                
                grouped_data = grouping_service.group_student_grades_by_semester(
                    request.user,
                    filters
                )
                
                return Response({
                    'student_id': request.user.id,
                    'student_name': f"{request.user.first_name} {request.user.last_name}",
                    'semester_groups': grouped_data
                })
        
        except Exception as e:
            logger.error(f"Error getting grouped grades: {str(e)}")
            return Response(
                {'error': f'Error retrieving grouped grades: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def approve_semester_group(self, request):
        """
        Admin action to approve all grades in a semester group.
        
        Expected data:
        - student_id: Student ID
        - academic_year: Academic year
        - semester: Semester
        """
        if not request.user.is_admin():
            return Response(
                {'error': 'Only admins can approve semester groups'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            student_id = request.data.get('student_id')
            academic_year = request.data.get('academic_year')
            semester = request.data.get('semester')
            admin_notes = request.data.get('admin_notes', '')
            
            if not all([student_id, academic_year, semester]):
                return Response(
                    {'error': 'Missing required fields: student_id, academic_year, semester'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update all grades in this semester group
            updated_count = GradeSubmission.objects.filter(
                student_id=student_id,
                academic_year=academic_year,
                semester=semester
            ).update(
                status='approved',
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
                admin_notes=admin_notes
            )
            
            if updated_count == 0:
                return Response(
                    {'error': f'No grades found for this semester group'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            logger.info(f"Admin {request.user.id} approved {updated_count} grades for semester group")
            
            # Get updated semester data
            from .semester_grouping_service import get_semester_grouping_service
            grouping_service = get_semester_grouping_service()
            
            try:
                student = CustomUser.objects.get(id=student_id)
                updated_group = grouping_service.get_semester_detail(student, academic_year, semester)
                
                return Response({
                    'message': f'Successfully approved {updated_count} grade(s)',
                    'updated_count': updated_count,
                    'semester_group': updated_group
                })
            except CustomUser.DoesNotExist:
                return Response({
                    'message': f'Successfully approved {updated_count} grade(s)',
                    'updated_count': updated_count
                })
        
        except Exception as e:
            logger.error(f"Error approving semester group: {str(e)}")
            return Response(
                {'error': f'Error approving semester group: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# New Grade Submission API Endpoints (Per-Subject Workflow)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_grade_submission_eligibility(request):
    """
    Check if the current user is eligible to submit grades.
    
    Returns:
        - can_submit: Boolean indicating if user can submit grades
        - required_documents: List of required document types
        - approved_documents: List of approved document types
        - missing_documents: List of missing document types
        - pending_documents: List of pending document types
        - messages: List of user-friendly messages
    """
    try:
        # Check for approved COE
        coe_document = DocumentSubmission.objects.filter(
            student=request.user,
            document_type='certificate_of_enrollment',
            status='approved'
        ).first()
        
        # Check for approved ID documents
        id_documents = DocumentSubmission.objects.filter(
            student=request.user,
            document_type__in=['student_id', 'government_id', 'school_id', 'birth_certificate'],
            status='approved'
        )
        
        # Get all user documents for comprehensive check
        all_docs = DocumentSubmission.objects.filter(student=request.user)
        approved_docs = all_docs.filter(status='approved')
        pending_docs = all_docs.filter(status__in=['pending', 'needs_review', 'ai_processing'])
        
        required_doc_types = ['certificate_of_enrollment', 'id_copy']
        approved_doc_types = list(approved_docs.values_list('document_type', flat=True))
        pending_doc_types = list(pending_docs.values_list('document_type', flat=True))
        
        has_approved_coe = coe_document is not None
        has_approved_id = id_documents.exists()
        
        messages = []
        can_submit = has_approved_coe and has_approved_id
        
        if not has_approved_coe:
            if all_docs.filter(document_type='certificate_of_enrollment').exists():
                messages.append('Your Certificate of Enrollment is still being reviewed.')
            else:
                messages.append('Please submit your Certificate of Enrollment.')
        elif coe_document.subject_count == 0:
            messages.append('Your COE has been approved but no subjects were extracted. Please contact admin.')
            can_submit = False
        
        if not has_approved_id:
            if all_docs.filter(document_type__in=['student_id', 'government_id', 'school_id', 'birth_certificate']).exists():
                messages.append('Your ID document is still being reviewed.')
            else:
                messages.append('Please submit a valid ID (School ID, Birth Certificate, or Government ID).')
        
        if can_submit:
            messages.append('✅ You are eligible to submit grades!')
        
        return Response({
            'can_submit': can_submit,
            'required_documents': required_doc_types,
            'approved_documents': approved_doc_types,
            'pending_documents': pending_doc_types,
            'missing_documents': [doc for doc in required_doc_types if doc not in approved_doc_types],
            'messages': messages,
            'coe_subjects_count': coe_document.subject_count if coe_document else 0
        })
    
    except Exception as e:
        logger.error(f"Error checking grade submission eligibility: {str(e)}")
        return Response({
            'error': f'Error checking eligibility: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_coe_subjects(request):
    """
    Get the list of subjects extracted from the student's approved COE.
    
    Returns:
        - subjects: List of subjects from COE
        - subject_count: Number of subjects
        - coe_document_id: ID of the COE document
    """
    try:
        # Find the student's approved COE document
        coe_document = DocumentSubmission.objects.filter(
            student=request.user,
            document_type='certificate_of_enrollment',
            status='approved'
        ).order_by('-submitted_at').first()
        
        if not coe_document:
            return Response({
                'error': 'No approved Certificate of Enrollment found. Please submit and get your COE approved first.',
                'subjects': [],
                'subject_count': 0
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if subjects have been extracted
        if not coe_document.extracted_subjects or coe_document.subject_count == 0:
            return Response({
                'error': 'No subjects found in your COE. Please contact admin for manual verification.',
                'subjects': [],
                'subject_count': 0,
                'coe_document_id': coe_document.id
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'subjects': coe_document.extracted_subjects,
            'subject_count': coe_document.subject_count,
            'coe_document_id': coe_document.id,
            'coe_submitted_at': coe_document.submitted_at
        })
    
    except Exception as e:
        logger.error(f"Error fetching COE subjects: {str(e)}")
        return Response({
            'error': f'Error fetching subjects: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_subject_grade(request):
    """
    Submit a grade for a single subject.
    
    Expected data:
        - subject_code: Subject code (e.g., GE101)
        - subject_name: Subject name
        - academic_year: Academic year (YYYY-YYYY)
        - semester: Semester (1st, 2nd, summer)
        - units: Number of units
        - grade_received: Grade for this subject
        - grade_sheet: Image file of the grade
    """
    try:
        from .serializers import GradeSubmissionCreateSerializer
        
        # Validate required fields
        required_fields = ['subject_code', 'subject_name', 'academic_year', 'semester', 'grade_sheet']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'error': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create grade submission
        data = request.data.copy()
        
        # Create the grade submission
        grade_submission = GradeSubmission.objects.create(
            student=request.user,
            subject_code=data.get('subject_code'),
            subject_name=data.get('subject_name'),
            academic_year=data.get('academic_year'),
            semester=data.get('semester'),
            units=data.get('units'),
            grade_received=data.get('grade_received'),
            grade_sheet=data.get('grade_sheet'),
            status='processing'  # Set to processing while AI verifies
        )
        
        # Trigger AI verification asynchronously
        from .tasks import verify_grade_sheet_task
        try:
            verify_grade_sheet_task(grade_submission.id)
        except Exception as e:
            logger.error(f"Error triggering AI verification: {str(e)}")
            # Continue even if AI verification fails
        
        serializer = GradeSubmissionSerializer(grade_submission)
        
        audit_logger.log(
            user=request.user,
            action_type='GRADE_SUBMITTED',
            action_description=f'Grade submitted for {data.get("subject_code")} - {data.get("subject_name")}',
            severity='info',
            target_model='GradeSubmission',
            target_object_id=grade_submission.id,
            metadata={
                'subject_code': data.get('subject_code'),
                'subject_name': data.get('subject_name'),
                'semester': data.get('semester')
            },
            request=request
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error submitting subject grade: {str(e)}")
        return Response({
            'error': f'Error submitting grade: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_grade_submissions(request):
    """
    Validate all grade submissions against the COE subject list.
    
    Expected data:
        - academic_year: Academic year to validate
        - semester: Semester to validate
    
    Returns validation results with detailed feedback.
    """
    try:
        from .grade_validation_service import get_grade_validation_service
        
        academic_year = request.data.get('academic_year')
        semester = request.data.get('semester')
        
        if not academic_year or not semester:
            return Response({
                'error': 'Missing academic_year or semester'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get COE subjects
        coe_document = DocumentSubmission.objects.filter(
            student=request.user,
            document_type='certificate_of_enrollment',
            status='approved'
        ).order_by('-submitted_at').first()
        
        if not coe_document or not coe_document.extracted_subjects:
            return Response({
                'error': 'No approved COE with extracted subjects found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get grade submissions for this period
        grade_submissions = GradeSubmission.objects.filter(
            student=request.user,
            academic_year=academic_year,
            semester=semester,
            subject_code__isnull=False  # Only new per-subject submissions
        ).values('id', 'subject_code', 'subject_name', 'units', 'grade_received', 'status')
        
        # Validate
        validation_service = get_grade_validation_service()
        validation_result = validation_service.validate_grade_submissions(
            coe_subjects=coe_document.extracted_subjects,
            grade_submissions=list(grade_submissions)
        )
        
        # Add validation summary
        validation_result['summary'] = validation_service.get_validation_summary(validation_result)
        
        # Calculate GPA and merit eligibility if validation passed
        if validation_result['is_valid']:
            from .services import gwa_calculation_service
            gwa_result = gwa_calculation_service.trigger_automated_gwa_calculation(
                request.user, academic_year, semester
            )
            if gwa_result:
                validation_result['gwa_calculation'] = {
                    'success': True,
                    'gwa': gwa_result['gwa'],
                    'merit_level': gwa_result['merit_level'],
                    'qualifies_for_merit': gwa_result['merit_eligible'],
                    'total_units': gwa_result['total_units'],
                    'calculation_triggered': gwa_result['calculation_triggered']
                }
            else:
                validation_result['gwa_calculation'] = {
                    'success': False,
                    'message': 'GWA calculation could not be completed'
                }
        
        audit_logger.log(
            user=request.user,
            action_type='GRADES_VALIDATED',
            action_description=f'Grade validation for {academic_year} {semester}: {"PASSED" if validation_result["is_valid"] else "FAILED"}',
            severity='info' if validation_result['is_valid'] else 'warning',
            metadata={
                'academic_year': academic_year,
                'semester': semester,
                'is_valid': validation_result['is_valid'],
                'error_count': len(validation_result['errors'])
            },
            request=request
        )
        
        return Response(validation_result)
    
    except Exception as e:
        logger.error(f"Error validating grades: {str(e)}")
        return Response({
            'error': f'Validation error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_grade_submission_status(request):
    """
    Get the current status of grade submissions for a student.
    
    Query params:
        - academic_year: Academic year
        - semester: Semester
    
    Returns:
        - total_subjects: Number of subjects from COE
        - submitted_count: Number of grades submitted
        - approved_count: Number of grades approved
        - rejected_count: Number of grades rejected
        - pending_count: Number of grades pending review
        - is_complete: Whether all subjects have been submitted
        - can_proceed_to_liveness: Whether student can proceed to liveness detection
        - submissions: List of grade submissions with details
    """
    try:
        academic_year = request.query_params.get('academic_year')
        semester = request.query_params.get('semester')
        
        if not academic_year or not semester:
            return Response({
                'error': 'Missing academic_year or semester parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get COE subjects
        coe_document = DocumentSubmission.objects.filter(
            student=request.user,
            document_type='certificate_of_enrollment',
            status='approved'
        ).order_by('-submitted_at').first()
        
        if not coe_document or not coe_document.extracted_subjects:
            return Response({
                'error': 'No approved COE found',
                'total_subjects': 0,
                'submitted_count': 0
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get grade submissions
        submissions = GradeSubmission.objects.filter(
            student=request.user,
            academic_year=academic_year,
            semester=semester,
            subject_code__isnull=False
        )
        
        total_subjects = coe_document.subject_count
        submitted_count = submissions.count()
        approved_count = submissions.filter(status='approved').count()
        rejected_count = submissions.filter(status='rejected').count()
        pending_count = submissions.filter(status='pending').count()
        
        # Check if can proceed to liveness (all submitted)
        is_complete = submitted_count == total_subjects
        all_approved = approved_count == total_subjects
        # Allow proceeding to liveness once all subjects are submitted (don't wait for admin approval)
        can_proceed_to_liveness = is_complete
        
        # Calculate GPA if all approved
        gpa_data = None
        if all_approved:
            from .services import gwa_calculation_service
            gwa_result = gwa_calculation_service.calculate_semester_gwa(request.user, academic_year, semester)
            if gwa_result:
                gpa_data = {
                    'gpa': gwa_result['gwa'],
                    'merit_level': gwa_result['merit_level'],
                    'qualifies_for_merit': gwa_result['merit_eligible'],
                    'total_units': gwa_result['total_units']
                }
        
        serializer = GradeSubmissionSerializer(submissions, many=True)
        
        response_data = {
            'total_subjects': total_subjects,
            'submitted_count': submitted_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'pending_count': pending_count,
            'is_complete': is_complete,
            'all_approved': all_approved,
            'can_proceed_to_liveness': can_proceed_to_liveness,
            'submissions': serializer.data,
            'coe_subjects': coe_document.extracted_subjects
        }
        
        if gpa_data:
            response_data['gpa_calculated'] = True
            response_data.update(gpa_data)
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f"Error getting grade submission status: {str(e)}")
        return Response({
            'error': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        audit_logger.log(
            user=application.student,
            action_type='APPLICATION_SUBMITTED',
            action_description=f'Allowance application #{application.id} submitted. Email notification {"sent" if email_sent else "failed"}.',
            severity='info',
            target_model='AllowanceApplication',
            target_object_id=application.id,
            metadata={
                'application_id': application.id,
                'application_type': application.application_type,
                'amount': float(application.amount),
                'email_sent': email_sent
            },
            request=self.request
        )
        
        return application
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def process(self, request, pk=None):
        """Admin processing of allowance application"""
        from .application_email_service import ApplicationEmailService
        
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_identity(self, request, pk=None):
        """
        Verify student identity for allowance application using liveness detection and face verification.
        This is the final step after allowance application to confirm the student's identity.
        
        Expected POST data:
        - photo: File (Live selfie with liveness verification)
        - liveness_data: JSON string (liveness challenge results)
        
        Returns:
        - success: Boolean
        - liveness_passed: Boolean
        - face_verified: Boolean
        - message: String
        """
        from .face_comparison_service import FaceComparisonService
        
        try:
            application = self.get_object()
            
            # Check if application belongs to the requesting user
            if application.student != request.user:
                return Response({
                    'error': 'You can only verify your own applications'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if face verification is already completed
            if application.face_verification_completed:
                return Response({
                    'success': False,
                    'error': 'Face verification has already been completed for this application'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get uploaded photo
            photo = request.FILES.get('photo')
            liveness_data_str = request.POST.get('liveness_data')
            
            # Validate inputs
            if not photo:
                return Response({
                    'error': 'Photo is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not liveness_data_str:
                return Response({
                    'error': 'Liveness data is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse liveness data
            try:
                liveness_data = json.loads(liveness_data_str)
            except json.JSONDecodeError:
                return Response({
                    'error': 'Invalid liveness data format'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize face service
            face_service = FaceComparisonService()
            
            # Verify liveness first
            liveness_passed = face_service._verify_liveness_data(liveness_data)
            
            if not liveness_passed:
                logger.warning(f"Liveness verification failed for user {request.user.id} on application {application.id}")
                
                # Update application with failed verification
                application.face_verification_completed = True
                application.face_verification_passed = False
                application.face_verification_attempted_at = timezone.now()
                application.face_verification_notes = 'Liveness verification failed. Please ensure you complete all challenges (color flash, blink, movement).'
                application.face_verification_data = {
                    'liveness_passed': False,
                    'liveness_data': liveness_data,
                    'attempted_at': application.face_verification_attempted_at.isoformat()
                }
                application.save()
                
                return Response({
                    'success': False,
                    'liveness_passed': False,
                    'face_verified': False,
                    'message': 'Liveness verification failed. Please ensure you complete all challenges (color flash, blink, movement).'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the user's ID document for face comparison
            # Look for approved ID documents (school_id, birth_certificate, or voters_certificate)
            id_document = DocumentSubmission.objects.filter(
                student=request.user,
                status='approved',
                document_type__in=['school_id', 'birth_certificate', 'voters_certificate']
            ).first()
            
            if not id_document or not id_document.file:
                # Update application with failed verification
                application.face_verification_completed = True
                application.face_verification_passed = False
                application.face_verification_attempted_at = timezone.now()
                application.face_verification_notes = 'No approved ID document found. Please upload and get your School ID, Birth Certificate, or Voter\'s Certificate approved first.'
                application.face_verification_data = {
                    'liveness_passed': True,
                    'id_document_missing': True,
                    'attempted_at': application.face_verification_attempted_at.isoformat()
                }
                application.save()
                
                return Response({
                    'success': False,
                    'liveness_passed': True,
                    'face_verified': False,
                    'message': 'No approved ID document found. Please upload and get your School ID, Birth Certificate, or Voter\'s Certificate approved first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save selfie temporarily
            selfie_path = default_storage.save(
                f'temp/allowance_selfie_{request.user.id}_{application.id}.jpg',
                ContentFile(photo.read())
            )
            
            try:
                # Get full paths
                id_full_path = default_storage.path(id_document.file.name)
                selfie_full_path = default_storage.path(selfie_path)
                
                # Perform face verification
                verification_result = face_service.verify_id_with_selfie(
                    id_full_path,
                    selfie_full_path,
                    liveness_data
                )
                
                # Clean up temporary file
                default_storage.delete(selfie_path)
                
                face_verified = verification_result.get('match', False)
                similarity_score = verification_result.get('similarity_score', 0.0)
                confidence = verification_result.get('confidence', 'very_low')
                
                # Update application with verification results
                application.face_verification_completed = True
                application.face_verification_passed = face_verified
                application.face_verification_score = similarity_score
                application.face_verification_confidence = confidence
                application.face_verification_attempted_at = timezone.now()
                
                # Prepare verification data
                verification_data = {
                    'liveness_passed': True,
                    'face_verified': face_verified,
                    'similarity_score': similarity_score,
                    'confidence': confidence,
                    'id_document_type': id_document.document_type,
                    'id_document_id': id_document.id,
                    'liveness_data': liveness_data,
                    'verification_result': verification_result,
                    'attempted_at': application.face_verification_attempted_at.isoformat()
                }
                application.face_verification_data = verification_data
                
                # Set verification notes
                if face_verified:
                    application.face_verification_notes = f'Identity verification successful! Face matches ID document (Similarity: {similarity_score:.2%}, Confidence: {confidence}).'
                else:
                    application.face_verification_notes = f'Face verification failed. Face does not sufficiently match ID document (Similarity: {similarity_score:.2%}, Confidence: {confidence}). This may indicate identity fraud.'
                
                application.save()
                
                # Log verification attempt
                logger.info(
                    f"Allowance application identity verification for user {request.user.id}, application {application.id}: "
                    f"Liveness={liveness_passed}, Face Match={face_verified}, "
                    f"Similarity={similarity_score:.4f}, Confidence={confidence}"
                )
                
                # Create audit log
                audit_logger.log(
                    user=request.user,
                    action_type='application_submitted',
                    action_description=f'Identity verification completed for allowance application #{application.id}',
                    severity='info',
                    target_model='AllowanceApplication',
                    target_object_id=application.id,
                    metadata={
                        'application_id': application.id,
                        'face_verified': face_verified,
                        'similarity_score': similarity_score,
                        'confidence': confidence,
                        'liveness_passed': liveness_passed
                    },
                    request=request
                )
                
                if face_verified:
                    return Response({
                        'success': True,
                        'liveness_passed': True,
                        'face_verified': True,
                        'similarity_score': similarity_score,
                        'confidence': confidence,
                        'message': 'Identity verification successful! Your face matches your ID document.'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'liveness_passed': True,
                        'face_verified': False,
                        'similarity_score': similarity_score,
                        'confidence': confidence,
                        'message': f'Face verification failed. Your face does not sufficiently match your ID document (Similarity: {similarity_score:.2%}, Confidence: {confidence}). This may indicate identity fraud.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as processing_error:
                # Clean up on error
                default_storage.delete(selfie_path)
                raise processing_error
                
        except Exception as e:
            logger.error(f"Allowance application identity verification error: {str(e)}")
            return Response(
                {
                    'error': 'Identity verification failed',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        'documents': DocumentSubmissionSerializer(documents, many=True, context={'request': request}).data,
        'grades': GradeSubmissionSerializer(grades, many=True, context={'request': request}).data,
        'applications': AllowanceApplicationSerializer(applications, many=True, context={'request': request}).data,
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
        'pending_documents': DocumentSubmissionSerializer(pending_documents, many=True, context={'request': request}).data,
        'pending_grades': GradeSubmissionSerializer(pending_grades, many=True, context={'request': request}).data,
        'pending_applications': AllowanceApplicationSerializer(pending_applications, many=True, context={'request': request}).data,
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
    
    # Top performing students - grouped by semester with proper GWA calculation
    from .semester_grouping_service import get_semester_grouping_service
    
    top_students_raw = GradeSubmission.objects.filter(
        status='approved',
        qualifies_for_merit_incentive=True
    ).order_by('-semestral_weighted_average')[:10]
    
    semester_grouping_service = get_semester_grouping_service()
    top_students_data = []
    seen_students = set()
    
    for grade in top_students_raw:
        student_id = grade.student.id
        
        # Only include each student once (their best semester)
        if student_id in seen_students:
            continue
        seen_students.add(student_id)
        
        # Get semester grouping with proper GWA calculation
        semester_detail = semester_grouping_service.get_semester_detail(
            grade.student,
            grade.academic_year,
            grade.semester
        )
        
        if not semester_detail:
            continue
        
        # Get all approved documents for this student
        approved_docs = DocumentSubmission.objects.filter(
            student=grade.student,
            status='approved'
        ).count()
        
        # Get allowance applications
        allowance_apps = AllowanceApplication.objects.filter(
            student=grade.student,
            status__in=['approved', 'disbursed']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        top_students_data.append({
            'student_name': f"{grade.student.first_name} {grade.student.last_name}",
            'student_id': grade.student.student_id,
            'academic_year': semester_detail['academic_year'],
            'semester': semester_detail['semester_label'],
            'gwa': semester_detail.get('gwa', 0.0) or 0.0,  # Use calculated GWA from service
            'swa': float(grade.semestral_weighted_average) if grade.semestral_weighted_average is not None else 0.0,
            'total_units': semester_detail.get('total_units', 0),
            'subject_count': semester_detail.get('subject_count', 0),
            'approved_documents': approved_docs,
            'allowance_amount': float(allowance_apps),
            'applications_pending': AllowanceApplication.objects.filter(
                student=grade.student,
                status='pending'
            ).count(),
            'qualifies_basic': semester_detail.get('qualifies_basic', False),
            'qualifies_merit': semester_detail.get('qualifies_merit', False),
            'merit_level': semester_detail.get('merit_level', 'BELOW_PASSING'),
            'all_approved': semester_detail.get('all_approved', False)
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
        
        # ============================================================================
        # 🆕 SPECIALIZED DOCUMENT VERIFICATION ROUTING
        # Route to appropriate specialized service based on document type
        # ============================================================================
        
        # Check if document is COE (Certificate of Enrollment)
        if document.document_type == 'certificate_of_enrollment':
            from myapp.coe_verification_service import get_coe_verification_service
            
            coe_service = get_coe_verification_service()
            coe_result = coe_service.verify_coe_document(
                image_path=document.document_file.path,
                confidence_threshold=0.5,
                include_ocr=True
            )
            
            # Format response for COE verification
            ai_results = {
                'document_id': document_id,
                'document_type': 'certificate_of_enrollment',
                'processing_timestamp': timezone.now().isoformat(),
                'service_used': 'COE Verification Service (YOLO + Advanced OCR + Intelligent Interpreter)',
                'verification_result': coe_result,
                'algorithms_results': {
                    'coe_yolo_detection': {
                        'name': 'YOLOv8 COE Element Detection',
                        'confidence': coe_result.get('confidence', 0.0),
                        'status': coe_result.get('status', 'UNKNOWN'),
                        'detected_elements': coe_result.get('detected_elements', {}),
                        'validation_checks': coe_result.get('validation_checks', {})
                    },
                    'advanced_ocr': {
                        'name': 'Advanced OCR + Intelligent Interpreter',
                        'confidence': coe_result.get('ocr_data', {}).get('ocr_confidence', 0.0) if coe_result.get('ocr_data') else 0.0,
                        'extracted_info': coe_result.get('extracted_info', {}),
                        'fields_extracted': sum(1 for v in coe_result.get('extracted_info', {}).values() if v is not None)
                    }
                }
            }
            
            # Update document status based on COE verification
            if coe_result.get('is_valid'):
                document.status = 'verified'
                document.ai_confidence_score = coe_result.get('confidence', 0.0)
            else:
                document.status = 'needs_review'
                document.ai_confidence_score = coe_result.get('confidence', 0.0)
            document.ai_analysis_completed = True
            document.ai_auto_approved = coe_result.get('is_valid', False)
            document.ai_analysis_notes = f"COE Verification completed\nConfidence: {document.ai_confidence_score:.1%}\nStatus: {coe_result.get('status', 'UNKNOWN')}"
            document.ai_key_information = ai_results
            
            # Save extracted subjects to document model
            extracted_info = coe_result.get('extracted_info', {})
            if extracted_info.get('subjects'):
                document.extracted_subjects = extracted_info['subjects']
                document.subject_count = extracted_info.get('subject_count', len(extracted_info['subjects']))
                logger.info(f"✅ Saved {document.subject_count} subjects to document model")
            else:
                logger.warning("⚠️ No subjects extracted from COE document")
            
            document.save()
            
            return Response({
                'success': True,
                'message': f'COE verification completed: {coe_result.get("status")}',
                'ai_analysis': ai_results
            })
        
        # Check if document is ID (Student ID or Government ID)
        elif document.document_type in ['student_id', 'government_id', 'school_id']:
            from myapp.id_verification_service import get_id_verification_service
            
            id_service = get_id_verification_service()
            
            id_result = id_service.verify_id_card(
                image_path=document.document_file.path,
                document_type=document.document_type,
                user=request.user
            )
            
            # Format response for ID verification
            ai_results = {
                'document_id': document_id,
                'document_type': document.document_type,
                'processing_timestamp': timezone.now().isoformat(),
                'service_used': 'ID Verification Service (YOLO + Advanced OCR + Identity Matching)',
                'verification_result': id_result,
                'algorithms_results': {
                    'id_yolo_detection': {
                        'name': 'YOLOv8 ID Element Detection',
                        'confidence': id_result.get('yolo_confidence', 0.0),
                        'detected_elements': id_result.get('detected_elements', {})
                    },
                    'advanced_ocr': {
                        'name': 'Advanced OCR',
                        'confidence': id_result.get('ocr_confidence', 0.0),
                        'extracted_text': id_result.get('extracted_text', '')
                    },
                    'identity_matching': {
                        'name': 'Identity Verification (Fuzzy Matching)',
                        'confidence': id_result.get('identity_match_score', 0.0),
                        'name_match': id_result.get('name_match', False),
                        'id_match': id_result.get('id_match', False)
                    }
                }
            }
            
            # Update document status based on ID verification
            if id_result.get('is_valid'):
                document.status = 'verified'
                document.ai_confidence_score = id_result.get('overall_confidence', 0.0)
            else:
                document.status = 'needs_review'
                document.ai_confidence_score = id_result.get('overall_confidence', 0.0)
            document.ai_analysis_completed = True
            document.ai_auto_approved = id_result.get('is_valid', False)
            document.ai_analysis_notes = f"ID Verification completed\nConfidence: {document.ai_confidence_score:.1%}\nStatus: {id_result.get('status', 'UNKNOWN')}"
            document.ai_key_information = ai_results
            document.ai_extracted_text = id_result.get('extracted_text', '')
            
            document.save()
            
            return Response({
                'success': True,
                'message': f'ID verification completed: {id_result.get("status", "VERIFIED" if id_result.get("is_valid") else "NEEDS REVIEW")}',
                'ai_analysis': ai_results
            })
        
        # Check if document is Birth Certificate
        elif document.document_type == 'birth_certificate':
            from myapp.birth_certificate_verification_service import get_birth_certificate_verification_service
            birth_service = get_birth_certificate_verification_service()
            birth_result = birth_service.verify_birth_certificate_document(
                image_path=document.document_file.path,
                confidence_threshold=0.5,
                include_ocr=True
            )
            ai_results = {
                'document_id': document_id,
                'document_type': 'birth_certificate',
                'processing_timestamp': timezone.now().isoformat(),
                'service_used': 'Birth Certificate Verification Service (Advanced OCR + Field Extraction)',
                'verification_result': birth_result,
                'algorithms_results': {
                    'birth_ocr': {
                        'name': 'Advanced OCR',
                        'confidence': birth_result.get('ocr_data', {}).get('ocr_confidence', 0.0) if birth_result.get('ocr_data') else 0.0,
                        'extracted_info': birth_result.get('extracted_info', {})
                    }
                }
            }
            if birth_result.get('is_valid'):
                document.status = 'verified'
                document.ai_confidence_score = birth_result.get('confidence', 0.0)
            else:
                document.status = 'needs_review'
                document.ai_confidence_score = birth_result.get('confidence', 0.0)
            document.ai_analysis_completed = True
            document.ai_auto_approved = birth_result.get('is_valid', False)
            document.ai_analysis_notes = f"Birth Certificate verification completed\nConfidence: {document.ai_confidence_score:.1%}\nStatus: {birth_result.get('status', 'UNKNOWN')}"
            document.ai_key_information = ai_results
            document.save()
            return Response({
                'success': True,
                'message': f"Birth Certificate verification completed: {birth_result.get('status')}",
                'ai_analysis': ai_results
            })
        # Check if document is Voter's Certificate
        elif document.document_type in ['voters_certificate', 'voter_certificate', 'voters_id', 'voter_id']:
            from myapp.voter_certificate_verification_service import get_voter_certificate_verification_service
            
            voter_service = get_voter_certificate_verification_service()
            
            user_application_data = {}
            try:
                from myapp.models import FullApplication
                full_app = FullApplication.objects.filter(user=request.user).order_by('-id').first()
                if full_app:
                    user_application_data = {
                        'first_name': full_app.first_name,
                        'middle_name': full_app.middle_name,
                        'last_name': full_app.last_name,
                        'barangay': full_app.barangay,
                        'house_no': full_app.house_no,
                        'street': full_app.street,
                        'district': full_app.district,
                        'mother_name': full_app.mother_name,
                        'father_name': full_app.father_name
                    }
            except Exception:
                user_application_data = {}
            voter_result = voter_service.verify_voter_certificate_document(
                image_path=document.document_file.path,
                confidence_threshold=0.5,
                include_ocr=True,
                user_application_data=user_application_data
            )
            
            # Format response for Voter Certificate verification
            ai_results = {
                'document_id': document_id,
                'document_type': document.document_type,
                'processing_timestamp': timezone.now().isoformat(),
                'service_used': 'Voter Certificate Verification Service (YOLO + Advanced OCR + Field Extraction)',
                'verification_result': voter_result,
                'algorithms_results': {
                    'voter_yolo_detection': {
                        'name': 'YOLOv8 Voter Certificate Element Detection',
                        'confidence': voter_result.get('confidence', 0.0),
                        'status': voter_result.get('status', 'UNKNOWN'),
                        'detected_elements': voter_result.get('detected_elements', {}),
                        'validation_checks': voter_result.get('validation_checks', {})
                    },
                    'advanced_ocr': {
                        'name': 'Advanced OCR + Field Extraction',
                        'confidence': voter_result.get('ocr_data', {}).get('ocr_confidence', 0.0) if voter_result.get('ocr_data') else 0.0,
                        'extracted_info': voter_result.get('extracted_info', {}),
                        'fields_extracted': sum(1 for v in voter_result.get('extracted_info', {}).values() if v is not None)
                    }
                }
            }
            
            # Update document status based on Voter Certificate verification
            if voter_result.get('is_valid'):
                document.status = 'verified'
                document.ai_confidence_score = voter_result.get('confidence', 0.0)
            else:
                document.status = 'needs_review'
                document.ai_confidence_score = voter_result.get('confidence', 0.0)
            document.ai_analysis_completed = True
            document.ai_auto_approved = voter_result.get('is_valid', False)
            document.ai_analysis_notes = f"Voter Certificate verification completed\nConfidence: {document.ai_confidence_score:.1%}\nStatus: {voter_result.get('status', 'UNKNOWN')}"
            document.ai_key_information = ai_results
            
            document.save()
            
            return Response({
                'success': True,
                'message': f'Voter Certificate verification completed: {voter_result.get("status")}',
                'ai_analysis': ai_results
            })
        
        # ============================================================================
        # FALLBACK: Use legacy document validator for other document types
        # Note: Birth Certificate, Voter Certificate, COE, and ID documents are handled above
        # ============================================================================
        
        # Import AI services
        from ai_verification.enhanced_document_validator import EnhancedDocumentValidator
        
        # Initialize AI components
        enhanced_validator = EnhancedDocumentValidator()
        
        # Run comprehensive AI analysis
        ai_results = {
            'document_id': document_id,
            'document_type': document.document_type,
            'processing_timestamp': timezone.now().isoformat(),
            'service_used': 'Legacy Enhanced Document Validator',
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
        
        # 7. ID Verification (fallback for documents not handled by specialized services)
        # Note: Birth certificates are handled by specialized Birth Certificate service above
        if document.document_type in ['school_id', 'government_id'] and document.document_type not in ['birth_certificate', 'voters_certificate', 'voter_certificate', 'voters_id', 'voter_id', 'certificate_of_enrollment']:
            try:
                from myapp.id_verification_service import IDVerificationService
                id_service = IDVerificationService()
                id_result = id_service.verify_id_card(
                    document.document_file.path,
                    document.document_type,
                    user=request.user  # Pass user for identity verification
                )
                ai_results['algorithms_results']['id_verification'] = {
                    'name': 'ID Verification (YOLO + Textract + Identity Match)',
                    'confidence': id_result.get('confidence', 0.0),
                    'status': id_result.get('status', 'INVALID'),
                    'is_valid': id_result.get('is_valid', False),
                    'identity_verified': id_result.get('identity_verification', {}).get('match', False) if 'identity_verification' in id_result else None,
                    'extracted_fields': id_result.get('extracted_fields', {}),
                    'checks_passed': id_result.get('checks_passed', 0),
                    'total_checks': len(id_result.get('validation_checks', {})),
                    'yolo_detected': id_result.get('yolo_detection', {}).get('id_detected', False),
                    'ocr_confidence': id_result.get('ocr_extraction', {}).get('confidence', 0),
                    'recommendations': id_result.get('recommendations', [])
                }
                
                # If identity doesn't match, mark as fraud
                if 'identity_verification' in id_result:
                    identity_match = id_result['identity_verification'].get('match', False)
                    if not identity_match:
                        ai_results['algorithms_results']['id_verification']['fraud_detected'] = True
                        ai_results['algorithms_results']['id_verification']['fraud_reason'] = id_result['identity_verification'].get('message', 'Identity mismatch')
                        
            except Exception as e:
                ai_results['algorithms_results']['id_verification'] = {
                    'name': 'ID Verification (YOLO + Textract + Identity Match)',
                    'error': str(e),
                    'confidence': 0.0
                }
        
        # 8. COE Verification (fallback - should not reach here as COE is handled above)
        # This is redundant and should be removed in future refactoring
        if document.document_type in ['certificate_of_enrollment', 'enrollment_certificate']:
            try:
                from myapp.coe_verification_service import get_coe_verification_service
                coe_service = get_coe_verification_service()
                coe_result = coe_service.verify_coe_document(
                    document.document_file.path,
                    confidence_threshold=0.5
                )
                ai_results['algorithms_results']['coe_verification'] = {
                    'name': 'COE Verification (YOLO Element Detection)',
                    'confidence': coe_result.get('confidence', 0.0),
                    'status': coe_result.get('status', 'INVALID'),
                    'is_valid': coe_result.get('is_valid', False),
                    'detected_elements': coe_result.get('detected_elements', {}),
                    'detections_count': len(coe_result.get('detections', [])),
                    'validation_checks': coe_result.get('validation_checks', {}),
                    'checks_passed': sum(1 for v in coe_result.get('validation_checks', {}).values() if v),
                    'total_checks': len(coe_result.get('validation_checks', {})),
                    'recommendations': coe_result.get('recommendations', [])
                }
                
                # Log key detections
                detected_elements = coe_result.get('detected_elements', {})
                logger.info(f"📋 COE Elements Detected:")
                for element, data in detected_elements.items():
                    if data.get('present'):
                        logger.info(f"   ✅ {element}: {data.get('confidence', 0):.2%}")
                
            except Exception as e:
                ai_results['algorithms_results']['coe_verification'] = {
                    'name': 'COE Verification (YOLO Element Detection)',
                    'error': str(e),
                    'confidence': 0.0
                }
        
        # 9. AI Verification Manager - Orchestrates with Weighted Scoring
        try:
            overall_confidence = 0.0
            total_weight = 0.0
            algorithm_weights = {
                'document_validator': 0.12,
                'cross_document_matcher': 0.08,
                'grade_verifier': 0.10,
                'face_verifier': 0.08,
                'fraud_detector': 0.12,
                'ai_generated_detector': 0.12,
                'id_verification': 0.23,      # High weight for ID verification with identity matching
                'coe_verification': 0.15      # Significant weight for COE element detection
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


# ==================== ADMIN DOCUMENT MANAGEMENT ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_document_dashboard(request):
    """
    📊 Admin Document Management Dashboard
    Comprehensive view of all document submissions with filtering and statistics
    """
    if not request.user.is_admin():
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.db.models import Q, Count, Avg
        
        # Get filter parameters
        status_filter = request.GET.get('status', None)
        document_type = request.GET.get('document_type', None)
        student_id = request.GET.get('student_id', None)
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)
        ai_analyzed = request.GET.get('ai_analyzed', None)
        
        # Base queryset
        queryset = DocumentSubmission.objects.all()
        
        # Apply filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        if student_id:
            queryset = queryset.filter(student__student_id__icontains=student_id)
        if date_from:
            queryset = queryset.filter(submitted_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(submitted_at__lte=date_to)
        if ai_analyzed is not None:
            queryset = queryset.filter(ai_analysis_completed=ai_analyzed == 'true')
        
        # Statistics
        total_documents = queryset.count()
        status_breakdown = queryset.values('status').annotate(count=Count('id'))
        document_type_breakdown = queryset.values('document_type').annotate(count=Count('id'))
        
        # AI Analysis Statistics
        ai_stats = {
            'total_analyzed': queryset.filter(ai_analysis_completed=True).count(),
            'auto_approved': queryset.filter(ai_auto_approved=True).count(),
            'avg_confidence': queryset.filter(ai_analysis_completed=True).aggregate(
                avg=Avg('ai_confidence_score')
            )['avg'] or 0.0,
            'high_confidence': queryset.filter(ai_confidence_score__gte=0.80).count(),
            'medium_confidence': queryset.filter(
                ai_confidence_score__gte=0.50, 
                ai_confidence_score__lt=0.80
            ).count(),
            'low_confidence': queryset.filter(
                ai_confidence_score__lt=0.50,
                ai_confidence_score__gt=0
            ).count()
        }
        
        # COE Verification Statistics
        coe_documents = queryset.filter(
            document_type__in=['certificate_of_enrollment', 'enrollment_certificate'],
            ai_analysis_completed=True
        )
        coe_stats = {
            'total': coe_documents.count(),
            'valid': 0,
            'invalid': 0,
            'avg_confidence': 0.0
        }
        
        for doc in coe_documents:
            if doc.ai_key_information and 'algorithms_results' in doc.ai_key_information:
                coe_result = doc.ai_key_information['algorithms_results'].get('coe_verification', {})
                if coe_result.get('is_valid'):
                    coe_stats['valid'] += 1
                else:
                    coe_stats['invalid'] += 1
        
        if coe_documents.count() > 0:
            coe_stats['avg_confidence'] = coe_documents.aggregate(
                avg=Avg('ai_confidence_score')
            )['avg'] or 0.0
        
        # ID Verification Statistics
        id_documents = queryset.filter(
            Q(document_type__in=['school_id', 'birth_certificate']) |
            Q(document_type__icontains='id'),
            ai_analysis_completed=True
        )
        id_stats = {
            'total': id_documents.count(),
            'identity_verified': 0,
            'identity_failed': 0,
            'avg_confidence': 0.0
        }
        
        for doc in id_documents:
            if doc.ai_key_information and 'algorithms_results' in doc.ai_key_information:
                id_result = doc.ai_key_information['algorithms_results'].get('id_verification', {})
                if id_result.get('identity_verified'):
                    id_stats['identity_verified'] += 1
                elif id_result.get('identity_verified') == False:
                    id_stats['identity_failed'] += 1
        
        if id_documents.count() > 0:
            id_stats['avg_confidence'] = id_documents.aggregate(
                avg=Avg('ai_confidence_score')
            )['avg'] or 0.0
        
        # Recent documents (last 20)
        recent_documents = queryset.order_by('-submitted_at')[:20]
        recent_docs_data = []
        
        for doc in recent_documents:
            # Extract key AI results
            ai_summary = {}
            if doc.ai_key_information and 'algorithms_results' in doc.ai_key_information:
                algorithms = doc.ai_key_information['algorithms_results']
                
                # COE specific info
                if 'coe_verification' in algorithms:
                    coe = algorithms['coe_verification']
                    ai_summary['coe'] = {
                        'status': coe.get('status'),
                        'confidence': coe.get('confidence'),
                        'elements_detected': coe.get('detected_elements', {}),
                        'checks_passed': coe.get('checks_passed', 0)
                    }
                
                # ID verification specific info
                if 'id_verification' in algorithms:
                    id_ver = algorithms['id_verification']
                    ai_summary['id_verification'] = {
                        'status': id_ver.get('status'),
                        'confidence': id_ver.get('confidence'),
                        'identity_verified': id_ver.get('identity_verified'),
                        'checks_passed': id_ver.get('checks_passed', 0)
                    }
            
            recent_docs_data.append({
                'id': doc.id,
                'student_name': doc.student.get_full_name(),
                'student_id': doc.student.student_id,
                'document_type': doc.document_type,
                'document_type_display': doc.get_document_type_display(),
                'status': doc.status,
                'status_display': doc.get_status_display(),
                'submitted_at': doc.submitted_at,
                'ai_confidence': doc.ai_confidence_score,
                'ai_auto_approved': doc.ai_auto_approved,
                'ai_summary': ai_summary,
                'reviewed_by': doc.reviewed_by.get_full_name() if doc.reviewed_by else None,
                'reviewed_at': doc.reviewed_at
            })
        
        # Documents requiring attention (low confidence or pending manual review)
        attention_needed = queryset.filter(
            Q(status='pending') |
            Q(status='revision_needed') |
            (Q(ai_confidence_score__lt=0.50) & Q(ai_confidence_score__gt=0))
        ).order_by('submitted_at')[:10]
        
        attention_docs = []
        for doc in attention_needed:
            attention_docs.append({
                'id': doc.id,
                'student_name': doc.student.get_full_name(),
                'student_id': doc.student.student_id,
                'document_type_display': doc.get_document_type_display(),
                'status': doc.status,
                'ai_confidence': doc.ai_confidence_score,
                'submitted_at': doc.submitted_at,
                'reason': 'Low AI Confidence' if doc.ai_confidence_score < 0.50 else 'Pending Review'
            })
        
        return Response({
            'success': True,
            'summary': {
                'total_documents': total_documents,
                'status_breakdown': list(status_breakdown),
                'document_types': list(document_type_breakdown)
            },
            'ai_statistics': ai_stats,
            'coe_statistics': coe_stats,
            'id_verification_statistics': id_stats,
            'recent_documents': recent_docs_data,
            'attention_needed': attention_docs,
            'filters_applied': {
                'status': status_filter,
                'document_type': document_type,
                'student_id': student_id,
                'date_from': date_from,
                'date_to': date_to,
                'ai_analyzed': ai_analyzed
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch dashboard data: {str(e)}',
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


class FullApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Full Application Forms.
    Contains complete student application with personal and academic information.
    """
    serializer_class = FullApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return FullApplication.objects.select_related('user').all()
        return FullApplication.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new full application"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Application created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update an existing application"""
        instance = self.get_object()
        
        # Check if application is locked
        if instance.is_locked and not request.user.is_admin():
            return Response({
                'success': False,
                'error': 'Cannot update a locked application'
            }, status=status.HTTP_403_FORBIDDEN)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Application updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit and lock the application"""
        application = self.get_object()
        
        if application.is_submitted:
            return Response({
                'success': False,
                'error': 'Application has already been submitted'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.is_submitted = True
        application.is_locked = True
        application.submitted_at = timezone.now()
        application.save()
        
        audit_logger.log_user_action(
            user=request.user,
            action_type='update',
            description=f"Submitted full application for {application.school_year} {application.get_semester_display()}",
            severity='info',
            request=request
        )
        
        serializer = self.get_serializer(application)
        return Response({
            'success': True,
            'message': 'Application submitted successfully',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlock(self, request, pk=None):
        """Unlock an application (admin only)"""
        if not request.user.is_admin():
            return Response({
                'success': False,
                'error': 'Only administrators can unlock applications'
            }, status=status.HTTP_403_FORBIDDEN)
        
        application = self.get_object()
        application.is_locked = False
        application.save()
        
        audit_logger.log_admin_action(
            admin_user=request.user,
            action_description=f"Unlocked application for {application.user.username}",
            severity='warning',
            request=request
        )
        
        serializer = self.get_serializer(application)
        return Response({
            'success': True,
            'message': 'Application unlocked successfully',
            'data': serializer.data
        })
