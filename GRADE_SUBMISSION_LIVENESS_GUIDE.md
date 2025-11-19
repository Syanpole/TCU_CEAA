# Grade Submission with Liveness Detection Guide

## 📋 Overview

The grade submission process now includes **mandatory liveness detection and face verification** as the final step. This ensures that the person submitting grades is the actual student, preventing identity fraud and ensuring academic integrity.

## 🔄 Complete Flow

### Step 1: Traditional Grade Submission
1. Student fills out grade submission form:
   - Semester (1st, 2nd, Summer)
   - Academic Year (e.g., 2024-2025)
   - Total Units (1-30)
   - General Weighted Average (GWA) in point scale (1.0-5.0)
   - Upload Grade Sheet file (PDF, JPG, PNG)

2. Backend processes and validates grades:
   - AI analyzes the grade sheet
   - OCR extracts grades and calculates GWA
   - System determines allowance eligibility
   - Grade submission is created with `pending` status

### Step 2: Automatic Liveness Verification (NEW!)
**Immediately after successful grade submission:**

1. **Liveness Detection Modal Appears**
   - User sees a clear explanation of what to expect
   - Instructions for 3 challenges displayed
   - Camera activates automatically

2. **Three Liveness Challenges** (10-15 seconds total):
   
   **A. Color Flash Detection**
   - Screen flashes 3 random colors (red, green, blue, yellow)
   - System captures frames during each flash
   - Verifies face presence and consistency
   
   **B. Blink Detection**
   - Captures 5 frames over 1 second
   - Detects natural eye blinking
   - Ensures a live person (not a photo/video)
   
   **C. Movement Detection**
   - Captures frames before and after 0.5s delay
   - Detects slight facial movement
   - Confirms natural human presence

3. **Face Verification Against ID**
   - System retrieves student's approved ID document:
     - School ID (preferred)
     - Birth Certificate
     - Voter's Certificate
   - Extracts face from ID using YOLO v8
   - Generates 512-dim embedding using InsightFace
   - Compares with live selfie face embedding
   - Calculates similarity score (0.0-1.0)

### Step 3: Verification Result

**✅ If Verification Passes** (Similarity ≥ 0.50):
- Grade submission is marked as identity-verified
- Success message displayed
- Student can proceed to application
- No further action needed

**❌ If Verification Fails**:

**Scenario A: Liveness Failed**
- User didn't complete challenges correctly
- Message: "Liveness verification failed. Please ensure you complete all challenges."
- User can retry immediately
- Grade submission remains but needs verification

**Scenario B: Face Doesn't Match** (Similarity < 0.50):
- User's face doesn't match ID document
- Message: "Face verification failed. Your face does not match your ID document."
- **This may indicate identity fraud**
- System logs the attempt for admin review
- User is blocked from proceeding

**Scenario C: No ID Document Found**
- User hasn't uploaded and gotten ID approved yet
- Message: "No approved ID document found. Please upload your School ID first."
- User must go back and upload ID documents
- Must wait for admin approval
- Then retry grade submission

## 🎯 Requirements

### For Students:
1. **Prerequisites**:
   - At least ONE approved ID document (School ID, Birth Certificate, or Voter's Certificate)
   - Working camera (mobile or desktop)
   - Good lighting conditions
   - Stable internet connection

2. **During Liveness Detection**:
   - Face must be clearly visible
   - Look directly at camera
   - Blink naturally during detection
   - Make small movements when prompted
   - Complete all 3 challenges successfully

3. **Best Practices**:
   - Use mobile camera (preferred) for better quality
   - Ensure face is well-lit
   - Remove glasses if causing glare
   - Keep face centered in frame
   - Don't move too quickly

### For Admins:
1. **Must approve ID documents FIRST** before students can complete grade submission
2. **Review failed verifications** for potential fraud cases
3. **Monitor similarity scores** - very low scores (<0.35) indicate possible fraud

## 🔐 Security Features

### Liveness Detection Prevents:
- ❌ Photo spoofing (holding up a printed photo)
- ❌ Video replay attacks (playing a video of the person)
- ❌ Static image uploads (trying to bypass camera)
- ❌ Deep fake videos (AI-generated faces)

### Face Verification Prevents:
- ❌ Identity theft (someone else using student's account)
- ❌ Grade falsification (submitting grades for wrong person)
- ❌ Account sharing (friends/family submitting for student)

### Fraud Detection:
- Similarity scores logged for all attempts
- Failed verifications flagged for admin review
- Multiple failures may trigger account suspension
- Natural facial changes accounted for (thresholds adjusted to 0.50)

## 📊 Similarity Score Interpretation

| Score Range | Confidence | Meaning | Action |
|-------------|-----------|---------|--------|
| **0.85 - 1.00** | Very High | Excellent match | ✅ Auto-approve |
| **0.70 - 0.84** | High | Strong match | ✅ Auto-approve |
| **0.55 - 0.69** | Medium | Good match | ✅ Auto-approve |
| **0.50 - 0.54** | Acceptable | Likely same person (accounting for natural changes) | ✅ Auto-approve |
| **0.45 - 0.49** | Low | Uncertain match (weight gain, aging, etc.) | ⚠️ Manual review |
| **0.35 - 0.44** | Very Low | Weak match | ⚠️ Fraud alert + manual review |
| **0.00 - 0.34** | Critical | Different person | 🚨 Fraud detected + suspend |

## 🛠️ Technical Implementation

### Frontend Components:
- **GradeSubmissionForm.tsx**: Main form with liveness flow integration
- **LiveCameraCapture.tsx**: Handles camera, liveness challenges, and capture
- State management for liveness verification modal

### Backend Components:
- **face_verification_views.py**: `verify_grade_submission_identity` endpoint
- **face_comparison_service.py**: YOLO + InsightFace face comparison
- **fraud_detection_service.py**: Analyzes failed verifications for fraud

### API Endpoint:
```
POST /api/face-verification/grade-submission/

Body (multipart/form-data):
- photo: File (live selfie image)
- liveness_data: JSON string with challenge results
- grade_submission_id: Integer (optional)

Response:
{
  "success": true,
  "liveness_passed": true,
  "face_verified": true,
  "similarity_score": 0.87,
  "confidence": "very_high",
  "message": "Identity verification successful!"
}
```

### Database Fields (Future Enhancement):
Currently, verification results are logged. Future versions may add these fields to `GradeSubmission` model:
- `liveness_verified`: Boolean
- `face_verified`: Boolean
- `verification_similarity`: Float
- `verification_confidence`: String
- `verification_timestamp`: DateTime

## 🐛 Troubleshooting

### "Liveness verification failed"
**Causes:**
- User didn't complete all 3 challenges
- Camera was blocked or not working
- Poor lighting conditions
- User moved away from camera

**Solutions:**
- Ensure camera permissions are granted
- Check lighting (face should be clearly visible)
- Stay in frame during all challenges
- Complete all 3 tests without interruption

### "Face verification failed"
**Causes:**
- Face doesn't match ID document
- Different person attempting submission
- Extremely poor quality selfie
- Natural changes (weight gain, aging) beyond threshold

**Solutions:**
- Ensure YOU are the person in the ID
- Retake with better lighting
- Look directly at camera
- Contact admin if legitimate natural changes

### "No approved ID document found"
**Causes:**
- No ID documents uploaded yet
- Uploaded IDs pending admin approval
- Uploaded wrong document types

**Solutions:**
- Upload School ID, Birth Certificate, or Voter's Certificate
- Wait for admin approval (typically 1-2 business days)
- Check document submission status in dashboard

### Camera won't start
**Causes:**
- Browser permissions denied
- Using HTTP instead of HTTPS (localhost only)
- Camera in use by another app

**Solutions:**
- Grant camera permissions in browser
- Close other apps using camera
- Refresh page and try again
- Use different browser if issues persist

## 📱 Device Compatibility

### Supported Browsers:
- ✅ Chrome/Edge (Desktop & Mobile) - **Recommended**
- ✅ Safari (Desktop & Mobile)
- ✅ Firefox (Desktop & Mobile)
- ⚠️ Opera (Most features work)
- ❌ Internet Explorer (Not supported)

### Camera Requirements:
- **Mobile**: Front-facing camera (preferred)
- **Desktop**: Webcam (built-in or external)
- **Minimum Resolution**: 640x480
- **Recommended Resolution**: 1280x720 or higher

## 📈 Future Enhancements

### Planned Features:
1. **Retry Mechanism**: Allow 3 retry attempts before blocking
2. **Admin Override**: Admin can manually verify in exceptional cases
3. **Natural Changes Tracking**: Monitor similarity scores over time
4. **Multi-factor Verification**: Combine with OTP for high-security
5. **Fraud Analytics Dashboard**: Visual analytics for admin review

### Under Consideration:
- Voice verification (speak a random phrase)
- 3D depth detection (prevent photo/video spoofing)
- AI-powered anomaly detection (unusual patterns)
- Blockchain verification records (immutable audit trail)

## 📞 Support

### For Students:
- **Technical Issues**: Contact IT support
- **Failed Verification**: Contact admin with student ID
- **Account Suspended**: Contact admin immediately

### For Admins:
- **Review Logs**: Check face verification attempts in admin panel
- **Fraud Cases**: Follow fraud investigation protocol
- **System Issues**: Contact development team

---

**Document Version**: 1.0  
**Last Updated**: November 14, 2025  
**Author**: Development Team  
**Status**: Active
