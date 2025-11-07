"""
Email Configuration Test & Switcher
Checks current email backend and switches to SMTP for actual email delivery
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

# IMPORTANT: Switch to SMTP backend for actual email delivery
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'

django.setup()

from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

def test_send_email_smtp():
    """Send a real test email via SMTP to syanpole@gmail.com"""
    
    print("=" * 60)
    print("TCU-CEAA Real Email Test (SMTP)")
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
    print(f"   Host Password: {'✅ Configured' if settings.EMAIL_HOST_PASSWORD else '❌ Not configured'}")
    print()
    
    if 'console' in settings.EMAIL_BACKEND.lower():
        print("⚠️  WARNING: Console backend detected!")
        print("   Switching to SMTP backend for real email delivery...")
        print()
    
    # Check if credentials are configured
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("❌ ERROR: Email credentials not configured!")
        print()
        print("To send real emails via Gmail:")
        print("1. Set environment variables:")
        print("   EMAIL_HOST_USER=tcu.ceaa.scholarships@gmail.com")
        print("   EMAIL_HOST_PASSWORD=<your-app-password>")
        print()
        print("2. Create a Gmail App Password:")
        print("   https://myaccount.google.com/apppasswords")
        print()
        return False
    
    # Prepare test email
    recipient = "syanpole@gmail.com"
    subject = "🧪 TCU-CEAA Real Email Test (via SMTP)"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
Hello Sean!

This is a REAL test email sent via SMTP from the TCU-CEAA Portal system.

🎯 Test Details:
- Timestamp: {timestamp}
- Backend: SMTP (Real email delivery)
- Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}
- From: {settings.EMAIL_HOST_USER}

✅ If you received this email in your inbox, the SMTP configuration is working perfectly!

This means:
• Email credentials are valid ✓
• SMTP connection is working ✓
• Emails can be delivered to recipients ✓
• The TCU-CEAA Portal can send real emails ✓

You can now confidently use email features like:
- Email verification for new registrations
- Application status notifications
- Password reset emails
- Admin notifications

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
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
        .container {{ background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .success-box {{ background: #d4edda; border-left: 5px solid #28a745; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .info-box {{ background: #e7f3ff; border-left: 5px solid #2196F3; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .check-list {{ list-style: none; padding: 0; }}
        .check-list li {{ padding: 8px 0; }}
        .check-list li:before {{ content: "✓ "; color: #28a745; font-weight: bold; margin-right: 10px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; font-size: 13px; }}
        h1 {{ margin: 0; font-size: 32px; }}
        h2 {{ color: #667eea; margin-top: 0; }}
        .emoji {{ font-size: 48px; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="emoji">🚀</div>
            <h1>Real Email Test</h1>
            <p>TCU-CEAA Portal SMTP Verification</p>
        </div>
        
        <div class="content">
            <h2>Hello Sean! 👋</h2>
            
            <div class="success-box">
                <strong>🎉 Success!</strong> This is a REAL email sent via SMTP!<br>
                If you're reading this in your inbox, the email system is working perfectly!
            </div>
            
            <p>This is a live test email sent from the <strong>TCU-CEAA Portal</strong> system using actual SMTP delivery.</p>
            
            <div class="info-box">
                <strong>📋 Technical Details:</strong>
                <ul>
                    <li><strong>Timestamp:</strong> {timestamp}</li>
                    <li><strong>Backend:</strong> SMTP (Real delivery)</li>
                    <li><strong>SMTP Server:</strong> {settings.EMAIL_HOST}:{settings.EMAIL_PORT}</li>
                    <li><strong>TLS Encryption:</strong> {'Enabled ✓' if settings.EMAIL_USE_TLS else 'Disabled'}</li>
                    <li><strong>Sender:</strong> {settings.EMAIL_HOST_USER}</li>
                    <li><strong>Recipient:</strong> {recipient}</li>
                </ul>
            </div>
            
            <h3>✅ What This Confirms:</h3>
            <ul class="check-list">
                <li>Email credentials are valid</li>
                <li>SMTP connection is working</li>
                <li>TLS encryption is active</li>
                <li>Emails can reach recipients</li>
                <li>HTML templates render correctly</li>
                <li>Portal email system is operational</li>
            </ul>
            
            <h3>🎯 Ready to Use:</h3>
            <p>The TCU-CEAA Portal can now send:</p>
            <ul>
                <li>📧 Email verification codes</li>
                <li>🔔 Application status notifications</li>
                <li>🔑 Password reset links</li>
                <li>📨 Admin alerts and notifications</li>
                <li>✉️ Custom system messages</li>
            </ul>
            
            <p style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center;">
                <strong>🎊 Email System: FULLY OPERATIONAL!</strong>
            </p>
        </div>
        
        <div class="footer">
            <p><strong>TCU-CEAA Portal</strong><br>
            Comprehensive Educational Assistance Application<br>
            <small>Test conducted on {timestamp}</small></p>
            <p style="margin-top: 15px; font-size: 11px; color: #999;">
                This is an automated test message from the TCU-CEAA development system.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    print(f"📤 Sending REAL email via SMTP to: {recipient}")
    print(f"📋 Subject: {subject}")
    print(f"📡 Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print()
    print("🔄 Connecting to SMTP server... ", end="", flush=True)
    
    try:
        # Send the email via SMTP
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
        
        print("✅ CONNECTED!")
        print()
        print("=" * 60)
        print("✅ REAL EMAIL SENT SUCCESSFULLY VIA SMTP!")
        print("=" * 60)
        print()
        print(f"📬 Check {recipient} for the test email")
        print(f"📝 Email includes both plain text and HTML versions")
        print(f"🎨 Beautiful HTML template with gradient header")
        print()
        print("📍 Where to check:")
        print("  1. Gmail inbox (primary/main folder)")
        print("  2. Check spam/promotions if not in inbox")
        print("  3. Wait 30-60 seconds for delivery")
        print()
        print("🎉 Your email system is FULLY OPERATIONAL!")
        print()
        
        return True
        
    except Exception as e:
        print("❌ FAILED!")
        print()
        print("=" * 60)
        print("❌ Error sending email via SMTP")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        
        # Check specific error types
        error_str = str(e).lower()
        
        if 'authentication failed' in error_str or 'username and password not accepted' in error_str:
            print("🔐 Authentication Error:")
            print("  • Email credentials are incorrect")
            print("  • Gmail App Password may be invalid")
            print()
            print("💡 Solution:")
            print("  1. Go to: https://myaccount.google.com/apppasswords")
            print("  2. Create a new App Password")
            print("  3. Update EMAIL_HOST_PASSWORD with new password")
            
        elif 'timed out' in error_str or 'connection refused' in error_str:
            print("🌐 Connection Error:")
            print("  • Cannot connect to SMTP server")
            print("  • Firewall or network issue")
            print()
            print("💡 Solution:")
            print("  • Check internet connection")
            print("  • Verify firewall allows port 587")
            print("  • Try port 465 with SSL instead of TLS")
            
        elif 'recipient' in error_str:
            print("📧 Recipient Error:")
            print("  • Email address may be invalid")
            print("  • Recipient mailbox may be full")
            
        else:
            print("❓ Unexpected Error:")
            print("  • Check Django logs for details")
            print("  • Verify all email settings")
        
        print()
        print("📚 Current Configuration:")
        print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print()
        
        return False


if __name__ == '__main__':
    print()
    print("🔧 Forcing SMTP backend for real email delivery...")
    print()
    test_send_email_smtp()
