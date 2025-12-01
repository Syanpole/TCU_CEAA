#!/usr/bin/env python
"""
Test email configuration for Django
Run this script to verify email settings are working
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    """Test the email configuration"""
    print("=" * 60)
    print("TESTING EMAIL CONFIGURATION")
    print("=" * 60)
    
    # Print current settings
    print(f"\nEmail Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"Email Host User: {settings.EMAIL_HOST_USER or 'NOT SET'}")
    print(f"Email Host Password: {'SET' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ ERROR: Email credentials are not configured!")
        print("Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env file")
        return False
    
    # Try to send a test email
    print("\n" + "=" * 60)
    print("SENDING TEST EMAIL")
    print("=" * 60)
    
    try:
        test_email = settings.EMAIL_HOST_USER
        print(f"\nSending test email to: {test_email}")
        
        send_mail(
            subject='TCU-CEAA Email Test',
            message='This is a test email from TCU-CEAA system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print("\n✅ SUCCESS: Test email sent successfully!")
        print(f"Check your inbox at: {test_email}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to send test email")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # Provide helpful troubleshooting tips
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING TIPS")
        print("=" * 60)
        
        if "Authentication" in str(e) or "Username and Password" in str(e):
            print("\n🔍 Authentication Error:")
            print("- Make sure you're using a Gmail App Password, not your regular password")
            print("- Enable 2-Factor Authentication on your Google account")
            print("- Generate an App Password at: https://myaccount.google.com/apppasswords")
            print("- Update EMAIL_HOST_PASSWORD in your .env file with the 16-character app password")
        
        elif "Connection" in str(e) or "timed out" in str(e):
            print("\n🔍 Connection Error:")
            print("- Check your internet connection")
            print("- Make sure port 587 is not blocked by firewall")
            print("- Try using port 465 with EMAIL_USE_SSL=True instead of EMAIL_USE_TLS")
        
        else:
            print("\n🔍 General Error:")
            print("- Verify EMAIL_HOST_USER is a valid Gmail address")
            print("- Check that .env file is in the backend directory")
            print("- Make sure python-dotenv is installed: pip install python-dotenv")
        
        return False

if __name__ == '__main__':
    success = test_email_config()
    sys.exit(0 if success else 1)
