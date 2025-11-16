# Fraud Detection & Reporting System

## Overview
This system automatically detects and reports potential fraud when face verification fails during the final application confirmation step (after grade verification). If a user fails face verification, it indicates they may be using someone else's identity.

## System Flow

### 1. **Normal Application Flow**
```
Student Registration → Document Upload → Grade Verification → 
Face Verification (Final Confirmation) → Application Approved
```

### 2. **Fraud Detection Trigger**
```
Face Verification FAILS → 
Fraud Report Created → 
User Account Suspended → 
Admin Notified → 
Real Owner Can Be Contacted
```

## When Fraud is Detected

### Automatic Actions:
1. ✅ **Fraud Report Created** - Unique report ID generated (e.g., FR-20251114153022-123)
2. ✅ **User Account Suspended** - Fraudulent account immediately suspended
3. ✅ **Admin Notifications Created** - All admins receive urgent notifications
4. ✅ **Email Alerts Sent** - Admins receive email about fraud attempt
5. ✅ **Evidence Collected** - Face match scores, liveness data, timestamps stored

### Natural Facial Changes Consideration

**The system accounts for natural changes in human appearance:**
- 🔹 **Weight gain/loss**: Affects cheeks, jawline, facial structure
- 🔹 **Facial hair growth**: Beard, mustache significantly change appearance  
- 🔹 **Aging**: Skin texture, wrinkles, facial features evolve over time
- 🔹 **Hairstyle changes**: Different hair length, color, or style
- 🔹 **Makeup differences**: Makeup vs. no makeup affects recognition
- 🔹 **Photo conditions**: Lighting, angles, expression variations

### Similarity Score Interpretation

| Score Range | Interpretation | Action |
|------------|----------------|---------|
| 0.85-1.00 | Excellent match, minimal changes | ✅ Auto-approve |
| 0.70-0.85 | Strong match, minor changes | ✅ Auto-approve |
| 0.55-0.70 | Good match, moderate changes | ✅ Auto-approve |
| 0.50-0.55 | Acceptable match, significant natural changes | ✅ Auto-approve |
| 0.45-0.50 | Uncertain - natural changes OR fraud | ⚠️ Manual review |
| 0.35-0.45 | Weak match - likely fraud, consider old IDs | ⚠️ Manual review required |
| < 0.35 | Very poor match - different person | ❌ Probable fraud |

### Fraud Detection Criteria:
- **Face Match Score < 0.35** → Likely stolen identity (Critical) - different person
- **Face Match Score 0.35-0.45** → Uncertain (Medium/High) - manual review needed
- **Face Match Score 0.45-0.50 + Liveness Passed** → Natural changes likely (Low) - manual review
- **Liveness Verification Failed** → Using static photo (High severity)
- **Multiple Failed Attempts (≥3)** → Repeated fraud attempts (Critical)

## Database Models

### FraudReport Model
Stores comprehensive fraud attempt information:

```python
- report_id: Unique identifier (e.g., FR-20251114153022-123)
- suspected_user: User who failed verification
- fraud_type: face_mismatch, liveness_failed, stolen_identity, etc.
- status: pending, investigating, confirmed_fraud, resolved, dismissed
- severity: low, medium, high, critical
- face_match_score: Similarity score (0.0-1.0)
- liveness_data: Color flash, blink, movement results
- verification_attempts: Number of failed attempts
- description: Detailed fraud description
- evidence_data: Timestamps, IP, device info, etc.
- real_owner_contacted: Whether real owner was reached
- real_owner_verified: Whether real owner was verified
- admin_notes: Investigation notes
- assigned_to: Admin handling the case
```

### FraudNotification Model
Notifies admins about fraud attempts:

```python
- fraud_report: Link to fraud report
- notification_type: new_fraud_report, high_severity_alert, etc.
- admin: Admin receiving notification
- title: Notification title
- message: Detailed message
- priority: low, medium, high, urgent
- read: Whether notification was read
```

### UserAccountAction Model
Tracks actions taken on user accounts:

```python
- user: Affected user
- fraud_report: Related fraud report
- action_type: suspended, flagged, reinstated, permanently_banned
- reason: Why action was taken
- performed_by: Admin who performed action
- expires_at: When temporary suspension expires
```

## Admin Workflow

### Step 1: Receive Fraud Alert
Admin receives multiple notifications:
- 🔔 **In-app notification**: Appears in admin panel
- 📧 **Email alert**: Critical security alert sent
- 🚨 **Dashboard badge**: Shows unread fraud reports

### Step 2: Review Fraud Report
Admin can view:
- Suspected user details (name, email, student ID)
- Face match score and confidence level
- Liveness verification results (color flash, blink, movement)
- Number of verification attempts
- All submitted documents
- Evidence data (timestamps, device info)
- Automatic actions taken (account suspension)

### Step 3: Investigate
Admin options:
- **Assign to self** - Take ownership of investigation
- **Add notes** - Document investigation progress
- **Review documents** - Examine all submitted documents
- **Check face comparison** - Review ID photo vs selfie
- **Update status** - Mark as investigating

### Step 4: Contact Real Owner (If Possible)
If contact information available:
- **Reach out to real identity owner**
- **Verify their identity** through separate channel
- **Guide them** through proper application process
- **Record contact** in system

### Step 5: Resolve Case
Three resolution options:

#### A. **Confirmed Fraud** ✅
- Fraud is confirmed
- Fraudulent account permanently banned
- Formal fraud report filed
- Real owner can still apply properly

#### B. **Real Owner Verified** ✅
- Real owner contacted and verified
- Guided through proper application
- Fraudulent account remains banned
- Real owner creates new legitimate account

#### C. **Dismissed** ❌
- False positive - not actual fraud
- User account reinstated
- User notified they can proceed
- Report marked as dismissed

## API Endpoints

### 1. Get Fraud Reports (Admin)
```
GET /api/fraud-reports/
Query Parameters:
  - status: Filter by status
  - severity: Filter by severity
  - limit: Number of results

Response:
{
  "reports": [...],
  "count": 10,
  "statistics": {
    "total": 50,
    "pending": 12,
    "investigating": 8,
    "confirmed": 15,
    "resolved": 10,
    "critical_severity": 5
  }
}
```

### 2. Get Fraud Report Detail (Admin)
```
GET /api/fraud-reports/{report_id}/

Response:
{
  "report_id": "FR-20251114153022-123",
  "suspected_user": {...},
  "fraud_details": {...},
  "liveness_data": {...},
  "evidence_data": {...},
  "real_owner": {...},
  "admin_info": {...},
  "account_actions": [...]
}
```

### 3. Update Fraud Report (Admin)
```
POST /api/fraud-reports/{report_id}/update/
Body:
{
  "assigned_to": 5,
  "status": "investigating",
  "admin_notes": "Started investigation..."
}
```

### 4. Resolve Fraud Report (Admin)
```
POST /api/fraud-reports/{report_id}/resolve/
Body:
{
  "resolution": "confirmed",  // or "dismissed" or "real_owner_verified"
  "notes": "Fraud confirmed after investigation..."
}
```

### 5. Contact Real Owner (Admin)
```
POST /api/fraud-reports/{report_id}/contact-real-owner/
Body:
{
  "method": "email",
  "details": "Contacted at real.owner@email.com",
  "verified": true
}
```

### 6. Get Fraud Notifications (Admin)
```
GET /api/fraud-notifications/

Response:
{
  "notifications": [...],
  "unread_count": 5
}
```

### 7. Mark Notification as Read (Admin)
```
POST /api/fraud-notifications/{notification_id}/mark-read/
```

## User Experience

### For Fraudulent User:
1. Submits documents with stolen identity
2. Grades verified successfully
3. Asked to confirm identity with face verification
4. **Face verification fails**
5. Receives message: 
   > "🚨 Face verification failed. Your account has been suspended for security review. If you are the real owner of this ID, please contact the admin immediately. Reference ID: FR-20251114153022-123"
6. Account suspended immediately
7. Cannot access application or submit new documents

### For Real Identity Owner:
1. May discover someone applied using their identity
2. Contacts admin with reference ID
3. Admin verifies real owner through alternative means
4. Real owner guided through proper application process
5. Can create legitimate application
6. Fraudulent account remains banned

## Email Alerts

### Admin Fraud Alert Email:
```
Subject: 🚨 FRAUD ALERT - FR-20251114153022-123

CRITICAL SECURITY ALERT - POTENTIAL SCHOLARSHIP FRAUD DETECTED

Report ID: FR-20251114153022-123
Timestamp: 2025-11-14 15:30:22
Severity: CRITICAL

SUSPECTED USER:
- Name: John Doe
- Email: fraudulent@email.com
- Student ID: 2024-12345

FRAUD DETAILS:
- Type: Stolen Identity
- Face Match Score: 0.2431 (Threshold: 0.60)
- Verification Attempts: 1
- Account Status: SUSPENDED

IMMEDIATE ACTIONS REQUIRED:
1. Log into admin panel to review fraud report
2. Examine all submitted documents
3. Contact real identity owner if contact information available
4. Coordinate with security team if necessary
5. File formal report if fraud confirmed

The user account has been automatically suspended to prevent further fraudulent activity.

DO NOT REPLY to this email. Log into the admin panel to take action.
```

## Security Features

### Prevention:
- ✅ Mobile devices: Camera-only (no file uploads)
- ✅ Liveness detection: Color flash, blink, movement
- ✅ Face matching: YOLO + InsightFace with 0.6 threshold
- ✅ Multiple attempts tracking

### Detection:
- ✅ Automatic fraud report creation
- ✅ Real-time admin notifications
- ✅ Evidence collection (scores, data, timestamps)
- ✅ Severity classification

### Response:
- ✅ Immediate account suspension
- ✅ Admin alerts (email + in-app)
- ✅ Investigation workflow
- ✅ Real owner contact system

### Recovery:
- ✅ False positive handling (reinstate account)
- ✅ Real owner verification process
- ✅ Permanent ban for confirmed fraud
- ✅ Documented resolution

## Configuration

### Fraud Detection Thresholds
Edit `fraud_detection_service.py`:
```python
FACE_MATCH_FRAUD_THRESHOLD = 0.4  # Below this = likely fraud
MAX_VERIFICATION_ATTEMPTS = 3      # Max attempts before flagging
```

### Email Recipients
Edit `settings.py`:
```python
FRAUD_ALERT_EMAILS = [
    'admin1@tcu.edu',
    'admin2@tcu.edu',
    'security@tcu.edu'
]
```

## Testing

### Test Fraud Detection:
1. Register test account with fake ID
2. Upload documents
3. Pass grade verification
4. Attempt face verification with different person's photo
5. Verify:
   - Account suspended
   - Fraud report created
   - Admin notified
   - Email sent

### Test False Positive:
1. Legitimate user fails due to poor lighting
2. Admin reviews case
3. Admin dismisses as false positive
4. User account reinstated
5. User notified they can proceed

## Database Migrations

After adding fraud detection models:
```bash
python manage.py makemigrations
python manage.py migrate
```

## URL Routes to Add

In `backend/myapp/urls.py`:
```python
from .fraud_management_views import (
    get_fraud_reports,
    get_fraud_report_detail,
    update_fraud_report,
    resolve_fraud_report,
    contact_real_owner,
    get_fraud_notifications,
    mark_notification_read
)

urlpatterns += [
    # Fraud Management (Admin Only)
    path('api/fraud-reports/', get_fraud_reports),
    path('api/fraud-reports/<int:report_id>/', get_fraud_report_detail),
    path('api/fraud-reports/<int:report_id>/update/', update_fraud_report),
    path('api/fraud-reports/<int:report_id>/resolve/', resolve_fraud_report),
    path('api/fraud-reports/<int:report_id>/contact-real-owner/', contact_real_owner),
    path('api/fraud-notifications/', get_fraud_notifications),
    path('api/fraud-notifications/<int:notification_id>/mark-read/', mark_notification_read),
]
```

## Success Metrics

- **Fraud Detection Rate**: % of fraud attempts caught
- **False Positive Rate**: < 5% (legitimate users flagged)
- **Response Time**: < 24 hours for admin review
- **Resolution Time**: < 7 days average case resolution
- **Real Owner Recovery**: % of real owners successfully verified

## Support for Real Owners

If real owner contacts:
1. **Verify identity** through alternative channel (phone call, video verification)
2. **Record contact** in fraud report
3. **Guide proper application**:
   - Create new account with verified email
   - Submit documents through proper channels
   - Complete face verification successfully
4. **Mark case as resolved** - Real owner verified
5. **Keep fraudulent account banned**

---

**Implementation Status**: ✅ Complete
**Version**: 1.0.0
**Last Updated**: November 14, 2025
