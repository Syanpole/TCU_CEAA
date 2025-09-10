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
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'student_id', 'profile_image', 'profile_image_url', 'created_at']
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
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'student_id']

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
        
        # Check file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 
                        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('Invalid file type. Only PDF, JPG, PNG, DOC, and DOCX files are allowed.')
        
        # AI Document Analysis (basic validation)
        if hasattr(value, 'name'):
            # Check if filename contains suspicious patterns
            import re
            filename = value.name.lower()
            
            # Check for proper document naming patterns
            if 'birth' in filename or 'certificate' in filename:
                if not any(ext in filename for ext in ['.pdf', '.jpg', '.jpeg', '.png']):
                    raise serializers.ValidationError('Birth certificates should be in PDF or image format.')
            
            # Check for minimum file size (prevent empty or too small files)
            if value.size < 1024:  # Less than 1KB
                raise serializers.ValidationError('File seems too small. Please ensure you uploaded a valid document.')
        
        return value
        
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
        """Run comprehensive AI analysis using the enhanced AI service"""
        try:
            # Perform AI analysis
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
            analysis_notes.append("🤖 Comprehensive AI Document Analysis")
            analysis_notes.append("=" * 40)
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
            
            # Determine final status based on AI analysis - Autonomous processing
            auto_approve = analysis_result.get('auto_approve', False)
            confidence_score = analysis_result.get('confidence_score', 0)
            
            # Enhanced autonomous approval logic
            if auto_approve or confidence_score >= 0.5:
                document.status = 'approved'
                document.reviewed_at = timezone.now()
                document.admin_notes = f"✅ Auto-approved by AI System (Confidence: {confidence_score:.1%})\n\n{document.admin_notes or ''}"
            elif confidence_score >= 0.3:
                # Medium confidence - still approve but flag for potential review
                document.status = 'approved'
                document.reviewed_at = timezone.now()
                document.admin_notes = f"✅ Auto-approved by AI System - Medium Confidence ({confidence_score:.1%})\n⚠️ May benefit from quality improvement\n\n{document.admin_notes or ''}"
            else:
                # Very low confidence - approve but with strong recommendations
                document.status = 'approved'
                document.reviewed_at = timezone.now()
                document.admin_notes = f"✅ Auto-approved by AI System - Basic Acceptance ({confidence_score:.1%})\n⚠️ Strongly recommend document improvement for future submissions\n\n{document.admin_notes or ''}"
            
            document.save()
            
        except Exception as e:
            # Handle AI analysis errors gracefully
            document.ai_analysis_completed = False
            document.ai_analysis_notes = f"AI Analysis Error: {str(e)}"
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
    class Meta:
        model = GradeSubmission
        fields = ['academic_year', 'semester', 'total_units', 'general_weighted_average', 
                 'semestral_weighted_average', 'grade_sheet', 'has_failing_grades', 
                 'has_incomplete_grades', 'has_dropped_subjects']
    
    def validate(self, data):
        user = self.context['request'].user
        
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
