from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Task, CustomUser, DocumentSubmission, GradeSubmission, AllowanceApplication

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
                 'student_name', 'student_id', 'reviewed_by_name']
        read_only_fields = ['id', 'status', 'admin_notes', 'submitted_at', 'reviewed_at', 'reviewed_by']

class DocumentSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSubmission
        fields = ['document_type', 'document_file', 'description']
        
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

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
                 'ai_evaluation_completed', 'ai_evaluation_notes', 'qualifies_for_basic_allowance',
                 'qualifies_for_merit_incentive', 'status', 'status_display', 'admin_notes',
                 'submitted_at', 'reviewed_at', 'student_name', 'student_id', 'reviewed_by_name']
        read_only_fields = ['id', 'ai_evaluation_completed', 'ai_evaluation_notes', 
                          'qualifies_for_basic_allowance', 'qualifies_for_merit_incentive',
                          'status', 'admin_notes', 'submitted_at', 'reviewed_at', 'reviewed_by']

class GradeSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeSubmission
        fields = ['academic_year', 'semester', 'total_units', 'general_weighted_average', 
                 'semestral_weighted_average', 'grade_sheet', 'has_failing_grades', 
                 'has_incomplete_grades', 'has_dropped_subjects']
        
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        grade_submission = super().create(validated_data)
        
        # Run AI evaluation
        grade_submission.calculate_allowance_eligibility()
        grade_submission.save()
        
        return grade_submission

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
