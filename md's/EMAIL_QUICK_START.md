# 📧 Quick Start: Email Notifications for TCU-CEAA

## 🎯 What You Need to Do RIGHT NOW

### Step 1: Get Gmail App Password (5 minutes)

1. Go to: https://myaccount.google.com/apppasswords
2. If asked, enable 2-Factor Authentication first
3. Select "Mail" → "Windows Computer" → Generate
4. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

### Step 2: Update .env File (1 minute)

Open `backend\.env` and replace these lines:

```properties
EMAIL_HOST_USER=your-gmail-address@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
```

With your actual values:

```properties
EMAIL_HOST_USER=tcu.ceaa@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```

### Step 3: Restart Backend (30 seconds)

```powershell
cd backend
python manage.py runserver
```

## ✅ That's It! Now It Works

### What Happens:
- Student submits application ➡️ Sees message about email notification
- Admin approves application ➡️ **Email automatically sent to student**
- Student receives beautiful HTML email with approval details

### Test It:
1. Login as **Lloyd Kenneth Ramos** (ramoslloydkenneth1@gmail.com)
2. Submit an allowance application
3. Login as admin and approve it
4. Check email at ramoslloydkenneth1@gmail.com

## 🚨 Quick Troubleshooting

**Email not sending?**
- Check you used the **App Password**, not your Gmail password
- Make sure 2-Factor Auth is enabled on Gmail
- Verify no extra spaces in .env file
- Look for errors in Django terminal

**Want to test without sending real emails?**

In `backend/backend_project/settings.py`, change:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Restart server. Emails will print to terminal instead.

---

## 📋 Full Documentation

See `EMAIL_NOTIFICATION_SETUP.md` for complete details.
