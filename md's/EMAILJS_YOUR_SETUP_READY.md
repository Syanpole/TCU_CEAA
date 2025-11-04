# 🎉 EmailJS Testing Guide - Your Credentials Are Ready!

## ✅ Your Configuration

Your `.env` file is now set up with your actual EmailJS credentials:

```env
✅ SERVICE_ID: service_kvnsvjk
✅ TEMPLATE_ID: template_n7hvacg
✅ PUBLIC_KEY: bJOQ5VKqFricP7zZG
```

---

## 🧪 Quick Test Options

### Option 1: Use the Test Component (Recommended)

1. **Temporarily update your `App.tsx` to use the test component:**

```tsx
import React from 'react';
import EmailJsTest from './components/EmailJsTest';

function App() {
  return (
    <div className="App">
      <EmailJsTest />
    </div>
  );
}

export default App;
```

2. **Start your dev server:**
```bash
cd frontend
npm start
```

3. **Test in the browser:**
   - Fill in your name and email
   - Click "Check .env Configuration"
   - Click "Send Test Email"
   - Check your inbox!

---

### Option 2: Quick Console Test

1. **Start your dev server:**
```bash
cd frontend
npm start
```

2. **Open browser console (F12) and paste:**
```javascript
import { sendApprovalEmail } from './services/email/emailService';

sendApprovalEmail('Test Student', 'your.email@example.com')
  .then(result => console.log(result));
```

---

### Option 3: Create a Quick Test Page

Create a new test route in your app:

**File: `frontend/src/pages/TestEmail.tsx`**
```tsx
import React, { useState } from 'react';
import { sendApprovalEmail } from '../services/email/emailService';

const TestEmail = () => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [result, setResult] = useState('');

  const handleTest = async () => {
    const res = await sendApprovalEmail(name, email);
    setResult(res.success ? '✅ Success!' : '❌ ' + res.message);
  };

  return (
    <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>🧪 Quick Email Test</h1>
      
      <input
        type="text"
        placeholder="Your Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        style={{ display: 'block', width: '100%', padding: '10px', marginBottom: '10px' }}
      />
      
      <input
        type="email"
        placeholder="Your Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{ display: 'block', width: '100%', padding: '10px', marginBottom: '10px' }}
      />
      
      <button onClick={handleTest} style={{ padding: '10px 20px', cursor: 'pointer' }}>
        Send Test Email
      </button>
      
      {result && <p style={{ marginTop: '20px', fontSize: '18px' }}>{result}</p>}
    </div>
  );
};

export default TestEmail;
```

---

## ⚡ Fastest Way to Test (Command Line)

Run this in your terminal:

```bash
cd frontend
npm start
```

Then in your browser console:
```javascript
// Paste this in console after page loads
fetch('https://api.emailjs.com/api/v1.0/email/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    service_id: 'service_kvnsvjk',
    template_id: 'template_n7hvacg',
    user_id: 'bJOQ5VKqFricP7zZG',
    template_params: {
      to_name: 'Test Student',
      to_email: 'your.email@example.com',
      student_name: 'Test Student'
    }
  })
}).then(res => res.text()).then(data => console.log('✅ Email sent!', data));
```

---

## 📧 Make Sure Your EmailJS Template is Set Up

Your template should have these variables:
- `{{to_name}}` - Student's name
- `{{to_email}}` - Student's email

### Template Subject:
```
Congratulations! Your TCU-CEAA Application Has Been Approved!
```

### Template Body:
Use the HTML from `EMAILJS_QUICK_START.md`

---

## ✅ Verification Checklist

- [x] EmailJS account created
- [x] Email service added
- [x] Email template created
- [x] Credentials added to `.env`
- [ ] **Dev server restarted** (Important!)
- [ ] Test email sent
- [ ] Email received

---

## 🔄 Important: Restart Your Dev Server!

If your dev server is already running, **restart it** to load the new environment variables:

```bash
# Stop the server (Ctrl+C)
# Then restart:
npm start
```

---

## 🎯 Expected Results

### ✅ Success:
```
{
  success: true,
  message: "Approval email sent successfully!"
}
```

You should receive an email within 1-2 minutes.

### ❌ If it fails:
1. Check that your EmailJS template exists (ID: `template_n7hvacg`)
2. Verify your service is active (ID: `service_kvnsvjk`)
3. Make sure template has `{{to_name}}` and `{{to_email}}` variables
4. Check EmailJS dashboard for error logs

---

## 📱 Test Email Content

When successful, you'll receive an email with:
- 🎓 TCU-CEAA Logo
- Congratulations message
- Personalized greeting with your name
- Approval details
- Next steps
- Contact information

---

## 🚀 Next: Integrate into Your App

Once testing is successful, integrate into your approval workflow:

### Simple Integration:
```tsx
import { sendApprovalEmail } from './services/email/emailService';

const handleApprove = async (student) => {
  // Approve student in database
  await approveStudent(student.id);
  
  // Send email
  const result = await sendApprovalEmail(student.name, student.email);
  
  if (result.success) {
    alert('Student approved and email sent!');
  }
};
```

---

## 📞 Need Help?

- **Check logs:** EmailJS Dashboard → Usage
- **Test template:** EmailJS Dashboard → Templates → Test
- **Verify service:** EmailJS Dashboard → Email Services

---

**You're all set! Start your dev server and test it now! 🚀**

```bash
cd frontend
npm start
```
