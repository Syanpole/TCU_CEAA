"""
Quick Email Password Setup
Interactive script to set Gmail App Password and test email
"""
import os
import sys

def setup_email_password():
    """Interactive setup for Gmail App Password"""
    
    print()
    print("=" * 60)
    print("TCU-CEAA Email Password Setup")
    print("=" * 60)
    print()
    
    print("📧 Current Email Account: tcu.ceaa.scholarships@gmail.com")
    print()
    
    # Check current password
    current_password = os.environ.get('EMAIL_HOST_PASSWORD', '')
    if current_password:
        masked = current_password[:2] + '*' * (len(current_password) - 4) + current_password[-2:] if len(current_password) > 4 else '*' * len(current_password)
        print(f"✅ Password currently set: {masked}")
        print()
        response = input("Update password? (y/n): ")
        if response.lower() != 'y':
            print("Using existing password...")
            return current_password
        print()
    else:
        print("❌ No password currently set")
        print()
    
    print("=" * 60)
    print("How to Get Gmail App Password:")
    print("=" * 60)
    print()
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Enable 2-Step Verification (if not already)")
    print("3. Create new App Password:")
    print("   - App: Other (Custom)")
    print("   - Name: TCU-CEAA Portal")
    print("4. Copy the 16-character password")
    print()
    print("The password looks like: abcd efgh ijkl mnop")
    print("(You can paste it with or without spaces)")
    print()
    print("=" * 60)
    print()
    
    # Get password
    password = input("Enter Gmail App Password (or 'skip' to skip): ").strip()
    
    if password.lower() == 'skip':
        print()
        print("⏭️  Skipping password setup")
        print("   (Email test will use console backend)")
        return None
    
    # Remove spaces from password
    password = password.replace(' ', '')
    
    if len(password) != 16:
        print()
        print(f"⚠️  Warning: Gmail App Passwords are usually 16 characters")
        print(f"   You entered {len(password)} characters")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return None
    
    # Set environment variable for this session
    os.environ['EMAIL_HOST_PASSWORD'] = password
    os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
    
    print()
    print("✅ Password set for this session!")
    print()
    print("💡 To make it permanent, add to your environment:")
    print(f"   $env:EMAIL_HOST_PASSWORD = \"{password}\"")
    print()
    print("   Or create a .env file (see EMAIL_SETUP_GUIDE.md)")
    print()
    
    return password


def test_email():
    """Run the email test"""
    print()
    print("=" * 60)
    print("Running Email Test...")
    print("=" * 60)
    print()
    
    # Import and run the SMTP test
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import after setting environment
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
    django.setup()
    
    from django.core.mail import send_mail
    from django.conf import settings
    from datetime import datetime
    
    recipient = "syanpole@gmail.com"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"📤 Sending to: {recipient}")
    print(f"📡 Via: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"🔒 Backend: {settings.EMAIL_BACKEND.split('.')[-1]}")
    print()
    
    if 'console' in settings.EMAIL_BACKEND.lower():
        print("⚠️  Using console backend (email will only print)")
        print("   Set EMAIL_HOST_PASSWORD to use real SMTP")
        print()
    
    try:
        subject = "🧪 TCU-CEAA Email Test"
        message = f"""
Hello Sean!

This is a test email from TCU-CEAA Portal.

Sent at: {timestamp}
Backend: {settings.EMAIL_BACKEND}

If you received this, the email system works! ✅

--
TCU-CEAA Portal
"""
        
        html = f"""
<html>
<body style="font-family: Arial; padding: 20px; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="margin: 0; font-size: 32px;">🎉 Email Test</h1>
        <p>TCU-CEAA Portal System</p>
    </div>
    <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 10px 10px;">
        <h2>Hello Sean! 👋</h2>
        <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0;">
            <strong>✅ Success!</strong> Email system is working!
        </div>
        <p><strong>Test Details:</strong></p>
        <ul>
            <li>Timestamp: {timestamp}</li>
            <li>Backend: {settings.EMAIL_BACKEND.split('.')[-1]}</li>
            <li>Server: {settings.EMAIL_HOST}</li>
        </ul>
        <p>The TCU-CEAA Portal can now send emails! 🎊</p>
    </div>
</body>
</html>
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html,
            fail_silently=False,
        )
        
        print("✅ Email sent successfully!")
        print()
        print("📬 Check your inbox at syanpole@gmail.com")
        print("   (Check spam folder if not in inbox)")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        
        error_str = str(e).lower()
        if 'authentication' in error_str or 'password' in error_str:
            print("🔐 Authentication failed!")
            print("   • Check your App Password is correct")
            print("   • Make sure 2FA is enabled on Gmail")
            print("   • Try generating a new App Password")
        elif 'application-specific' in error_str:
            print("🔐 Need Gmail App Password!")
            print("   • Regular Gmail passwords don't work")
            print("   • Create an App Password at:")
            print("     https://myaccount.google.com/apppasswords")
        
        print()
        print("📖 See EMAIL_SETUP_GUIDE.md for detailed instructions")
        print()
        return False


if __name__ == '__main__':
    try:
        password = setup_email_password()
        
        if password or os.environ.get('EMAIL_HOST_PASSWORD'):
            response = input("Run email test now? (y/n): ")
            if response.lower() == 'y':
                test_email()
        else:
            print()
            print("⏭️  Email test skipped (no password configured)")
            print()
        
        print()
        print("=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print()
        print("📚 Next steps:")
        print("   1. Run: python test_send_email_smtp.py")
        print("   2. Check: syanpole@gmail.com")
        print("   3. See: EMAIL_SETUP_GUIDE.md for more info")
        print()
        
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Setup cancelled")
        print()
