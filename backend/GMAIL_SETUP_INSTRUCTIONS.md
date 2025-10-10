
# How to Create a Gmail App Password for TCU-CEAA

## Prerequisites
- Gmail account with 2-Factor Authentication (2FA) enabled

## Steps:

### 1. Enable 2-Factor Authentication
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click "2-Step Verification"
4. Follow the prompts to set up 2FA if not already enabled

### 2. Generate App Password
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click "App passwords"
4. You may need to sign in again
5. At the bottom, click "Select app" and choose "Mail"
6. Click "Select device" and choose "Other (Custom name)"
7. Type "TCU-CEAA System" as the custom name
8. Click "Generate"
9. Google will display a 16-character password
10. Copy this password - you'll use it in the setup script

### 3. Important Security Notes
- Never share your app password with anyone
- This password is specifically for the TCU-CEAA application
- You can revoke this password anytime from your Google Account settings
- If you suspect it's compromised, revoke and generate a new one

### 4. Troubleshooting
- If you don't see "App passwords" option, make sure 2FA is enabled
- If emails aren't sending, check Django logs for error messages
- For development, you can use console backend instead of SMTP

### 5. Alternative for Development
If you want to test locally without real emails:
1. Open backend_project/settings.py
2. Comment out the SMTP configuration lines
3. Uncomment: EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
4. Emails will be printed to your Django console instead of being sent

### 6. Production Considerations
- In production, use environment variables for email credentials
- Never commit real email credentials to version control
- Consider using a dedicated service email account
- Set up proper monitoring for email delivery
