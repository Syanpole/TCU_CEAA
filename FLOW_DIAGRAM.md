# Visual Flow Diagram: Grade Submission with Liveness Detection

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GRADE SUBMISSION WITH LIVENESS FLOW                  │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: GRADE SUBMISSION FORM
┌─────────────────────────────────────┐
│  📝 Grade Submission Form           │
│  ┌───────────────────────────────┐  │
│  │ Semester: [1st Semester ▼]    │  │
│  │ Academic Year: [2024-2025]    │  │
│  │ GWA: [1.75]                   │  │
│  │ Total Units: [21]             │  │
│  │ Grade Sheet: [📄 Upload...]   │  │
│  └───────────────────────────────┘  │
│                                     │
│  [ Cancel ]    [Submit Grade ✓]    │
└─────────────────────────────────────┘
            ↓
            ↓ Click Submit
            ↓
┌─────────────────────────────────────┐
│  ⏳ Processing...                   │
│  Backend: AI analyzes grade sheet  │
│  Backend: Validates GWA             │
│  Backend: Creates submission        │
└─────────────────────────────────────┘
            ↓
            ↓ Success!
            ↓
Step 2: TRANSITIONAL MESSAGE
┌─────────────────────────────────────┐
│  ✅ Grades processed successfully!  │
│  Now completing final identity      │
│  verification...                    │
└─────────────────────────────────────┘
            ↓
            ↓ 2 seconds
            ↓
Step 3: LIVENESS VERIFICATION SCREEN
┌─────────────────────────────────────────────────────────────┐
│  🔒 Final Identity Verification                             │
│  ─────────────────────────────────────────────────────────  │
│  Your grades have been processed! Complete this quick       │
│  identity verification to proceed.                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 📋 What to Expect:                                   │  │
│  │                                                      │  │
│  │ 🎨 Color Flash: Look at the screen as colors flash  │  │
│  │ 👁️ Blink Detection: Blink naturally                 │  │
│  │ 📱 Movement Check: Move your face slightly          │  │
│  │                                                      │  │
│  │ ⚡ This takes only 10-15 seconds!                    │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │          [LIVE CAMERA FEED]                         │  │
│  │            👤 Your Face                             │  │
│  │                                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│            [ Start Verification ]    [ Cancel ]            │
└─────────────────────────────────────────────────────────────┘
            ↓
            ↓ Click Start
            ↓
Step 4: CHALLENGE 1 - COLOR FLASH
┌─────────────────────────────────────┐
│  🎨 Color Flash Verification...     │
│  ═══════════════════ 33%            │
│  ┌───────────────────────────────┐  │
│  │  [CAMERA FEED]                │  │
│  │  Screen flashes RED           │  │
│  │  Capturing frame...           │  │
│  └───────────────────────────────┘  │
│  Flash 1 of 3: RED ✓                │
└─────────────────────────────────────┘
            ↓ 300ms
┌─────────────────────────────────────┐
│  Screen flashes GREEN               │
│  Flash 2 of 3: GREEN ✓              │
└─────────────────────────────────────┘
            ↓ 300ms
┌─────────────────────────────────────┐
│  Screen flashes BLUE                │
│  Flash 3 of 3: BLUE ✓               │
└─────────────────────────────────────┘
            ↓
            ↓ Color Flash PASSED ✓
            ↓
Step 5: CHALLENGE 2 - BLINK DETECTION
┌─────────────────────────────────────┐
│  👁️ Blink Detection...              │
│  ═══════════════════════ 66%        │
│  ┌───────────────────────────────┐  │
│  │  [CAMERA FEED]                │  │
│  │  Detecting natural blinking   │  │
│  │  Capturing 5 frames...        │  │
│  └───────────────────────────────┘  │
│  Frames captured: ████░ 4/5          │
└─────────────────────────────────────┘
            ↓ 1 second
┌─────────────────────────────────────┐
│  Blink detected! ✓                  │
│  Frames captured: █████ 5/5          │
└─────────────────────────────────────┘
            ↓
            ↓ Blink Detection PASSED ✓
            ↓
Step 6: CHALLENGE 3 - MOVEMENT DETECTION
┌─────────────────────────────────────┐
│  🚶 Movement Verification...        │
│  ████████████████████████ 100%      │
│  ┌───────────────────────────────┐  │
│  │  [CAMERA FEED]                │  │
│  │  Detecting facial movement    │  │
│  │  Comparing frames...          │  │
│  └───────────────────────────────┘  │
│  Movement: Analyzing...             │
└─────────────────────────────────────┘
            ↓ 500ms
┌─────────────────────────────────────┐
│  Movement detected! ✓               │
│  All liveness checks passed!        │
└─────────────────────────────────────┘
            ↓
            ↓ All Challenges PASSED ✓
            ↓
Step 7: FACE VERIFICATION WITH ID
┌─────────────────────────────────────┐
│  🔍 Verifying your identity...      │
│  ┌───────────────────────────────┐  │
│  │  Retrieving your ID document  │  │
│  │  ✓ Found: School ID           │  │
│  │                               │  │
│  │  Extracting face from ID...   │  │
│  │  ✓ Face detected              │  │
│  │                               │  │
│  │  Comparing with live photo... │  │
│  │  ✓ Calculating similarity     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
            ↓
            ↓ Processing...
            ↓
         ┌──┴──┐
         │     │
    Match?     │
         │     │
    ┌────┴─────┴────┐
    │                │
   YES              NO
    │                │
    ↓                ↓

Step 8A: SUCCESS PATH          Step 8B: FAILURE PATH
┌─────────────────────────┐    ┌─────────────────────────┐
│  ✅ SUCCESS!             │    │  ❌ Verification Failed  │
│  ────────────────────    │    │  ────────────────────   │
│  Your identity has been  │    │  Your face does not     │
│  VERIFIED!               │    │  match your ID document │
│                          │    │                         │
│  The AI system has:      │    │  Similarity: 0.32       │
│  ✅ Analyzed grades      │    │  Confidence: very_low   │
│  ✅ Validated liveness   │    │                         │
│  ✅ Verified identity    │    │  This may indicate      │
│  ✅ Approved submission  │    │  identity fraud.        │
│                          │    │                         │
│  Your application is     │    │  Please contact admin   │
│  now complete!           │    │  if this is an error.   │
│                          │    │                         │
│  [ Continue → ]          │    │  [ Try Again ]          │
└─────────────────────────┘    └─────────────────────────┘
            ↓                              ↓
            ↓                              ↓
    ✅ COMPLETE!                   🚨 BLOCKED

═══════════════════════════════════════════════════════════════

TECHNICAL FLOW BEHIND THE SCENES:

Frontend (GradeSubmissionForm.tsx):
1. handleSubmit() → POST /api/grades/
2. Store grade_submission_id
3. setShowLivenessVerification(true)
4. LiveCameraCapture component renders
5. User completes liveness challenges
6. handleLivenessCapture() called with image + data
7. POST /api/face-verification/grade-submission/
8. Show success/failure message

Backend (face_verification_views.py):
1. verify_grade_submission_identity() receives request
2. Validate photo and liveness_data
3. face_service._verify_liveness_data() checks challenges
4. Query DocumentSubmission for approved ID
5. face_service.verify_id_with_selfie() compares faces
6. Calculate similarity score (0.0-1.0)
7. Determine confidence level (very_low to very_high)
8. Return result to frontend

Database (if future enhancement):
1. GradeSubmission record updated:
   - liveness_verified = True
   - face_verified = True/False
   - verification_similarity = 0.87
   - verification_confidence = "very_high"
   - verification_timestamp = NOW()

═══════════════════════════════════════════════════════════════

SECURITY LAYERS:

Layer 1: Liveness Detection
├─ Color Flash: Prevents photo spoofing
├─ Blink Detection: Prevents static images
└─ Movement Detection: Prevents video replay

Layer 2: Face Verification
├─ YOLO v8: Detects faces in ID and selfie
├─ InsightFace: Generates 512-dim embeddings
├─ Cosine Similarity: Compares embeddings (0.0-1.0)
└─ Threshold: 0.50 (accounts for natural changes)

Layer 3: Fraud Detection
├─ Similarity < 0.35: Critical fraud alert
├─ Similarity 0.35-0.45: Manual review required
├─ Similarity 0.45-0.50: Uncertain, needs review
└─ Similarity ≥ 0.50: Approved

Layer 4: Audit Trail
├─ All attempts logged
├─ Timestamps recorded
├─ Similarity scores saved
└─ Fraud alerts generated

═══════════════════════════════════════════════════════════════

TIMING BREAKDOWN:

┌─────────────────────────┬──────────────┐
│ Action                  │ Time         │
├─────────────────────────┼──────────────┤
│ Fill grade form         │ 2-3 minutes  │
│ Backend processing      │ 2-3 seconds  │
│ Transitional message    │ 2 seconds    │
│ Color flash (3x)        │ 3 seconds    │
│ Blink detection         │ 1 second     │
│ Movement detection      │ 0.5 seconds  │
│ Face verification       │ 2-3 seconds  │
│ Result display          │ 2 seconds    │
├─────────────────────────┼──────────────┤
│ TOTAL (approx)          │ 3-4 minutes  │
│ Liveness only (approx)  │ 10-15 sec    │
└─────────────────────────┴──────────────┘

═══════════════════════════════════════════════════════════════
```

**Visual Legend:**
- ┌─┐ = UI containers/boxes
- ═══ = Progress bars
- ↓ = Flow direction
- ✓ = Success indicator
- ✅ = Completed step
- ❌ = Failed step
- 🎨 👁️ 📱 = Challenge types
- 🔒 = Security feature

**Status**: ✅ Complete and Ready for Testing
