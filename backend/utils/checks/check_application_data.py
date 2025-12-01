"""
Check for full application submissions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, BasicQualification, FullApplication
from django.utils import timezone

print("=" * 80)
print("📋 APPLICATION DATA CHECK")
print("=" * 80)

# Get the user
user = CustomUser.objects.get(username='4peytonly')
print(f"\n👤 User: {user.get_full_name()} ({user.username})")
print(f"   Student ID: {user.student_id}")
print(f"   Email: {user.email}")

# Check Basic Qualification
print(f"\n{'=' * 80}")
print("✓ BASIC QUALIFICATION STATUS")
print("=" * 80)

try:
    basic_qual = BasicQualification.objects.get(student=user)
    print(f"   Status: {'✅ QUALIFIED' if basic_qual.is_qualified else '❌ NOT QUALIFIED'}")
    print(f"   Is Enrolled at TCU: {basic_qual.is_enrolled}")
    print(f"   Is Taguig Resident: {basic_qual.is_resident}")
    print(f"   Is 18 or Older: {basic_qual.is_eighteen_or_older}")
    print(f"   Is Registered Voter: {basic_qual.is_registered_voter}")
    print(f"   Parent is Voter: {basic_qual.parent_is_voter}")
    print(f"   Applicant Type: {basic_qual.applicant_type}")
    print(f"   Completed: {basic_qual.completed_at}")
    print(f"   Updated: {basic_qual.updated_at}")
except BasicQualification.DoesNotExist:
    print("   ❌ No basic qualification record found")

# Check Full Application
print(f"\n{'=' * 80}")
print("📄 FULL APPLICATION STATUS")
print("=" * 80)

full_apps = FullApplication.objects.filter(user=user).order_by('-submitted_at')

if full_apps.exists():
    print(f"\n✅ Found {full_apps.count()} full application(s)\n")
    
    for idx, app in enumerate(full_apps, 1):
        print(f"\n{'─' * 80}")
        print(f"📋 Application #{idx}")
        print(f"{'─' * 80}")
        print(f"   ID: {app.id}")
        print(f"   Status: {app.status.upper()}")
        print(f"   Submitted: {app.submitted_at}")
        print(f"   Updated: {app.updated_at}")
        
        print(f"\n   Personal Information:")
        print(f"      First Name: {app.first_name}")
        print(f"      Middle Name: {app.middle_name}")
        print(f"      Last Name: {app.last_name}")
        print(f"      Sex: {app.sex}")
        print(f"      Date of Birth: {app.date_of_birth}")
        print(f"      Place of Birth: {app.place_of_birth}")
        print(f"      Age: {app.age}")
        print(f"      Citizenship: {app.citizenship}")
        print(f"      Religion: {app.religion}")
        print(f"      Marital Status: {app.marital_status}")
        print(f"      Mobile: {app.mobile_no}")
        print(f"      Email: {app.email}")
        
        print(f"\n   Address:")
        print(f"      House No: {app.house_no}")
        print(f"      Street: {app.street}")
        print(f"      Barangay: {app.barangay}")
        print(f"      District: {app.district}")
        print(f"      Zip: {app.zip_code}")
        print(f"      Years of Residency: {app.years_of_residency}")
        
        print(f"\n   School Information:")
        print(f"      School Name: {app.school_name}")
        print(f"      School Address: {app.school_address}")
        print(f"      Course Name: {app.course_name}")
        print(f"      Year Level: {app.year_level}")
        print(f"      School Year: {app.school_year}")
        print(f"      Semester: {app.semester}")
        print(f"      Units Enrolled: {app.units_enrolled}")
        
        print(f"\n   Family Information:")
        print(f"      Father: {app.father_name}")
        if app.father_name:
            print(f"         Occupation: {app.father_occupation}")
            print(f"         Contact: {app.father_contact}")
            print(f"         Deceased: {app.father_deceased}")
        print(f"      Mother: {app.mother_name}")
        if app.mother_name:
            print(f"         Occupation: {app.mother_occupation}")
            print(f"         Contact: {app.mother_contact}")
            print(f"         Deceased: {app.mother_deceased}")
else:
    print("\n❌ No full application found")
    print("\n💡 This means:")
    print("   • Basic qualification was completed ✓")
    print("   • Full application form was NOT submitted yet")
    print("   • User needs to click 'Complete Application Form' button")

print("\n" + "=" * 80)

# Check if there are any pending/draft applications
print("\n🔍 CHECKING FOR RECENT DATABASE ACTIVITY...")
print("=" * 80)

from django.contrib.contenttypes.models import ContentType
from myapp.models import AuditLog

# Check audit logs for application activity
audit_logs = AuditLog.objects.filter(
    user=user,
    action_type__icontains='application'
).order_by('-timestamp')[:10]

if audit_logs.exists():
    print(f"\n📝 Recent Application-Related Activity:\n")
    for log in audit_logs:
        print(f"   {log.timestamp} - {log.action_type}: {log.action_description}")
else:
    print("\n❌ No application-related audit logs found")

print("\n" + "=" * 80)
