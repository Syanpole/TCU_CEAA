# Backend Integration Guide - Full Application Form

## Overview
This guide helps backend developers create the Django models, serializers, and API endpoints for the Full Application Form feature.

## Database Model

### Create Model: `backend/myapp/models.py`

```python
from django.db import models
from django.conf import settings

class FullApplication(models.Model):
    """
    Stores comprehensive application form data for TCU-CEAA scholarship applicants.
    One application per user per academic period.
    """
    
    # Relationship
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='full_applications'
    )
    
    # Application Details
    facebook_link = models.URLField(max_length=500, blank=True)
    application_type = models.CharField(max_length=20, choices=[
        ('NEW', 'New'),
        ('RENEW', 'Renewing')
    ], default='RENEW')
    scholarship_type = models.CharField(max_length=50, default='TCU-CEAA')
    school_year = models.CharField(max_length=20)  # e.g., "2025-2026"
    semester = models.CharField(max_length=20, choices=[
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('Summer', 'Summer')
    ])
    applying_for_merit = models.CharField(max_length=3, choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ])
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    house_no = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=10)
    barangay = models.CharField(max_length=100)
    district = models.CharField(max_length=50, blank=True)
    mobile_no = models.CharField(max_length=20)
    other_contact = models.CharField(max_length=20, default='N/A')
    email = models.EmailField()
    date_of_birth = models.DateField()
    age = models.IntegerField(null=True, blank=True)  # Auto-calculated
    citizenship = models.CharField(max_length=50, default='Filipino')
    sex = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female')
    ])
    marital_status = models.CharField(max_length=20, choices=[
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated')
    ])
    religion = models.CharField(max_length=50, choices=[
        ('Roman Catholic', 'Roman Catholic'),
        ('Islam', 'Islam'),
        ('Iglesia ni Cristo', 'Iglesia ni Cristo'),
        ('Protestant', 'Protestant'),
        ('Others', 'Others')
    ])
    place_of_birth = models.CharField(max_length=200, default='Taguig City')
    years_of_residency = models.CharField(max_length=20)
    
    # School Information
    course_name = models.CharField(max_length=200)
    ladderized = models.CharField(max_length=3, choices=[
        ('YES', 'Yes'),
        ('NO', 'No')
    ], default='NO')
    year_level = models.CharField(max_length=20, choices=[
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
        ('5th Year', '5th Year')
    ])
    swa_input = models.CharField(max_length=50, default='NOT AVAILABLE')
    units_enrolled = models.CharField(max_length=10)
    course_duration = models.CharField(max_length=20, choices=[
        ('4 Years', '4 Years'),
        ('5 Years', '5 Years')
    ])
    school_name = models.CharField(max_length=200, default='TAGUIG CITY UNIVERSITY (TCU)')
    school_address = models.CharField(max_length=500, default='Gen. Santos Ave., Central Bicutan, Taguig City')
    graduating_this_term = models.CharField(max_length=3, choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ])
    semesters_to_graduate = models.CharField(max_length=10, blank=True)
    with_honors = models.CharField(max_length=3, blank=True, choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ])
    transferee = models.CharField(max_length=3, choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ])
    shiftee = models.CharField(max_length=3, choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ])
    status = models.CharField(max_length=20, choices=[
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular')
    ])
    
    # Educational Background - Senior High School
    shs_attended = models.CharField(max_length=200, blank=True)
    shs_type = models.CharField(max_length=20, blank=True, choices=[
        ('Public', 'Public'),
        ('Private', 'Private')
    ])
    shs_address = models.CharField(max_length=500, blank=True)
    shs_years = models.CharField(max_length=50, blank=True)
    shs_honors = models.CharField(max_length=200, blank=True)
    
    # Educational Background - Junior High School / ALS
    jhs_attended = models.CharField(max_length=200)
    jhs_type = models.CharField(max_length=20, choices=[
        ('Public', 'Public'),
        ('Private', 'Private')
    ])
    jhs_address = models.CharField(max_length=500)
    jhs_years = models.CharField(max_length=50)
    jhs_honors = models.CharField(max_length=200, blank=True)
    
    # Educational Background - Elementary
    elem_attended = models.CharField(max_length=200)
    elem_type = models.CharField(max_length=20, choices=[
        ('Public', 'Public'),
        ('Private', 'Private')
    ])
    elem_address = models.CharField(max_length=500)
    elem_years = models.CharField(max_length=50)
    elem_honors = models.CharField(max_length=200, blank=True)
    
    # Father's Information
    father_name = models.CharField(max_length=200)
    father_address = models.CharField(max_length=500)
    father_contact = models.CharField(max_length=20)
    father_occupation = models.CharField(max_length=100)
    father_place_of_work = models.CharField(max_length=200)
    father_education = models.CharField(max_length=50, choices=[
        ('Elementary', 'Elementary'),
        ('High School', 'High School'),
        ('Senior High School', 'Senior High School'),
        ('College Graduate', 'College Graduate'),
        ('Vocational', 'Vocational')
    ])
    father_deceased = models.BooleanField(default=False)
    
    # Mother's Information
    mother_name = models.CharField(max_length=200)
    mother_address = models.CharField(max_length=500)
    mother_contact = models.CharField(max_length=20)
    mother_occupation = models.CharField(max_length=100)
    mother_place_of_work = models.CharField(max_length=200)
    mother_education = models.CharField(max_length=50, choices=[
        ('Elementary', 'Elementary'),
        ('High School', 'High School'),
        ('Senior High School', 'Senior High School'),
        ('College Graduate', 'College Graduate'),
        ('Vocational', 'Vocational')
    ])
    mother_deceased = models.BooleanField(default=False)
    
    # Status and Timestamps
    is_submitted = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)  # Locked after submission
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Full Application'
        verbose_name_plural = 'Full Applications'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.school_year} ({self.semester})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate age from date of birth
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        super().save(*args, **kwargs)
```

## Serializer

### Create Serializer: `backend/myapp/serializers.py`

```python
from rest_framework import serializers
from .models import FullApplication

class FullApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FullApplication
        fields = '__all__'
        read_only_fields = ['user', 'age', 'is_submitted', 'is_locked', 'created_at', 'updated_at', 'submitted_at']
    
    def validate(self, data):
        """
        Validate application data
        """
        # Ensure barangay is a valid Taguig barangay
        valid_barangays = [
            'Bagumbayan', 'Bambang', 'Calzada', 'Central Bicutan', 'Central Signal Village',
            'Fort Bonifacio', 'Hagonoy', 'Ibayo-Tipas', 'Katuparan', 'Ligid-Tipas',
            'Lower Bicutan', 'Maharlika Village', 'Napindan', 'New Lower Bicutan',
            'North Daang Hari', 'North Signal Village', 'Palingon', 'Pinagsama',
            'San Miguel', 'Santa Ana', 'South Daang Hari', 'South Signal Village',
            'Tanyag', 'Tuktukan', 'Upper Bicutan', 'Ususan', 'Wawa', 'Western Bicutan'
        ]
        
        if data.get('barangay') and data['barangay'] not in valid_barangays:
            raise serializers.ValidationError({
                'barangay': 'Must be a valid Taguig City barangay.'
            })
        
        # Validate conditional fields based on graduation status
        if data.get('graduating_this_term') == 'Yes':
            if not data.get('with_honors'):
                raise serializers.ValidationError({
                    'with_honors': 'This field is required when graduating this term.'
                })
        elif data.get('graduating_this_term') == 'No':
            if not data.get('semesters_to_graduate'):
                raise serializers.ValidationError({
                    'semesters_to_graduate': 'This field is required when not graduating this term.'
                })
        
        return data
```

## ViewSet

### Create ViewSet: `backend/myapp/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import FullApplication
from .serializers import FullApplicationSerializer

class FullApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing full application submissions.
    """
    serializer_class = FullApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return applications for the current user
        return FullApplication.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def check_status(self, request):
        """
        Check if user has completed the full application form.
        """
        try:
            application = FullApplication.objects.get(
                user=request.user,
                is_submitted=True
            )
            serializer = self.get_serializer(application)
            return Response({
                'completed': True,
                'data': serializer.data
            })
        except FullApplication.DoesNotExist:
            return Response({
                'completed': False,
                'data': None
            })
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """
        Submit or update full application form.
        """
        try:
            # Check if user already has an application
            application = FullApplication.objects.filter(
                user=request.user,
                is_locked=False  # Don't allow editing locked applications
            ).first()
            
            if application:
                # Update existing application
                serializer = self.get_serializer(application, data=request.data, partial=True)
            else:
                # Create new application
                serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                application = serializer.save(
                    user=request.user,
                    is_submitted=True,
                    is_locked=True,  # Lock application after submission
                    submitted_at=timezone.now()
                )
                
                return Response({
                    'success': True,
                    'message': 'Application submitted successfully.',
                    'data': FullApplicationSerializer(application).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation error.',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def save_draft(self, request):
        """
        Save application as draft (not locked, can edit later).
        """
        try:
            application = FullApplication.objects.filter(
                user=request.user,
                is_locked=False
            ).first()
            
            if application:
                serializer = self.get_serializer(application, data=request.data, partial=True)
            else:
                serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                application = serializer.save(
                    user=request.user,
                    is_submitted=False,
                    is_locked=False
                )
                
                return Response({
                    'success': True,
                    'message': 'Draft saved successfully.',
                    'data': FullApplicationSerializer(application).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation error.',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

## URL Configuration

### Update URLs: `backend/myapp/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FullApplicationViewSet

router = DefaultRouter()
router.register(r'full-application', FullApplicationViewSet, basename='full-application')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## Migration Commands

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Create admin user (if needed)
python manage.py createsuperuser
```

## Admin Panel

### Register in Admin: `backend/myapp/admin.py`

```python
from django.contrib import admin
from .models import FullApplication

@admin.register(FullApplication)
class FullApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'first_name',
        'last_name',
        'school_year',
        'semester',
        'application_type',
        'is_submitted',
        'is_locked',
        'submitted_at'
    ]
    list_filter = [
        'application_type',
        'school_year',
        'semester',
        'is_submitted',
        'is_locked',
        'barangay'
    ]
    search_fields = [
        'user__username',
        'first_name',
        'last_name',
        'email',
        'student_number'
    ]
    readonly_fields = [
        'age',
        'created_at',
        'updated_at',
        'submitted_at'
    ]
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Application Details', {
            'fields': (
                'facebook_link',
                'application_type',
                'scholarship_type',
                'school_year',
                'semester',
                'applying_for_merit'
            )
        }),
        ('Personal Information', {
            'fields': (
                'first_name',
                'middle_name',
                'last_name',
                'house_no',
                'street',
                'zip_code',
                'barangay',
                'district',
                'mobile_no',
                'other_contact',
                'email',
                'date_of_birth',
                'age',
                'citizenship',
                'sex',
                'marital_status',
                'religion',
                'place_of_birth',
                'years_of_residency'
            )
        }),
        ('School Information', {
            'fields': (
                'course_name',
                'ladderized',
                'year_level',
                'swa_input',
                'units_enrolled',
                'course_duration',
                'school_name',
                'school_address',
                'graduating_this_term',
                'semesters_to_graduate',
                'with_honors',
                'transferee',
                'shiftee',
                'status'
            )
        }),
        ('Educational Background', {
            'fields': (
                'shs_attended',
                'shs_type',
                'shs_address',
                'shs_years',
                'shs_honors',
                'jhs_attended',
                'jhs_type',
                'jhs_address',
                'jhs_years',
                'jhs_honors',
                'elem_attended',
                'elem_type',
                'elem_address',
                'elem_years',
                'elem_honors'
            )
        }),
        ('Parents Information', {
            'fields': (
                'father_name',
                'father_address',
                'father_contact',
                'father_occupation',
                'father_place_of_work',
                'father_education',
                'father_deceased',
                'mother_name',
                'mother_address',
                'mother_contact',
                'mother_occupation',
                'mother_place_of_work',
                'mother_education',
                'mother_deceased'
            )
        }),
        ('Status', {
            'fields': (
                'is_submitted',
                'is_locked',
                'created_at',
                'updated_at',
                'submitted_at'
            )
        })
    )
```

## API Endpoints

### Available Endpoints

```
GET    /api/full-application/               - List user's applications
POST   /api/full-application/               - Create new application
GET    /api/full-application/{id}/          - Get specific application
PUT    /api/full-application/{id}/          - Update application (if not locked)
DELETE /api/full-application/{id}/          - Delete application

GET    /api/full-application/check_status/  - Check if user completed application
POST   /api/full-application/submit/        - Submit and lock application
POST   /api/full-application/save_draft/    - Save draft (editable)
```

## Frontend Integration

### Update FullApplicationForm.tsx

Replace the simulated API call in `handleSubmit`:

```typescript
const handleSubmit = async () => {
  setShowConfirmDialog(false);
  setIsSubmitting(true);

  try {
    const response = await apiClient.post('/full-application/submit/', formData);
    
    if (response.data.success) {
      setIsSubmitting(false);
      setShowSuccess(true);
    } else {
      throw new Error(response.data.message || 'Submission failed');
    }
  } catch (error: any) {
    setIsSubmitting(false);
    alert('Error submitting application: ' + (error.response?.data?.message || error.message));
  }
};
```

### Check Application Status on Dashboard Load

In `StudentDashboard.tsx`, add to `useEffect`:

```typescript
useEffect(() => {
  const checkApplicationStatus = async () => {
    try {
      const response = await apiClient.get('/full-application/check_status/');
      if (response.data.completed) {
        setHasCompletedApplication(true);
      }
    } catch (err) {
      console.error('Error checking application status:', err);
    }
  };

  if (user && hasCompletedQualification && isQualified) {
    checkApplicationStatus();
  }
}, [user, hasCompletedQualification, isQualified]);
```

## Testing

### Test API with cURL

```bash
# Check status
curl -X GET http://localhost:8000/api/full-application/check_status/ \
  -H "Authorization: Token YOUR_TOKEN"

# Submit application
curl -X POST http://localhost:8000/api/full-application/submit/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "facebook_link": "https://facebook.com/test",
    "school_year": "2025-2026",
    "semester": "1st",
    "applying_for_merit": "Yes",
    ...
  }'
```

## Validation Rules

1. **Barangay**: Must be one of 28 Taguig barangays
2. **Graduating Conditional**:
   - If `graduating_this_term` = "Yes" → `with_honors` required
   - If `graduating_this_term` = "No" → `semesters_to_graduate` required
3. **Email**: Must be valid email format
4. **Date of Birth**: Age auto-calculated
5. **Required Fields**: All fields except those marked `blank=True`

## Database Indexes (Optional Performance Optimization)

Add to model Meta class:

```python
class Meta:
    ordering = ['-created_at']
    indexes = [
        models.Index(fields=['user', 'is_submitted']),
        models.Index(fields=['school_year', 'semester']),
        models.Index(fields=['barangay']),
    ]
```

## Security Considerations

1. **User Isolation**: Users can only see/edit their own applications
2. **Lock Mechanism**: Submitted applications are locked (read-only)
3. **Authentication Required**: All endpoints require valid token
4. **Data Validation**: Server-side validation for all fields
5. **SQL Injection**: Prevented by Django ORM

## Status Codes

- `200 OK`: Success (GET, draft save)
- `201 Created`: Application submitted successfully
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Application not found
- `500 Internal Server Error`: Server error

