# Grade Submission Workflow Refactor - Progress Summary

**Date:** November 17, 2025  
**Feature Branch:** `feature/liveness-detection-live-camera`  
**Status:** Backend Implementation Complete (50% Overall Progress)

## 🎯 Refactor Objectives

1. **COE-Based Validation**: Extract subjects from Certificate of Enrollment and validate grade submissions against them
2. **Per-Subject Submission**: Change from bulk grade submission to one image per subject
3. **Enhanced Validation**: Validate subject codes, names, and counts
4. **Workflow Reorganization**: Move liveness detection to occur AFTER grade computation
5. **Disclaimer Screen**: Add mandatory disclaimer before liveness verification

---

## ✅ Completed Tasks (Backend - 100%)

### 1. COE Verification Service Enhancement ✅
**File:** `backend/myapp/coe_verification_service.py`

**Added Methods:**
- `extract_subject_list(image_path)` - Main extraction method
- `_extract_subjects_from_text(text)` - Regex-based subject parsing
- Updated `extract_coe_text()` to include subject extraction
- Updated `verify_coe_document()` to return subject data

**Capabilities:**
- Extracts subject codes (e.g., GE101, MATH102)
- Extracts subject names (e.g., Technopreneurship, Mathematics)
- Supports multiple COE formats with regex patterns
- Returns confidence scores
- Handles OCR errors gracefully

**Example Output:**
```json
{
  "success": true,
  "subjects": [
    {"subject_code": "GE101", "subject_name": "Technopreneurship"},
    {"subject_code": "MATH102", "subject_name": "College Algebra"},
    {"subject_code": "ENG101", "subject_name": "Communication Skills"}
  ],
  "subject_count": 3,
  "confidence": 0.92
}
```

---

### 2. Database Models Updated ✅
**File:** `backend/myapp/models.py`  
**Migration:** `0027_add_subject_tracking_fields.py`

**DocumentSubmission Model - New Fields:**
```python
extracted_subjects = models.JSONField(default=list, help_text="List of subjects from COE")
subject_count = models.IntegerField(default=0, help_text="Total subjects extracted")
```

**GradeSubmission Model - New Fields:**
```python
# Per-subject fields
subject_code = models.CharField(max_length=20)
subject_name = models.CharField(max_length=200)
units = models.IntegerField()
grade_received = models.DecimalField(max_digits=5, decimal_places=2)

# Legacy fields made optional for backward compatibility
total_units = models.IntegerField(blank=True, null=True)
general_weighted_average = models.DecimalField(blank=True, null=True)
```

**Migration Status:** ✅ Applied successfully

---

### 3. Grade Validation Service ✅
**File:** `backend/myapp/grade_validation_service.py` (NEW)

**Class:** `GradeValidationService`

**Methods:**
- `validate_grade_submissions(coe_subjects, grade_submissions)` - Main validation
- `_validate_subject_count()` - Ensures count matches
- `_validate_subjects()` - Validates codes and names
- `_normalize_code()` - Normalizes subject codes for comparison
- `_calculate_similarity()` - Fuzzy string matching (85% threshold)
- `get_validation_summary()` - Human-readable report

**Validation Checks:**
1. ✅ Subject count matches between COE and submissions
2. ✅ All subject codes match (normalized, case-insensitive)
3. ✅ All subject names match (fuzzy matching at 85% similarity)
4. ✅ No missing subjects (all COE subjects submitted)
5. ✅ No extra subjects (no submissions without COE match)

**Example Validation Result:**
```json
{
  "is_valid": true,
  "validation_results": {
    "subject_count_match": true,
    "all_codes_match": true,
    "all_names_match": true
  },
  "matched_subjects": [
    {"subject_code": "GE101", "subject_name": "Technopreneurship", "name_similarity": 1.0}
  ],
  "missing_subjects": [],
  "extra_subjects": [],
  "errors": [],
  "warnings": []
}
```

---

### 4. API Endpoints Created ✅
**File:** `backend/myapp/views.py` and `backend/myapp/urls.py`

**New Endpoints:**

#### 1. `GET /api/grades/coe-subjects/`
Get list of subjects from student's approved COE.

**Response:**
```json
{
  "subjects": [...],
  "subject_count": 5,
  "coe_document_id": 123,
  "coe_submitted_at": "2025-11-15T10:30:00Z"
}
```

#### 2. `POST /api/grades/submit-subject/`
Submit grade for a single subject.

**Request:**
```json
{
  "subject_code": "GE101",
  "subject_name": "Technopreneurship",
  "academic_year": "2024-2025",
  "semester": "1st",
  "units": 3,
  "grade_received": 1.5,
  "grade_sheet": <file>
}
```

#### 3. `POST /api/grades/validate/`
Validate all grade submissions against COE.

**Request:**
```json
{
  "academic_year": "2024-2025",
  "semester": "1st"
}
```

**Response:** Full validation result with errors, warnings, matched/missing subjects

#### 4. `GET /api/grades/status/`
Get grade submission status and progress.

**Query Params:** `academic_year`, `semester`

**Response:**
```json
{
  "total_subjects": 5,
  "submitted_count": 5,
  "approved_count": 4,
  "rejected_count": 0,
  "pending_count": 1,
  "is_complete": true,
  "all_approved": false,
  "can_proceed_to_liveness": false,
  "submissions": [...],
  "coe_subjects": [...]
}
```

---

### 5. Serializers Updated ✅
**File:** `backend/myapp/serializers.py`

**GradeSubmissionSerializer:**
- Added `subject_code`, `subject_name`, `units`, `grade_received` fields
- Maintains backward compatibility with legacy fields

**DocumentSubmissionSerializer:**
- Added `extracted_subjects` and `subject_count` fields
- Both fields are read-only (auto-populated)

---

### 6. Automatic Subject Extraction ✅
**File:** `backend/myapp/views.py` (DocumentSubmissionViewSet.review)

**Behavior:**
When admin approves a COE document:
1. Automatically calls `coe_verification_service.extract_subject_list()`
2. Stores results in `extracted_subjects` and `subject_count` fields
3. Logs extraction in audit trail
4. Handles errors gracefully with fallback

**Code Location:** Lines 581-613 in views.py

---

## 🔄 Pending Tasks (Frontend & Integration - 50%)

### 6. Frontend GradeSubmissionForm Refactor (Not Started)
**File:** `frontend/src/components/GradeSubmissionForm.tsx`

**Required Changes:**
1. Fetch COE subjects on component mount (`GET /api/grades/coe-subjects/`)
2. Display subject list from COE
3. For each subject, show:
   - Subject code and name
   - Upload button for grade image
   - Status indicator (not submitted / pending / approved / rejected)
4. Submit one grade at a time using `POST /api/grades/submit-subject/`
5. Show validation feedback using `POST /api/grades/validate/`
6. Track progress using `GET /api/grades/status/`
7. Remove old fields: total_units, general_weighted_average, semestral_weighted_average
8. Add validation error display

**UI Flow:**
```
┌─────────────────────────────────────┐
│ Grade Submission                    │
├─────────────────────────────────────┤
│ From your COE: 5 subjects found     │
│                                     │
│ ☐ GE101 - Technopreneurship (3u)   │
│   [Upload Grade Image]              │
│                                     │
│ ✓ MATH102 - College Algebra (3u)   │
│   [✓ Approved] [View]               │
│                                     │
│ ⏳ ENG101 - Communication (3u)      │
│   [Pending Review]                  │
│                                     │
│ Progress: 3/5 submitted, 1 approved │
│ [Validate All] [Submit More]        │
└─────────────────────────────────────┘
```

---

### 7. Move Liveness Detection Workflow (Not Started)
**Files:** 
- `frontend/src/components/GradeSubmissionForm.tsx`
- `frontend/src/components/LiveCameraCapture.tsx`

**Current Behavior:**
- Liveness triggers immediately after grade submission

**New Behavior:**
1. Wait for ALL grades to be submitted
2. Wait for ALL grades to be approved by admin
3. Calculate GPA/GWA from all grades
4. Show disclaimer screen
5. THEN trigger liveness detection

**Logic:**
```typescript
// Check if can proceed to liveness
const canProceed = async () => {
  const status = await apiClient.get('/api/grades/status/', {
    params: { academic_year, semester }
  });
  
  return status.data.can_proceed_to_liveness; // all submitted AND all approved
};
```

---

### 8. Create Disclaimer Screen (Not Started)
**File:** `frontend/src/components/LivenessDisclaimer.tsx` (NEW)

**Requirements:**
1. Show disclaimer text about liveness verification
2. Explain what will happen (camera access, face scanning, challenges)
3. Require user acknowledgment (checkbox + button)
4. Only proceed to liveness after acknowledgment
5. Store acknowledgment timestamp

**Content Example:**
```
┌────────────────────────────────────────┐
│ Identity Verification Required         │
├────────────────────────────────────────┤
│ Before we can complete your            │
│ application, we need to verify your    │
│ identity through liveness detection.   │
│                                        │
│ What this involves:                    │
│ • Camera access permission             │
│ • Face scanning with challenges        │
│ • Color flash, blink, and movement     │
│ • Comparison with your ID photo        │
│                                        │
│ Your privacy is protected. All data    │
│ is encrypted and used only for         │
│ verification purposes.                 │
│                                        │
│ ☐ I understand and consent to this    │
│   identity verification process        │
│                                        │
│ [Proceed to Verification]              │
└────────────────────────────────────────┘
```

---

### 9. Workflow State Management (Not Started)
**Files:** Multiple (views, components, state management)

**Required State Transitions:**
```
1. COE uploaded → pending review
2. COE approved → subjects extracted
3. Grade submission enabled
4. Each grade: submitted → pending → approved/rejected
5. All grades approved → GPA calculated
6. Disclaimer shown → user acknowledges
7. Liveness detection → face verified
8. Application complete
```

**State Tracking:**
```typescript
interface WorkflowState {
  coe_status: 'not_submitted' | 'pending' | 'approved' | 'rejected';
  coe_subjects_extracted: boolean;
  grades_status: {
    total: number;
    submitted: number;
    approved: number;
    can_submit_more: boolean;
  };
  gpa_calculated: boolean;
  disclaimer_accepted: boolean;
  liveness_completed: boolean;
}
```

---

### 10. End-to-End Testing (Not Started)

**Test Scenarios:**

**Scenario 1: Happy Path**
1. Upload COE → Admin approves → Subjects extracted (5 subjects)
2. Upload grade for Subject 1 → Pending
3. Upload grade for Subject 2 → Pending
4. ... (all 5 subjects)
5. Admin approves all grades
6. System calculates GPA
7. Disclaimer shown → User accepts
8. Liveness detection → Camera opens
9. Complete challenges → Face verified
10. Application status: Complete

**Scenario 2: Validation Failures**
1. Upload COE with 5 subjects
2. Upload only 3 grades
3. Validation fails: "2 subjects missing"
4. Upload remaining 2 grades
5. Validation passes

**Scenario 3: Subject Mismatch**
1. Upload COE with subjects A, B, C
2. Try to upload grade for subject D
3. API rejects: "Subject not found in COE"

**Test Checklist:**
- [ ] COE upload and approval
- [ ] Subject extraction accuracy
- [ ] Per-subject grade submission
- [ ] Validation API responses
- [ ] Progress tracking
- [ ] Approval workflow
- [ ] GPA calculation
- [ ] Disclaimer display and acceptance
- [ ] Liveness detection trigger timing
- [ ] Mobile device compatibility
- [ ] Error handling at each step

---

## 📁 Files Modified/Created

### Backend Files Modified:
1. ✅ `backend/myapp/models.py` - Added fields to DocumentSubmission and GradeSubmission
2. ✅ `backend/myapp/coe_verification_service.py` - Added subject extraction methods
3. ✅ `backend/myapp/views.py` - Added 4 new API endpoints, updated review method
4. ✅ `backend/myapp/serializers.py` - Updated serializers with new fields
5. ✅ `backend/myapp/urls.py` - Added URL routes for new endpoints

### Backend Files Created:
6. ✅ `backend/myapp/grade_validation_service.py` - NEW validation service
7. ✅ `backend/myapp/migrations/0027_add_subject_tracking_fields.py` - NEW migration

### Frontend Files To Modify:
8. ⏳ `frontend/src/components/GradeSubmissionForm.tsx` - Complete refactor needed
9. ⏳ `frontend/src/components/GradeSubmissionForm.css` - Update styles

### Frontend Files To Create:
10. ⏳ `frontend/src/components/LivenessDisclaimer.tsx` - NEW component
11. ⏳ `frontend/src/components/LivenessDisclaimer.css` - NEW styles

---

## 🔌 API Integration Guide

### For Frontend Developers:

**Step 1: Fetch COE Subjects**
```typescript
const response = await apiClient.get('/api/grades/coe-subjects/');
const { subjects, subject_count } = response.data;
```

**Step 2: Submit Grade Per Subject**
```typescript
const formData = new FormData();
formData.append('subject_code', 'GE101');
formData.append('subject_name', 'Technopreneurship');
formData.append('academic_year', '2024-2025');
formData.append('semester', '1st');
formData.append('units', '3');
formData.append('grade_received', '1.5');
formData.append('grade_sheet', fileBlob);

await apiClient.post('/api/grades/submit-subject/', formData);
```

**Step 3: Validate All Submissions**
```typescript
const validation = await apiClient.post('/api/grades/validate/', {
  academic_year: '2024-2025',
  semester: '1st'
});

if (!validation.data.is_valid) {
  // Show errors: validation.data.errors
  // Show missing: validation.data.missing_subjects
}
```

**Step 4: Check Status**
```typescript
const status = await apiClient.get('/api/grades/status/', {
  params: { academic_year: '2024-2025', semester: '1st' }
});

if (status.data.can_proceed_to_liveness) {
  // Show disclaimer, then liveness
}
```

---

## 🧪 Testing the Backend

**Test Subject Extraction:**
```bash
cd backend
python manage.py shell
```

```python
from myapp.coe_verification_service import get_coe_verification_service
from myapp.models import DocumentSubmission

# Get a COE document
coe = DocumentSubmission.objects.filter(document_type='certificate_of_enrollment').first()

# Extract subjects
service = get_coe_verification_service()
result = service.extract_subject_list(coe.document_file.path)

print(f"Success: {result['success']}")
print(f"Subjects: {result['subjects']}")
print(f"Count: {result['subject_count']}")
```

**Test Validation:**
```python
from myapp.grade_validation_service import get_grade_validation_service

coe_subjects = [
    {'subject_code': 'GE101', 'subject_name': 'Technopreneurship'},
    {'subject_code': 'MATH102', 'subject_name': 'College Algebra'}
]

submissions = [
    {'subject_code': 'GE101', 'subject_name': 'Technopreneurship'},
    {'subject_code': 'MATH102', 'subject_name': 'College Algebra'}
]

service = get_grade_validation_service()
result = service.validate_grade_submissions(coe_subjects, submissions)

print(service.get_validation_summary(result))
```

---

## 📊 Progress Metrics

- **Backend Implementation:** 100% ✅
- **Frontend Implementation:** 0% ⏳
- **Integration Testing:** 0% ⏳
- **Overall Progress:** 50% 🔄

**Estimated Remaining Work:** 4-6 hours
- Frontend refactor: 2-3 hours
- Disclaimer component: 30 minutes
- Workflow state management: 1-2 hours
- Testing: 1 hour

---

## 🚀 Next Steps

1. **Immediate:** Start frontend refactor of GradeSubmissionForm
2. **Then:** Create LivenessDisclaimer component
3. **Then:** Update workflow to move liveness after GPA
4. **Finally:** End-to-end testing on desktop and mobile

---

## 📝 Notes

- All backend changes are backward compatible (legacy fields nullable)
- Existing grade submissions still work (use legacy fields)
- New submissions use per-subject workflow
- COE subject extraction runs automatically on approval
- Validation service uses fuzzy matching for name variations
- All changes logged in audit trail

---

**Last Updated:** November 17, 2025  
**Next Review:** After frontend implementation complete
