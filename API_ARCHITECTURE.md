# TCU-CEAA Scholarship System - API Architecture

## System Overview

The TCU-CEAA (Tarlac City University - City Educational Assistance for Allowances) scholarship system is designed around modular REST APIs to ensure scalability, maintainability, and seamless integration of components. The architecture leverages cutting-edge AI technologies, biometric verification, and comprehensive document processing to automate and secure the scholarship application workflow.

---

## Core API Modules

### 1. Authentication & Authorization API

**Purpose**: Manages secure user authentication, session handling, and role-based access control using JWT tokens.

**Key Features**:
- **JWT Token-Based Authentication**: Secure token generation and validation for stateless authentication
- **Multi-Factor Email Verification**: Email verification with time-limited codes before account activation
- **Role-Based Access Control (RBAC)**: Segregates access between students, admins, and evaluators
- **Session Management**: Token lifecycle management with secure logout and token revocation
- **Password Reset Flow**: Secure password recovery with verification codes
- **Account Archiving**: Soft-delete mechanism for user deactivation with audit trail

**Endpoints**:
```
POST   /api/auth/login/                      - User login with credentials
POST   /api/auth/logout/                     - Secure logout with token deletion
POST   /api/auth/register/                   - Student registration with email verification
POST   /api/auth/validate-registration/      - Pre-registration field validation
POST   /api/auth/verify-student/             - Verify student against verified database
POST   /api/auth/send-verification-code/     - Send email verification code
POST   /api/auth/verify-email-code/          - Verify email with code
POST   /api/auth/resend-verification-code/   - Resend verification code
POST   /api/auth/request-password-reset/     - Initiate password reset
POST   /api/auth/verify-reset-code/          - Verify password reset code
POST   /api/auth/reset-password/             - Complete password reset
GET    /api/auth/profile/                    - Get user profile
PUT    /api/auth/profile/                    - Update user profile
POST   /api/auth/profile/image/              - Upload profile image
DELETE /api/auth/profile/image/              - Remove profile image
GET    /api/auth/check-admin/                - Check admin privileges
```

**Security Measures**:
- Passwords hashed with Django's PBKDF2 algorithm
- JWT tokens with configurable expiration
- Rate limiting on authentication attempts
- Email verification required before account activation
- Audit logging for all authentication events

---

### 2. Document Processing & AI Verification API

**Purpose**: Handles document submission, validation, and AI-powered verification using multiple specialized algorithms.

**Key Features**:
- **Multi-Algorithm AI Analysis**: 7 specialized verification services
  1. **Document Validator**: OCR (Tesseract) + pattern matching
  2. **Cross-Document Matcher**: Fuzzy string matching for consistency checks
  3. **Grade Verifier**: GWA calculation + pattern detection
  4. **Face Verifier**: OpenCV face detection
  5. **Fraud Detector**: Metadata analysis + tampering detection
  6. **AI-Generated Content Detector**: Identifies synthetic documents
  7. **Biometric Verification Service**: AWS Rekognition Face Liveness

- **Specialized Document Verification**:
  - **Certificate of Enrollment (COE)**: YOLOv8 element detection + Advanced OCR + subject extraction
  - **ID Documents**: YOLOv8 ID detection + identity matching
  - **Birth Certificates**: Advanced OCR + field extraction
  - **Voter's Certificates**: YOLO detection + identity verification + parent matching

- **Auto-Approval System**: Confidence-based automatic document approval (>75% threshold)
- **S3 Cloud Storage**: Secure document storage with AWS S3 integration
- **Audit Trail**: Complete history of AI decisions and admin reviews

**Endpoints**:
```
# Document Submission
GET    /api/documents/                       - List user's documents
POST   /api/documents/                       - Submit new document
GET    /api/documents/{id}/                  - Get document details
PUT    /api/documents/{id}/                  - Update document
DELETE /api/documents/{id}/                  - Delete document
POST   /api/documents/{id}/review/           - Admin review document
POST   /api/documents/{id}/reanalyze/        - Trigger AI re-analysis
GET    /api/documents/{id}/ai-details/       - Get AI analysis details

# AI Processing
POST   /api/ai/analyze-document/             - Trigger AI document analysis
GET    /api/ai/status/{document_id}/         - Check AI analysis status
GET    /api/ai/dashboard-stats/              - AI system statistics
POST   /api/ai/batch-process/                - Batch process multiple documents

# Admin Dashboard
GET    /api/admin/documents/dashboard/       - Comprehensive document dashboard
```

**AI Confidence Scoring**:
- **High Confidence (>75%)**: Auto-approved, minimal admin review
- **Medium Confidence (50-75%)**: Flagged for manual review
- **Low Confidence (<50%)**: Auto-rejected with detailed feedback

**Document Types Supported**:
- Certificate of Enrollment (COE)
- School ID / Student ID
- Birth Certificate
- Voter's Certificate / Voter's ID
- Government ID
- Grade Sheets / Report Cards
- Transcript of Records

---

### 3. Grade Submission & Evaluation API

**Purpose**: Manages grade submission workflow with per-subject verification, GWA calculation, and merit eligibility determination.

**Key Features**:
- **Per-Subject Submission Workflow**: Individual grade verification per subject
- **COE-Based Validation**: Validates grades against extracted COE subjects
- **Automated GWA Calculation**: Real-time GWA computation with merit level classification
- **Grade Sheet AI Verification**: OCR-based grade extraction and authenticity verification
- **Session-Based Submission**: 2-hour window for completing all subject submissions
- **Draft System**: Auto-save functionality for incomplete submissions
- **Confidence Boosting**: Intelligent confidence adjustment for authentic documents with OCR failures

**Endpoints**:
```
# Grade Management
GET    /api/grades/                          - List grade submissions
POST   /api/grades/                          - Submit grade
GET    /api/grades/{id}/                     - Get grade details
PUT    /api/grades/{id}/                     - Update grade
DELETE /api/grades/{id}/                     - Delete grade (admin only)
POST   /api/grades/{id}/review/              - Admin review grade
POST   /api/grades/{id}/recalculate/         - Recalculate AI evaluation

# Per-Subject Workflow
GET    /api/grade-workflow/check-eligibility/    - Check submission eligibility
GET    /api/grade-workflow/coe-subjects/         - Get COE subjects list
POST   /api/grade-workflow/submit-subject/       - Submit single subject grade
POST   /api/grade-workflow/validate/             - Validate all submissions
GET    /api/grade-workflow/status/               - Get submission status

# Semester Grouping
GET    /api/grades/grouped_by_semester/      - Get grades grouped by semester
POST   /api/grades/approve_semester_group/   - Approve all grades in semester
POST   /api/grades/reprocess_semester/       - Reprocess semester with AI
```

**Merit Level Classification**:
- **HIGH DISTINCTION (GWA < 1.25)**: Top-tier merit allowance
- **DISTINCTION (GWA 1.25-1.50)**: High merit allowance
- **HONORS (GWA 1.51-1.75)**: Standard merit allowance
- **PASSING (GWA 1.76-2.00)**: Basic allowance eligibility
- **BELOW PASSING (GWA > 2.00)**: Ineligible

**Automatic Disqualification Rules**:
- Three (3) or more grades of 3.00 or below → Automatic rejection
- GWA > 2.00 → Ineligible for merit incentive
- Incomplete semester → Pending until all subjects submitted

---

### 4. Biometric Face Verification API

**Purpose**: Provides advanced biometric verification using AWS Rekognition Face Liveness to prevent identity fraud and spoofing attacks.

**Key Features**:
- **AWS Rekognition Face Liveness**: 3D video-based anti-spoofing detection
- **Live Selfie Comparison**: Compares live selfie against ID documents with >99% similarity threshold
- **Multi-Stage Verification Flow**:
  1. **Consent**: Mandatory biometric usage disclaimer
  2. **Liveness Detection**: 3D challenge-response video analysis
  3. **Identity Match**: Face comparison against approved ID documents
  4. **Admin Adjudication**: Human-in-the-loop review for all verifications

- **Fraud Prevention**: Detects photo/video replay attacks, deepfakes, and mask spoofing
- **Cross-Document Verification**: Validates faces across multiple submitted documents
- **Rate Limiting**: 20 verification attempts per day per user (configurable)
- **Session Management**: AWS Cognito Identity Pool for secure credential access

**Endpoints**:
```
# Face Liveness
POST   /api/face-verification/create-liveness-session/   - Create AWS liveness session
POST   /api/face-verification/verify-liveness/           - Verify liveness results
POST   /api/face-verification/verify-with-liveness/      - Complete verification flow
GET    /api/face-verification/aws-config/                - Get AWS Amplify config
GET    /api/face-verification/aws-credentials/           - Get temporary AWS credentials
GET    /api/face-verification/check-pending/             - Check pending adjudications

# Identity Verification
POST   /api/face-verification/verify/                    - Verify face with ID
POST   /api/face-verification/extract-face/              - Extract face from ID
POST   /api/face-verification/liveness/                  - Liveness-only verification
POST   /api/face-verification/grade-submission/          - Verify for grade submission
POST   /api/face-verification/allowance-application/     - Verify for allowance application

# Admin Adjudication
GET    /api/admin/face-adjudications/                    - List pending adjudications
GET    /api/admin/face-adjudications/{id}/               - Get adjudication details
POST   /api/admin/face-adjudications/{id}/approve/       - Approve verification
POST   /api/admin/face-adjudications/{id}/reject/        - Reject verification
POST   /api/admin/face-adjudications/{id}/request-retry/ - Request new verification
```

**Verification Status Flow**:
```
PENDING → LIVENESS_PASSED → ADMIN_REVIEW → APPROVED/REJECTED
```

**Security Thresholds**:
- **Liveness Confidence**: >80% required to pass
- **Face Similarity**: >99% for auto-tagging (still requires admin approval)
- **Daily Limit**: 20 attempts/day with progressive cooldown (2-15 minutes)
- **Fraud Alert**: 25+ attempts triggers fraud investigation

---

### 5. Allowance Application & Recommendation API

**Purpose**: Manages allowance applications, calculates eligibility, and generates tailored grant recommendations based on verified documents and academic performance.

**Key Features**:
- **Eligibility Engine**: Multi-phase logic to determine scholarship qualification
  - **Phase 1**: Document completeness check (COE, ID, Birth Certificate, Voter's Certificate)
  - **Phase 2**: Academic evaluation (GWA calculation, grade verification)
  - **Phase 3**: Identity verification (Face Liveness + ID comparison)
  
- **Recommendation System**: Generates and ranks suitable grant options
  - Basic Allowance (GWA 1.76-2.00): ₱500-₱1,000/semester
  - Merit Incentive (GWA 1.00-1.75): ₱1,500-₱3,000/semester
  - High Distinction (GWA < 1.25): ₱3,500-₱5,000/semester

- **Application Types**:
  - Basic Allowance Application
  - Merit Incentive Application
  - Emergency Assistance Application

- **Status Workflow**: `pending` → `processing` → `approved` → `disbursed`

**Endpoints**:
```
# Application Management
GET    /api/applications/                    - List user's applications
POST   /api/applications/                    - Submit allowance application
GET    /api/applications/{id}/               - Get application details
PUT    /api/applications/{id}/               - Update application
DELETE /api/applications/{id}/               - Cancel application
POST   /api/applications/{id}/process/       - Admin process application
POST   /api/applications/{id}/verify_identity/  - Complete biometric verification

# Basic & Full Application
GET    /api/basic-qualification/             - List basic qualifications
POST   /api/basic-qualification/             - Submit basic qualification
GET    /api/full-application/                - List full applications
POST   /api/full-application/                - Submit full application
```

**Automatic Disqualification Triggers**:
- Missing required documents (COE, ID, Birth Certificate, Voter's Certificate)
- Failed biometric verification (liveness or face comparison)
- GWA below 2.00 (for merit incentive)
- Three (3) or more failing grades (3.00 or below)
- Inconsistent identity information across documents

**Recommendation Logic**:
```python
if gwa < 1.25:
    recommendation = "High Distinction Grant (₱5,000)"
elif gwa <= 1.50:
    recommendation = "Distinction Grant (₱3,500)"
elif gwa <= 1.75:
    recommendation = "Honors Grant (₱2,500)"
elif gwa <= 2.00:
    recommendation = "Basic Allowance (₱1,000)"
else:
    recommendation = "Ineligible"
```

---

### 6. Fraud Management & Detection API

**Purpose**: Monitors, detects, and manages identity fraud attempts, duplicate accounts, and suspicious verification patterns.

**Key Features**:
- **Real-Time Fraud Detection**: 
  - Duplicate document submissions
  - Identity mismatch across documents
  - Failed biometric verifications
  - Suspicious face comparison patterns
  
- **Automated Fraud Reporting**: System-generated fraud reports with evidence
- **Admin Investigation Tools**: Detailed fraud case management dashboard
- **Notification System**: Real-time alerts for administrators
- **Resolution Workflow**: Investigation → Contact Real Owner → Resolve/Suspend

**Endpoints**:
```
# Fraud Reports
GET    /api/fraud-reports/                   - List fraud reports
GET    /api/fraud-reports/{id}/              - Get fraud report details
POST   /api/fraud-reports/{id}/update/       - Update fraud report
POST   /api/fraud-reports/{id}/resolve/      - Resolve fraud case
POST   /api/fraud-reports/{id}/contact-real-owner/  - Contact legitimate owner

# Notifications
GET    /api/fraud-reports/notifications/     - Get fraud notifications
POST   /api/fraud-reports/notifications/{id}/read/  - Mark notification as read
```

**Fraud Detection Triggers**:
- Face verification fails with high suspicion score
- Multiple accounts using same documents
- Identity mismatch between documents (name, ID number, photos)
- Abnormal verification attempt patterns (20+ failures)
- AI-detected tampered/forged documents

---

### 7. User & Admin Management API

**Purpose**: Handles user registration, profile management, role-based access control, and administrative functions.

**Key Features**:
- **User Registration**: Students register with verified Student ID validation
- **Profile Management**: Update personal information, upload profile images
- **Role-Based Access**: Students, Admins, Evaluators with distinct permissions
- **User Archiving**: Soft-delete mechanism with restoration capability
- **Audit Logging**: Complete history of user actions and system events

**Endpoints**:
```
# User Management
GET    /api/users/                           - List users (admin only)
POST   /api/users/                           - Create user (admin only)
GET    /api/users/{id}/                      - Get user details
PUT    /api/users/{id}/                      - Update user
DELETE /api/users/{id}/                      - Archive user (admin only)
POST   /api/users/{id}/restore/              - Restore archived user
GET    /api/users/archive/                   - List archived users

# Student List
GET    /api/students/                        - Get students list (admin only)
```

---

### 8. Dashboard & Analytics API

**Purpose**: Provides comprehensive statistics, trends, and insights for both students and administrators.

**Key Features**:
- **Student Dashboard**: Personal submission status, application history, GWA tracking
- **Admin Dashboard**: System-wide statistics, pending reviews, AI performance metrics
- **Analytics Overview**: Submission trends, approval rates, financial summaries
- **AI Statistics**: Algorithm performance, confidence distribution, processing rates

**Endpoints**:
```
# Dashboards
GET    /api/dashboard/student/               - Student dashboard data
GET    /api/dashboard/admin/                 - Admin dashboard data

# Analytics
GET    /api/analytics/                       - System analytics overview
GET    /api/ai-stats/                        - AI processing statistics
GET    /api/audit-logs/                      - Audit log list (admin only)
```

**Analytics Metrics**:
- Total students, documents, grades, applications
- Pending vs approved vs rejected counts
- AI processing rate and auto-approval rate
- Average confidence scores per document type
- Top performing students (by GWA)
- Financial summary (total disbursed, pending amounts)

---

## Technical Architecture

### Backend Stack
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 13+ with JSONB for metadata
- **Storage**: AWS S3 for document storage (USE_CLOUD_STORAGE=True)
- **Authentication**: JWT tokens with Django REST Framework Token Authentication
- **Task Queue**: Background tasks for AI processing
- **Logging**: Python logging with audit trail storage

### AI & Machine Learning Services
- **OCR**: 
  - Tesseract (legacy fallback)
  - Advanced OCR Service (EasyOCR, PaddleOCR, Surya)
- **Computer Vision**: 
  - OpenCV for face detection
  - YOLOv8 for document element detection
- **Biometric Verification**: 
  - AWS Rekognition Face Liveness
  - AWS Rekognition CompareFaces
- **Natural Language Processing**: 
  - Fuzzy string matching (fuzzywuzzy)
  - Pattern recognition for document validation

### Cloud Services
- **AWS Rekognition**: Face Liveness, CompareFaces, DetectText
- **AWS S3**: Secure document storage with presigned URLs
- **AWS Cognito**: Identity pool for cross-cloud authentication
- **Google Cloud (Optional)**: Backup storage and processing

### Security Measures
- **Encryption**: 
  - TLS 1.3 for data in transit
  - S3 server-side encryption for data at rest
- **Authentication**: 
  - JWT tokens with expiration
  - Multi-factor email verification
- **Rate Limiting**: 
  - API throttling (100 requests/minute per user)
  - Face verification limits (20/day)
- **Audit Logging**: 
  - Complete action history with IP tracking
  - Admin action logs with user agent capture

---

## API Response Standards

### Success Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-12-11T10:30:45Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "VALIDATION_ERROR",
  "details": { ... },
  "timestamp": "2025-12-11T10:30:45Z"
}
```

### HTTP Status Codes
- `200 OK`: Successful GET, PUT requests
- `201 Created`: Successful POST requests
- `204 No Content`: Successful DELETE requests
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

---

## Integration Examples

### 1. Document Submission Flow
```python
# Step 1: Upload document
POST /api/documents/
{
  "document_type": "certificate_of_enrollment",
  "document_file": <file>
}
→ Response: { "id": 123, "status": "ai_processing" }

# Step 2: Check AI analysis status
GET /api/ai/status/123/
→ Response: { "status": "completed", "confidence": 0.87, "ai_auto_approved": true }

# Step 3: Admin review (if needed)
POST /api/documents/123/review/
{
  "status": "approved",
  "admin_notes": "Document verified and approved"
}
```

### 2. Grade Submission Workflow
```python
# Step 1: Check eligibility
GET /api/grade-workflow/check-eligibility/
→ Response: { "can_submit": true, "coe_subjects_count": 8 }

# Step 2: Get COE subjects
GET /api/grade-workflow/coe-subjects/
→ Response: { "subjects": [...], "subject_count": 8 }

# Step 3: Submit each subject grade
POST /api/grade-workflow/submit-subject/
{
  "subject_code": "IT101",
  "subject_name": "Introduction to IT",
  "grade_received": 1.25,
  "grade_sheet": <file>
}

# Step 4: Validate all submissions
POST /api/grade-workflow/validate/
{
  "academic_year": "2024-2025",
  "semester": "1st"
}
→ Response: { "is_valid": true, "gwa_calculated": 1.45, "merit_level": "DISTINCTION" }
```

### 3. Biometric Verification Flow
```python
# Step 1: Create liveness session
POST /api/face-verification/create-liveness-session/
→ Response: { "session_id": "abc-123", "expires_at": "2025-12-11T11:00:00Z" }

# Step 2: Complete liveness challenge (client-side with AWS Amplify)
# User performs 3D liveness challenge on frontend

# Step 3: Verify liveness results
POST /api/face-verification/verify-liveness/
{
  "session_id": "abc-123"
}
→ Response: { "liveness_passed": true, "confidence": 95.2 }

# Step 4: Complete identity verification
POST /api/face-verification/verify-with-liveness/
{
  "session_id": "abc-123",
  "id_document_id": 456
}
→ Response: { "verification_passed": true, "similarity": 99.4, "status": "admin_review" }

# Step 5: Admin adjudication
POST /api/admin/face-adjudications/789/approve/
{
  "admin_notes": "Face matches ID, identity confirmed"
}
```

---

## Performance Metrics

### AI Processing Performance
- **Average Document Processing Time**: 15-30 seconds
- **AI Confidence Distribution**:
  - High (>75%): 62% of documents
  - Medium (50-75%): 28% of documents
  - Low (<50%): 10% of documents
- **Auto-Approval Rate**: 58% of documents
- **Manual Review Rate**: 42% of documents

### System Scalability
- **Concurrent Users**: Supports 500+ concurrent users
- **API Response Time**: <200ms average for GET requests
- **Document Storage**: Unlimited (AWS S3)
- **Database Performance**: Optimized indexes for <50ms query times

---

## Future Enhancements

### Planned Features
1. **Mobile Application**: Native iOS/Android apps with offline support
2. **Blockchain Integration**: Immutable audit trail for document verification
3. **Advanced Fraud Detection**: Machine learning-based anomaly detection
4. **Real-Time Notifications**: WebSocket-based push notifications
5. **Multi-Language Support**: Internationalization for Filipino/English
6. **API Versioning**: v2 API with GraphQL support
7. **Batch Processing**: Bulk document upload and verification
8. **Export Capabilities**: PDF reports, CSV data exports

### API Versioning Strategy
- Current Version: `v1` (default)
- Deprecation Policy: 6-month notice before version sunset
- Backward Compatibility: Maintained for at least 2 major versions

---

## Support & Documentation

### Developer Resources
- **API Documentation**: [Swagger/OpenAPI specification]
- **Code Examples**: GitHub repository with sample integrations
- **SDK Libraries**: Python, JavaScript, PHP client libraries
- **Postman Collection**: Pre-configured API test collection

### Contact Information
- **Technical Support**: support@tcu-ceaa.edu.ph
- **API Issues**: api-support@tcu-ceaa.edu.ph
- **Security Concerns**: security@tcu-ceaa.edu.ph

---

**Last Updated**: December 11, 2025  
**API Version**: 1.0.0  
**Documentation Version**: 1.2.0
