# AWS Rekognition Biometric Verification - Complete Implementation Guide ✅

## Overview

Production-grade biometric verification system with AWS Rekognition Face Liveness, strict >99% similarity threshold, and mandatory human-in-the-loop admin review.

**Implementation Status**: ✅ Backend Core Complete | ⏳ AWS Configuration Required | ⏳ Frontend Integration Required

---

## Security Flow

```
User Action → Consent Modal → Liveness Challenge (3D Video) → Identity Match (>99%) → Admin Review Queue → Final Decision
```

### Key Security Features

1. **Non-Dismissible Consent**: Biometric usage disclaimer must be accepted
2. **3D Liveness Detection**: AWS Rekognition prevents photo/video/deepfake spoofing
3. **Strict Threshold**: >99% similarity required for auto-tagging
4. **Mandatory Admin Review**: ALL verifications routed to human review (no automatic approval)
5. **Cross-Cloud Authentication**: Secure Google Cloud ↔ AWS integration

---

## Files Implemented

### Backend (Python/Django)

| File | Status | Changes |
|------|--------|---------|
| `backend/myapp/rekognition_service.py` | ✅ Complete | Enhanced with create_liveness_session(), get_liveness_session_results(), verify_identity_with_liveness(), Config(connect_timeout=30, read_timeout=60), strict 99% threshold, mandatory admin review flags |
| `backend/myapp/face_verification_views.py` | ✅ Complete | Added create_liveness_session() and verify_with_liveness() endpoints, VerificationAdjudication record creation |
| `backend/myapp/urls.py` | ✅ Complete | Registered /api/face-verification/create-liveness-session/ and /api/face-verification/verify-with-liveness/ |

### Frontend (React/TypeScript)

| File | Status | Changes |
|------|--------|---------|
| `frontend/src/services/livenessService.ts` | ✅ Created | Complete service with startLivenessSession(), completeLivenessChallenge(), 60s timeout |
| `frontend/src/components/BiometricConsentDisclaimer.tsx` | ✅ Updated | Reflects AWS Rekognition, 3D liveness, >99% threshold, cross-cloud processing, human-in-the-loop |

---

## AWS Configuration (REQUIRED)

### 1. Create S3 Bucket

```bash
# Create bucket for liveness audit images
aws s3 mb s3://tcu-ceaa-bucket --region us-east-1

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket tcu-ceaa-bucket \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

### 2. Create IAM User & Policy

**IAM Policy JSON** (save as `rekognition-policy.json`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:CreateFaceLivenessSession",
        "rekognition:GetFaceLivenessSessionResults",
        "rekognition:CompareFaces"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::tcu-ceaa-bucket/*"
    }
  ]
}
```

**Create IAM User**:

```bash
# Create policy
aws iam create-policy \
  --policy-name TCU-CEAA-Rekognition-Policy \
  --policy-document file://rekognition-policy.json

# Create user
aws iam create-user --user-name tcu-ceaa-rekognition-service

# Attach policy
aws iam attach-user-policy \
  --user-name tcu-ceaa-rekognition-service \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/TCU-CEAA-Rekognition-Policy

# Create access key
aws iam create-access-key --user-name tcu-ceaa-rekognition-service
```

Save the `AccessKeyId` and `SecretAccessKey` from the output.

### 3. Configure Environment Variables

Add to `.env` or Google Secret Manager:

```bash
# Enable AWS Rekognition
VERIFICATION_SERVICE_ENABLED=True

# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# S3 Bucket
AWS_STORAGE_BUCKET_NAME=tcu-ceaa-bucket

# AWS Region
VERIFICATION_SERVICE_REGION=us-east-1

# Liveness Confidence Threshold (optional)
VERIFICATION_SERVICE_MIN_CONFIDENCE=80
```

**For Google Secret Manager**:

```bash
# Create secrets
echo -n "AKIAIOSFODNN7EXAMPLE" | gcloud secrets create AWS_ACCESS_KEY_ID --data-file=-
echo -n "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" | gcloud secrets create AWS_SECRET_ACCESS_KEY --data-file=-

# Grant access to App Engine
gcloud secrets add-iam-policy-binding AWS_ACCESS_KEY_ID \
  --member="serviceAccount:YOUR_PROJECT@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding AWS_SECRET_ACCESS_KEY \
  --member="serviceAccount:YOUR_PROJECT@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## API Endpoints

### 1. Create Liveness Session

**Request**:
```http
POST /api/face-verification/create-liveness-session/
Authorization: Bearer {token}
Content-Type: application/json
```

**Response**:
```json
{
  "success": true,
  "session_id": "1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6",
  "error": null
}
```

### 2. Verify with Liveness

**Request**:
```http
POST /api/face-verification/verify-with-liveness/
Authorization: Bearer {token}
Content-Type: multipart/form-data

session_id: "1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6"
school_id_image: [binary file data]
application_id: 123  (optional)
```

**Response**:
```json
{
  "success": true,
  "liveness_passed": true,
  "face_match": true,
  "similarity_score": 0.9912,
  "similarity_percentage": 99.12,
  "confidence": "very_high",
  "requires_admin_review": true,
  "adjudication_id": 456,
  "adjudication_status": "pending",
  "message": "Automated verification suggests a match (Similarity: 99.1%). Your verification is now pending administrative review for final approval."
}
```

---

## Frontend Integration

### Step 1: Import Liveness Service

```tsx
import { startLivenessSession, completeLivenessChallenge } from './services/livenessService';
```

### Step 2: Complete Flow Example

```tsx
async function handleBiometricVerification() {
  try {
    // Step 1: Show consent modal
    setShowConsentModal(true);
    
    // Step 2: User accepts consent
    const consentAccepted = await waitForConsent();
    if (!consentAccepted) return;
    
    // Step 3: Create liveness session
    const sessionResult = await startLivenessSession();
    if (!sessionResult.success) {
      throw new Error(sessionResult.error);
    }
    
    // Step 4: User completes 3D liveness challenge
    // (Use AWS Amplify FaceLivenessDetector or custom video capture)
    setShowLivenessUI(true);
    const livenessCompleted = await waitForLivenessCompletion();
    if (!livenessCompleted) return;
    
    // Step 5: Complete verification with backend
    const verificationResult = await completeLivenessChallenge(
      sessionResult.session_id!,
      schoolIdFile,
      applicationId
    );
    
    // Step 6: Show result
    if (verificationResult.success) {
      setVerificationStatus('pending_admin_review');
      showMessage(verificationResult.message);
    } else {
      setVerificationStatus('failed');
      showError(verificationResult.error || 'Verification failed');
    }
    
  } catch (error) {
    console.error('Biometric verification error:', error);
    showError('Verification process failed. Please try again.');
  }
}
```

### Step 3: Optional - AWS Amplify Integration

**Install Amplify**:

```bash
npm install @aws-amplify/ui-react-liveness aws-amplify
```

**Configure Amplify** (in App.tsx or main component):

```tsx
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    region: 'us-east-1',
    // No Cognito required for Rekognition Face Liveness
  }
});
```

**Use Liveness Detector**:

```tsx
import { FaceLivenessDetector } from '@aws-amplify/ui-react-liveness';

function LivenessChallenge({ sessionId, onComplete }) {
  return (
    <FaceLivenessDetector
      sessionId={sessionId}
      region="us-east-1"
      onAnalysisComplete={onComplete}
      onError={(error) => console.error('Liveness error:', error)}
    />
  );
}
```

---

## Testing Guide

### Backend Testing

**Test 1: Check AWS Configuration**

```python
python manage.py shell
>>> from myapp.rekognition_service import get_verification_service
>>> service = get_verification_service()
>>> print(f"Enabled: {service.enabled}")
>>> print(f"Threshold: {service.similarity_threshold}%")
Enabled: True
Threshold: 99.0%
```

**Test 2: Create Liveness Session**

```bash
curl -X POST http://localhost:8000/api/face-verification/create-liveness-session/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

Expected response:
```json
{"success": true, "session_id": "...", "error": null}
```

**Test 3: Complete Verification**

```bash
curl -X POST http://localhost:8000/api/face-verification/verify-with-liveness/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "session_id=YOUR_SESSION_ID" \
  -F "school_id_image=@/path/to/school_id.jpg"
```

### Frontend Testing

**Browser Console**:

```javascript
// Test session creation
import { startLivenessSession } from './services/livenessService';
const session = await startLivenessSession();
console.log('Session:', session);

// Test complete verification
import { completeLivenessChallenge } from './services/livenessService';
const file = new File([blob], 'school_id.jpg', { type: 'image/jpeg' });
const result = await completeLivenessChallenge(session.session_id, file);
console.log('Result:', result);
```

### End-to-End Test Checklist

- [ ] User clicks "Verify Identity" button
- [ ] Consent modal appears (non-dismissible)
- [ ] User accepts consent (checkbox + button)
- [ ] Backend creates liveness session (logs show session_id)
- [ ] Liveness UI appears (video capture or AWS Amplify)
- [ ] User completes 3D liveness challenge
- [ ] Backend retrieves liveness results (logs show confidence score)
- [ ] Backend compares faces (logs show similarity percentage)
- [ ] VerificationAdjudication record created (admin_decision='pending')
- [ ] Frontend displays "Pending Admin Review" message
- [ ] Admin dashboard shows new adjudication entry
- [ ] Admin reviews side-by-side images
- [ ] Admin approves/rejects with notes
- [ ] User notified of final decision

---

## Performance Metrics

| Operation | Expected Time | Max Timeout |
|-----------|--------------|-------------|
| Create liveness session | 2-5 seconds | 30 seconds |
| User completes liveness | 10-30 seconds | 60 seconds |
| Backend verification | 15-45 seconds | 60 seconds |
| **Total End-to-End** | **30-80 seconds** | **2 minutes** |

**Cross-Cloud Latency**: Google Cloud (hosting) → AWS (Rekognition) adds 5-15 seconds overhead.

---

## Troubleshooting

### Error: "Service access denied"

**Cause**: AWS credentials missing or invalid IAM permissions

**Fix**:
1. Check `.env` file has `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
2. Verify IAM policy attached to user
3. Test AWS connection: `aws rekognition describe-collection --collection-id test`

### Error: "Liveness session not found"

**Cause**: Session expired (default 10 minutes) or invalid session_id

**Fix**:
1. Create new session
2. Complete liveness challenge within 10 minutes
3. Don't reuse session IDs

### Error: "Verification timeout"

**Cause**: Slow network or AWS service latency

**Fix**:
1. Check internet connection
2. Verify AWS region (use closest: `us-east-1`, `ap-southeast-1`)
3. Increase timeout in `livenessService.ts` (currently 60s)

### Low Similarity Score

**Cause**: Poor image quality, different person, or lighting issues

**Fix**:
1. Ensure School ID image has clear face photo
2. Use good lighting for liveness challenge
3. Same person as School ID must complete verification
4. Admin can override if AI is wrong

---

## Admin Adjudication

### Dashboard Access

```
URL: /admin/face-adjudication/
Permission: role='admin'
```

### Review Process

1. **View Queue**: See all pending verifications
2. **Side-by-Side**: Compare liveness reference image + School ID
3. **Check Scores**:
   - Liveness confidence: 0.80-1.00 (80-100%)
   - Similarity score: 0.99+ for match (99%+)
4. **Make Decision**:
   - ✅ Approve: Identity confirmed
   - ❌ Reject: No match or quality issues
   - 🔺 Escalate: Suspicious for fraud investigation
5. **Add Notes**: Document reasoning
6. **Submit**: Decision saved with timestamp

### Fraud Detection Indicators

- Liveness confidence <85%
- Similarity score 85-99% (borderline)
- Multiple failed attempts from same user
- Different lighting/angle suggesting photo manipulation
- Mismatched facial features (eyes, nose, mouth)

---

## Migration from Old System

### Fallback Support

System automatically uses `FaceComparisonService` (YOLO + InsightFace) if:
- `VERIFICATION_SERVICE_ENABLED=False`
- AWS credentials not configured
- AWS service unavailable

### Gradual Rollout

1. **Week 1**: Enable for 10% of users (test group)
2. **Week 2**: Enable for 50% of users
3. **Week 3**: Enable for 100% of users
4. **Month 2**: Deprecate old FaceComparisonService

---

## Next Steps

### Immediate (Today)

1. ✅ Configure AWS credentials (30 minutes)
2. ✅ Test backend endpoints (30 minutes)
3. ✅ Deploy to staging environment (1 hour)

### Short-Term (This Week)

1. ⏳ Integrate frontend liveness UI (2-4 hours)
2. ⏳ End-to-end testing on staging (2 hours)
3. ⏳ Train admins on adjudication dashboard (1 hour)

### Medium-Term (Next Week)

1. ⏳ Deploy to production (1 hour)
2. ⏳ Monitor first 50 verifications (ongoing)
3. ⏳ Collect feedback and iterate (ongoing)

---

## Support

- **AWS Rekognition Docs**: https://docs.aws.amazon.com/rekognition/latest/dg/face-liveness.html
- **AWS Amplify Liveness**: https://ui.docs.amplify.aws/react/connected-components/liveness
- **Data Privacy Compliance**: https://www.privacy.gov.ph/data-privacy-act/

For technical issues, contact the development team or file a GitHub issue.

---

**Status**: ✅ Backend Implementation Complete | ⚠️ AWS Configuration Required | ⏳ Frontend Integration Pending

Last Updated: November 20, 2025
