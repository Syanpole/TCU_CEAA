# 🧪 Testing Guide: Document Submission with AI Verification

## 🎯 Test Objectives

Verify that:
1. Document upload works correctly
2. AI verification runs automatically
3. UI displays proper feedback
4. Status tracking works in real-time
5. All CRUD operations function properly

## 📋 Pre-Testing Checklist

### Backend Requirements:
- [ ] Django server is running (`python manage.py runserver`)
- [ ] Database migrations are applied
- [ ] AI verification system is configured
- [ ] User is authenticated with valid token
- [ ] `/api/documents/` endpoint is accessible

### Frontend Requirements:
- [ ] React development server is running (`npm start`)
- [ ] User is logged in as a student
- [ ] Application qualification is completed
- [ ] Full application form is submitted

## 🧪 Test Cases

### Test 1: Upload Valid Document ✅

**Steps:**
1. Navigate to "Submission of Requirements" section
2. Click "Add Document" button
3. Select document type: "[H] Birth Certificate"
4. Choose a valid PDF file (< 10MB)
5. Add optional description
6. Click "Upload Document"

**Expected Results:**
- ✅ Upload progress bar appears (0% → 100%)
- ✅ Success message: "Document uploaded successfully! AI is now analyzing..."
- ✅ Modal closes after 2 seconds
- ✅ Document appears in the grid with status "AI Processing" 🤖
- ✅ After AI analysis (2-5 seconds), status updates to "Approved" ✅ or "Rejected" ❌
- ✅ AI confidence score displays (e.g., "85.3%")
- ✅ AI verified badge appears when complete

**API Call:**
```
POST /api/documents/
Content-Type: multipart/form-data
Body: {
  document_type: "birth_certificate",
  file: <File>,
  description: "My birth certificate"
}
```

---

### Test 2: File Size Validation ❌

**Steps:**
1. Click "Add Document"
2. Select document type
3. Choose a file > 10MB

**Expected Results:**
- ❌ Error message: "File size must be less than 10MB"
- ❌ File is not uploaded
- ❌ Upload button remains disabled

---

### Test 3: Invalid File Type ❌

**Steps:**
1. Click "Add Document"
2. Select document type
3. Choose a .docx or .txt file

**Expected Results:**
- ❌ Error message: "Only PDF, JPG, and PNG files are allowed"
- ❌ File is rejected
- ❌ Upload button remains disabled

---

### Test 4: Missing Required Fields ❌

**Steps:**
1. Click "Add Document"
2. Don't select document type
3. Choose a valid file
4. Click "Upload Document"

**Expected Results:**
- ❌ Error message: "Please select document type and file to upload"
- ❌ Upload doesn't proceed

---

### Test 5: View Document Details 👁️

**Steps:**
1. Find an uploaded document in the grid
2. Click "View Details" button

**Expected Results:**
- ✅ Alert/Modal shows:
  - Document type
  - Status
  - AI confidence score
  - AI analysis notes

---

### Test 6: Delete Document 🗑️

**Steps:**
1. Click delete button (×) on a document card
2. Confirm deletion in popup

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ Document is removed from grid
- ✅ Success message appears
- ✅ Document list refreshes

**API Call:**
```
DELETE /api/documents/{id}/
```

---

### Test 7: Empty State Display 📄

**Steps:**
1. Delete all documents (or use fresh account)
2. View "Submission of Requirements" section

**Expected Results:**
- ✅ Empty state icon displays (📄)
- ✅ Message: "No Documents Uploaded Yet"
- ✅ Tip about AI verification shows
- ✅ "Upload Your First Document" button visible

---

### Test 8: Loading State 🔄

**Steps:**
1. Refresh page while on "Submission of Requirements"
2. Observe initial load

**Expected Results:**
- ✅ Loading spinner appears
- ✅ Message: "Loading your documents..."
- ✅ Grid appears after documents load

---

### Test 9: AI Confidence Display 🤖

**Steps:**
1. Upload multiple documents
2. Wait for AI analysis to complete
3. Check confidence scores

**Expected Results:**
- ✅ Confidence scores display as percentages (0-100%)
- ✅ High confidence (≥75%) → Green "Approved" status
- ✅ Medium confidence (50-74%) → Yellow "Pending" status
- ✅ Low confidence (<50%) → Red "Rejected" status
- ✅ "AI Verified" badge appears on completed documents

---

### Test 10: Responsive Design 📱

**Steps:**
1. Test on desktop (1920px)
2. Test on tablet (768px)
3. Test on mobile (375px)

**Expected Results:**
- ✅ Desktop: 3-4 column grid
- ✅ Tablet: 2 column grid
- ✅ Mobile: Single column
- ✅ All buttons accessible
- ✅ Text is readable
- ✅ Modal fits screen

---

### Test 11: Upload Progress Tracking 📊

**Steps:**
1. Upload a large file (5-9MB)
2. Observe progress bar

**Expected Results:**
- ✅ Progress starts at 0%
- ✅ Increases to ~90% during upload
- ✅ Shows "Uploading... X%"
- ✅ Reaches 100% when complete
- ✅ Shows "Processing with AI..." at 100%

---

### Test 12: Error Handling 🔴

**Steps:**
1. Disconnect internet
2. Try uploading document

**Expected Results:**
- ❌ Error message displays
- ❌ Clear error description
- ❌ Upload button re-enabled
- ❌ User can retry

---

### Test 13: Dark Mode Support 🌙

**Steps:**
1. Toggle dark mode
2. Check all UI elements

**Expected Results:**
- ✅ Background colors invert properly
- ✅ Text remains readable
- ✅ Cards have proper contrast
- ✅ Buttons look correct

---

## 🔍 Backend Verification

### Check Database:
```sql
SELECT * FROM myapp_documentsubmission 
WHERE student_id = <your_user_id>
ORDER BY submitted_at DESC;
```

**Expected Fields:**
- `document_type`: Matches selected type
- `status`: 'ai_processing' → 'approved' or 'rejected'
- `ai_confidence_score`: Number between 0 and 1
- `ai_analysis_completed`: True after processing
- `ai_analysis_notes`: Contains analysis summary

### Check AI Logs:
```bash
# Backend console should show:
- "🤖 AI Analysis Started for document <id>"
- "Running 6 AI algorithms..."
- "✅ AI Analysis Complete: <confidence>%"
- "Decision: <approved/rejected>"
```

---

## 📊 Performance Metrics

### Target Benchmarks:
- **Upload Time**: < 3 seconds for 2MB file
- **AI Analysis**: 2-5 seconds average
- **UI Response**: < 100ms for interactions
- **Page Load**: < 1 second for document list

### Measure Performance:
```javascript
// In browser console:
console.time('upload');
// Upload document
console.timeEnd('upload');
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Failed to load documents"
**Solution:** 
- Check if backend is running
- Verify authentication token
- Check browser console for CORS errors

### Issue 2: AI confidence not showing
**Solution:**
- Wait 5-10 seconds after upload
- Refresh page
- Check if AI system is configured

### Issue 3: Upload gets stuck at 90%
**Solution:**
- Check file size (max 10MB)
- Verify backend disk space
- Check network connection

### Issue 4: Document type mismatch
**Solution:**
- Verify `documentTypeMapping` in code
- Check backend `DOCUMENT_TYPES` in models.py
- Ensure types match exactly

---

## ✅ Success Criteria

All tests must pass:
- [x] Upload works without errors
- [x] AI verification completes
- [x] Status updates in real-time
- [x] UI is responsive
- [x] Error handling is robust
- [x] Performance meets targets
- [x] All CRUD operations work
- [x] Dark mode works correctly

---

## 📝 Test Report Template

```
Test Date: _____________
Tester: _____________
Environment: [Development / Staging / Production]

Test Results:
✅ Test 1: Passed
✅ Test 2: Passed
❌ Test 3: Failed - [reason]
...

Issues Found:
1. [Issue description]
2. [Issue description]

Performance Notes:
- Upload time: _____ seconds
- AI processing: _____ seconds
- Page load: _____ seconds

Overall Status: [PASS / FAIL]
```

---

## 🚀 Next Steps After Testing

1. **If all tests pass:**
   - Deploy to staging
   - Conduct user acceptance testing
   - Prepare for production

2. **If issues found:**
   - Log bugs in issue tracker
   - Prioritize fixes
   - Re-test after fixes

---

**Last Updated:** November 5, 2025
**Version:** 1.0
**Status:** Ready for QA Testing
