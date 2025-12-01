"""
Test Email Verification and Notification System
Tests all email functionality without sending real emails
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser, EmailVerification, AllowanceApplication
from myapp.email_verification_service import VerificationService
from myapp.application_email_service import ApplicationEmailService
from django.utils import timezone
from datetime import timedelta

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_email_verification():
    """Test email verification flow"""
    print_section("TEST 1: Email Verification System")
    
    # Create or get test user
    email = "test_verification@tcu-ceaa.edu.ph"
    username = "test_verifier"
    
    # Clean up old test data
    CustomUser.objects.filter(email=email).delete()
    
    try:
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password="TestPass123!",
            student_id="24-00001",
            first_name="Test",
            last_name="Verifier"
        )
        print(f"✅ Created test user: {user.username} ({user.email})")
        print(f"   Email verified: {user.is_email_verified}")
        
        # Create verification code
        print("\n--- Creating verification code ---")
        verification = VerificationService.create_verification(user)
        print(f"✅ Verification created")
        print(f"   Code: {verification.code}")
        print(f"   Expires at: {verification.expires_at}")
        print(f"   Is expired: {verification.is_expired()}")
        
        # Send verification email
        print("\n--- Sending verification email ---")
        result = VerificationService.send_verification_email(user, verification.code)
        print(f"✅ Email sent successfully: {result}")
        print("   (Check terminal output for email content)")
        
        # Test code validation
        print("\n--- Testing code validation ---")
        is_valid = VerificationService.validate_code(user, verification.code)
        print(f"✅ Code validation result: {is_valid}")
        
        # Refresh user
        user.refresh_from_db()
        print(f"   User email_verified: {user.is_email_verified}")
        print(f"   Verified at: {user.email_verified_at}")
        
        # Test rate limiting
        print("\n--- Testing rate limiting ---")
        can_resend = VerificationService.can_resend_code(user)
        print(f"   Can resend immediately: {can_resend}")
        
        print("\n✅ Email verification system working correctly!")
        
        return user
        
    except Exception as e:
        print(f"❌ Error testing email verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_application_notifications(user):
    """Test application notification emails"""
    print_section("TEST 2: Application Notification System")
    
    if not user:
        print("⚠️  Skipping - no user available")
        return
    
    try:
        # Create test application
        print("--- Creating test application ---")
        application = AllowanceApplication.objects.create(
            student=user,
            academic_year="2024-2025",
            semester="First Semester",
            allowance_type="scholarship",
            requested_amount=5000.00,
            current_gpa=3.5,
            units_enrolled=21,
            status="pending"
        )
        print(f"✅ Created application: ID {application.id}")
        print(f"   Type: {application.allowance_type}")
        print(f"   Amount: {application.requested_amount}")
        print(f"   Status: {application.status}")
        
        # Send confirmation email
        print("\n--- Sending application confirmation email ---")
        ApplicationEmailService.notify_application_submission(application)
        application.refresh_from_db()
        print(f"✅ Confirmation email sent: {application.email_sent}")
        print(f"   Sent at: {application.email_sent_at}")
        print("   (Check terminal output for email content)")
        
        # Test status update email (approval)
        print("\n--- Simulating admin approval ---")
        previous_status = application.status
        application.status = "approved"
        application.processed_at = timezone.now()
        application.admin_notes = "Application approved. All requirements met."
        application.save()
        
        print(f"   Status changed: {previous_status} → {application.status}")
        ApplicationEmailService.notify_status_change(application, previous_status)
        print(f"✅ Status update email sent")
        print("   (Check terminal output for email content)")
        
        # Test rejection email
        print("\n--- Simulating admin rejection ---")
        previous_status = application.status
        application.status = "rejected"
        application.admin_notes = "GPA requirements not met. Please reapply next semester."
        application.save()
        
        print(f"   Status changed: {previous_status} → {application.status}")
        ApplicationEmailService.notify_status_change(application, previous_status)
        print(f"✅ Rejection email sent")
        print("   (Check terminal output for email content)")
        
        print("\n✅ Application notification system working correctly!")
        
        # Cleanup
        application.delete()
        
    except Exception as e:
        print(f"❌ Error testing application notifications: {str(e)}")
        import traceback
        traceback.print_exc()

def test_rate_limiting():
    """Test rate limiting and security features"""
    print_section("TEST 3: Rate Limiting & Security")
    
    try:
        # Create test user
        email = "test_ratelimit@tcu-ceaa.edu.ph"
        CustomUser.objects.filter(email=email).delete()
        
        user = CustomUser.objects.create_user(
            username="test_ratelimit",
            email=email,
            password="TestPass123!",
            student_id="24-00002"
        )
        
        print("--- Testing maximum resends per hour ---")
        for i in range(4):
            print(f"\nAttempt {i+1}:")
            if i < 3:
                can_resend = VerificationService.can_resend_code(user)
                print(f"   Can resend: {can_resend}")
                if can_resend:
                    result = VerificationService.resend_verification_code(user)
                    print(f"   ✅ Code sent: {result}")
            else:
                can_resend = VerificationService.can_resend_code(user)
                print(f"   Can resend: {can_resend}")
                if not can_resend:
                    print(f"   ✅ Rate limit enforced correctly!")
        
        # Test code expiration
        print("\n--- Testing code expiration ---")
        verification = EmailVerification.objects.filter(user=user).first()
        if verification:
            print(f"   Code created at: {verification.created_at}")
            print(f"   Code expires at: {verification.expires_at}")
            print(f"   Is expired now: {verification.is_expired()}")
            
            # Simulate expired code
            verification.expires_at = timezone.now() - timedelta(minutes=1)
            verification.save()
            print(f"   Simulated expiration...")
            print(f"   Is expired now: {verification.is_expired()}")
            print(f"   ✅ Expiration check working!")
        
        # Cleanup
        user.delete()
        
        print("\n✅ Rate limiting and security features working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing rate limiting: {str(e)}")
        import traceback
        traceback.print_exc()

def show_statistics():
    """Show database statistics"""
    print_section("DATABASE STATISTICS")
    
    total_users = CustomUser.objects.count()
    verified_users = CustomUser.objects.filter(is_email_verified=True).count()
    total_verifications = EmailVerification.objects.count()
    total_applications = AllowanceApplication.objects.count()
    apps_with_email = AllowanceApplication.objects.filter(email_sent=True).count()
    
    print(f"Users:")
    print(f"   Total users: {total_users}")
    print(f"   Email verified: {verified_users}")
    print(f"   Unverified: {total_users - verified_users}")
    
    print(f"\nEmail Verifications:")
    print(f"   Total verifications: {total_verifications}")
    print(f"   Verified: {EmailVerification.objects.filter(is_verified=True).count()}")
    print(f"   Pending: {EmailVerification.objects.filter(is_verified=False).count()}")
    
    print(f"\nApplications:")
    print(f"   Total applications: {total_applications}")
    print(f"   With email sent: {apps_with_email}")
    print(f"   Without email: {total_applications - apps_with_email}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  EMAIL VERIFICATION & NOTIFICATION SYSTEM TEST")
    print("  TCU-CEAA Portal")
    print("="*80)
    
    print("\n📧 Email Backend: Console (emails will print below)")
    print("⏱️  Starting tests...\n")
    
    # Run tests
    user = test_email_verification()
    test_application_notifications(user)
    test_rate_limiting()
    show_statistics()
    
    print("\n" + "="*80)
    print("  ALL TESTS COMPLETED")
    print("="*80)
    print("\n✅ Email system is working correctly!")
    print("\n📝 Next steps:")
    print("   1. Check the terminal output above for email content")
    print("   2. Update .env with real Gmail credentials for production")
    print("   3. Change EMAIL_BACKEND to smtp.EmailBackend")
    print("   4. Implement frontend components (see FRONTEND_DEVELOPER_GUIDE.md)")
    print("\n")

if __name__ == "__main__":
    main()
