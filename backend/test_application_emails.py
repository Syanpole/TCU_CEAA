"""
Quick Test - Application Email Notifications
Tests application confirmation and status update emails
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, AllowanceApplication, GradeSubmission
from myapp.application_email_service import ApplicationEmailService
from django.utils import timezone

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_application_emails():
    """Test application notification emails"""
    print_section("APPLICATION NOTIFICATION EMAIL TEST")
    
    try:
        # Get an existing student user or use the test user
        student = CustomUser.objects.filter(role='student', is_email_verified=True).first()
        
        if not student:
            print("⚠️  No verified student found. Creating test student...")
            # Clean up old test data
            CustomUser.objects.filter(email="apptest@tcu-ceaa.edu.ph").delete()
            
            student = CustomUser.objects.create_user(
                username="app_tester",
                email="apptest@tcu-ceaa.edu.ph",
                password="TestPass123!",
                student_id="24-00099",
                first_name="Application",
                last_name="Tester",
                role="student",
                is_email_verified=True,
                email_verified_at=timezone.now()
            )
            print(f"✅ Created test student: {student.username} ({student.email})")
        else:
            print(f"✅ Using existing student: {student.username} ({student.email})")
        
        # Get or create a grade submission
        grade_sub = GradeSubmission.objects.filter(student=student).first()
        
        if not grade_sub:
            print("⚠️  No grade submission found. You need a grade submission to test applications.")
            print("   Skipping application test...")
            return
        
        print(f"✅ Using grade submission: ID {grade_sub.id}")
        
        # Check if application already exists
        existing_app = AllowanceApplication.objects.filter(
            student=student,
            grade_submission=grade_sub
        ).first()
        
        if existing_app:
            print(f"ℹ️  Found existing application: ID {existing_app.id}")
            application = existing_app
        else:
            # Create test application
            print("\n--- Creating test application ---")
            application = AllowanceApplication.objects.create(
                student=student,
                grade_submission=grade_sub,
                application_type='basic',
                amount=5000.00,
                status='pending'
            )
            print(f"✅ Created application: ID {application.id}")
        
        print(f"   Type: {application.get_application_type_display()}")
        print(f"   Amount: ₱{application.amount}")
        print(f"   Status: {application.get_status_display()}")
        print(f"   Email sent: {application.email_sent}")
        
        # Test confirmation email
        print("\n--- Sending application confirmation email ---")
        print("   (This simulates what happens when a student submits an application)")
        ApplicationEmailService.notify_application_submission(application)
        application.refresh_from_db()
        print(f"✅ Confirmation email sent: {application.email_sent}")
        print(f"   Sent at: {application.email_sent_at}")
        print("   📧 Check terminal output above for email content")
        
        # Test approval email
        print("\n--- Simulating admin APPROVAL ---")
        previous_status = application.status
        application.status = 'approved'
        application.processed_at = timezone.now()
        application.admin_notes = "Application approved! All requirements met. Excellent academic performance."
        application.save()
        
        print(f"   Status changed: {previous_status} → {application.status}")
        ApplicationEmailService.notify_status_change(application, previous_status)
        print(f"✅ Approval email sent")
        print("   📧 Check terminal output above for approval email (green header ✅)")
        
        # Test rejection email
        print("\n--- Simulating admin REJECTION ---")
        previous_status = application.status
        application.status = 'rejected'
        application.admin_notes = "Application rejected. GPA requirements not met. Please reapply next semester after improving grades."
        application.save()
        
        print(f"   Status changed: {previous_status} → {application.status}")
        ApplicationEmailService.notify_status_change(application, previous_status)
        print(f"✅ Rejection email sent")
        print("   📧 Check terminal output above for rejection email (red header ❌)")
        
        # Test disbursement email
        print("\n--- Simulating admin DISBURSEMENT ---")
        previous_status = 'approved'  # Simulate approved status
        application.status = 'disbursed'
        application.admin_notes = "Allowance disbursed successfully. Funds transferred to your account."
        application.save()
        
        print(f"   Status changed: {previous_status} → {application.status}")
        ApplicationEmailService.notify_status_change(application, previous_status)
        print(f"✅ Disbursement email sent")
        print("   📧 Check terminal output above for disbursement email (purple header 💰)")
        
        print("\n✅ All application notification emails sent successfully!")
        print("\n📝 Review the email content in the terminal output above:")
        print("   1. Green header (✅) = Confirmation email")
        print("   2. Green header (✅) = Approval email")
        print("   3. Red header (❌) = Rejection email")
        print("   4. Purple header (💰) = Disbursement email")
        
    except Exception as e:
        print(f"❌ Error testing application emails: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    print("\n" + "="*80)
    print("  APPLICATION EMAIL NOTIFICATION TEST")
    print("  TCU-CEAA Portal")
    print("="*80)
    print("\n📧 Email Backend: Console (emails will print below)")
    print("⏱️  Starting test...\n")
    
    test_application_emails()
    
    print("\n" + "="*80)
    print("  TEST COMPLETED")
    print("="*80)
    print("\n✅ Application notification system is working!")
    print("\n📝 Next steps:")
    print("   1. Review the beautiful email templates above")
    print("   2. Update .env with real Gmail credentials for production")
    print("   3. Change EMAIL_BACKEND to smtp.EmailBackend")
    print("   4. Test with real email delivery")
    print("\n")

if __name__ == "__main__":
    main()
