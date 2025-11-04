# 📧 EmailJS Quick Reference Card

## ✅ System Status: 100% READY TO USE

---

## 🔑 Your Credentials (Already Configured)

```
SERVICE_ID: service_kvnsvjk
TEMPLATE_ID: template_n7hvacg
PUBLIC_KEY: bJOQ5VKqFricP7zZG
```

Location: `frontend/.env`

---

## 🎯 What It Does

**Automatic email confirmation sent to students immediately after submitting allowance application!**

---

## 🧪 Quick Test (30 seconds)

1. **Start Frontend:**
   ```powershell
   cd frontend
   npm start
   ```

2. **Login:** Use any student account (Lloyd Kenneth Ramos: ramoslloydkenneth1@gmail.com)

3. **Submit Application:** Applications → Apply for Allowance → Submit

4. **Check:** 
   - ✅ See success message with email confirmation
   - 📧 Check email inbox
   - 🔍 Check browser console (F12)

---

## 📋 Email Template Variables

Copy this to your EmailJS template:

**Subject:**
```
✅ TCU-CEAA Application Submitted - {{application_id}}
```

**Body Variables:**
- `{{to_email}}` - Student email
- `{{student_name}}` - Full name
- `{{application_id}}` - APP-123
- `{{application_type}}` - Type of allowance
- `{{amount}}` - ₱5,000.00
- `{{submission_date}}` - October 25, 2025
- `{{from_name}}` - TCU-CEAA Scholarship Office
- `{{reply_to}}` - ceaainfo@tcu.edu.ph

---

## ✅ Success Indicators

### In Console (F12):
```
📧 Sending confirmation email to: ramoslloydkenneth1@gmail.com
✅ Email sent successfully!
```

### On Screen:
```
✅ Application submitted successfully! 
A confirmation email has been sent to ramoslloydkenneth1@gmail.com
```

### In Email:
```
Subject: ✅ TCU-CEAA Application Submitted - APP-123
From: TCU-CEAA Scholarship Office

Dear Ramos, Lloyd Kenneth,
Congratulations! Your scholarship application has been successfully submitted...
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No email received | Check spam folder |
| Console shows error | Verify .env credentials |
| Template error | Check all `{{variables}}` exist in template |
| 403 Forbidden | Public key incorrect in .env |
| 404 Not Found | Service/Template ID incorrect |

---

## 📁 Files to Know

| File | Purpose |
|------|---------|
| `frontend/.env` | EmailJS credentials |
| `frontend/src/services/email/emailService.ts` | Email sending logic |
| `frontend/src/components/AllowanceApplicationForm.tsx` | Integration point |

---

## 🔗 Important Links

- **EmailJS Dashboard:** https://dashboard.emailjs.com/
- **Email History:** Dashboard → Email Services → View Logs
- **Template Editor:** Dashboard → Email Templates → Your Template
- **Documentation:** https://www.emailjs.com/docs/

---

## 💡 Quick Tips

✅ **Free tier:** 200 emails/month (perfect for TCU-CEAA)
✅ **No backend needed:** Works directly from React
✅ **Instant delivery:** Emails sent in seconds
✅ **Graceful failures:** App works even if email fails
✅ **Full data:** Uses real application info (ID, type, amount)

---

## 🎯 Test Account

**Student:** Lloyd Kenneth Ramos
**Email:** ramoslloydkenneth1@gmail.com

Use this account for testing!

---

**Status:** ✅ Ready to Use
**Date:** October 25, 2025
**Version:** v2.0
