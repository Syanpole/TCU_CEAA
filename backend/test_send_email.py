"""
Simple Email Test Script
Sends a test email to verify email configuration
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

def test_send_email():
    """Send a test email to syanpole@gmail.com"""
    
    print("=" * 60)
    print("TCU-CEAA Email Test")
    print("=" * 60)
    print()
    
    # Check email configuration
    print("📧 Email Configuration:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   Host User: {settings.EMAIL_HOST_USER or '(Not configured)'}")
    print(f"   Host Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(Not configured)'}")
    print()
    
    # Check if credentials are configured
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("⚠️  WARNING: Email credentials not configured!")
        print("   Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Test cancelled")
            return
        print()
    
    # Prepare test email
    recipient = "syanpole@gmail.com"
    subject = "TCU-CEAA Email Test"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
Hello!

This is a test email from the TCU-CEAA Portal system.

Test Details:
- Timestamp: {timestamp}
- Email Backend: {settings.EMAIL_BACKEND}
- SMTP Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}
- TLS Enabled: {settings.EMAIL_USE_TLS}

If you received this email, the email configuration is working correctly! ✅

--
TCU-CEAA Portal
Automated Email System
"""
    
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .success {{ background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }}
        .info {{ background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #777; margin-top: 30px; font-size: 12px; }}
        h1 {{ margin: 0; font-size: 28px; }}
        h2 {{ color: #667eea; margin-top: 0; }}
        .emoji {{ font-size: 24px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="emoji">📧</span>
            <h1>TCU-CEAA Email Test</h1>
            <p>Portal Email System Verification</p>
        </div>
        <div class="content">
            <h2>Hello! 👋</h2>
            
            <p>This is a test email from the <strong>TCU-CEAA Portal</strong> system.</p>
            
            <div class="success">
                <strong>✅ Success!</strong> If you're reading this, the email system is working correctly!
            </div>
            
            <div class="info">
                <strong>📋 Test Details:</strong>
                <ul>
                    <li><strong>Timestamp:</strong> {timestamp}</li>
                    <li><strong>Email Backend:</strong> {settings.EMAIL_BACKEND.split('.')[-1]}</li>
                    <li><strong>SMTP Server:</strong> {settings.EMAIL_HOST}:{settings.EMAIL_PORT}</li>
                    <li><strong>TLS Enabled:</strong> {'Yes' if settings.EMAIL_USE_TLS else 'No'}</li>
                    <li><strong>Recipient:</strong> {recipient}</li>
                </ul>
            </div>
            
            <p>This confirms that:</p>
            <ul>
                <li>✅ Django email settings are configured correctly</li>
                <li>✅ SMTP connection is working</li>
                <li>✅ Email templates can be rendered</li>
                <li>✅ Emails can be delivered successfully</li>
            </ul>
            
            <p>You can now safely use the email features in the TCU-CEAA Portal!</p>
        </div>
        
        <div class="footer">
            <p>--<br>
            <strong>TCU-CEAA Portal</strong><br>
            Automated Email System<br>
            Test conducted on {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""
    
    print(f"📤 Sending test email to: {recipient}")
    print(f"📋 Subject: {subject}")
    print()
    print("Sending email... ", end="", flush=True)
    
    try:
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
        
        print("✅ SUCCESS!")
        print()
        print("=" * 60)
        print("✅ Email sent successfully!")
        print("=" * 60)
        print()
        print(f"📬 Check {recipient} for the test email")
        print("📝 The email includes both plain text and HTML versions")
        print()
        print("If you don't see the email:")
        print("  1. Check your spam/junk folder")
        print("  2. Wait a few minutes for delivery")
        print("  3. Verify email credentials are correct")
        print()
        
        return True
        
    except Exception as e:
        print("❌ FAILED!")
        print()
        print("=" * 60)
        print("❌ Error sending email")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  1. Invalid email credentials (EMAIL_HOST_USER/EMAIL_HOST_PASSWORD)")
        print("  2. Gmail App Password not configured (if using Gmail)")
        print("  3. SMTP server blocked or firewall issues")
        print("  4. Two-factor authentication required")
        print()
        print("💡 For Gmail:")
        print("   - Enable 2FA on your Google account")
        print("   - Create an App Password at: https://myaccount.google.com/apppasswords")
        print("   - Use the App Password as EMAIL_HOST_PASSWORD")
        print()
        
        return False


if __name__ == '__main__':
    result = test_send_email()
    sys.exit(0 if result else 1)
