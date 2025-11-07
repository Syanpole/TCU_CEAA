"""
Create sample full applications for testing the admin dashboard
"""
import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, FullApplication
from django.utils import timezone

def create_sample_applications():
    """Create sample full applications"""
    
    # Get all student users
    students = CustomUser.objects.filter(role='student')
    
    if not students.exists():
        print("❌ No students found in the database.")
        print("Please create student accounts first.")
        return
    
    print(f"✅ Found {students.count()} student(s)")
    
    # Sample data for applications
    barangays = [
        'Bagumbayan', 'Bambang', 'Central Bicutan', 'Fort Bonifacio', 
        'Hagonoy', 'Ibayo-Tipas', 'Lower Bicutan', 'Napindan', 
        'Pinagsama', 'Tanyag', 'Upper Bicutan', 'Western Bicutan'
    ]
    
    semesters = ['1st', '2nd']
    school_years = ['S.Y 2024-2025', 'S.Y 2025-2026']
    application_types = ['new', 'renewal']
    
    created_count = 0
    
    for i, student in enumerate(students[:10]):  # Limit to first 10 students
        # Check if student already has a full application
        if FullApplication.objects.filter(user=student).exists():
            print(f"⏭️  Skipping {student.username} - already has application")
            continue
        
        # Create application
        birth_date = datetime(2000 + (i % 5), (i % 12) + 1, (i % 28) + 1).date()
        
        application = FullApplication.objects.create(
            user=student,
            school_year=school_years[i % 2],
            semester=semesters[i % 2],
            application_type=application_types[i % 2],
            email=student.email or f"{student.username}@tcu.edu.ph",
            contact_number=f"09{100000000 + i:09d}",
            birth_date=birth_date,
            barangay=barangays[i % len(barangays)],
            is_submitted=i % 3 != 0,  # 2/3 submitted, 1/3 in progress
            is_locked=i % 3 != 0,
            submitted_at=timezone.now() - timedelta(days=i) if i % 3 != 0 else None
        )
        
        created_count += 1
        status = "✅ Submitted & Locked" if application.is_submitted else "📝 In Progress"
        print(f"✨ Created application for {student.first_name} {student.last_name} ({student.student_id}) - {status}")
    
    print(f"\n🎉 Successfully created {created_count} full application(s)!")
    print(f"💡 Total applications in database: {FullApplication.objects.count()}")
    print(f"   - Submitted & Locked: {FullApplication.objects.filter(is_submitted=True, is_locked=True).count()}")
    print(f"   - In Progress: {FullApplication.objects.filter(is_submitted=False).count()}")
    print(f"\n🔍 You can now view these applications in the admin dashboard under 'Full Applications' tab!")

if __name__ == '__main__':
    print("🚀 Creating sample full applications...\n")
    create_sample_applications()
