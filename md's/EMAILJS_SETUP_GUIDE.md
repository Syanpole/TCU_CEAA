# 📧 EmailJS Complete Setup Guide for TCU-CEAA

## 🎯 What This Does

This system sends an **instant email notification** to students immediately after they submit an allowance application. The email is sent using **EmailJS** (a free service) and requires no backend code!

### Email Flow:
```
Student submits application → EmailJS sends confirmation email → Student receives email instantly
```

---

## 📋 Step-by-Step Setup Instructions

### Step 1: Create EmailJS Account (5 minutes)

1. **Go to EmailJS website:**
   - Visit: https://www.emailjs.com/
   
2. **Sign Up for Free:**
   - Click "Sign Up Free"
   - Use your email (can be Gmail)
   - Verify your email address
   - Free tier includes: **200 emails/month**

3. **Login to Dashboard:**
   - After verification, login to: https://dashboard.emailjs.com/

---

### Step 2: Add Email Service (Gmail) (3 minutes)

1. **Navigate to Email Services:**
   - In the dashboard, click **"Email Services"** in the sidebar
   
2. **Add New Service:**
   - Click **"Add New Service"**
   - Select **"Gmail"**
   
3. **Connect Your Gmail:**
   - Click **"Connect Account"**
   - Login with your Gmail account
   - Grant permissions to EmailJS
   
4. **Service Created:**
   - You'll get a **Service ID** (example: `service_abc1234`)
   - **Copy and save this ID** - you'll need it later!
   
5. **Example Service ID:**
   ```
   service_xyz123abc
   ```

---

### Step 3: Create Email Template (5 minutes)

1. **Navigate to Email Templates:**
   - Click **"Email Templates"** in sidebar
   
2. **Create New Template:**
   - Click **"Create New Template"**
   
3. **Template Name:**
   ```
   TCU-CEAA Application Confirmation
   ```

4. **Template Content - Use This Exact Format:**

   **Subject:**
   ```
   ✅ TCU-CEAA Application Submitted Successfully - {{application_id}}
   ```

   **Content (Body):**
   ```
   Dear {{student_name}},

   Congratulations! Your scholarship application has been successfully submitted to the Taguig City University - City Educational Assistance Allowance (TCU-CEAA) program.

   📋 Application Details:
   • Application ID: {{application_id}}
   • Application Type: {{application_type}}
   • Amount: {{amount}}
   • Submitted Date: {{submission_date}}

   ✅ Next Steps:
   Your application is now under review by the CEAA office. You can expect:
   • Review completion within 3-5 business days
   • Email notification when your application status changes
   • Updates available in your student dashboard

   📊 Track Your Application:
   Login to your TCU-CEAA dashboard at any time to check your application status and view updates.

   ⚠️ Important Reminders:
   • Ensure all your contact information is up to date
   • Check your email regularly for updates
   • Keep your student ID and application number for reference

   For questions or concerns, please contact:
   📧 Email: ceaainfo@tcu.edu.ph
   🌐 Website: www.tcu.edu.ph

   Thank you for using the TCU-CEAA online application system!

   Best regards,
   Scholarship and Financial Assistance Office
   Taguig City University (TCU-CEAA)

   ---
   © 2025 Taguig City University
   This is an automated message. Please do not reply to this email.
   ```

5. **Template Variables to Add:**
   
   Click on the variables section and make sure you have:
   - `{{student_name}}` - Student's full name
   - `{{application_id}}` - Application ID/number
   - `{{application_type}}` - Type of allowance
   - `{{amount}}` - Amount in pesos
   - `{{submission_date}}` - Date submitted
   - `{{to_email}}` - Recipient email (student's email)
   - `{{reply_to}}` - Reply-to email (optional)

6. **Save Template:**
   - Click **"Save"**
   - You'll get a **Template ID** (example: `template_xyz789`)
   - **Copy and save this ID!**

7. **Example Template ID:**
   ```
   template_abc789xyz
   ```

---

### Step 4: Get Your Public Key (1 minute)

1. **Navigate to Account:**
   - Click on your profile/account in the top right
   - Select **"Account"** or **"General"**

2. **Find Public Key:**
   - Look for **"Public Key"** or **"API Keys"**
   - Copy the public key (example: `AbCdEfGhIjK1234567`)

3. **Example Public Key:**
   ```
   Your_Public_Key_Here_123456789
   ```

---

### Step 5: Test Your Setup (2 minutes)

1. **In EmailJS Dashboard:**
   - Go to your template
   - Click **"Test it"** button

2. **Fill Test Values:**
   ```
   student_name: Test Student
   application_id: APP-001
   application_type: Basic Educational Assistance
   amount: ₱5,000.00
   submission_date: October 25, 2025
   to_email: your-email@gmail.com
   ```

3. **Send Test:**
   - Click **"Send Test Email"**
   - Check your email inbox
   - Verify the email looks correct

---

## 🔑 Your EmailJS Credentials

After completing the setup, you should have:

```javascript
SERVICE_ID: "service_xyz123abc"      // From Step 2
TEMPLATE_ID: "template_abc789xyz"     // From Step 3
PUBLIC_KEY: "Your_Public_Key_123"     // From Step 4
```

**⚠️ Important:** Keep these credentials safe but note they're meant to be public (used in frontend)!

---

## 📝 EmailJS Template Variable Reference

### Variables You MUST Include in Your Template:

| Variable Name | Description | Example Value |
|--------------|-------------|---------------|
| `{{student_name}}` | Full name of student | "Ramos, Lloyd Kenneth" |
| `{{application_id}}` | Application ID number | "APP-2025-001" |
| `{{application_type}}` | Type of allowance | "Basic Educational Assistance (₱5,000)" |
| `{{amount}}` | Amount in pesos | "₱5,000.00" |
| `{{submission_date}}` | Date submitted | "October 25, 2025" |
| `{{to_email}}` | Student's email | "ramoslloydkenneth1@gmail.com" |
| `{{reply_to}}` | Reply-to address | "ceaainfo@tcu.edu.ph" |

---

## 🎨 Email Preview

Your students will receive an email like this:

```
From: Your Name (via EmailJS)
To: ramoslloydkenneth1@gmail.com
Subject: ✅ TCU-CEAA Application Submitted Successfully - APP-2025-001

Dear Ramos, Lloyd Kenneth,

Congratulations! Your scholarship application has been successfully submitted...

📋 Application Details:
• Application ID: APP-2025-001
• Application Type: Basic Educational Assistance (₱5,000)
• Amount: ₱5,000.00
• Submitted Date: October 25, 2025

[Rest of the content...]
```

---

## 🚀 Integration with Your System

After completing the EmailJS setup, you'll need to:

1. **Install EmailJS SDK** (if using npm):
   ```bash
   npm install @emailjs/browser
   ```

2. **Or use CDN** (add to HTML):
   ```html
   <script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
   ```

3. **Configure in your React app** - We'll do this in the next steps!

---

## ✅ Verification Checklist

Before proceeding to code integration:

- [ ] EmailJS account created and verified
- [ ] Gmail service connected (Service ID obtained)
- [ ] Email template created with all variables
- [ ] Template tested successfully
- [ ] Public key obtained
- [ ] Test email received in inbox
- [ ] All three credentials saved:
  - [ ] Service ID
  - [ ] Template ID  
  - [ ] Public Key

---

## 📊 Free Tier Limits

EmailJS Free Plan includes:
- ✅ **200 emails per month**
- ✅ **Unlimited templates**
- ✅ **Multiple email services**
- ✅ **Basic analytics**

For TCU-CEAA with ~50-100 applications/month, the free tier is perfect!

---

## 🔒 Security Notes

1. **Public Key is Safe:**
   - Public keys are meant to be used in frontend code
   - They're rate-limited and domain-restricted
   - No sensitive data exposure

2. **Email Protection:**
   - EmailJS uses reCAPTCHA to prevent spam
   - Can whitelist your domain for extra security

3. **Template Protection:**
   - Templates are stored on EmailJS servers
   - Users can't modify the template content
   - Only variable values are sent from your app

---

## 🆘 Troubleshooting

### Can't Find Service ID?
- Go to "Email Services" → Your service → Copy the ID shown

### Can't Find Template ID?
- Go to "Email Templates" → Your template → ID shown at top

### Can't Find Public Key?
- Account → General → Public Key (or API Keys)

### Test Email Not Received?
- Check spam folder
- Verify Gmail service is connected
- Check template variables are correct
- Ensure "to_email" variable is in template

---

## 📞 Support

- **EmailJS Documentation:** https://www.emailjs.com/docs/
- **EmailJS Support:** support@emailjs.com
- **Dashboard:** https://dashboard.emailjs.com/

---

**Next Steps:** Once you have your credentials, proceed to the code implementation guide!

**Setup Date:** October 25, 2025
**System:** TCU-CEAA EmailJS Integration
