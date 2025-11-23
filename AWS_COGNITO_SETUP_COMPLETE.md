# AWS Cognito Identity Pool - Face Liveness Setup Complete

## ✅ Configuration Status: READY

Your AWS Cognito Identity Pool is properly configured for Face Liveness Detection.

---

## 📋 Current Configuration

### AWS Cognito Identity Pool
- **Identity Pool ID**: `us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5`
- **Region**: `us-east-1` (US East - N. Virginia)
- **Guest Access**: Enabled
- **Purpose**: Provides temporary AWS credentials for browser-based AWS Rekognition Face Liveness

### Backend AWS Credentials
- **Access Key ID**: `AKIAWZNMCNNJEXB7DKWK`
- **Region**: `us-east-1`
- **Services Used**: 
  - Amazon Rekognition (Face Liveness Detection)
  - Amazon S3 (Document Storage)
  - Amazon Textract (OCR Processing)

---

## 🔧 How It Works

### Authentication Flow

1. **User Login** → Frontend stores authentication token in `localStorage`
2. **Face Verification Request** → Component calls `initializeAmplify()`
3. **Credential Fetch** → Backend provides AWS credentials via `/face-verification/aws-credentials/`
4. **Amplify Configuration** → Configures with Cognito Identity Pool ID
5. **Temporary Credentials** → Cognito provides time-limited credentials to browser
6. **Face Liveness** → FaceLivenessDetector uses temp credentials to call Rekognition
7. **Verification** → Results stored in database with device fingerprint

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (Browser)                                          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ FaceLivenessDetector Component                         │ │
│ │ - Uses AWS Amplify                                      │ │
│ │ - Cognito Identity Pool: a1252e7a-7da3-4703-88da-...   │ │
│ │ - Gets temporary credentials (expires in 1 hour)        │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ AWS Cognito Identity Pool                                   │
│ - Validates identity pool ID                                │
│ - Issues temporary STS credentials                          │
│ - Limited to Rekognition:DetectFaces permissions           │
│ - Auto-expires after 1 hour                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ AWS Rekognition                                             │
│ - Performs 3D liveness detection                            │
│ - Returns confidence score (0-100)                          │
│ - Detects presentation attacks (photos, videos, masks)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Backend (Django)                                            │
│ - Stores verification session                               │
│ - Records device fingerprint                                │
│ - Enforces rate limiting                                    │
│ - Requires admin review for approval                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 IAM Permissions Required

### Cognito Identity Pool IAM Role

Your Cognito Identity Pool must have an IAM role with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:CreateFaceLivenessSession",
        "rekognition:StartFaceLivenessSession",
        "rekognition:GetFaceLivenessSessionResults"
      ],
      "Resource": "*"
    }
  ]
}
```

### How to Verify/Add Permissions

1. Go to AWS Console → Cognito → Identity Pools
2. Select your pool: `us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5`
3. Click "Edit identity pool"
4. Note the "Authenticated role" and "Unauthenticated role" ARNs
5. Go to IAM → Roles → Select the role
6. Add the Rekognition permissions policy above

---

## 🧪 Testing Your Setup

### Step 1: Start Backend Server

```powershell
cd backend
python manage.py runserver
```

Expected output:
```
System check identified no issues (0 silenced).
November 24, 2025 - 10:00:00
Django version 5.2.5, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
```

### Step 2: Start Frontend Server

```powershell
cd frontend
npm start
```

Expected output:
```
Compiled successfully!
You can now view tcu-ceaa-frontend in the browser.
  Local: http://localhost:3000
```

### Step 3: Test Face Liveness Detection

1. **Login**: Navigate to `http://localhost:3000` and login
2. **Navigate**: Go to Student Dashboard → Apply for Allowance
3. **Start Verification**: Click "Start Verification" button
4. **Monitor Console**: Open browser DevTools (F12) → Console tab

**Expected Console Output:**

```
🔧 Fetching AWS credentials from backend...
🔧 Configuring AWS Amplify with region: us-east-1
✅ Amplify configured successfully
🎥 Initializing Face Liveness Detector...
✅ Session created: [session-id]
📸 Camera ready - Follow on-screen instructions
✅ Liveness check passed with 95% confidence
```

### Step 4: Verify Backend Storage

Check Django admin or database:
```sql
SELECT id, user_id, session_id, liveness_confidence, device_fingerprint, created_at
FROM myapp_faceverificationsession
ORDER BY created_at DESC
LIMIT 5;
```

---

## 🐛 Troubleshooting

### Error: "No credentials provided"

**Cause**: Amplify not initialized or Identity Pool ID incorrect

**Fix**:
1. Verify `identityPoolId` in `frontend/src/services/amplifyService.ts` matches: `us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5`
2. Check browser console for initialization errors
3. Verify you're logged in (token in localStorage)

### Error: "Access Denied" or 403

**Cause**: IAM role lacks Rekognition permissions

**Fix**:
1. Go to AWS Console → Cognito → Your Identity Pool
2. Check IAM role permissions
3. Add Rekognition policy (see IAM Permissions section)

### Error: "Region mismatch"

**Cause**: Cognito pool region doesn't match backend region

**Fix**:
1. Verify both are in `us-east-1`
2. Check `backend/.env`: `VERIFICATION_SERVICE_REGION=us-east-1`
3. Check `backend/.env`: `AWS_S3_REGION_NAME=us-east-1`

### Camera Won't Open

**Cause**: Browser permissions or HTTPS requirement

**Fix**:
1. Click browser address bar → Camera icon → Allow
2. For production, ensure HTTPS enabled (cameras require secure context)
3. Try Chrome/Edge (best compatibility)

### "Liveness check failed" (Low Confidence)

**Cause**: Poor lighting, motion blur, or presentation attack

**User Actions**:
- Ensure good lighting (face clearly visible)
- Stay still during capture
- Look directly at camera
- Remove glasses if causing glare
- Don't use photos or videos (will be detected)

---

## 📊 Configuration Files Reference

### Frontend Configuration

**File**: `frontend/src/services/amplifyService.ts`

```typescript
Amplify.configure({
  Auth: {
    Cognito: {
      identityPoolId: 'us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5',
      allowGuestAccess: true
    }
  }
});
```

### Backend Configuration

**File**: `backend/.env`

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAWZNMCNNJEXB7DKWK
AWS_SECRET_ACCESS_KEY=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
AWS_STORAGE_BUCKET_NAME=tcu-ceaa-documents
AWS_S3_REGION_NAME=us-east-1

# Face Liveness Service
VERIFICATION_SERVICE_ENABLED=True
VERIFICATION_SERVICE_REGION=us-east-1
VERIFICATION_SERVICE_MIN_CONFIDENCE=80
FACE_SIMILARITY_THRESHOLD=0.99
```

---

## 🚀 Production Deployment Checklist

Before deploying to production:

- [ ] **Security**: Remove backend credential exposure endpoint
- [ ] **HTTPS**: Enable SSL/TLS (required for camera access)
- [ ] **Environment Variables**: Use AWS Secrets Manager or similar
- [ ] **IAM Roles**: Use least-privilege permissions
- [ ] **Rate Limiting**: Re-enable rate limiting (currently disabled for dev)
- [ ] **Monitoring**: Set up CloudWatch for Rekognition API calls
- [ ] **Costs**: Monitor AWS Rekognition usage (charged per liveness check)
- [ ] **Backup**: Ensure Cognito Identity Pool has backup/DR plan
- [ ] **Compliance**: Verify GDPR/data protection for biometric data

---

## 💰 AWS Costs

### Face Liveness Detection Pricing
- **First 10,000 checks/month**: $0.01 per check
- **Next 990,000 checks/month**: $0.008 per check
- **Over 1M checks/month**: $0.006 per check

### Example Costs
- 100 students/month: ~$1.00
- 1,000 students/month: ~$10.00
- 10,000 students/month: ~$100.00

*Note: Prices as of 2025, check AWS pricing page for current rates*

---

## 📚 Additional Resources

### AWS Documentation
- [AWS Rekognition Face Liveness](https://docs.aws.amazon.com/rekognition/latest/dg/face-liveness.html)
- [Cognito Identity Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/identity-pools.html)
- [AWS Amplify for React](https://docs.amplify.aws/react/)

### Internal Documentation
- [BIOMETRIC_VERIFICATION_IMPLEMENTATION.md](./BIOMETRIC_VERIFICATION_IMPLEMENTATION.md)
- [FACE_VERIFICATION_GUIDE.md](./FACE_VERIFICATION_GUIDE.md)
- [FRAUD_DETECTION_GUIDE.md](./FRAUD_DETECTION_GUIDE.md)

---

## ✅ Status Summary

| Component | Status | Details |
|-----------|--------|---------|
| Cognito Identity Pool | ✅ Configured | `us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5` |
| Frontend Amplify | ✅ Configured | `amplifyService.ts` with proper ID |
| Backend Credentials | ✅ Configured | AWS keys in `.env` file |
| IAM Permissions | ⚠️ Verify | Check Rekognition permissions |
| Rate Limiting | ⚠️ Disabled | Re-enable for production |
| HTTPS | ⚠️ Local Only | Required for production |

---

**Last Updated**: November 24, 2025  
**Configuration Version**: 1.0  
**Cognito Pool**: `us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5`
