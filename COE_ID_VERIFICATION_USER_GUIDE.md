# 🎓 COE & ID Verification System - User Guide

## Overview
This guide explains how students can upload documents and how admins can review them using the AI-powered COE (Certificate of Enrollment) and ID verification systems.

## 📋 Table of Contents
1. [Student Document Upload](#student-document-upload)
2. [Admin Document Review](#admin-document-review)
3. [API Endpoints](#api-endpoints)
4. [COE Verification Details](#coe-verification-details)
5. [ID Verification Details](#id-verification-details)

---

## 🎒 Student Document Upload

### How Students Upload Documents

#### 1. Upload COE Document
**Endpoint:** `POST /api/documents/`

**Request:**
```json
{
  "document_type": "certificate_of_enrollment",
  "file": "<file_upload>",
  "description": "First Semester 2025-2026 COE"
}
```

**Supported COE Document Types:**
- `certificate_of_enrollment` - Certificate of Enrollment
- `enrollment_certificate` - Enrollment Certificate

**Response:**
```json
{
  "id": 123,
  "document_type": "certificate_of_enrollment",
  "document_type_display": "Certificate of Enrollment",
  "status": "ai_processing",
  "submitted_at": "2025-11-11T10:30:00Z"
}
```

#### 2. Upload ID Documents
**Endpoint:** `POST /api/documents/`

**Supported ID Types:**
- `school_id` - School ID
- `birth_certificate` - Birth Certificate
- `umid_card` - UMID Card
- `drivers_license` - Driver's License
- `passport` - Passport
- `voters_id` - Voter's ID
- `philsys_id` - Philippine National ID
- And many more government-issued IDs

**Request:**
```json
{
  "document_type": "school_id",
  "file": "<file_upload>",
  "description": "TCU Student ID"
}
```

#### 3. Check Document Status
**Endpoint:** `GET /api/ai/status/{document_id}/`

**Response:**
```json
{
  "document_id": 123,
  "status": "approved",
  "ai_completed": true,
  "confidence_score": 0.88,
  "auto_approved": false,
  "analysis_notes": "AI Analysis completed. COE verified with high confidence.",
  "recommendations": ["approved"]
}
```

#### 4. View All Your Documents
**Endpoint:** `GET /api/documents/`

Students can only see their own documents.

---

## 👨‍💼 Admin Document Review

### Admin Dashboard

#### 1. View Document Dashboard
**Endpoint:** `GET /api/admin/documents/dashboard/`

**Optional Query Parameters:**
- `status` - Filter by status (pending, approved, rejected, ai_processing)
- `document_type` - Filter by document type
- `student_id` - Search by student ID
- `date_from` - Filter from date (YYYY-MM-DD)
- `date_to` - Filter to date (YYYY-MM-DD)
- `ai_analyzed` - Filter by AI analysis status (true/false)

**Example Request:**
```
GET /api/admin/documents/dashboard/?status=pending&document_type=certificate_of_enrollment
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_documents": 250,
    "status_breakdown": [
      {"status": "pending", "count": 45},
      {"status": "approved", "count": 180},
      {"status": "rejected", "count": 15}
    ]
  },
  "ai_statistics": {
    "total_analyzed": 230,
    "auto_approved": 150,
    "avg_confidence": 0.82,
    "high_confidence": 180,
    "medium_confidence": 40,
    "low_confidence": 10
  },
  "coe_statistics": {
    "total": 85,
    "valid": 78,
    "invalid": 7,
    "avg_confidence": 0.86
  },
  "id_verification_statistics": {
    "total": 120,
    "identity_verified": 110,
    "identity_failed": 10,
    "avg_confidence": 0.84
  },
  "recent_documents": [...],
  "attention_needed": [...]
}
```

#### 2. View Detailed AI Analysis
**Endpoint:** `GET /api/documents/{id}/ai_details/`

**Response:**
```json
{
  "document_id": 123,
  "student": {
    "name": "Juan Dela Cruz",
    "student_id": "19-0643",
    "email": "juan@tcu.edu.ph"
  },
  "document_type": "certificate_of_enrollment",
  "ai_analysis": {
    "completed": true,
    "confidence_score": 0.883,
    "auto_approved": false,
    "algorithms_results": {
      "coe_verification": {
        "name": "COE Verification (YOLO Element Detection)",
        "confidence": 0.883,
        "status": "VALID",
        "is_valid": true,
        "detected_elements": {
          "city_logo": {"present": true, "count": 1, "confidence": 0.87},
          "enrolled_text": {"present": true, "count": 1, "confidence": 0.90},
          "free_tuition": {"present": true, "count": 2, "confidence": 0.90},
          "university_logo": {"present": true, "count": 1, "confidence": 0.91},
          "validated": {"present": true, "count": 1, "confidence": 0.90},
          "watermark": {"present": true, "count": 1, "confidence": 0.85}
        },
        "validation_checks": {
          "has_city_logo": true,
          "has_enrolled_text": true,
          "has_university_logo": true,
          "has_required_elements": true,
          "has_security_features": true
        },
        "checks_passed": 5,
        "total_checks": 5
      }
    },
    "overall_analysis": {
      "overall_confidence": 0.856,
      "recommendation": "approved"
    }
  }
}
```

#### 3. Review Document (Approve/Reject)
**Endpoint:** `POST /api/documents/{id}/review/`

**Request:**
```json
{
  "status": "approved",
  "admin_notes": "Document verified. All COE elements detected with high confidence."
}
```

**Status Options:**
- `approved` - Approve document
- `rejected` - Reject document
- `revision_needed` - Request revision from student

**Response:**
```json
{
  "id": 123,
  "status": "approved",
  "admin_notes": "Document verified...",
  "reviewed_at": "2025-11-11T15:45:00Z",
  "reviewed_by_name": "Admin User"
}
```

#### 4. Trigger Re-Analysis
**Endpoint:** `POST /api/documents/{id}/reanalyze/`

Admins can trigger a fresh AI analysis of any document.

**Response:**
```json
{
  "success": true,
  "message": "Document re-analyzed successfully",
  "new_confidence": 0.89,
  "new_status": "approved"
}
```

#### 5. View All Documents (Admin)
**Endpoint:** `GET /api/documents/`

Admins can see ALL documents from all students.

---

## 🔌 API Endpoints Summary

### Student Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/` | Upload a new document |
| GET | `/api/documents/` | List your documents |
| GET | `/api/documents/{id}/` | View document details |
| GET | `/api/ai/status/{id}/` | Check AI analysis status |

### Admin Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/documents/dashboard/` | Document management dashboard |
| GET | `/api/documents/` | List ALL documents |
| GET | `/api/documents/{id}/ai_details/` | View detailed AI analysis |
| POST | `/api/documents/{id}/review/` | Approve/reject document |
| POST | `/api/documents/{id}/reanalyze/` | Trigger re-analysis |

### AI System Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/analyze-document/` | Manual AI analysis trigger |
| GET | `/api/ai/dashboard-stats/` | AI system statistics |
| POST | `/api/ai/batch-process/` | Batch process multiple docs |

---

## 🎓 COE Verification Details

### What the AI Detects

The COE verification system uses **YOLOv8 object detection** to identify 7 key elements:

1. **City of Taguig Logo** ⭐ (Required)
2. **ENROLLED Text** ⭐ (Required)
3. **Free Tuition Indicator**
4. **Taguig City University Logo** ⭐ (Required)
5. **Validated Stamp**
6. **Watermark**
7. **IloveTaguig Logo**

### Validation Checks

The system performs 5 validation checks:

1. ✅ **Has City Logo** - Verifies presence of City of Taguig logo
2. ✅ **Has Enrolled Text** - Detects "ENROLLED" text
3. ✅ **Has University Logo** - Finds TCU logo
4. ✅ **Has Required Elements** - All 3 required elements present
5. ✅ **Has Security Features** - Detects watermark/validation stamps

### Confidence Scoring

The COE confidence is calculated using weighted components:
- **40%** - Detection quality and confidence
- **30%** - Required elements (logos, ENROLLED text)
- **15%** - Optional elements (Free tuition, IloveTaguig)
- **15%** - Security features (watermark, validated stamp)

### Status Determination

- **VALID** (≥70% confidence, all required elements)
- **QUESTIONABLE** (50-70% confidence, some elements missing)
- **INVALID** (<50% confidence, missing required elements)

---

## 🆔 ID Verification Details

### What the AI Verifies

The ID verification system uses **YOLOv8 + AWS Textract + Identity Matching**:

1. **YOLO Detection**
   - Detects if ID card is present
   - Identifies ID card boundaries
   - Verifies it's a valid ID document

2. **OCR Extraction** (AWS Textract)
   - Extracts text from ID
   - Identifies key fields (name, ID number, address)
   - Validates text quality

3. **Identity Matching**
   - Compares extracted name with student profile
   - Validates student ID matches
   - Checks address consistency
   - Uses fuzzy string matching for accuracy

### Validation Checks

1. ✅ **ID Detected** - YOLO confirms ID card presence
2. ✅ **Text Readable** - OCR successfully extracts text
3. ✅ **Name Matches** - Name matches student profile (≥80% similarity)
4. ✅ **ID Number Valid** - ID number format is valid
5. ✅ **Quality Acceptable** - Image quality sufficient

### Identity Verification Process

```
1. YOLO Detection (30%) → Confirms ID card present
2. OCR Extraction (30%) → Extracts text fields
3. Identity Match (40%) → Verifies student identity
   ├─ Name similarity ≥ 80% → Match
   ├─ ID number matches → Verified
   └─ Address similar → Confirmed
```

### Status Determination

- **VALID + Identity Verified** (≥80% confidence, identity matches)
- **VALID + Identity Unverified** (≥70% confidence, no identity data)
- **QUESTIONABLE** (50-70% confidence, partial data)
- **INVALID** (<50% confidence, failed checks)

---

## 📊 Example Workflows

### Student Workflow

1. **Upload COE**
   ```bash
   POST /api/documents/
   {
     "document_type": "certificate_of_enrollment",
     "file": <coe_file>,
     "description": "First Sem 2025-2026"
   }
   ```

2. **Check Status**
   ```bash
   GET /api/ai/status/123/
   ```

3. **View Result**
   - Status: `approved` (if AI confidence ≥85%)
   - Status: `pending` (if 50% ≤ confidence < 85%)
   - Status: `rejected` (if confidence < 30%)

### Admin Workflow

1. **View Dashboard**
   ```bash
   GET /api/admin/documents/dashboard/?status=pending
   ```

2. **Review Documents Needing Attention**
   - Dashboard shows `attention_needed` list
   - Documents with low AI confidence
   - Documents pending manual review

3. **Check AI Details**
   ```bash
   GET /api/documents/123/ai_details/
   ```

4. **Make Decision**
   ```bash
   POST /api/documents/123/review/
   {
     "status": "approved",
     "admin_notes": "Verified. All elements detected."
   }
   ```

5. **Re-analyze if needed**
   ```bash
   POST /api/documents/123/reanalyze/
   ```

---

## 🔐 Authentication

All endpoints require authentication via JWT token:

```bash
# Login
POST /api/auth/login/
{
  "email": "user@tcu.edu.ph",
  "password": "password"
}

# Use token in headers
Authorization: Bearer <token>
```

---

## ⚠️ Important Notes

### For Students
- ✅ Upload clear, high-quality images/PDFs
- ✅ Ensure all COE elements are visible
- ✅ Use valid ID documents
- ✅ Wait for AI processing (typically 10-30 seconds)
- ⚠️ Documents with confidence ≥85% are auto-approved
- ⚠️ Low confidence documents require manual review

### For Admins
- ✅ Use dashboard filters to manage documents efficiently
- ✅ Review AI analysis details before making decisions
- ✅ Add clear admin notes for student reference
- ✅ Re-analyze if document quality was poor initially
- ⚠️ Pay attention to identity verification results for IDs
- ⚠️ Review documents in "attention_needed" list regularly

---

## 📈 Algorithm Weights

When AI analyzes documents, it uses weighted scoring:

| Algorithm | Weight | Purpose |
|-----------|--------|---------|
| Document Validator | 12% | OCR + Pattern Matching |
| Cross-Document Matcher | 8% | Fuzzy String Matching |
| Grade Verifier | 10% | GWA Calculation |
| Face Verifier | 8% | Face Detection |
| Fraud Detector | 12% | Metadata Analysis |
| AI Generated Detector | 12% | AI Content Detection |
| **ID Verification** | **23%** | YOLO + Textract + Identity |
| **COE Verification** | **15%** | YOLO Element Detection |
| **Total** | **100%** | Overall Confidence |

---

## 🎯 Success Criteria

### COE Documents
- ✅ **Auto-Approved**: ≥85% confidence, all checks passed
- ⚠️ **Manual Review**: 50-85% confidence
- ❌ **Auto-Rejected**: <30% confidence

### ID Documents
- ✅ **Auto-Approved**: ≥85% confidence, identity verified
- ⚠️ **Manual Review**: 50-85% confidence, identity unverified
- ❌ **Auto-Rejected**: <30% confidence, identity failed

---

## 🛠️ Testing

### Test COE Verification
```bash
python backend/test_coe_verification.py "path/to/coe.jpg"
```

### Test COE with OCR
```bash
python backend/test_coe_with_ocr.py "path/to/coe.jpg"
```

### Test ID Verification
```bash
python backend/test_id_verification.py "path/to/id.jpg"
```

---

## 📞 Support

For technical issues or questions:
- Check AI analysis details in admin dashboard
- Review audit logs for detailed processing history
- Contact system administrator for algorithm adjustments

---

**Last Updated:** November 11, 2025
**System Version:** 2.0 (with COE & ID Verification)
