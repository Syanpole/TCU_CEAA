"""
Quick test script to verify email sending works with the new App Password
"""
import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.email_utils import send_verification_code_email

print("=" * 60)
print("Testing Email Configuration...")
print("=" * 60)

# Test with your email
test_email = "ramoslloydkenneth1@gmail.com"
test_code = "123456"

print(f"\n📧 Sending test email to: {test_email}")
print(f"🔐 Test verification code: {test_code}")
print("\nAttempting to send email...\n")

success, error = send_verification_code_email(test_email, test_code)

print("=" * 60)
if success:
    print("✅ SUCCESS! Email sent successfully!")
    print("=" * 60)
    print("\n📬 Check your inbox at:", test_email)
    print("You should receive an email with verification code:", test_code)
    print("\n🎉 Your email configuration is working perfectly!")
else:
    print("❌ FAILED! Email sending failed")
    print("=" * 60)
    print(f"\n❗ Error: {error}")
    print("\n🔍 Possible issues:")
    print("  1. App Password might be incorrect")
    print("  2. Spaces in the password (should be removed)")
    print("  3. 2-Factor Authentication not enabled")
    print("  4. Gmail blocked the login attempt (check security alerts)")
    
print("=" * 60)
