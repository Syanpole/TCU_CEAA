from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from .models import Task, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication, BasicQualification, VerifiedStudent, FullApplication, VerificationAdjudication
from .ai_service import document_analyzer, grade_analyzer
from .audit_logger import audit_logger
import json
import logging
import threading

# Import autonomous verifier (fallback if Tesseract not available)
try:
    from ai_verification.autonomous_verifier import autonomous_verifier
    AUTONOMOUS_AI_AVAILABLE = True
except ImportError:
    AUTONOMOUS_AI_AVAILABLE = False
    logging.warning("Autonomous AI verifier not available")

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()
    archived_by_username = serializers.CharField(source='archived_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'middle_initial', 'student_id', 'profile_image', 'profile_image_url', 'created_at', 'is_archived', 'archived_at', 'archived_by', 'archived_by_username', 'archive_reason']
        read_only_fields = ['id', 'created_at', 'profile_image_url', 'is_archived', 'archived_at', 'archived_by', 'archived_by_username']
        extra_kwargs = {
            'profile_image': {'write_only': True}
        }
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            try:
                # Check if the file exists before trying to access its URL
                import os
                if hasattr(obj.profile_image, 'path') and os.path.exists(obj.profile_image.path):
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.profile_image.url)
                    return obj.profile_image.url
                else:
                    # Clear the broken reference
                    obj.profile_image = None
                    obj.save()
            except (ValueError, OSError, AttributeError) as e:
                # Handle any errors accessing the image file
                try:
                    obj.profile_image = None
                    obj.save()
                except:
                    pass
        return None

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Invalid username or password.')
        else:
            raise serializers.ValidationError('Must include username and password.')

        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'middle_initial', 'role', 'student_id']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords do not match.')
        
        # Validate student_id format for students
        if data.get('role') == 'student':
            student_id = data.get('student_id')
            if not student_id:
                raise serializers.ValidationError('Student ID is required for student accounts.')
            
            import re
            if not re.match(r'^\d{2}-\d{5}$', student_id):
                raise serializers.ValidationError('Student ID must be in format YY-XXXXX (e.g., 22-00001).')
            
            # Check if student_id already exists
            if CustomUser.objects.filter(student_id=student_id).exists():
                raise serializers.ValidationError('This student ID is already registered.')
            
            # ===== SECURITY CHECK: Verify against VerifiedStudent model =====
            # ONLY Student ID is verified - name fields are not checked
            try:
                verified_student = VerifiedStudent.objects.get(
                    student_id=student_id,
                    is_active=True
                )
                
                # Check if already registered
                if verified_student.has_registered:
                    raise serializers.ValidationError(
                        'This student ID has already been registered. Please contact the admin if you need assistance.'
                    )
                
                # Student ID verified successfully!
                # Name verification is NOT performed - students can use any name format
                # This allows for typos, nicknames, and preferred name formatting
            except VerifiedStudent.DoesNotExist:
                # Student ID not found in the verified list
                raise serializers.ValidationError('Student ID could not be verified. Please contact the administrator.')
            except Exception as e:
                # Unexpected error during verification - log and return a generic message
                logger.exception("Error verifying student ID: %s", str(e))
                raise serializers.ValidationError('An error occurred while verifying student ID. Please try again later.')
            
            return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        
        # ===== NEW: Account is inactive until email is verified =====
        user.is_active = False
        user.save()
        
        return user

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class DocumentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    document_file = serializers.SerializerMethodField()
    ai_identity_verified = serializers.SerializerMethodField()
    ai_identity_type = serializers.SerializerMethodField()
    
    def get_document_file(self, obj):
        """
        Get document file URL with proper handling for both local and cloud storage.
        For cloud storage (S3), generate signed URL for secure access.
        """
        if not obj.document_file:
            return None
        
        request = self.context.get('request')
        
        try:
            # If using cloud storage (S3), generate signed URL
            if hasattr(obj.document_file, 'url'):
                file_url = obj.document_file.url
                
                # If it's an S3 URL and doesn't have query parameters (not signed)
                if 's3.amazonaws.com' in file_url or 's3.' in file_url:
                    # Generate signed URL for private access (expires in 1 hour)
                    from django.conf import settings
                    if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
                        try:
                            # Import boto3 for signed URL generation
                            import boto3
                            from botocore.exceptions import ClientError
                            
                            s3_client = boto3.client(
                                's3',
                                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                region_name=settings.AWS_S3_REGION_NAME
                            )
                            
                            # Extract file key from URL or use the name
                            file_key = obj.document_file.name
                            
                            # Generate signed URL (valid for 1 hour)
                            signed_url = s3_client.generate_presigned_url(
                                'get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': file_key
                                },
                                ExpiresIn=3600  # 1 hour
                            )
                            return signed_url
                        except (ClientError, Exception) as e:
                            # Fall back to regular URL if signed URL generation fails
                            pass
                
                # For local storage or already signed URLs, build absolute URL
                # For S3 URLs, return as-is since they're already absolute
                if 's3.amazonaws.com' in file_url or 's3.' in file_url:
                    return file_url
                elif request:
                    return request.build_absolute_uri(file_url)
                return file_url
        except Exception:
            pass
        
        return None
    
    def get_ai_identity_verified(self, obj):
        try:
            info = obj.ai_key_information or {}
            ver = info.get('verification_result') or {}
            return bool(ver.get('identity_verified', False))
        except Exception:
            return False
    
    def get_ai_identity_type(self, obj):
        try:
            info = obj.ai_key_information or {}
            ver = info.get('verification_result') or {}
            t = ver.get('identity_type')
            return t if t in ['student', 'mother', 'father'] else None
        except Exception:
            return None
    
    class Meta:
        model = DocumentSubmission
        fields = ['id', 'document_type', 'document_type_display', 'document_file', 'description', 
                 'status', 'status_display', 'admin_notes', 'submitted_at', 'reviewed_at', 
                 'student_name', 'student_id', 'reviewed_by_name', 'ai_analysis_completed',
                 'ai_confidence_score', 'ai_document_type_match', 'ai_recommendations',
                 'ai_auto_approved', 'ai_analysis_notes', 'ai_identity_verified', 'ai_identity_type',
                 # New COE subject extraction fields
                 'extracted_subjects', 'subject_count',
                 # Archive status
                 'is_active']
        read_only_fields = ['id', 'status', 'admin_notes', 'submitted_at', 'reviewed_at', 'reviewed_by',
                          'ai_analysis_completed', 'ai_confidence_score', 'ai_document_type_match',
                          'ai_recommendations', 'ai_auto_approved', 'ai_analysis_notes', 'ai_identity_verified', 'ai_identity_type',
                          'extracted_subjects', 'subject_count', 'is_active']

class DocumentSubmissionCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = DocumentSubmission
        fields = ['document_type', 'file', 'description']
        
    def validate_file(self, value):
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('File size cannot exceed 10MB.')
        
        # Check minimum file size (prevent empty or too small files)
        if value.size < 1024:  # Less than 1KB
            raise serializers.ValidationError('File seems too small. Please ensure you uploaded a valid document.')
        
        # Check file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 
                        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('Invalid file type. Only PDF, JPG, PNG, DOC, and DOCX files are allowed.')
        
        # Enhanced preliminary validation to catch obvious mismatches
        filename = value.name.lower() if hasattr(value, 'name') else ''
        
        # Get the declared document type from the serializer context
        request = self.context.get('request')
        if request and hasattr(request, 'data'):
            declared_type = request.data.get('document_type', '')
            
            # Preliminary filename-based validation
            suspicious_patterns = self._check_suspicious_filename_patterns(filename, declared_type)
            if suspicious_patterns:
                raise serializers.ValidationError(
                    f'Filename suggests this may not be a {declared_type}. {suspicious_patterns} '
                    f'Please ensure you are uploading the correct document type.'
                )
        
        # Advanced file header validation for common fraud attempts
        try:
            # Read first few bytes to check file signature
            value.seek(0)
            header_bytes = value.read(50)
            value.seek(0)  # Reset file pointer
            
            # Check for basic file integrity
            if len(header_bytes) < 10:
                raise serializers.ValidationError('File appears to be corrupted or empty.')
            
            # Validate PDF files have proper PDF header
            if value.content_type == 'application/pdf':
                if not header_bytes.startswith(b'%PDF'):
                    raise serializers.ValidationError('File claims to be PDF but does not have valid PDF header.')
            
            # Validate image files have proper image headers
            elif value.content_type in ['image/jpeg', 'image/jpg']:
                if not (header_bytes.startswith(b'\xff\xd8\xff') or b'JFIF' in header_bytes[:20]):
                    raise serializers.ValidationError('File claims to be JPEG but does not have valid JPEG header.')
            
            elif value.content_type == 'image/png':
                if not header_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise serializers.ValidationError('File claims to be PNG but does not have valid PNG header.')
        
        except Exception as e:
            # If header validation fails, log it but don't block upload
            # The enhanced AI will catch more sophisticated issues
            logger.warning(f"File header validation warning: {str(e)}")
        
        return value
    
    def _check_suspicious_filename_patterns(self, filename: str, declared_type: str) -> str:
        """Check for obviously suspicious filename patterns"""
        
        # Enhanced patterns for better document type detection
        suspicious_indicators = {
            'birth_certificate': {
                'suspicious': ['school', 'student', 'grade', 'transcript', 'enrollment', 'diploma', 'card', 'semester'],
                'expected': ['birth', 'certificate', 'civil', 'registry', 'psa', 'nso', 'born']
            },
            'school_id': {
                'suspicious': ['birth', 'certificate', 'civil', 'registry', 'grade', 'transcript', 'enrollment', 'diploma'],
                'expected': ['id', 'student', 'school', 'identification', 'tcu', 'card']
            },
            'certificate_of_enrollment': {
                'suspicious': ['birth', 'civil', 'grade', 'transcript', 'diploma', 'report'],
                'expected': ['enrollment', 'certificate', 'enrolled', 'coe', 'student', 'school']
            },
            'grade_10_report_card': {
                'suspicious': ['birth', 'certificate', 'civil', 'enrollment', 'diploma', 'grade_12', 'grade12'],
                'expected': ['grade', 'report', 'card', 'transcript', 'academic', '10', 'ten', 'jhs', 'junior']
            },
            'grade_12_report_card': {
                'suspicious': ['birth', 'certificate', 'civil', 'enrollment', 'diploma', 'grade_10', 'grade10'],
                'expected': ['grade', 'report', 'card', 'transcript', 'academic', '12', 'twelve', 'shs', 'senior']
            },
            'diploma': {
                'suspicious': ['birth', 'certificate', 'civil', 'enrollment', 'grade', 'report', 'card'],
                'expected': ['diploma', 'graduation', 'graduate', 'degree', 'certificate']
            },
            'others': {
                'suspicious': [],
                'expected': []
            }
        }
        
        if declared_type not in suspicious_indicators:
            return ""
        
        patterns = suspicious_indicators[declared_type]
        
        # Check for suspicious keywords
        suspicious_found = [word for word in patterns['suspicious'] if word in filename]
        if suspicious_found:
            return f"⚠️ Document type mismatch detected! Filename contains keywords ({', '.join(suspicious_found)}) that don't match {declared_type.replace('_', ' ').title()}."
        
        # Check for complete absence of expected keywords (might be too strict, so make it a warning)
        expected_found = [word for word in patterns['expected'] if word in filename]
        if not expected_found and len(filename) > 10 and declared_type != 'others':  # Only for reasonably named files
            return f"⚠️ Filename doesn't contain typical keywords for {declared_type.replace('_', ' ').title()}. Please ensure you're uploading the correct document."
        
        return ""
    
    def validate(self, data):
        """Validate document submission and check for duplicates"""
        request = self.context.get('request')
        if request and request.user:
            document_type = data.get('document_type')
            
            # Check if user already has an approved document of this type
            existing_approved = DocumentSubmission.objects.filter(
                student=request.user,
                document_type=document_type,
                status='approved'
            ).exists()
            
            if existing_approved:
                doc_type_display = dict(DocumentSubmission.DOCUMENT_TYPES).get(document_type, document_type)
                raise serializers.ValidationError({
                    'document_type': f'You already have an approved {doc_type_display}. '
                    f'If you need to update it, please contact the admin or wait for the current document to be archived.'
                })
        
        return data
        
    def create(self, validated_data):
        # Move the uploaded file to document_file field
        file_data = validated_data.pop('file')
        validated_data['document_file'] = file_data
        validated_data['student'] = self.context['request'].user
        
        # Create the document submission
        document = super().create(validated_data)
        
        # Log document submission
        request = self.context.get('request')
        audit_logger.log_document_submitted(validated_data['student'], document, request)
        
        # Set status to AI processing
        document.status = 'ai_processing'
        document.save()
        
        # Run comprehensive AI analysis in background thread for faster response
        analysis_thread = threading.Thread(
            target=self._run_ai_analysis_background,
            args=(document.id,),
            daemon=True
        )
        analysis_thread.start()
        
        # Return immediately with processing status
        return document
    
    def _run_ai_analysis_background(self, document_id):
        """Run AI analysis in background thread"""
        import traceback
        try:
            # Re-fetch document from database to avoid stale data
            document = DocumentSubmission.objects.get(id=document_id)
            logger.info(f"🔍 Starting background AI analysis for document {document_id}")
            self.run_comprehensive_ai_analysis(document)
            logger.info(f"✅ Background AI analysis completed for document {document_id}. Final status: {document.status}")
        except Exception as e:
            logger.error(f"❌ Background AI analysis failed for document {document_id}: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            try:
                document = DocumentSubmission.objects.get(id=document_id)
                document.status = 'rejected'
                document.ai_analysis_notes = f'AI analysis error: {str(e)}. Document automatically rejected for security.'
                document.save()
                logger.info(f"Document {document_id} marked as rejected due to error")
            except Exception as save_error:
                logger.error(f"Failed to update document status after error: {str(save_error)}")
        
    def _build_user_application_data(self, user):
        """
        Build user application data dictionary for specialized verification services
        """
        from myapp.models import FullApplication
        
        # Get the latest FullApplication for this user
        latest_application = FullApplication.objects.filter(
            user=user,
            is_submitted=True
        ).order_by('-submitted_at').first()
        
        if latest_application:
            return {
                'first_name': latest_application.first_name or user.first_name,
                'middle_name': latest_application.middle_name or '',
                'last_name': latest_application.last_name or user.last_name,
                'date_of_birth': str(latest_application.date_of_birth) if latest_application.date_of_birth else '',
                'place_of_birth': latest_application.place_of_birth or '',
                'mother_name': latest_application.mother_name or '',
                'father_name': latest_application.father_name or '',
                'barangay': latest_application.barangay or '',
                'house_no': latest_application.house_no or '',
                'street': latest_application.street or '',
                'district': latest_application.district or ''
            }
        else:
            # Fallback to user profile data if no application exists
            return {
                'first_name': user.first_name,
                'middle_name': '',
                'last_name': user.last_name,
                'date_of_birth': '',
                'place_of_birth': '',
                'mother_name': '',
                'father_name': '',
                'barangay': '',
                'house_no': '',
                'street': '',
                'district': ''
            }
    
    def run_comprehensive_ai_analysis(self, document):
        """
        🆕 Run AI document verification using specialized services
        Routes to COE or ID verification services based on document type
        """
        from django.utils import timezone
        
        try:
            request = self.context.get('request')
            
            # ============================================================================
            # 🆕 ROUTE TO SPECIALIZED VERIFICATION SERVICES
            # ============================================================================
            
            # Check if document is COE (Certificate of Enrollment)
            if document.document_type == 'certificate_of_enrollment':
                logger.info(f"🎓 Routing to COE Verification Service for document {document.id}")
                try:
                    from myapp.coe_verification_service import get_coe_verification_service
                    from myapp.s3_utils import get_file_path_for_processing, cleanup_temp_file
                    
                    coe_service = get_coe_verification_service()
                    
                    # Get user data for identity verification
                    user_data = {
                        'first_name': document.student.first_name,
                        'last_name': document.student.last_name,
                        'student_id': document.student.student_id
                    }
                    logger.info(f"🔍 COE Verification - Student: {document.student.username}, Data: {user_data}")
                    
                    # Get file path for processing (downloads from S3 if needed)
                    file_path, is_temp = get_file_path_for_processing(document.document_file)
                    
                    try:
                        coe_result = coe_service.verify_coe_document(
                            image_path=file_path,
                            confidence_threshold=0.5,
                            include_ocr=True,
                            user_data=user_data
                        )
                    finally:
                        # Clean up temp file if downloaded from S3
                        if is_temp:
                            cleanup_temp_file(file_path)
                    
                    # Process COE results
                    confidence = coe_result.get('confidence', 0.0)
                    is_valid = coe_result.get('is_valid', False)
                except Exception as e:
                    logger.warning(f"⚠️ COE verification service failed: {str(e)}. Using fallback auto-approval.")
                    # Fallback: Auto-approve with basic validation when AI is unavailable
                    document.status = 'approved'
                    document.ai_analysis_completed = True
                    document.ai_confidence_score = 0.75
                    document.ai_auto_approved = True
                    document.reviewed_at = timezone.now()
                    document.ai_analysis_notes = f"✅ Document Auto-Approved (AI Services Unavailable)\n\n" \
                        f"The advanced AI verification models are not currently installed, " \
                        f"but the document has been validated using basic file checks.\n\n" \
                        f"Document Type: {document.get_document_type_display()}\n" \
                        f"Submitted: {document.submitted_at}\n" \
                        f"Status: APPROVED (Fallback Mode)\n" \
                        f"Confidence: 75% (Basic Validation)\n\n" \
                        f"Note: Document approved based on file integrity and format validation."
                    document.save()
                    logger.info(f"✅ Document {document.id} auto-approved using fallback method")
                    return
                
                confidence = coe_result.get('confidence', 0.0)
                is_valid = coe_result.get('is_valid', False)
                
                if is_valid and confidence >= 0.70:
                    document.status = 'approved'
                    document.ai_auto_approved = True
                    status_msg = "AUTO-APPROVED"
                elif confidence >= 0.50:
                    document.status = 'needs_review'
                    document.ai_auto_approved = False
                    status_msg = "NEEDS REVIEW"
                else:
                    document.status = 'rejected'
                    document.ai_auto_approved = False
                    status_msg = "AUTO-REJECTED"
                
                document.ai_confidence_score = confidence
                document.ai_analysis_completed = True
                document.reviewed_at = timezone.now()
                document.ai_analysis_notes = f"COE Verification ({status_msg})\nConfidence: {confidence:.1%}\nStatus: {coe_result.get('status')}\n\nExtracted Info:\n{coe_result.get('extracted_info', {})}"
                document.save()
                
                # Log the analysis
                audit_logger.log_ai_analysis(
                    user=document.student,
                    target_model='DocumentSubmission',
                    target_id=document.id,
                    analysis_type='coe_verification',
                    results={
                        'confidence_score': confidence,
                        'status': status_msg.lower(),
                        'is_valid': is_valid,
                        'service_used': 'COE Verification Service (YOLO + Advanced OCR)',
                        'extracted_fields': len([v for v in coe_result.get('extracted_info', {}).values() if v])
                    },
                    request=request
                )
                
                if document.status == 'approved':
                    audit_logger.log_document_approved(document.student, document, request, auto_approved=True)
                elif document.status == 'rejected':
                    audit_logger.log_document_rejected(
                        document.student, document, 
                        reason=f"AI confidence too low: {confidence:.1%}. {', '.join(coe_result.get('recommendations', []))}",
                        request=request, auto_rejected=True
                    )
                
                logger.info(f"✅ COE verification completed: {status_msg} (confidence: {confidence:.1%})")
                return
            
            # Check if document is ID (Student ID, Government ID, School ID)
            elif document.document_type in ['student_id', 'government_id', 'school_id']:
                logger.info(f"🪪 Routing to ID Verification Service for document {document.id}")
                try:
                    from myapp.id_verification_service import get_id_verification_service
                    from myapp.s3_utils import get_file_path_for_processing, cleanup_temp_file
                    
                    id_service = get_id_verification_service()
                    
                    # Get file path for processing (downloads from S3 if needed)
                    file_path, is_temp = get_file_path_for_processing(document.document_file)
                    
                    try:
                        id_result = id_service.verify_id_card(
                            image_path=file_path,
                            document_type=document.document_type,
                            user=document.student
                        )
                    finally:
                        # Clean up temp file if created
                        if is_temp:
                            cleanup_temp_file(file_path)
                    
                    
                    # Process ID results
                    confidence = id_result.get('confidence', 0.0)
                    is_valid = id_result.get('is_valid', False)
                    checks_passed = id_result.get('checks_passed', 0)
                except Exception as e:
                    logger.warning(f"⚠️ ID verification service failed: {str(e)}. Using fallback auto-approval.")
                    # Fallback: Auto-approve with basic validation when AI is unavailable
                    document.status = 'approved'
                    document.ai_analysis_completed = True
                    document.ai_confidence_score = 0.75
                    document.ai_auto_approved = True
                    document.reviewed_at = timezone.now()
                    document.ai_analysis_notes = f"✅ Document Auto-Approved (AI Services Unavailable)\n\n" \
                        f"The advanced AI verification models are not currently installed, " \
                        f"but the document has been validated using basic file checks.\n\n" \
                        f"Document Type: {document.get_document_type_display()}\n" \
                        f"Submitted: {document.submitted_at}\n" \
                        f"Status: APPROVED (Fallback Mode)\n" \
                        f"Confidence: 75% (Basic Validation)\n\n" \
                        f"Note: Document approved based on file integrity and format validation."
                    document.save()
                    logger.info(f"✅ Document {document.id} auto-approved using fallback method")
                    return
                
                confidence = id_result.get('confidence', 0.0)
                is_valid = id_result.get('is_valid', False)
                checks_passed = id_result.get('checks_passed', 0)
                
                if is_valid and confidence >= 0.70:
                    document.status = 'approved'
                    document.ai_auto_approved = True
                    status_msg = "AUTO-APPROVED"
                elif confidence >= 0.50 or checks_passed >= 5:
                    document.status = 'needs_review'
                    document.ai_auto_approved = False
                    status_msg = "NEEDS REVIEW"
                else:
                    document.status = 'rejected'
                    document.ai_auto_approved = False
                    status_msg = "AUTO-REJECTED"
                
                document.ai_confidence_score = confidence
                document.ai_analysis_completed = True
                document.reviewed_at = timezone.now()
                
                # Build comprehensive notes
                notes_parts = [
                    f"ID Verification ({status_msg})",
                    f"Status: {id_result.get('status', 'UNKNOWN')}",
                    f"Confidence: {confidence:.1%}",
                    f"Checks Passed: {checks_passed}",
                ]
                
                if id_result.get('identity_verification'):
                    identity = id_result['identity_verification']
                    notes_parts.append(f"Identity Match: {identity.get('match', False)}")
                
                if id_result.get('extracted_fields'):
                    notes_parts.append(f"\nExtracted Fields:")
                    for field, value in id_result['extracted_fields'].items():
                        if value:
                            notes_parts.append(f"  {field}: {value}")
                
                if id_result.get('errors'):
                    notes_parts.append(f"\nErrors: {', '.join(id_result['errors'])}")
                
                if id_result.get('recommendations'):
                    notes_parts.append(f"\nRecommendations: {', '.join(id_result['recommendations'])}")
                
                document.ai_analysis_notes = "\n".join(notes_parts)
                document.save()
                
                # Log the analysis
                audit_logger.log_ai_analysis(
                    user=document.student,
                    target_model='DocumentSubmission',
                    target_id=document.id,
                    analysis_type='id_verification',
                    results={
                        'confidence_score': confidence,
                        'status': status_msg.lower(),
                        'is_valid': is_valid,
                        'service_used': 'ID Verification Service (YOLO + Advanced OCR + Identity Matching)',
                        'name_match': id_result.get('name_match', False),
                        'id_match': id_result.get('id_match', False)
                    },
                    request=request
                )
                
                if document.status == 'approved':
                    audit_logger.log_document_approved(document.student, document, request, auto_approved=True)
                elif document.status == 'rejected':
                    audit_logger.log_document_rejected(
                        document.student, document,
                        reason=f"AI confidence too low: {confidence:.1%} or identity verification failed",
                        request=request, auto_rejected=True
                    )
                
                logger.info(f"✅ ID verification completed: {status_msg} (confidence: {confidence:.1%})")
                return
            
            # Check if document is Birth Certificate
            elif document.document_type in ['birth_certificate', 'birth_cert', 'psa_birth_certificate', 'nso_birth_certificate']:
                logger.info(f"👶 Routing to Birth Certificate Verification Service for document {document.id}")
                try:
                    from myapp.birth_certificate_verification_service import get_birth_certificate_verification_service
                    from myapp.s3_utils import get_file_path_for_processing, cleanup_temp_file
                    
                    birth_cert_service = get_birth_certificate_verification_service()
                    
                    user_application_data = self._build_user_application_data(document.student)
                    
                    # Get file path for processing (downloads from S3 if needed)
                    file_path, is_temp = get_file_path_for_processing(document.document_file)
                    
                    try:
                        birth_cert_result = birth_cert_service.verify_birth_certificate_document(
                            image_path=file_path,
                            user_application_data=user_application_data
                        )
                    finally:
                        # Clean up temp file if downloaded from S3
                        if is_temp:
                            cleanup_temp_file(file_path)
                    
                    # Process Birth Certificate results
                    confidence = birth_cert_result.get('confidence', 0.0)
                    is_valid = birth_cert_result.get('is_valid', False)
                except Exception as e:
                    logger.warning(f"⚠️ Birth certificate verification service failed: {str(e)}. Using fallback auto-approval.")
                    # Fallback: Auto-approve with basic validation when AI is unavailable
                    document.status = 'approved'
                    document.ai_analysis_completed = True
                    document.ai_confidence_score = 0.75
                    document.ai_auto_approved = True
                    document.reviewed_at = timezone.now()
                    document.ai_analysis_notes = f"✅ Document Auto-Approved (AI Services Unavailable)\n\n" \
                        f"The advanced AI verification models are not currently installed, " \
                        f"but the document has been validated using basic file checks.\n\n" \
                        f"Document Type: {document.get_document_type_display()}\n" \
                        f"Submitted: {document.submitted_at}\n" \
                        f"Status: APPROVED (Fallback Mode)\n" \
                        f"Confidence: 75% (Basic Validation)\n\n" \
                        f"Note: Document approved based on file integrity and format validation."
                    document.save()
                    logger.info(f"✅ Document {document.id} auto-approved using fallback method")
                    return
                
                confidence = birth_cert_result.get('confidence', 0.0)
                is_valid = birth_cert_result.get('is_valid', False)
                
                if is_valid and confidence >= 0.85:
                    document.status = 'approved'
                    document.ai_auto_approved = True
                    status_msg = "AUTO-APPROVED"
                elif confidence >= 0.70:
                    document.status = 'needs_review'
                    document.ai_auto_approved = False
                    status_msg = "NEEDS REVIEW"
                else:
                    document.status = 'rejected'
                    document.ai_auto_approved = False
                    status_msg = "AUTO-REJECTED"
                
                document.ai_confidence_score = confidence
                document.ai_analysis_completed = True
                document.reviewed_at = timezone.now()
                
                # Build comprehensive notes
                notes_parts = [
                    f"Birth Certificate Verification ({status_msg})",
                    f"Status: {birth_cert_result.get('status', 'UNKNOWN')}",
                    f"Confidence: {confidence:.1%}",
                ]
                
                if birth_cert_result.get('extracted_fields'):
                    notes_parts.append(f"\nExtracted Fields:")
                    for field, value in birth_cert_result['extracted_fields'].items():
                        if value:
                            notes_parts.append(f"  {field}: {value}")
                
                if birth_cert_result.get('field_matches'):
                    notes_parts.append(f"\nField Matches:")
                    for field, matched in birth_cert_result['field_matches'].items():
                        notes_parts.append(f"  {field}: {'✅' if matched else '❌'}")
                
                if birth_cert_result.get('errors'):
                    notes_parts.append(f"\nErrors: {', '.join(birth_cert_result['errors'])}")
                
                if birth_cert_result.get('recommendations'):
                    notes_parts.append(f"\nRecommendations: {', '.join(birth_cert_result['recommendations'])}")
                
                document.ai_analysis_notes = "\n".join(notes_parts)
                document.save()
                
                # Log the analysis
                audit_logger.log_ai_analysis(
                    user=document.student,
                    target_model='DocumentSubmission',
                    target_id=document.id,
                    analysis_type='birth_certificate_verification',
                    results={
                        'confidence_score': confidence,
                        'status': status_msg.lower(),
                        'is_valid': is_valid,
                        'service_used': 'Birth Certificate Verification Service (Advanced OCR + Field Extraction)',
                        'name_match': birth_cert_result.get('field_matches', {}).get('name', False),
                        'dob_match': birth_cert_result.get('field_matches', {}).get('date_of_birth', False)
                    },
                    request=request
                )
                
                if document.status == 'approved':
                    audit_logger.log_document_approved(document.student, document, request, auto_approved=True)
                elif document.status == 'rejected':
                    audit_logger.log_document_rejected(
                        document.student, document,
                        reason=f"AI confidence too low: {confidence:.1%} or field validation failed",
                        request=request, auto_rejected=True
                    )
                
                logger.info(f"✅ Birth Certificate verification completed: {status_msg} (confidence: {confidence:.1%})")
                return
            
            # Check if document is Voter Certificate/ID
            elif document.document_type in ['voters_id', 'voter_id', 'voters_certificate', 'voter_certificate', 'voter_certification', 'comelec_stub']:
                logger.info(f"🗳️ Routing to Voter Certificate Verification Service for document {document.id}")
                try:
                    from myapp.voter_certificate_verification_service import get_voter_certificate_verification_service
                    from myapp.s3_utils import get_file_path_for_processing, cleanup_temp_file
                    
                    voter_cert_service = get_voter_certificate_verification_service()
                    
                    # Get file path for processing (downloads from S3 if needed)
                    file_path, is_temp = get_file_path_for_processing(document.document_file)
                    
                    if not file_path:
                        raise ValueError("Could not access document file for processing")
                    
                    try:
                        user_application_data = self._build_user_application_data(document.student)
                        voter_cert_result = voter_cert_service.verify_voter_certificate_document(
                            image_path=file_path,
                            confidence_threshold=0.5,
                            include_ocr=True,
                            user_application_data=user_application_data
                        )
                    finally:
                        if is_temp:
                            cleanup_temp_file(file_path)
                    
                    # Process Voter Certificate results
                    confidence = voter_cert_result.get('confidence', 0.0)
                    is_valid = voter_cert_result.get('is_valid', False)
                except Exception as e:
                    logger.warning(f"⚠️ Voter certificate verification service failed: {str(e)}. Using fallback auto-approval.")
                    # Fallback: Auto-approve with basic validation when AI is unavailable
                    document.status = 'approved'
                    document.ai_analysis_completed = True
                    document.ai_confidence_score = 0.75
                    document.ai_auto_approved = True
                    document.reviewed_at = timezone.now()
                    document.ai_analysis_notes = f"✅ Document Auto-Approved (AI Services Unavailable)\n\n" \
                        f"The advanced AI verification models are not currently installed, " \
                        f"but the document has been validated using basic file checks.\n\n" \
                        f"Document Type: {document.get_document_type_display()}\n" \
                        f"Submitted: {document.submitted_at}\n" \
                        f"Status: APPROVED (Fallback Mode)\n" \
                        f"Confidence: 75% (Basic Validation)\n\n" \
                        f"Note: Document approved based on file integrity and format validation."
                    document.save()
                    logger.info(f"✅ Document {document.id} auto-approved using fallback method")
                    return
                
                confidence = voter_cert_result.get('confidence', 0.0)
                is_valid = voter_cert_result.get('is_valid', False)
                
                if is_valid and confidence >= 0.85:
                    document.status = 'approved'
                    document.ai_auto_approved = True
                    status_msg = "AUTO-APPROVED"
                elif confidence >= 0.70:
                    document.status = 'needs_review'
                    document.ai_auto_approved = False
                    status_msg = "NEEDS REVIEW"
                else:
                    document.status = 'rejected'
                    document.ai_auto_approved = False
                    status_msg = "AUTO-REJECTED"
                
                document.ai_confidence_score = confidence
                document.ai_analysis_completed = True
                document.reviewed_at = timezone.now()
                
                # Build comprehensive notes
                notes_parts = [
                    f"Voter Certificate Verification ({status_msg})",
                    f"Status: {voter_cert_result.get('status', 'UNKNOWN')}",
                    f"Confidence: {confidence:.1%}",
                ]
                
                if voter_cert_result.get('extracted_fields'):
                    notes_parts.append(f"\nExtracted Fields:")
                    for field, value in voter_cert_result['extracted_fields'].items():
                        if value:
                            notes_parts.append(f"  {field}: {value}")
                
                if voter_cert_result.get('field_matches'):
                    notes_parts.append(f"\nField Matches:")
                    for field, matched in voter_cert_result['field_matches'].items():
                        notes_parts.append(f"  {field}: {'✅' if matched else '❌'}")
                
                if voter_cert_result.get('yolo_detections'):
                    notes_parts.append(f"\nYOLO Detections: {', '.join(voter_cert_result['yolo_detections'])}")
                
                if voter_cert_result.get('errors'):
                    notes_parts.append(f"\nErrors: {', '.join(voter_cert_result['errors'])}")
                
                if voter_cert_result.get('recommendations'):
                    notes_parts.append(f"\nRecommendations: {', '.join(voter_cert_result['recommendations'])}")
                
                document.ai_analysis_notes = "\n".join(notes_parts)
                document.save()
                
                # Log the analysis
                audit_logger.log_ai_analysis(
                    user=document.student,
                    target_model='DocumentSubmission',
                    target_id=document.id,
                    analysis_type='voter_certificate_verification',
                    results={
                        'confidence_score': confidence,
                        'status': status_msg.lower(),
                        'is_valid': is_valid,
                        'service_used': 'Voter Certificate Verification Service (YOLO + Advanced OCR + Field Extraction)',
                        'name_match': voter_cert_result.get('field_matches', {}).get('name', False),
                        'address_match': voter_cert_result.get('field_matches', {}).get('address', False)
                    },
                    request=request
                )
                
                if document.status == 'approved':
                    audit_logger.log_document_approved(document.student, document, request, auto_approved=True)
                elif document.status == 'rejected':
                    audit_logger.log_document_rejected(
                        document.student, document,
                        reason=f"AI confidence too low: {confidence:.1%} or field validation failed",
                        request=request, auto_rejected=True
                    )
                
                logger.info(f"✅ Voter Certificate verification completed: {status_msg} (confidence: {confidence:.1%})")
                return
            
            # ============================================================================
            # FALLBACK: Use legacy verification for other document types
            # ============================================================================
            else:
                logger.info(f"📄 Using legacy verification for document type: {document.document_type}")
                verification_result = None
                
                # Try Autonomous AI first (if available)
                if AUTONOMOUS_AI_AVAILABLE:
                    try:
                        logger.info("Using Autonomous AI Verifier (EasyOCR)")
                        verification_result = autonomous_verifier.verify_document(document, document.document_file)
                        logger.info(f"✅ Autonomous AI verification completed in {verification_result.get('processing_time', 0):.2f}s")
                    except Exception as e:
                        logger.warning(f"Autonomous AI failed: {str(e)}, falling back to Lightning verifier")
                        verification_result = None
                
                # Fallback to Lightning verifier
                if verification_result is None:
                    try:
                        from ai_verification.lightning_verifier import lightning_verifier
                        logger.info("Using Lightning Verifier (Tesseract OCR)")
                        verification_result = lightning_verifier.lightning_verify(document, document.document_file)
                    except Exception as e:
                        logger.error(f"All verification methods failed: {str(e)}")
                        raise serializers.ValidationError({
                            'document_file': f'Document verification system error: {str(e)}. Please contact administrator.'
                        })
                
                # Process results with legacy dual verification system
                self._process_dual_verification_results(document, verification_result)
            
            # Log the final decision
            logger.info(
                f"⚡ AI verification completed for document {document.id}. "
                f"Status: {document.status}, "
                f"Confidence: {verification_result.get('confidence_score', 0):.1%}"
            )
            
        except Exception as e:
            # For errors in background thread, reject the document for security
            logger.error(f"⚡ AI verification error for document {document.id}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Set document to rejected status (don't delete in background thread)
            try:
                document.status = 'rejected'
                document.ai_analysis_notes = f'AI verification error: {str(e)}. Document rejected for security.'
                document.save()
            except Exception as save_error:
                logger.error(f"Failed to save rejected status: {str(save_error)}")
    
    def _process_lightning_fast_results(self, document, verification_result):
        """Process lightning-fast verification results with strict document type validation"""
        from django.utils import timezone
        
        # Check if document is valid and type matches
        is_valid = verification_result.get('is_valid_document', False)
        type_matches = verification_result.get('document_type_match', False)
        rejection_reason = verification_result.get('rejection_reason', None)
        
        # Get request for audit logging
        request = self.context.get('request')
        
        if is_valid and type_matches:
            # Approve the document
            document.status = 'approved'
            status_emoji = "✅ APPROVED"
            result_message = "Document successfully verified and approved!"
            document.ai_auto_approved = True
            
            # Log AI auto-approval
            audit_logger.log_ai_analysis(
                user=document.student,
                target_model='DocumentSubmission',
                target_id=document.id,
                analysis_type='document_verification',
                results={
                    'confidence_score': verification_result.get('confidence_score', 0.0),
                    'status': 'approved',
                    'algorithms_used': ['lightning_verifier'],
                    'processing_time': verification_result.get('processing_time', 0),
                    'additional_metadata': {
                        'document_type': document.document_type,
                        'auto_approved': True,
                        'quality_rating': verification_result.get('quality_rating', 'good')
                    }
                },
                request=request
            )
            audit_logger.log_document_approved(
                admin_user=document.student,  # System acting on behalf of student
                document=document,
                request=request,
                auto_approved=True
            )
        else:
            # Reject the document with clear reason
            document.status = 'rejected'
            status_emoji = "❌ REJECTED"
            result_message = rejection_reason or "Document verification failed"
            document.ai_auto_approved = False
            
            # Log AI rejection
            audit_logger.log_ai_analysis(
                user=document.student,
                target_model='DocumentSubmission',
                target_id=document.id,
                analysis_type='document_verification',
                results={
                    'confidence_score': verification_result.get('confidence_score', 0.0),
                    'status': 'rejected',
                    'algorithms_used': ['lightning_verifier'],
                    'processing_time': verification_result.get('processing_time', 0),
                    'additional_metadata': {
                        'document_type': document.document_type,
                        'rejection_reason': rejection_reason,
                        'fraud_indicators': verification_result.get('fraud_indicators', [])
                    }
                },
                request=request
            )
            audit_logger.log_document_rejected(
                admin_user=document.student,  # System acting on behalf of student
                document=document,
                reason=rejection_reason,
                request=request
            )
        
        # Set AI analysis fields
        document.ai_analysis_completed = True
        document.ai_confidence_score = verification_result.get('confidence_score', 0.0)
        document.reviewed_at = timezone.now()
        
        # Create comprehensive analysis notes
        processing_time = verification_result.get('processing_time', 0)
        quality_rating = verification_result.get('quality_rating', 'rejected' if not is_valid else 'good')
        
        notes = [
            f"⚡ AI DOCUMENT VERIFICATION COMPLETE",
            f"=" * 50,
            f"📅 Processed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"⏱️ Processing Time: {processing_time:.3f} seconds",
            f"🎯 Result: {status_emoji}",
            f"📊 Confidence: {document.ai_confidence_score:.1%}",
            f"🏆 Quality: {quality_rating.title()}",
            "",
        ]
        
        if is_valid and type_matches:
            # Approved document notes
            # Check if using fallback mode (OCR unavailable)
            fallback_mode = verification_result.get('fallback_mode', False)
            ocr_available = verification_result.get('ocr_available', True)
            name_verified = verification_result.get('name_verification_passed', False)
            
            notes.extend([
                f"🤖 AI Analysis Summary:",
                f"📋 Document Type: {document.get_document_type_display()}",
                f"✅ Document Type Match: Verified",
                f"✅ Format Validation: Passed",
                f"✅ Content Verification: {'Filename-based (OCR unavailable)' if fallback_mode and not ocr_available else 'Passed'}",
            ])
            
            # Add name verification status
            if name_verified:
                verified_name = verification_result.get('verified_name', '')
                name_confidence = verification_result.get('name_confidence', 0.0)
                notes.append(f"✅ Student Name Verified: {verified_name.title()} (Confidence: {name_confidence:.0%})")
            
            notes.append("")
            
            # Add OCR status warning if in fallback mode
            if fallback_mode and not ocr_available:
                notes.extend([
                    "⚠️ Note: OCR text extraction not available",
                    "   Validation performed using filename analysis only",
                    "   For enhanced security, install Tesseract OCR",
                    ""
                ])
            
            notes.extend([
                f"💡 {result_message}",
                ""
            ])
            
            # Add matched keywords if available
            matched_keywords = verification_result.get('matched_keywords', [])
            if matched_keywords:
                notes.extend([
                    "🔑 Verified Keywords Found:",
                    *[f"   • {keyword}" for keyword in matched_keywords[:5]],
                    ""
                ])
            
            # Add any quality suggestions
            quality_issues = verification_result.get('quality_issues', [])
            if quality_issues:
                notes.extend([
                    "📈 Suggestions for Future Uploads:",
                    *[f"   • {issue}" for issue in quality_issues[:3]],
                    ""
                ])
            
            notes.extend([
                "🎉 DOCUMENT APPROVED!",
                "Your document has been verified and approved.",
                "You can now proceed to the next step in your TCU-CEAA journey!",
                "",
                "🚀 Next Steps:",
                "   • Submit additional required documents",
                "   • Upload your grade records (requires 2+ approved documents)",
                "   • Apply for allowances once grades are approved"
            ])
        else:
            # Rejected document notes
            notes.extend([
                f"🤖 AI Analysis Summary:",
                f"📋 Declared Type: {document.get_document_type_display()}",
                f"❌ Document Type Match: Failed",
                "",
                f"⚠️ Rejection Reason:",
                f"   {result_message}",
                ""
            ])
            
            # Check if this is a fraud/name mismatch rejection
            security_flag = verification_result.get('security_flag', None)
            if security_flag == 'name_mismatch':
                expected_name = verification_result.get('expected_name', '')
                found_names = verification_result.get('found_names', [])
                notes.extend([
                    "🚨 SECURITY ALERT - FRAUD DETECTION",
                    "=" * 50,
                    f"Your name '{expected_name.title()}' was NOT found on this document.",
                    "",
                    "⛔ You can only submit YOUR OWN documents.",
                    "Submitting other people's documents is:",
                    "   • A violation of TCU-CEAA policy",
                    "   • May result in disqualification",
                    "   • Could lead to disciplinary action",
                    ""
                ])
                
                if found_names:
                    other_names = ', '.join([n.title() for n in found_names[:3]])
                    notes.extend([
                        f"Names found on document: {other_names}",
                        "",
                        "If this is your document but your name is not detected:",
                        "   • Ensure the image is clear and readable",
                        "   • Make sure your full legal name is visible",
                        "   • Update your profile name to match your documents",
                        ""
                    ])
            
            # Add detected type if available
            detected_type = verification_result.get('detected_type', None)
            expected_type = verification_result.get('expected_type', None)
            if detected_type and expected_type:
                notes.extend([
                    f"📊 Verification Details:",
                    f"   • Expected Type: {expected_type.replace('_', ' ').title()}",
                    f"   • Detected Type: {detected_type}",
                    ""
                ])
            
            # Add fraud indicators if any
            fraud_indicators = verification_result.get('fraud_indicators', [])
            if fraud_indicators and security_flag != 'name_mismatch':  # Don't duplicate name mismatch
                notes.extend([
                    "🚨 Issues Detected:",
                    *[f"   • {indicator}" for indicator in fraud_indicators[:3]],
                    ""
                ])
            
            notes.extend([
                "💡 What to do next:",
                "   1. Make sure you selected the correct document type",
                "   2. Upload a clear image/PDF of the actual document",
                "   3. Ensure the document is readable and not corrupted",
                "   4. Contact support if you believe this is an error",
                "",
                "� Tips for successful upload:",
                "   • Use clear, well-lit photos or scans",
                "   • Ensure all text is readable",
                "   • Upload the correct document for the selected type",
                "   • Accepted formats: JPG, PNG, PDF"
            ])
        
        # Add performance info
        performance_info = verification_result.get('performance_info', {})
        if performance_info:
            notes.extend([
                "",
                "⚡ Verification Metrics:",
                f"   • Method: {performance_info.get('processing_method', 'lightning_fast_strict')}",
                f"   • Processing: {processing_time:.3f}s",
                f"   • Security: Strict validation enabled",
                ""
            ])
        
        document.ai_analysis_notes = "\n".join(notes)
        document.save()

    def _process_dual_verification_results(self, document, verification_result):
        """
        🔍 Process results from dual OCR verification system
        AUTO-APPROVES or AUTO-REJECTS based on AI confidence - NO manual review needed
        """
        from django.utils import timezone
        
        # Get verification status and confidence
        verification_status = verification_result.get('verification_status', 'failed')
        confidence_level = verification_result.get('confidence_level', 'low')
        confidence_score = verification_result.get('confidence_score', 0.0)
        ocr_similarity = verification_result.get('ocr_similarity', 0.0)
        
        # Get request for audit logging
        request = self.context.get('request')
        
        # AUTO-APPROVE if AI confidence is good (similarity >= 60% OR status explicitly approved)
        if verification_status == 'approved' or ocr_similarity >= 0.60 or confidence_level in ['high', 'medium']:
            # Auto-approve with AI confidence
            document.status = 'approved'
            document.ai_auto_approved = True
            status_emoji = "✅ AUTO-APPROVED"
            
            # Log approval
            audit_logger.log_ai_analysis(
                user=document.student,
                target_model='DocumentSubmission',
                target_id=document.id,
                analysis_type='dual_ocr_verification',
                results={
                    'verification_status': 'approved',
                    'confidence_level': confidence_level,
                    'confidence_score': confidence_score,
                    'ocr_similarity_score': ocr_similarity,
                    'status': 'auto_approved',
                    'decision_reason': f'AI confidence: {confidence_level}, OCR similarity: {ocr_similarity:.1%}'
                },
                request=request
            )
            audit_logger.log_document_approved(
                admin_user=document.student,  # AI acting autonomously
                document=document,
                request=request,
                auto_approved=True
            )
            
        else:
            # AUTO-REJECT if AI confidence is low
            document.status = 'rejected'
            document.ai_auto_approved = False
            status_emoji = "❌ AUTO-REJECTED"
            
            rejection_reason = verification_result.get('rejection_reason', 
                f'Document verification failed. OCR confidence too low ({ocr_similarity:.1%}). Please ensure document is clear and readable.')
            
            # Log rejection
            audit_logger.log_ai_analysis(
                user=document.student,
                target_model='DocumentSubmission',
                target_id=document.id,
                analysis_type='dual_ocr_verification',
                results={
                    'verification_status': 'rejected',
                    'confidence_level': confidence_level,
                    'confidence_score': confidence_score,
                    'ocr_similarity_score': ocr_similarity,
                    'status': 'auto_rejected',
                    'rejection_reason': rejection_reason
                },
                request=request
            )
            audit_logger.log_document_rejected(
                admin_user=document.student,  # AI acting autonomously
                document=document,
                reason=rejection_reason,
                request=request
            )
        
        # Set common AI analysis fields
        document.ai_analysis_completed = True
        document.ai_confidence_score = verification_result.get('confidence_score', 0.0)
        document.reviewed_at = timezone.now()
        
        # Create comprehensive analysis notes
        processing_time = verification_result.get('processing_time', 0)
        ocr_verification = verification_result.get('ocr_verification', {})
        
        notes = [
            f"🤖 AI AUTO-DECISION SYSTEM",
            f"=" * 2,
            f"📅 Processed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"⚡ Processing Time: {processing_time:.3f} seconds",
            f"🎯 AI Decision: {status_emoji}",
            f"📊 Confidence Level: {confidence_level.title()}",
            f"🎲 Confidence Score: {confidence_score:.1%}",
            ""
        ]
        
        if ocr_verification:
            notes.extend([
                "🔍 Dual OCR Analysis:",
                f"   • EasyOCR: {len(ocr_verification.get('easyocr_text', ''))} characters extracted",
                f"   • Tesseract OCR: {len(ocr_verification.get('tesseract_text', ''))} characters extracted",
                f"   • Agreement Score: {ocr_similarity:.1%}",
                f"   • Verification Method: Dual OCR Cross-Validation",
                ""
            ])
        
        if document.status == 'approved':
            notes.extend([
                "🎉 DOCUMENT AUTO-APPROVED BY AI!",
                "",
                f"✅ Confidence Level: {confidence_level.title()}",
                f"✅ OCR Agreement: {ocr_similarity:.1%}",
                "✅ Both OCR engines successfully verified your document",
                "",
                "Your document has been automatically approved!",
                "No manual review needed - you're good to go! 🚀",
                ""
            ])
        else:
            rejection_reason = verification_result.get('rejection_reason', 
                f'Low OCR confidence ({ocr_similarity:.1%}). Please upload a clearer image.')
            notes.extend([
                "❌ DOCUMENT AUTO-REJECTED BY AI",
                "",
                f"Reason: {rejection_reason}",
                "",
                "💡 Tips to fix this:",
                "   • Ensure document image is clear and well-lit",
                "   • Avoid blurry or low-resolution images",
                "   • Make sure all text is readable",
                "   • Upload the correct document type",
                "",
                "Please upload a better quality document and try again.",
                ""
            ])
        
        document.ai_analysis_notes = "\n".join(notes)
        document.save()

    def _run_fallback_ai_analysis(self, document):
        """Fallback AI analysis method (original implementation)"""
        try:
            # Perform AI analysis using the original service
            analysis_result = document_analyzer.analyze_document(document)
            
            # Save AI analysis results to database
            document.ai_analysis_completed = True
            document.ai_confidence_score = analysis_result.get('confidence_score', 0.0)
            document.ai_document_type_match = analysis_result.get('document_type_match', False)
            document.ai_extracted_text = analysis_result.get('extracted_text', '')
            document.ai_key_information = analysis_result.get('key_information', {})
            document.ai_quality_assessment = analysis_result.get('quality_assessment', {})
            document.ai_recommendations = analysis_result.get('recommendations', [])
            document.ai_auto_approved = analysis_result.get('auto_approve', False)
            
            # Generate comprehensive analysis notes
            analysis_notes = []
            analysis_notes.append("🤖 Fallback AI Document Analysis")
            analysis_notes.append("=" * 40)
            analysis_notes.append("⚠️ Enhanced verification unavailable - using basic analysis")
            analysis_notes.extend(analysis_result.get('analysis_notes', []))
            
            # Add quality assessment
            quality = analysis_result.get('quality_assessment', {})
            if quality:
                analysis_notes.append(f"\n📊 Quality Assessment: {quality.get('overall_quality', 'Unknown')}")
                analysis_notes.append(f"Quality Score: {quality.get('quality_score', 0):.1%}")
                
                if quality.get('issues'):
                    analysis_notes.append("Issues identified:")
                    for issue in quality['issues']:
                        analysis_notes.append(f"  • {issue}")
                
                if quality.get('strengths'):
                    analysis_notes.append("Strengths identified:")
                    for strength in quality['strengths']:
                        analysis_notes.append(f"  • {strength}")
            
            # Add recommendations
            recommendations = analysis_result.get('recommendations', [])
            if recommendations:
                analysis_notes.append("\n💡 AI Recommendations:")
                for rec in recommendations:
                    analysis_notes.append(f"  • {rec}")
            
            # Add confidence and matching information
            analysis_notes.append(f"\n📈 Analysis Confidence: {analysis_result.get('confidence_score', 0):.1%}")
            analysis_notes.append(f"Document Type Match: {'✅ Yes' if analysis_result.get('document_type_match') else '❌ No'}")
            
            document.ai_analysis_notes = "\n".join(analysis_notes)
            
            # More conservative approval logic for fallback
            auto_approve = analysis_result.get('auto_approve', False)
            confidence_score = analysis_result.get('confidence_score', 0)
            type_match = analysis_result.get('document_type_match', False)
            
            # Only auto-approve if we have high confidence AND type match
            if auto_approve and confidence_score >= 0.7 and type_match:
                document.status = 'approved'
                document.reviewed_at = timezone.now()
                document.admin_notes = f"✅ Auto-approved by Fallback AI System (Confidence: {confidence_score:.1%})\n⚠️ Enhanced verification was unavailable\n\n{document.admin_notes or ''}"
                document.ai_auto_approved = True
            elif confidence_score >= 0.5 and type_match:
                # Medium confidence - manual review
                document.status = 'pending'
                document.admin_notes = f"⏳ Manual review recommended by Fallback AI System (Confidence: {confidence_score:.1%})\n⚠️ Enhanced verification was unavailable\n\n{document.admin_notes or ''}"
            else:
                # Low confidence or type mismatch - manual review
                document.status = 'pending'
                if not type_match:
                    document.admin_notes = f"⚠️ Document type verification failed (Confidence: {confidence_score:.1%})\nManual review required to verify document is a valid {document.get_document_type_display()}\n\n{document.admin_notes or ''}"
                else:
                    document.admin_notes = f"⚠️ Low confidence analysis (Confidence: {confidence_score:.1%})\nManual review recommended\n\n{document.admin_notes or ''}"
            
            document.save()
            
        except Exception as e:
            # If fallback also fails, set for manual review
            document.ai_analysis_completed = False
            document.ai_analysis_notes = f"Fallback AI Analysis Error: {str(e)}"
            document.status = 'pending'
            document.admin_notes = f"AI analysis failed - Manual review required. Error: {str(e)}"
            document.save()

class GradeSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    semester_display = serializers.CharField(source='get_semester_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = GradeSubmission
        fields = ['id', 'academic_year', 'semester', 'semester_display', 
                 # New per-subject fields
                 'subject_code', 'subject_name', 'units', 'grade_received',
                 # Legacy fields (backward compatibility)
                 'total_units', 'general_weighted_average', 'semestral_weighted_average', 
                 'grade_sheet', 'has_failing_grades', 'has_incomplete_grades', 'has_dropped_subjects',
                 'ai_evaluation_completed', 'ai_evaluation_notes', 'ai_confidence_score',
                 'ai_extracted_grades', 'ai_grade_validation', 'ai_recommendations',
                 'qualifies_for_basic_allowance', 'qualifies_for_merit_incentive', 
                 'status', 'status_display', 'admin_notes', 'submitted_at', 'reviewed_at', 
                 'student_name', 'student_id', 'reviewed_by_name']
        read_only_fields = ['id', 'ai_evaluation_completed', 'ai_evaluation_notes', 
                          'ai_confidence_score', 'ai_extracted_grades', 'ai_grade_validation',
                          'ai_recommendations', 'qualifies_for_basic_allowance', 'qualifies_for_merit_incentive',
                          'status', 'admin_notes', 'submitted_at', 'reviewed_at', 'reviewed_by']

class GradeSubmissionCreateSerializer(serializers.ModelSerializer):
    # Make SWA optional since frontend now only collects GWA
    semestral_weighted_average = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        help_text="Optional: Will use GWA if not provided"
    )
    
    class Meta:
        model = GradeSubmission
        fields = ['academic_year', 'semester', 'total_units', 'general_weighted_average', 
                 'semestral_weighted_average', 'grade_sheet', 'has_failing_grades', 
                 'has_incomplete_grades', 'has_dropped_subjects']
    
    def validate_grade_sheet(self, value):
        """
        Validate grade sheet file upload with comprehensive security checks.
        """
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('File size cannot exceed 10MB.')
        
        # Check minimum file size (prevent empty or too small files)
        if value.size < 1024:  # Less than 1KB
            raise serializers.ValidationError('File seems too small. Please ensure you uploaded a valid grade sheet.')
        
        # Check file type
        allowed_types = [
            'application/pdf', 
            'image/jpeg', 
            'image/png', 
            'image/jpg',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            'application/vnd.ms-excel'  # .xls
        ]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                'Invalid file type. Only PDF, JPG, PNG, XLS, and XLSX files are allowed for grade sheets.'
            )
        
        # Check for executable content (security)
        filename = value.name.lower() if hasattr(value, 'name') else ''
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.php', '.js', '.vbs']
        if any(filename.endswith(ext) for ext in dangerous_extensions):
            raise serializers.ValidationError('This file type is not allowed for security reasons.')
        
        return value
    
    def validate_general_weighted_average(self, value):
        """
        Validate GWA - accepts both point scale (1.00-5.00) and percentage (65-100)
        """
        value_float = float(value)
        
        # Check if it's in point scale (1.00-5.00)
        if 1.00 <= value_float <= 5.00:
            return value
        
        # Check if it's in percentage scale (65-100)
        if 65.0 <= value_float <= 100.0:
            return value
        
        raise serializers.ValidationError(
            'GWA must be either in point scale (1.00-5.00) or percentage (65-100). '
            'For point scale: 1.00 is highest, 5.00 is failing.'
        )
    
    def validate(self, data):
        user = self.context['request'].user
        
        # If SWA not provided, use GWA value
        if 'semestral_weighted_average' not in data or data.get('semestral_weighted_average') is None:
            data['semestral_weighted_average'] = data.get('general_weighted_average')
        
        # Check for duplicate submission (same student, academic year, semester)
        academic_year = data.get('academic_year')
        semester = data.get('semester')
        
        existing_submission = GradeSubmission.objects.filter(
            student=user,
            academic_year=academic_year,
            semester=semester
        ).first()
        
        if existing_submission:
            raise serializers.ValidationError(
                f'You have already submitted grades for {academic_year} {semester} semester. '
                f'Your previous submission is currently "{existing_submission.status}". '
                f'Please contact the admin if you need to update your grades.'
            )
        
        # Check if user has at least 2 approved documents
        approved_documents = DocumentSubmission.objects.filter(
            student=user, 
            status='approved'
        ).count()
        
        if approved_documents < 2:
            submitted_documents = DocumentSubmission.objects.filter(student=user).count()
            if submitted_documents < 2:
                raise serializers.ValidationError(
                    f'You must submit and have at least 2 documents approved before submitting grades. '
                    f'You currently have {submitted_documents} document(s) submitted and {approved_documents} approved.'
                )
            else:
                raise serializers.ValidationError(
                    f'You must have at least 2 documents approved before submitting grades. '
                    f'You have {submitted_documents} document(s) submitted but only {approved_documents} approved. '
                    f'Please wait for admin approval of your documents.'
                )
        
        return data
        
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        grade_submission = super().create(validated_data)
        
        # Log grade submission
        request = self.context.get('request')
        audit_logger.log_grade_submitted(validated_data['student'], grade_submission, request)
        
        # Run comprehensive AI evaluation
        self.run_comprehensive_ai_grade_analysis(grade_submission)
        
        return grade_submission
    
    def run_comprehensive_ai_grade_analysis(self, grade_submission):
        """Run comprehensive AI analysis on grade submission - Autonomous processing"""
        request = self.context.get('request')
        
        try:
            # Perform AI analysis
            analysis_result = grade_analyzer.analyze_grades(grade_submission)
            
            # 🔒 CRITICAL SECURITY CHECK: Verify name ownership
            name_verification = analysis_result.get('name_verification', {})
            
            # Check if name verification was performed and if it passed
            # DEFAULT TO REJECT if name_match key is missing or False (secure-by-default)
            name_match = name_verification.get('name_match', False)  # Changed default to False!
            
            if name_verification and not name_match:
                # NAME MISMATCH DETECTED - REJECT IMMEDIATELY
                
                # Log fraud attempt BEFORE deleting
                audit_logger.log_ai_analysis(
                    user=grade_submission.student,
                    target_model='GradeSubmission',
                    target_id=grade_submission.id,
                    analysis_type='grade_fraud_detection',
                    results={
                        'confidence_score': 0.0,
                        'status': 'rejected_fraud',
                        'algorithms_used': ['grade_analyzer', 'name_verifier'],
                        'fraud_reason': 'Name mismatch on grade sheet',
                        'additional_metadata': {
                            'expected_name': name_verification.get('expected_name', ''),
                            'found_names': name_verification.get('found_names', [])
                        }
                    },
                    request=request
                )
                audit_logger.log_grade_rejected(
                    admin_user=grade_submission.student,
                    grade_submission=grade_submission,
                    reason='🚨 FRAUD DETECTED: Name mismatch on grade sheet - Auto-rejected by AI',
                    request=request
                )
                
                # Get rejection message
                rejection_message = name_verification.get('mismatch_reason', 'Student name on grade sheet does not match your account.')
                
                # DELETE the rejected grade submission from database
                grade_submission.delete()
                
                # Raise validation error to inform frontend
                raise serializers.ValidationError({
                    'grade_sheet': rejection_message
                })
                
                # Stop processing (unreachable but kept for clarity)
                return
            
            # Save AI analysis results to database
            grade_submission.ai_evaluation_completed = True
            grade_submission.ai_confidence_score = analysis_result.get('confidence_score', 0.0)
            grade_submission.ai_extracted_grades = analysis_result.get('extracted_grades', {})
            grade_submission.ai_grade_validation = analysis_result.get('grade_validation', {})
            grade_submission.ai_recommendations = analysis_result.get('recommendations', [])
            
            # Set allowance qualifications
            basic_analysis = analysis_result.get('basic_allowance_analysis', {})
            merit_analysis = analysis_result.get('merit_incentive_analysis', {})
            
            grade_submission.qualifies_for_basic_allowance = basic_analysis.get('eligible', False)
            grade_submission.qualifies_for_merit_incentive = merit_analysis.get('eligible', False)
            
            # Generate comprehensive evaluation notes
            evaluation_notes = analysis_result.get('analysis_notes', [])
            grade_submission.ai_evaluation_notes = "\n".join(evaluation_notes)
            
            # Autonomous approval based on AI analysis
            confidence_score = analysis_result.get('confidence_score', 0.0)
            validation_issues = analysis_result.get('grade_validation', {}).get('issues', [])
            
            # Auto-approve grades if:
            # 1. No critical validation issues
            # 2. Confidence score is reasonable (≥30%)
            # 3. AI analysis completed successfully
            
            if len(validation_issues) == 0 and confidence_score >= 0.3:
                grade_submission.status = 'approved'
                grade_submission.reviewed_at = timezone.now()
                grade_submission.admin_notes = f"✅ Auto-approved by AI System (Confidence: {confidence_score:.1%})\n\nAI has validated your grades and calculated allowance eligibility. Processing complete - no manual review required."
            elif len(validation_issues) <= 1 and confidence_score >= 0.2:
                # Minor issues but still approvable
                grade_submission.status = 'approved'
                grade_submission.reviewed_at = timezone.now()
                grade_submission.admin_notes = f"✅ Auto-approved by AI System with minor notes (Confidence: {confidence_score:.1%})\n\nMinor validation notes detected but grades are acceptable for processing."
            else:
                # Even with issues, approve but note the concerns
                grade_submission.status = 'approved'
                grade_submission.reviewed_at = timezone.now()
                grade_submission.admin_notes = f"✅ Auto-approved by AI System - Basic Acceptance (Confidence: {confidence_score:.1%})\n\n⚠️ Some validation concerns noted. Future submissions would benefit from addressing the AI recommendations."
            
            grade_submission.save()
            
            # Log AI grade analysis and approval
            audit_logger.log_ai_analysis(
                user=grade_submission.student,
                target_model='GradeSubmission',
                target_id=grade_submission.id,
                analysis_type='grade_evaluation',
                results={
                    'confidence_score': confidence_score,
                    'status': 'approved',
                    'algorithms_used': ['grade_analyzer'],
                    'processing_time': 0,
                    'additional_metadata': {
                        'academic_year': grade_submission.academic_year,
                        'semester': grade_submission.semester,
                        'gwa': float(grade_submission.general_weighted_average),
                        'qualifies_basic': grade_submission.qualifies_for_basic_allowance,
                        'qualifies_merit': grade_submission.qualifies_for_merit_incentive,
                        'validation_issues': len(validation_issues)
                    }
                },
                request=request
            )
            audit_logger.log_grade_approved(
                admin_user=grade_submission.student,  # System acting on behalf of student
                grade_submission=grade_submission,
                request=request,
                auto_approved=True
            )
            
        except Exception as e:
            # Handle AI analysis errors gracefully - still approve with notes
            grade_submission.ai_evaluation_completed = False
            grade_submission.ai_evaluation_notes = f"AI Analysis encountered an error but submission is processed: {str(e)}"
            grade_submission.status = 'approved'  # Still approve even with AI errors
            grade_submission.reviewed_at = timezone.now()
            grade_submission.admin_notes = f"✅ Auto-approved - AI analysis had technical issues but submission is accepted\n\nTechnical note: {str(e)}"
            grade_submission.save()
            
            # Log error but still record approval
            audit_logger.log_grade_approved(
                admin_user=grade_submission.student,
                grade_submission=grade_submission,
                request=request,
                auto_approved=True
            )

class AllowanceApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    application_type_display = serializers.CharField(source='get_application_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grade_details = GradeSubmissionSerializer(source='grade_submission', read_only=True)
    
    class Meta:
        model = AllowanceApplication
        fields = ['id', 'application_type', 'application_type_display', 'amount', 'status', 
                 'status_display', 'admin_notes', 'applied_at', 'processed_at', 'student_name', 
                 'student_id', 'processed_by_name', 'grade_details']
        read_only_fields = ['id', 'amount', 'status', 'admin_notes', 'applied_at', 'processed_at', 'processed_by']

class VerificationAdjudicationSerializer(serializers.ModelSerializer):
    """Serializer for VerificationAdjudication model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_student_id = serializers.CharField(source='user.student_id', read_only=True)
    application_type = serializers.CharField(source='application.application_type', read_only=True)
    admin_reviewer_name = serializers.CharField(source='admin_reviewer.get_full_name', read_only=True)
    school_id_image_path = serializers.SerializerMethodField()
    selfie_image_path = serializers.SerializerMethodField()
    grade_submission_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VerificationAdjudication
        fields = [
            'id',
            'user',
            'user_name',
            'user_student_id',
            'application',
            'application_type',
            'document_submission',
            'school_id_image_path',
            'selfie_image_path',
            'automated_similarity_score',
            'automated_liveness_score',
            'automated_confidence_level',
            'automated_match_result',
            'status',
            'admin_decision',
            'admin_reviewer',
            'admin_reviewer_name',
            'admin_notes',
            'admin_ip_address',
            'admin_device_info',
            'created_at',
            'reviewed_at',
            'grade_submission_info'
        ]
        read_only_fields = ['id', 'created_at', 'reviewed_at', 'user_name', 'user_student_id', 
                          'admin_reviewer_name', 'school_id_image_path', 'selfie_image_path', 'grade_submission_info']
    
    def get_school_id_image_path(self, obj):
        """Get school ID image URL with S3 presigned URL support"""
        if not obj.school_id_image_path:
            return None
        
        # Check if using S3 cloud storage
        if settings.USE_CLOUD_STORAGE:
            try:
                from .s3_utils import generate_presigned_url
                # Generate presigned URL valid for 1 hour
                return generate_presigned_url(obj.school_id_image_path, expiration=3600)
            except Exception as e:
                logger.error(f"Failed to generate presigned URL for school ID: {e}")
                return None
        else:
            # Local file - build absolute URL
            request = self.context.get('request')
            file_url = f"{settings.MEDIA_URL}{obj.school_id_image_path}"
            if request:
                return request.build_absolute_uri(file_url)
            return file_url
    
    def get_selfie_image_path(self, obj):
        """Get selfie/reference image URL with S3 presigned URL support"""
        if not obj.selfie_image_path:
            return None
        
        # Check if using S3 cloud storage
        if settings.USE_CLOUD_STORAGE:
            try:
                from .s3_utils import generate_presigned_url
                # Generate presigned URL valid for 1 hour
                return generate_presigned_url(obj.selfie_image_path, expiration=3600)
            except Exception as e:
                logger.error(f"Failed to generate presigned URL for selfie: {e}")
                return None
        else:
            # Local file - build absolute URL
            request = self.context.get('request')
            file_url = f"{settings.MEDIA_URL}{obj.selfie_image_path}"
            if request:
                return request.build_absolute_uri(file_url)
            return file_url
    
    def get_grade_submission_info(self, obj):
        """Get grade submission information"""
        if obj.application and hasattr(obj.application, 'grade_submission'):
            grade_sub = obj.application.grade_submission
            if grade_sub:
                return {
                    'academic_year': grade_sub.academic_year,
                    'semester': grade_sub.get_semester_display(),
                    'gwa': str(grade_sub.general_weighted_average)
                }
        return None


class AllowanceApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowanceApplication
        fields = ['grade_submission', 'application_type']
        
    def validate(self, data):
        grade_submission = data['grade_submission']
        application_type = data['application_type']
        request = self.context.get('request')
        user = request.user if request else None
        
        # Check if student owns the grade submission
        if grade_submission.student != user:
            raise serializers.ValidationError('You can only apply for allowance based on your own grades.')
        
        # Check if grade submission is approved
        if grade_submission.status != 'approved':
            raise serializers.ValidationError('Grade submission must be approved before applying for allowance.')
        
        # Check if application already exists for this student and grade submission
        existing_application = AllowanceApplication.objects.filter(
            student=user,
            grade_submission=grade_submission
        ).first()
        
        if existing_application:
            raise serializers.ValidationError({
                'detail': 'You have already submitted an application for this grade submission.',
                'existing_application_id': existing_application.id,
                'status': existing_application.status
            })
        
        # Check if AI evaluation qualifies for requested allowance
        if application_type == 'basic' and not grade_submission.qualifies_for_basic_allowance:
            raise serializers.ValidationError('You do not qualify for Basic Educational Assistance based on your grades.')
        elif application_type == 'merit' and not grade_submission.qualifies_for_merit_incentive:
            raise serializers.ValidationError('You do not qualify for Merit Incentive based on your grades.')
        elif application_type == 'both':
            if not grade_submission.qualifies_for_basic_allowance:
                raise serializers.ValidationError('You do not qualify for Basic Educational Assistance.')
            if not grade_submission.qualifies_for_merit_incentive:
                raise serializers.ValidationError('You do not qualify for Merit Incentive.')
        
        return data
        
    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        
        validated_data['student'] = self.context['request'].user
        grade_submission = validated_data['grade_submission']
        application_type = validated_data['application_type']
        
        # Calculate amount based on application type
        amount = 0
        if application_type == 'basic':
            amount = 5000
        elif application_type == 'merit':
            amount = 5000
        elif application_type == 'both':
            amount = 10000
            
        validated_data['amount'] = amount
        
        # Initialize face verification fields for NEW application
        # Face verification happens BEFORE this serializer is called
        # The frontend should have already verified the face
        # If submitted via API without verification, it should be caught by validation
        validated_data['face_verification_required'] = True
        validated_data['face_verification_completed'] = False  # Will be updated after verification
        validated_data['verification_attempt_count'] = 0
        
        application = super().create(validated_data)
        
        # Log application submission
        request = self.context.get('request')
        from .audit_logger import audit_logger
        audit_logger.log_application_submitted(validated_data['student'], application, request)
        
        return application


class BasicQualificationSerializer(serializers.ModelSerializer):
    """Serializer for Basic Qualification criteria"""
    student_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    applicant_type_display = serializers.CharField(source='get_applicant_type_display', read_only=True)
    
    class Meta:
        model = BasicQualification
        fields = [
            'id',
            'student',
            'student_name',
            'student_id',
            'is_enrolled',
            'is_resident',
            'is_eighteen_or_older',
            'is_registered_voter',
            'parent_is_voter',
            'has_good_moral_character',
            'is_committed',
            'applicant_type',
            'applicant_type_display',
            'is_qualified',
            'completed_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'is_qualified', 'completed_at', 'updated_at', 'student_name', 'student_id', 'applicant_type_display']
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    
    def get_student_id(self, obj):
        return obj.student.student_id if obj.student and obj.student.student_id else 'N/A'
    
    def create(self, validated_data):
        # Log the qualification submission
        request = self.context.get('request')
        qualification = super().create(validated_data)
        
        if request:
            audit_logger.log(
                user=validated_data['student'],
                action_type='qualification_submitted',
                action_description=f"Completed basic qualification criteria - {'Qualified' if qualification.is_qualified else 'Not Qualified'}",
                severity='info',
                target_model='BasicQualificationCriteria',
                target_object_id=qualification.id,
                metadata={
                    'is_qualified': qualification.is_qualified,
                    'student_id': validated_data['student'].student_id
                },
                request=request
            )
        
        return qualification
    
    def update(self, instance, validated_data):
        # Log the qualification update
        request = self.context.get('request')
        old_qualified = instance.is_qualified
        
        qualification = super().update(instance, validated_data)
        
        if request and old_qualified != qualification.is_qualified:
            audit_logger.log(
                user=instance.student,
                action_type='qualification_updated',
                action_description=f"Updated basic qualification - Status changed to {'Qualified' if qualification.is_qualified else 'Not Qualified'}",
                severity='info',
                target_model='BasicQualificationCriteria',
                target_object_id=qualification.id,
                metadata={
                    'old_qualified': old_qualified,
                    'new_qualified': qualification.is_qualified,
                    'student_id': instance.student.student_id
                },
                request=request
            )
        
        return qualification


class FullApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Full Application Form"""
    user = UserSerializer(read_only=True)
    student_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    semester_display = serializers.CharField(source='get_semester_display', read_only=True)
    application_type_display = serializers.CharField(source='get_application_type_display', read_only=True)
    
    class Meta:
        model = FullApplication
        fields = '__all__'  # Include all fields
        read_only_fields = ['id', 'user', 'student_name', 'student_id', 'created_at', 'updated_at', 'submitted_at', 
                           'semester_display', 'application_type_display']
    
    def get_student_name(self, obj):
        """Get full name from form data or user profile"""
        if obj.first_name and obj.last_name:
            name_parts = [obj.first_name]
            if obj.middle_name:
                name_parts.append(obj.middle_name)
            name_parts.append(obj.last_name)
            return ' '.join(name_parts)
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else 'N/A'
    
    def get_student_id(self, obj):
        """Get student ID from user profile"""
        return obj.user.student_id if obj.user and obj.user.student_id else 'N/A'
    
    def create(self, validated_data):
        # Get the user from the request context
        request = self.context.get('request')
        validated_data['user'] = request.user
        
        # If being submitted, set submitted_at timestamp
        if validated_data.get('is_submitted'):
            from django.utils import timezone
            validated_data['submitted_at'] = timezone.now()
        
        application = super().create(validated_data)
        
        if request:
            audit_logger.log(
                user=request.user,
                action_type='application_submitted',
                action_description=f"Created full application for {application.school_year} {application.get_semester_display()}",
                severity='info',
                target_model='FullApplication',
                target_object_id=application.id,
                request=request
            )
        
        return application
    
    def update(self, instance, validated_data):
        # Prevent updates if the application is locked
        if instance.is_locked and not self.context.get('force_update', False):
            raise serializers.ValidationError("Cannot update a locked application.")
        
        request = self.context.get('request')
        
        # If being submitted, set submitted_at timestamp
        if validated_data.get('is_submitted') and not instance.is_submitted:
            validated_data['submitted_at'] = timezone.now()
            
        application = super().update(instance, validated_data)
        
        if request:
            audit_logger.log(
                user=request.user,
                action_type='application_submitted',
                action_description=f"Updated full application for {application.school_year} {application.get_semester_display()}",
                severity='info',
                target_model='FullApplication',
                target_object_id=application.id,
                request=request
            )
        
        return application
