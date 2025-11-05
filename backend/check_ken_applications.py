"""
Check all applications for Ken Kazuha
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import FullApplication, CustomUser

# Find Ken
ken = CustomUser.objects.filter(email='ken.kazuha987@gmail.com').first()

if ken:
    print(f"👤 Found user: {ken.first_name} {ken.last_name} ({ken.email})")
    print(f"   Student ID: {ken.student_id}")
    print(f"   Username: {ken.username}\n")
    
    applications = FullApplication.objects.filter(user=ken).order_by('-created_at')
    
    print(f"📝 Full Applications for {ken.first_name}:")
    for app in applications:
        print(f"\n   Application #{app.id}:")
        print(f"   - School Year: {app.school_year}")
        print(f"   - Semester: {app.semester}")
        print(f"   - Email: {app.email}")
        print(f"   - Contact: {app.contact_number}")
        print(f"   - Barangay: {app.barangay}")
        print(f"   - Birth Date: {app.birth_date}")
        print(f"   - Submitted: {'✅ Yes' if app.is_submitted else '❌ No'}")
        print(f"   - Locked: {'🔒 Yes' if app.is_locked else '🔓 No'}")
        print(f"   - Created: {app.created_at}")
        print(f"   - Updated: {app.updated_at}")
        if app.submitted_at:
            print(f"   - Submitted At: {app.submitted_at}")
    
    if not applications.exists():
        print("   ❌ No full applications found for this user")
else:
    print("❌ User with email ken.kazuha987@gmail.com not found")
