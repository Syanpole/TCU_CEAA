# 📧 Gmail App Password Setup for TCU-CEAA Email System

## Current Status
❌ **Error**: Application-specific password required  
🔐 **Issue**: The current `EMAIL_HOST_PASSWORD` is not a valid Gmail App Password

---

## ✅ How to Fix - Create Gmail App Password

### Step 1: Enable 2-Step Verification
1. Go to your Google Account: https://myaccount.google.com
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", enable **2-Step Verification**
4. Follow the prompts to set up 2FA

### Step 2: Create App Password
1. Go to: **https://myaccount.google.com/apppasswords**
2. You may need to sign in again
3. In the "Select app" dropdown, choose **Other (Custom name)**
4. Enter: `TCU-CEAA Portal`
5. Click **Generate**
6. Google will show you a **16-character password** (e.g., `abcd efgh ijkl mnop`)
7. **COPY THIS PASSWORD** - you won't see it again!

### Step 3: Update Environment Variable

#### Option A: Set in Current PowerShell Session
```powershell
$env:EMAIL_HOST_PASSWORD = "your-16-char-app-password-here"
```

#### Option B: Create .env File (Recommended)
Create file: `D:\xp\htdocs\TCU_CEAA\backend\.env`

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tcu.ceaa.scholarships@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password-here
DEFAULT_FROM_EMAIL=TCU-CEAA Portal <noreply@tcu-ceaa.edu.ph>
```

#### Option C: Set Permanent Windows Environment Variable
1. Press `Win + X` and select **System**
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under "User variables", click **New**
5. Variable name: `EMAIL_HOST_PASSWORD`
6. Variable value: Your 16-character app password
7. Click **OK** and restart PowerShell

---

## 🧪 Test After Setup

### Quick Test (PowerShell)
```powershell
# Set the password
$env:EMAIL_HOST_PASSWORD = "your-app-password"

# Run the test
cd D:\xp\htdocs\TCU_CEAA\backend
python test_send_email_smtp.py
```

### Expected Output
```
✅ REAL EMAIL SENT SUCCESSFULLY VIA SMTP!
📬 Check syanpole@gmail.com for the test email
🎉 Your email system is FULLY OPERATIONAL!
```

---

## 📋 Current Configuration

**Email Account**: tcu.ceaa.scholarships@gmail.com  
**SMTP Server**: smtp.gmail.com:587  
**TLS**: Enabled  
**Backend**: SMTP (Real delivery)

---

## ⚠️ Important Notes

1. **Never commit the App Password to Git!**
   - Add `.env` to `.gitignore`
   - Keep passwords secret

2. **App Password vs Regular Password**
   - Do NOT use your regular Gmail password
   - App Passwords are more secure for automated systems
   - They can be revoked without changing your main password

3. **Security Best Practice**
   - Create one App Password per application
   - Label it clearly (e.g., "TCU-CEAA Portal")
   - Revoke App Passwords you're not using

4. **Testing vs Production**
   - Use console backend for local testing
   - Use SMTP backend for staging/production
   - Set `EMAIL_BACKEND` environment variable to switch

---

## 🔧 Troubleshooting

### "Invalid credentials" error
- Double-check you copied the full 16-character password
- Remove any spaces from the password
- Generate a new App Password if needed

### "2-Step Verification required" error
- You must enable 2FA on the Google account first
- Go to: https://myaccount.google.com/security

### Still not working?
1. Check if email account is active
2. Verify no typos in EMAIL_HOST_USER
3. Try generating a new App Password
4. Check your internet connection/firewall

---

## 📚 Related Files

- **Email Service**: `backend/myapp/application_email_service.py`
- **Settings**: `backend/backend_project/settings.py`
- **Test Scripts**: 
  - `backend/test_send_email.py` (console)
  - `backend/test_send_email_smtp.py` (SMTP)

---

## 🎯 Next Steps

1. ✅ Create Gmail App Password
2. ✅ Set `EMAIL_HOST_PASSWORD` environment variable
3. ✅ Run `python test_send_email_smtp.py`
4. ✅ Check syanpole@gmail.com inbox
5. ✅ Start using email features in the portal!

---

**Need help?** Check the Google support page:  
https://support.google.com/mail/?p=InvalidSecondFactor
