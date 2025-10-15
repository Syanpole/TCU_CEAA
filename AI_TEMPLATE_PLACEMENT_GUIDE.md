# 🎯 AI Template Files - Placement Guide

## ✅ VERIFICATION COMPLETE!

Your AI system is **FULLY CONNECTED** to the client side:
- ✅ Frontend → Backend API → AI Verification → Reference Templates
- ✅ 35 Document types configured
- ✅ AI modules ready
- ✅ Frontend service integrated

---

## 📂 Where to Place Your Template Files

### ✅ Already Placed (6 templates found):

#### 1. Birth Certificates
```
✅ backend/ai_model_data/reference_documents/birth_certificates/
   └── NSO_BIRTH_CERTIFICATE_TEMPLATE 1.jpg (1.4 MB)
```

#### 2. School IDs
```
✅ backend/ai_model_data/reference_documents/school_ids/
   ├── CAS_ID_TEMPLATE 1.jpg (112 KB)
   ├── CBM_ID_TEMPLATE 1.jpg (71 KB)
   ├── CCJ_ID_TEMPLATE 1.jpg (182 KB)
   └── CICT_ID_TEMPLATE 1.jpg (165 KB)
```

#### 3. Government IDs
```
✅ backend/ai_model_data/reference_documents/government_ids/
   └── VOTERS_CERTIFICATE_TEMPLATE 1.jpg (647 KB)
```

### ⚠️ Need to Place (3 templates):

#### 4. Certificates of Enrollment
```
📁 backend/ai_model_data/reference_documents/certificates_of_enrollment/
   ├── GENERAL_COE_FORMAT 1.jpg  ← Place this file here
   └── GENERAL_COE_FORMAT 2.jpg  ← Place this file here
```

#### 5. Transcripts of Records
```
📁 backend/ai_model_data/reference_documents/transcripts/
   └── TOR_TEMPLATE 1.jpg  ← Place this file here
```

---

## 🚀 Quick Setup Options

### Option 1: Manual Copy (Easiest)
1. Locate your template files:
   - `GENERAL_COE_FORMAT 1.jpg`
   - `GENERAL_COE_FORMAT 2.jpg`
   - `TOR_TEMPLATE 1.jpg`

2. Copy them to the appropriate folders:
   ```
   Copy GENERAL_COE_FORMAT 1.jpg → backend/ai_model_data/reference_documents/certificates_of_enrollment/
   Copy GENERAL_COE_FORMAT 2.jpg → backend/ai_model_data/reference_documents/certificates_of_enrollment/
   Copy TOR_TEMPLATE 1.jpg → backend/ai_model_data/reference_documents/transcripts/
   ```

### Option 2: Run Organizer Script (Automatic)
```powershell
# Run this command in PowerShell from project root:
.\organize_templates.ps1
```
This script will automatically find and move all template files to the correct locations.

### Option 3: Manual Commands
```powershell
# Copy COE templates
Copy-Item "GENERAL_COE_FORMAT 1.jpg" -Destination "backend\ai_model_data\reference_documents\certificates_of_enrollment\"
Copy-Item "GENERAL_COE_FORMAT 2.jpg" -Destination "backend\ai_model_data\reference_documents\certificates_of_enrollment\"

# Copy TOR template
Copy-Item "TOR_TEMPLATE 1.jpg" -Destination "backend\ai_model_data\reference_documents\transcripts\"
```

---

## 🔗 How Frontend Connects to Templates

### 1. User Uploads Document (Frontend)
```typescript
// frontend/src/components/DocumentUploadForm.tsx
const uploadDocument = async (file: File, documentType: string) => {
  await apiClient.post('/documents/', formData);
};
```

### 2. Backend Receives & Processes (API)
```python
# backend/myapp/views.py
@api_view(['POST'])
def upload_document(request):
    # Saves to database
    document = DocumentSubmission.objects.create(...)
    
    # Triggers AI verification
    ai_result = analyze_document(document)
```

### 3. AI Analyzes Against Templates
```python
# backend/ai_verification/base_verifier.py
def verify_document(document):
    # Loads reference templates from:
    templates = load_templates(f'ai_model_data/reference_documents/{doc_type}/')
    
    # Compares submitted document against templates
    confidence_score = compare_features(document, templates)
    
    return verification_result
```

### 4. Results Display in Frontend
```typescript
// frontend/src/components/DocumentDetailsModal.tsx
<div className="ai-analysis">
  <div className="confidence-score">{aiConfidence}%</div>
  <div className="ai-notes">{aiAnalysisNotes}</div>
</div>
```

---

## 📊 Document Type Mapping

| Template File | Database Code | Frontend Label | AI Use Case |
|--------------|---------------|----------------|-------------|
| NSO_BIRTH_CERTIFICATE_TEMPLATE 1.jpg | `birth_certificate` | Birth Certificate (PSA/NSO) | Verify birth certificate authenticity |
| CAS_ID_TEMPLATE 1.jpg | `school_id` | School ID | Verify CAS student ID |
| CBM_ID_TEMPLATE 1.jpg | `school_id` | School ID | Verify CBM student ID |
| CCJ_ID_TEMPLATE 1.jpg | `school_id` | School ID | Verify CCJ student ID |
| CICT_ID_TEMPLATE 1.jpg | `school_id` | School ID | Verify CICT student ID |
| VOTERS_CERTIFICATE_TEMPLATE 1.jpg | `voters_id` | Voter's ID | Verify voter's certificate |
| GENERAL_COE_FORMAT 1.jpg | `certificate_of_enrollment` | Certificate of Enrollment | Verify COE format 1 |
| GENERAL_COE_FORMAT 2.jpg | `certificate_of_enrollment` | Certificate of Enrollment | Verify COE format 2 |
| TOR_TEMPLATE 1.jpg | `transcript_of_records` | Transcript of Records | Verify TOR authenticity |

---

## 🎨 AI Verification Features

Once all templates are in place, the AI can:

1. **Document Type Detection** - Automatically identify document types
2. **Layout Matching** - Compare document structure against templates
3. **Text Extraction** - Extract key information (names, dates, IDs)
4. **Quality Assessment** - Check image quality, completeness
5. **Fraud Detection** - Flag suspicious or manipulated documents
6. **Confidence Scoring** - Assign 0-100% confidence scores
7. **Auto-Approval** - Auto-approve high-confidence matches (>90%)

---

## ✅ Verification Checklist

- [x] Birth certificates template (1 file)
- [x] School IDs templates (4 files)
- [x] Government IDs template (1 file)
- [ ] COE templates (2 files) - **PLACE THESE**
- [ ] TOR template (1 file) - **PLACE THIS**
- [x] Frontend document service configured
- [x] Backend API endpoints ready
- [x] AI verification modules installed
- [x] Database models configured

---

## 🚀 Next Steps

1. **Place remaining templates** (COE formats 1 & 2, TOR)
2. **Run verification again**:
   ```bash
   python backend\verify_ai_templates.py
   ```
3. **Test AI verification**:
   - Upload a test document
   - Check AI confidence score
   - Review AI analysis notes

---

## 📞 Need Help?

If you need to add more templates:
1. Place image files in appropriate folder
2. Use descriptive names: `{TYPE}_TEMPLATE_{NUMBER}.jpg`
3. Recommended: 300 DPI, JPG/PNG format
4. Maximum 5MB per file

---

**Last Updated**: October 14, 2025
**Status**: 6 of 9 templates in place (67% complete)
**Action Required**: Place 3 remaining template files
