from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Task, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication
from .ai_service import document_analyzer, grade_analyzer
import json

class UserSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'middle_initial', 'student_id', 'profile_image', 'profile_image_url', 'created_at']
        read_only_fields = ['id', 'created_at', 'profile_image_url']
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
        
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
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
    
    class Meta:
        model = DocumentSubmission
        fields = ['id', 'document_type', 'document_type_display', 'document_file', 'description', 
                 'status', 'status_display', 'admin_notes', 'submitted_at', 'reviewed_at', 
                 'student_name', 'student_id', 'reviewed_by_name', 'ai_analysis_completed',
                 'ai_confidence_score', 'ai_document_type_match', 'ai_recommendations',
                 'ai_auto_approved', 'ai_analysis_notes']
        read_only_fields = ['id', 'status', 'admin_notes', 'submitted_at', 'reviewed_at', 'reviewed_by',
                          'ai_analysis_completed', 'ai_confidence_score', 'ai_document_type_match',
                          'ai_recommendations', 'ai_auto_approved', 'ai_analysis_notes']

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
            import logging
            logger = logging.getLogger(__name__)
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
        
    def create(self, validated_data):
        # Move the uploaded file to document_file field
        file_data = validated_data.pop('file')
        validated_data['document_file'] = file_data
        validated_data['student'] = self.context['request'].user
        
        # Create the document submission
        document = super().create(validated_data)
        
        # Set status to AI processing
        document.status = 'ai_processing'
        document.save()
        
        # Run comprehensive AI analysis
        self.run_comprehensive_ai_analysis(document)
        
        return document
    
    def run_comprehensive_ai_analysis(self, document):
        """Run LIGHTNING-FAST AI document verification with strict type validation"""
        try:
            # Import the lightning-fast verification system for instant processing
            from ai_verification.lightning_verifier import lightning_verifier
            
            # Use lightning-fast verifier with strict validation (< 0.5 seconds)
            verification_result = lightning_verifier.lightning_verify(document, document.document_file)
            
            # Process results and update document immediately
            self._process_lightning_fast_results(document, verification_result)
            
            # Check if document was rejected
            if document.status == 'rejected':
                rejection_reason = verification_result.get('rejection_reason', 'Document verification failed')
                
                # Delete the rejected document from database
                document.delete()
                
                # Raise validation error to inform user
                raise serializers.ValidationError({
                    'document_file': rejection_reason
                })
            
            # Log the verification outcome
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"⚡ AI verification completed for document {document.id} in {verification_result.get('processing_time', 0):.3f}s. "
                f"Status: {document.status}, "
                f"Confidence: {verification_result.get('confidence_score', 0):.1%}"
            )
            
        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # For other errors, reject the document for security
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"⚡ AI verification error for document {document.id}: {str(e)}")
            
            # Delete the document and raise error
            try:
                document.delete()
            except:
                pass
            
            raise serializers.ValidationError({
                'document_file': 'Document verification failed. Please try uploading again or contact support.'
            })
    
    def _process_lightning_fast_results(self, document, verification_result):
        """Process lightning-fast verification results with strict document type validation"""
        from django.utils import timezone
        
        # Check if document is valid and type matches
        is_valid = verification_result.get('is_valid_document', False)
        type_matches = verification_result.get('document_type_match', False)
        rejection_reason = verification_result.get('rejection_reason', None)
        
        if is_valid and type_matches:
            # Approve the document
            document.status = 'approved'
            status_emoji = "✅ APPROVED"
            result_message = "Document successfully verified and approved!"
            document.ai_auto_approved = True
        else:
            # Reject the document with clear reason
            document.status = 'rejected'
            status_emoji = "❌ REJECTED"
            result_message = rejection_reason or "Document verification failed"
            document.ai_auto_approved = False
        
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
            
            notes.extend([
                f"🤖 AI Analysis Summary:",
                f"📋 Document Type: {document.get_document_type_display()}",
                f"✅ Document Type Match: Verified",
                f"✅ Format Validation: Passed",
                f"✅ Content Verification: {'Filename-based (OCR unavailable)' if fallback_mode and not ocr_available else 'Passed'}",
                "",
            ])
            
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
            if fraud_indicators:
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
        fields = ['id', 'academic_year', 'semester', 'semester_display', 'total_units', 
                 'general_weighted_average', 'semestral_weighted_average', 'grade_sheet',
                 'has_failing_grades', 'has_incomplete_grades', 'has_dropped_subjects',
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
        
        # Run comprehensive AI evaluation
        self.run_comprehensive_ai_grade_analysis(grade_submission)
        
        return grade_submission
    
    def run_comprehensive_ai_grade_analysis(self, grade_submission):
        """Run comprehensive AI analysis on grade submission - Autonomous processing"""
        try:
            # Perform AI analysis
            analysis_result = grade_analyzer.analyze_grades(grade_submission)
            
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
            
        except Exception as e:
            # Handle AI analysis errors gracefully - still approve with notes
            grade_submission.ai_evaluation_completed = False
            grade_submission.ai_evaluation_notes = f"AI Analysis encountered an error but submission is processed: {str(e)}"
            grade_submission.status = 'approved'  # Still approve even with AI errors
            grade_submission.reviewed_at = timezone.now()
            grade_submission.admin_notes = f"✅ Auto-approved - AI analysis had technical issues but submission is accepted\n\nTechnical note: {str(e)}"
            grade_submission.save()

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

class AllowanceApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowanceApplication
        fields = ['grade_submission', 'application_type']
        
    def validate(self, data):
        grade_submission = data['grade_submission']
        application_type = data['application_type']
        
        # Check if student owns the grade submission
        if grade_submission.student != self.context['request'].user:
            raise serializers.ValidationError('You can only apply for allowance based on your own grades.')
        
        # Check if grade submission is approved
        if grade_submission.status != 'approved':
            raise serializers.ValidationError('Grade submission must be approved before applying for allowance.')
        
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
        return super().create(validated_data)
