# 📧 Gmail SMTP Setup Guide - Get Your App Password NOW!

## 🚀 Quick Setup (5 Minutes)

Follow these exact steps to enable email verification:

---

## Step 1: Enable 2-Factor Authentication (If Not Already Enabled)

### 1.1 Go to Google Account Security
```
URL: https://myaccount.google.com/security
```

### 1.2 Find "2-Step Verification"
- Scroll down to "How you sign in to Google"
- Click on "2-Step Verification"

### 1.3 Enable It
- Click "GET STARTED"
- Follow the prompts to set up:
  - Enter your password
  - Add your phone number
  - Enter verification code sent to your phone
- Click "TURN ON"

✅ **2-Factor Authentication is now enabled!**

---

## Step 2: Generate App Password for Django

### 2.1 Go to App Passwords Page
```
URL: https://myaccount.google.com/apppasswords
```

**OR:**
1. Go to https://myaccount.google.com/
2. Click "Security" (left sidebar)
3. Scroll to "How you sign in to Google"
4. Click "2-Step Verification"
5. Scroll down and click "App passwords"

### 2.2 Generate New App Password

**If you see the App Passwords option:**
1. Click "Select app" dropdown → Choose "Mail"
2. Click "Select device" dropdown → Choose "Other (Custom name)"
3. Type: `TCU-CEAA Django`
4. Click "GENERATE"

**You'll see a 16-character password like:**
```
abcd efgh ijkl mnop
```

### 2.3 Copy the Password
- Copy the entire 16-character password (without spaces)
- Example: `abcdefghijklmnop`

✅ **App Password generated!**

---

## Step 3: Update Your .env File

### 3.1 Open Your .env File
```
File: C:\xampp\htdocs\TCU_CEAA\backend\.env
```

### 3.2 Update EMAIL_HOST_PASSWORD
Replace `REPLACE_WITH_YOUR_APP_PASSWORD` with your actual app password:

```env
EMAIL_HOST_USER=ramoslloydkenneth1@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=TCU-CEAA <ramoslloydkenneth1@gmail.com>
```

**IMPORTANT:** 
- Remove spaces from the password
- Use the 16-character app password (NOT your Gmail password)
- Save the file

✅ **.env file updated!**

---

## Step 4: Restart Your Backend Server

### 4.1 Stop Backend (if running)
```powershell
# In your backend terminal, press Ctrl+C
```

### 4.2 Start Backend Again
```powershell
cd backend
python manage.py runserver
```

✅ **Backend restarted with new email config!**

---

## Step 5: Test Email Sending

### 5.1 Test Registration
1. Go to http://localhost:3000
2. Click "Register"
3. Fill in form with YOUR email
4. Click "Create Student Account"

### 5.2 Check Results

**Expected:**
- ✅ Verification modal appears
- ✅ Check your email inbox
- ✅ You should receive email with 6-digit code
- ✅ Enter code and complete registration

**If still failing:**
- Check backend terminal for error messages
- Verify app password is correct (no spaces)
- Try generating a new app password

---

## 🔧 Troubleshooting

### Issue 1: "App Passwords" option not showing

**Reason:** 2-Step Verification not enabled

**Solution:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" first
3. Wait 5 minutes
4. Try accessing App Passwords again

---

### Issue 2: "Authentication failed" error

**Possible causes:**
- Wrong app password
- App password has spaces
- Using regular Gmail password instead of app password

**Solution:**
1. Generate a NEW app password
2. Copy it WITHOUT spaces
3. Update .env file
4. Restart backend server

---

### Issue 3: Email not received

**Check:**
1. Spam/Junk folder
2. Email address is correct
3. Backend terminal shows "Email sent successfully"
4. Gmail hasn't blocked the email

**Solution:**
- Check spam folder
- Verify EMAIL_HOST_USER in .env is correct
- Test with different email address
- Check Gmail account for security alerts

---

### Issue 4: "SMTPAuthenticationError"

**Error message:**
```
(535, b'5.7.8 Username and Password not accepted')
```

**Solution:**
1. You're using regular password, not app password
2. Generate app password from https://myaccount.google.com/apppasswords
3. Use the 16-character app password

---

## 📋 Quick Checklist

Before testing, verify:

- [ ] 2-Factor Authentication is enabled on Gmail
- [ ] App Password generated from Google
- [ ] App Password copied WITHOUT spaces
- [ ] EMAIL_HOST_PASSWORD updated in .env file
- [ ] EMAIL_HOST_USER is correct: `ramoslloydkenneth1@gmail.com`
- [ ] Backend server restarted after .env changes
- [ ] No typos in .env file
- [ ] .env file saved

---

## 🎯 Current Configuration

Your `.env` should look like this:

```env
# Email Configuration
EMAIL_HOST_USER=ramoslloydkenneth1@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop  ← Replace with YOUR app password
DEFAULT_FROM_EMAIL=TCU-CEAA <ramoslloydkenneth1@gmail.com>
```

**Django settings.py** (already configured):
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

---

## 🧪 Test Email Manually (Optional)

You can test email sending from Django shell:

```powershell
cd backend
python manage.py shell
```

```python
from myapp.email_utils import send_verification_code_email

# Test sending email
success, error = send_verification_code_email('YOUR_EMAIL@gmail.com', '123456')

if success:
    print("✅ Email sent successfully!")
else:
    print(f"❌ Failed: {error}")
```

---

## ✅ Success Indicators

When everything works, you'll see:

**Backend Terminal:**
```
INFO - Verification code sent successfully to user@example.com
```

**Your Email Inbox:**
```
Subject: TCU-CEAA Email Verification Code
From: TCU-CEAA <ramoslloydkenneth1@gmail.com>

Your Verification Code: 123456
```

**Frontend:**
```
✅ Verification modal appears
✅ "Verification code sent to your email!" message
```

---

## 🔗 Important Links

- **App Passwords:** https://myaccount.google.com/apppasswords
- **Security Settings:** https://myaccount.google.com/security
- **2-Step Verification:** https://myaccount.google.com/signinoptions/two-step-verification

---

## 📞 Still Not Working?

If emails still aren't sending after following all steps:

1. **Check Backend Logs:**
   - Look at terminal where `python manage.py runserver` is running
   - Look for specific error messages

2. **Verify .env File:**
   - Open `backend\.env`
   - Ensure no extra spaces or quotes
   - Ensure file is saved

3. **Alternative: Use Console Email Backend (for testing only)**
   
   Update `backend/backend_project/settings.py`:
   ```python
   # Temporarily for testing
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```
   
   Emails will print in terminal instead of sending.
   **Change back to SMTP for production!**

---

## 🎉 You're All Set!

Once you:
1. ✅ Enable 2-Factor Authentication
2. ✅ Generate App Password
3. ✅ Update .env file
4. ✅ Restart backend

Your email verification system will work perfectly! 🚀

**Go ahead and test it now!**
