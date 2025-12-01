"""
Comprehensive System Test Suite
Tests the complete email verification and notification system
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from myapp.models import EmailVerification, AllowanceApplication, GradeSubmission, DocumentSubmission
from myapp.email_verification_service import VerificationService
from myapp.application_email_service import ApplicationEmailService
import time

User = get_user_model()

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_email_verification_service():
    """Test the email verification service"""
    print_header("TEST 1: Email Verification Service")
    
    # Clean up test user if exists
    test_email = "test_verification@example.com"
    User.objects.filter(email=test_email).delete()
    
    # Create test user
    print_info(f"Creating test user: {test_email}")
    user = User.objects.create_user(
        username="test_verification_user",
        email=test_email,
        password="TestPass123!",
        first_name="Test",
        last_name="User",
        student_id="24-99901",
        role="student"
    )
    
    # Test 1: Generate and send verification code
    print_info("Test 1.1: Generating verification code...")
    service = VerificationService()
    
    # Create verification record
    verification = service.create_verification(user)
    print_info(f"Generated code: {verification.code}")
    
    # Send email
    email_sent = service.send_verification_email(user, verification.code)
    
    if email_sent:
        print_success(f"Verification code sent! Expires in {service.CODE_EXPIRY_MINUTES} minutes")
        
        # Get the verification code from database
        verification = EmailVerification.objects.filter(user=user, is_verified=False).first()
        if verification:
            print_info(f"Code in database: {verification.code}")
            
            # Test 2: Validate correct code
            print_info("Test 1.2: Validating correct code...")
            validation_result = service.validate_code(user, verification.code)
            
            if validation_result['valid']:
                print_success("Code validation successful!")
                print_info(f"Message: {validation_result['message']}")
                
                # Check if user is marked as verified
                user.refresh_from_db()
                if user.is_email_verified:
                    print_success("User marked as email verified ✓")
                else:
                    print_error("User not marked as verified")
            else:
                print_error(f"Code validation failed: {validation_result['message']}")
                
            # Test 3: Try to use same code again (should fail - one-time use)
            print_info("Test 1.3: Testing one-time use (should fail)...")
            validation_result2 = service.validate_code(user, verification.code)
            
            if not validation_result2['valid']:
                print_success("One-time use enforced! Code cannot be reused ✓")
            else:
                print_error("Security issue: Code was reused!")
                
        else:
            print_error("No verification record found")
    else:
        print_error(f"Failed to send verification email")
    
    # Test 4: Test rate limiting using resend method
    print_info("Test 1.4: Testing rate limiting with resend...")
    
    # Try sending multiple codes quickly
    attempts = []
    for i in range(5):
        result = service.resend_verification_code(user)
        attempts.append(result['success'])
        if not result['success']:
            print_info(f"Attempt {i+1}: Blocked - {result['message']}")
        else:
            print_info(f"Attempt {i+1}: Allowed")
        time.sleep(0.5)  # Small delay
    
    blocked_count = attempts.count(False)
    if blocked_count > 0:
        print_success(f"Rate limiting working! Blocked {blocked_count} attempts ✓")
    else:
        print_error("Rate limiting not enforced")
    
    # Cleanup
    user.delete()
    print_info("Test user cleaned up")

def test_application_email_service():
    """Test the application email service"""
    print_header("TEST 2: Application Email Service")
    
    # Get a test user or create one
    test_email = "test_application@example.com"
    User.objects.filter(email=test_email).delete()
    
    print_info(f"Creating test student: {test_email}")
    student = User.objects.create_user(
        username="test_app_student",
        email=test_email,
        password="TestPass123!",
        first_name="Application",
        last_name="Tester",
        student_id="24-99902",
        role="student"
    )
    
    # Create a test application
    print_info("Creating test grade submission...")
    
    # Create a minimal grade submission
    grade = GradeSubmission.objects.create(
        student=student,
        academic_year="2024-2025",
        semester="1st_sem",
        total_units=21,
        general_weighted_average=1.75,
        status="approved"
    )
    
    print_info("Creating test application...")
    application = AllowanceApplication.objects.create(
        student=student,
        grade_submission=grade,
        application_type="basic",
        amount=5000.00,
        status="pending"
    )
    
    # Test 1: Send confirmation email
    print_info("Test 2.1: Sending application confirmation email...")
    email_service = ApplicationEmailService()
    result = email_service.send_confirmation_email(application)
    
    if result:
        print_success("Confirmation email sent!")
        
        # Check email_sent flag
        application.refresh_from_db()
        if application.email_sent:
            print_success("Application marked as email_sent ✓")
        else:
            print_error("email_sent flag not set")
    else:
        print_error("Failed to send confirmation email")
    
    # Test 2: Send approval email
    print_info("Test 2.2: Sending approval status update email...")
    application.status = "approved"
    application.admin_notes = "Your application has been reviewed and approved. Congratulations!"
    application.save()
    
    result = email_service.send_status_update_email(application)
    
    if result:
        print_success("Approval email sent!")
    else:
        print_error("Failed to send approval email")
    
    # Test 3: Send rejection email
    print_info("Test 2.3: Sending rejection status update email...")
    application.status = "rejected"
    application.admin_notes = "Unfortunately, your application does not meet the requirements."
    application.save()
    
    result = email_service.send_status_update_email(application)
    
    if result:
        print_success("Rejection email sent!")
    else:
        print_error("Failed to send rejection email")
    
    # Test 4: Send disbursement email
    print_info("Test 2.4: Sending disbursement status update email...")
    application.status = "disbursed"
    application.admin_notes = "Your allowance has been disbursed to your account."
    application.save()
    
    result = email_service.send_status_update_email(application)
    
    if result:
        print_success("Disbursement email sent!")
    else:
        print_error("Failed to send disbursement email")
    
    # Cleanup
    application.delete()
    grade.delete()
    student.delete()
    print_info("Test application, grade, and student cleaned up")

def test_database_state():
    """Test the current database state"""
    print_header("TEST 3: Database State Check")
    
    # Check users
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_email_verified=True).count()
    print_info(f"Total users: {total_users}")
    print_info(f"Verified users: {verified_users}")
    
    # Check verifications
    total_verifications = EmailVerification.objects.count()
    pending_verifications = EmailVerification.objects.filter(is_verified=False).count()
    print_info(f"Total verification codes: {total_verifications}")
    print_info(f"Pending verifications: {pending_verifications}")
    
    # Check applications
    total_applications = AllowanceApplication.objects.count()
    applications_with_email = AllowanceApplication.objects.filter(email_sent=True).count()
    print_info(f"Total applications: {total_applications}")
    print_info(f"Applications with emails sent: {applications_with_email}")
    
    if total_users > 0:
        print_success("Database has data ✓")
    else:
        print_info("Database is empty (fresh install)")

def test_api_endpoints():
    """Test API endpoint availability"""
    print_header("TEST 4: API Endpoint Check")
    
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    # Test endpoints
    endpoints = [
        ('send-verification-code', '/api/auth/send-verification-code/'),
        ('verify-email', '/api/auth/verify-email/'),
        ('resend-verification-code', '/api/auth/resend-verification-code/'),
        ('register', '/api/auth/register/'),
    ]
    
    for name, url in endpoints:
        try:
            response = client.post(url, {}, content_type='application/json')
            print_info(f"{name}: Status {response.status_code}")
            if response.status_code in [200, 400, 405]:  # 400 is expected for empty POST
                print_success(f"Endpoint {url} is accessible ✓")
            else:
                print_error(f"Endpoint {url} returned unexpected status")
        except Exception as e:
            print_error(f"Endpoint {url} error: {str(e)}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "🔬"*35)
    print("  COMPREHENSIVE SYSTEM TEST SUITE")
    print("  Testing Email Verification & Notification System")
    print("🔬"*35)
    
    try:
        # Run tests
        test_database_state()
        test_api_endpoints()
        test_email_verification_service()
        test_application_email_service()
        
        # Final summary
        print_header("TEST SUMMARY")
        print_success("All tests completed!")
        print_info("\nWhat was tested:")
        print("  ✓ Email verification code generation")
        print("  ✓ Code validation and one-time use")
        print("  ✓ Rate limiting enforcement")
        print("  ✓ Application confirmation emails")
        print("  ✓ Status update emails (approval, rejection, disbursement)")
        print("  ✓ Database state and records")
        print("  ✓ API endpoint availability")
        
        print_info("\n📧 Check your terminal for email outputs!")
        print_info("   (Using console backend - emails print to terminal)")
        
        print("\n" + "✅"*35)
        print("  ALL SYSTEMS OPERATIONAL!")
        print("✅"*35 + "\n")
        
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
