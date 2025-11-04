# 📧 TCU-CEAA Email Notification - Visual Flow Guide

## 🎯 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    STUDENT SUBMITS APPLICATION                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend: AllowanceApplicationForm.tsx                          │
│  ✅ Application Submitted Successfully!                          │
│  📧 "You will receive an email notification once approved"       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend: POST /applications/                                    │
│  • Creates AllowanceApplication record                           │
│  • Status: "pending"                                             │
│  • email_sent: False                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ADMIN REVIEWS APPLICATION                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend: ApplicationsManagement.tsx                            │
│  Admin clicks "Approve" button                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend: POST /applications/{id}/process/                       │
│  views.py: AllowanceApplicationViewSet.process()                 │
│                                                                   │
│  1. Update status to "approved"                                  │
│  2. Call send_approval_email(application)                        │
│  3. Track email status                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend: email_utils.py                                         │
│  send_approval_email(application)                                │
│                                                                   │
│  1. Get student details (name, email)                            │
│  2. Load HTML template: approved_email.html                      │
│  3. Render with context (name, type, amount)                     │
│  4. Create EmailMultiAlternatives                                │
│  5. Send via Gmail SMTP                                          │
│  6. Update application.email_sent = True                         │
│  7. Set application.email_sent_at = now()                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GMAIL SMTP SERVER                             │
│  smtp.gmail.com:587                                              │
│  Authenticates with App Password                                 │
│  Sends email to student                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STUDENT RECEIVES EMAIL                        │
│  To: ramoslloydkenneth1@gmail.com                                │
│  Subject: "Congratulations! Your TCU-CEAA Application Approved!" │
│                                                                   │
│  Content:                                                        │
│  • Congratulations message                                       │
│  • ✅ Status: APPROVED                                           │
│  • 📋 Type: Basic Educational Assistance                         │
│  • 💰 Amount: ₱5,000.00                                          │
│  • Next steps                                                    │
│  • Contact information                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Email Template Structure

```
┌───────────────────────────────────────────────────────────┐
│                     EMAIL PREVIEW                         │
├───────────────────────────────────────────────────────────┤
│                                                           │
│                         🎓                                │
│                Taguig City University                     │
│                                                           │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                           │
│   Congratulations! Your TCU-CEAA Application             │
│   Has Been Approved!                                      │
│                                                           │
│   Dear Lloyd Kenneth Ramos,                               │
│                                                           │
│   Congratulations! We are happy to inform you that        │
│   your application for the Taguig City University –       │
│   City Educational Assistance Allowance (TCU-CEAA)        │
│   has been approved.                                      │
│                                                           │
│   ┌─────────────────────────────────────────────┐       │
│   │  ✅ Application Status: APPROVED            │       │
│   │  📋 Application Type: Basic Educational     │       │
│   │     Assistance (₱5,000)                     │       │
│   │  💰 Amount: ₱5,000.00                       │       │
│   └─────────────────────────────────────────────┘       │
│                                                           │
│   Your documents have been reviewed and verified.         │
│   You are now an official beneficiary of the              │
│   TCU-CEAA program.                                       │
│                                                           │
│   Next Steps:                                             │
│   • Wait for further instructions regarding the           │
│     release schedule                                      │
│   • Make sure your student information is updated         │
│   • Check your dashboard regularly for updates            │
│   • Ensure contact information is up to date              │
│                                                           │
│   For questions: ceaainfo@tcu.edu.ph                      │
│                                                           │
│   Best regards,                                           │
│   Scholarship and Financial Assistance Office             │
│   Taguig City University (TCU-CEAA)                       │
│                                                           │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│   © 2025 Taguig City University – CEAA                    │
│   This is an automated message                            │
└───────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Quick Reference

### Backend `.env` File:
```properties
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=TCU-CEAA <noreply@tcu.edu.ph>
```

### Backend `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
```

---

## 📊 Database Schema

```
AllowanceApplication
├── id (Primary Key)
├── student (Foreign Key → CustomUser)
├── grade_submission (Foreign Key → GradeSubmission)
├── application_type (CharField)
├── amount (DecimalField)
├── status (CharField) ← "approved" triggers email
├── applied_at (DateTimeField)
├── processed_at (DateTimeField)
├── processed_by (Foreign Key → CustomUser)
├── email_sent (BooleanField) ← NEW: Tracks if email sent
├── email_sent_at (DateTimeField) ← NEW: When email was sent
└── notification_error (TextField) ← NEW: Error message if failed
```

---

## 🎭 User Interface Updates

### Application Form (Student View):
```
┌────────────────────────────────────────────────┐
│  ✅ Application Submitted Successfully!        │
│                                                │
│  📧 You will receive an email notification     │
│     at your registered email address once      │
│     your application is approved by admin.     │
└────────────────────────────────────────────────┘
```

### Student Dashboard:
```
┌────────────────────────────────────────────────┐
│  ✅ Allowance Application Submitted!           │
│                                                │
│  Your allowance application has been           │
│  submitted successfully. It will be            │
│  reviewed by admin within 3-5 business         │
│  days. You will receive an email               │
│  notification at your registered email         │
│  address once your application is approved.    │
└────────────────────────────────────────────────┘
```

---

## 🧪 Testing Workflow

### Step 1: Configure Email
```
1. Go to: https://myaccount.google.com/apppasswords
2. Generate App Password
3. Copy 16-character code
4. Update backend/.env
5. Restart Django server
```

### Step 2: Create Test Application
```
1. Login as: Lloyd Kenneth Ramos
2. Email: ramoslloydkenneth1@gmail.com
3. Navigate to Applications
4. Click "Apply for Allowance"
5. Submit application
6. See notification about email on approval
```

### Step 3: Admin Approval
```
1. Login as admin
2. Go to Applications Management
3. Find Lloyd's application
4. Click "Approve" button
5. Verify success message
6. Check logs for email status
```

### Step 4: Verify Email
```
1. Open Gmail: ramoslloydkenneth1@gmail.com
2. Check inbox for new email
3. Verify sender: TCU-CEAA
4. Check email content and formatting
5. Verify all details are correct
```

---

## 🔍 Debugging Checklist

### If Email Not Received:

1. **Check Django Logs:**
   ```
   Look in terminal where Django is running
   Search for: "Approval email sent" or error messages
   ```

2. **Verify Configuration:**
   ```
   ✓ EMAIL_HOST_USER is set in .env
   ✓ EMAIL_HOST_PASSWORD is set in .env
   ✓ Password is App Password, not Gmail password
   ✓ 2-Factor Auth is enabled on Gmail
   ✓ No extra spaces or quotes in .env
   ```

3. **Check Student Email:**
   ```
   ✓ Student has email in profile
   ✓ Email is valid format
   ✓ Email is not in spam folder
   ```

4. **Test Email System:**
   ```python
   # In Django shell: python manage.py shell
   from django.core.mail import send_mail
   
   send_mail(
       'Test',
       'Test message',
       'your-email@gmail.com',
       ['recipient@gmail.com'],
   )
   ```

---

## 📈 Success Metrics

### What Success Looks Like:

✅ **Student Experience:**
- Application submitted with clear notification
- Email received within seconds of approval
- Email is professional and readable
- Next steps are clear

✅ **Admin Experience:**
- One-click approval sends email automatically
- No manual email sending needed
- Status tracking in database

✅ **System Health:**
- No errors in logs
- Email delivery confirmed
- Database tracking working
- Error handling graceful

---

## 🎉 Final Result

### Email Sent Successfully:
```
INFO: Approval email sent successfully to ramoslloydkenneth1@gmail.com 
      for application 123
```

### Database Updated:
```
AllowanceApplication #123
├── status: "approved"
├── email_sent: True
├── email_sent_at: 2025-10-19 14:30:00
└── notification_error: NULL
```

### Student Receives:
```
📧 New Email
From: TCU-CEAA <noreply@tcu.edu.ph>
Subject: Congratulations! Your TCU-CEAA Application Has Been Approved!

[Beautiful HTML email with all details]
```

---

**Documentation Created:** October 19, 2025
**System:** TCU-CEAA Application Management
**Status:** ✅ Implementation Complete - Ready for Testing
