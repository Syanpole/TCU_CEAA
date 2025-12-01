import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, BasicQualification, FullApplication

# Find the user
try:
    user = CustomUser.objects.get(email='ken.kazuha987@gmail.com')
    print(f"✅ User found: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Student ID: {user.student_id}")
    print(f"   First Name: {user.first_name}")
    print(f"   Last Name: {user.last_name}")
    print(f"   Full Name: {user.get_full_name()}")
    print(f"   User ID: {user.id}")
    
    # Check BasicQualification
    print("\n--- BasicQualification Records ---")
    qualifications = BasicQualification.objects.filter(student=user)
    if qualifications.exists():
        for qual in qualifications:
            print(f"   ID: {qual.id}")
            print(f"   Student: {qual.student}")
            print(f"   Student ID: {qual.student.student_id if qual.student else 'N/A'}")
            print(f"   Student Name: {qual.student.get_full_name() if qual.student else 'N/A'}")
            print(f"   Is Qualified: {qual.is_qualified}")
            print(f"   Completed: {qual.completed_at}")
    else:
        print("   No qualification records found")
    
    # Check FullApplication
    print("\n--- FullApplication Records ---")
    applications = FullApplication.objects.filter(user=user)
    if applications.exists():
        for app in applications:
            print(f"   ID: {app.id}")
            print(f"   User: {app.user}")
            print(f"   User Student ID: {app.user.student_id if app.user else 'N/A'}")
            print(f"   Form First Name: {app.first_name}")
            print(f"   Form Last Name: {app.last_name}")
            print(f"   School Year: {app.school_year}")
            print(f"   Semester: {app.semester}")
    else:
        print("   No application records found")
        
except CustomUser.DoesNotExist:
    print("❌ User not found with email: ken.kazuha987@gmail.com")
