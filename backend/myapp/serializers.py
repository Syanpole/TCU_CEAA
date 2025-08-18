from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Task, CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'student_id', 'created_at']
        read_only_fields = ['id', 'created_at']

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
