# Application Flow Visual Diagram

## Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                      STUDENT DASHBOARD                          │
│                                                                 │
│  Sidebar:                         Main Content:                │
│  ┌─────────────────┐             ┌────────────────────────┐   │
│  │ ☐ Overview      │             │  LOCKED: Please       │   │
│  │ ☐ Application   │◄────────────┤  complete application │   │
│  │ ☐ Submission of │             │  first                │   │
│  │   Requirements  │             └────────────────────────┘   │
│  │ ☐ Grades        │                                          │
│  └─────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓ User clicks "Application"
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION SECTION                        │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │     Complete Basic Qualification                       │   │
│  │                                                         │   │
│  │     Before you can access documents and grades,        │   │
│  │     you need to complete the basic qualification      │   │
│  │     criteria.                                          │   │
│  │                                                         │   │
│  │     ┌──────────────────────────────────┐               │   │
│  │     │  Start Application Process        │               │   │
│  │     └──────────────────────────────────┘               │   │
│  │                                                         │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Clicks button
┌─────────────────────────────────────────────────────────────────┐
│              BASIC QUALIFICATION MODAL                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Question 1/8: Are you a Filipino Citizen?             │  │
│  │  ⚪ Yes  ⚪ No                                           │  │
│  │                                                          │  │
│  │  Question 2/8: Are you enrolled at Taguig City          │  │
│  │  University?                                             │  │
│  │  ⚪ Yes  ⚪ No                                           │  │
│  │                                                          │  │
│  │  ... (6 more questions)                                  │  │
│  │                                                          │  │
│  │  [Clear All]                    [Next]                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Completes all 8 questions
┌─────────────────────────────────────────────────────────────────┐
│                    QUALIFICATION REVIEW                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Review Your Responses                                   │  │
│  │                                                          │  │
│  │  Q: Are you a Filipino Citizen?        A: Yes           │  │
│  │  Q: Are you enrolled at TCU?           A: Yes           │  │
│  │  Q: Are you a Taguig resident?         A: Yes           │  │
│  │  ... (all answers shown)                                 │  │
│  │                                                          │  │
│  │  [Go Back]                    [Submit]                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Clicks Submit
┌─────────────────────────────────────────────────────────────────┐
│        ✓ NOTIFICATION: Qualification Completed!                │
│        Please complete the full application form.               │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Automatically opens...
┌─────────────────────────────────────────────────────────────────┐
│             FULL APPLICATION FORM MODAL                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  TCU-CEAA Application Form                           ✕  │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  ● ○ ○ ○ ○                                             │  │
│  │  Application Details                                     │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  STEP 1: APPLICATION DETAILS                            │  │
│  │                                                          │  │
│  │  Facebook Link:    [___________________________]        │  │
│  │  Application Type: [RENEW] (disabled)                   │  │
│  │  School Year:      [S.Y 2025-2026 ▼] ◄─────────────┐   │  │
│  │  Semester:         [1ST SEMESTER ▼]  ◄──────────────│──┐│  │
│  │  Merit Incentive:  [Yes ▼]                         │  ││  │
│  │                                                      │  ││  │
│  │  [Next]                                              │  ││  │
│  └──────────────────────────────────────────────────────│──│┘  │
└──────────────────────────────────────────────────────────│──│───┘
                                                           │  │
                    ↓ Completes 5 steps                   │  │
                                                           │  │
┌──────────────────────────────────────────────────────────│──│───┐
│                    REVIEW PAGE                           │  │   │
│  ┌──────────────────────────────────────────────────────│──│──┐│
│  │  Review Your Application                             │  │  ││
│  │                                                       │  │  ││
│  │  ━━━━ Application Details ━━━━                       │  │  ││
│  │  School Year: S.Y 2025-2026  ◄───────────────────────┘  │  ││
│  │  Semester: 1ST SEMESTER  ◄──────────────────────────────┘  ││
│  │  ... (all other data)                                     ││
│  │                                                            ││
│  │  [Edit Application]      [Submit Application]             ││
│  └───────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                            ↓ Clicks Submit
┌─────────────────────────────────────────────────────────────────┐
│              CONFIRMATION DIALOG                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                      ⚠️                                  │  │
│  │                                                          │  │
│  │          Submit your application?                       │  │
│  │                                                          │  │
│  │  This will lock your application and you will no        │  │
│  │  longer be able to edit it.                             │  │
│  │                                                          │  │
│  │  [Cancel]              [Yes, submit]                     │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Clicks Yes
┌─────────────────────────────────────────────────────────────────┐
│                    LOADING...                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                       ⟳                                  │  │
│  │                   (spinning)                             │  │
│  │                                                          │  │
│  │          Submitting your application...                 │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ After 2 seconds
┌─────────────────────────────────────────────────────────────────┐
│                    SUCCESS PAGE                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                      ✓                                   │  │
│  │                 (green circle)                           │  │
│  │                                                          │  │
│  │          Information Submitted                          │  │
│  │                                                          │  │
│  │  We will review your application and get back to        │  │
│  │  you shortly.                                            │  │
│  │                                                          │  │
│  │  [Go to Dashboard]  [Go to Submission of Requirements]  │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Clicks either button
┌─────────────────────────────────────────────────────────────────┐
│        ✓ NOTIFICATION: Application Completed & Locked!         │
│        Your application for 1ST SEMESTER S.Y 2025-2026 has    │
│        been successfully submitted and locked.                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Navigates to...
┌─────────────────────────────────────────────────────────────────┐
│                  APPLICATION SECTION (LOCKED)                   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │                     ✓                                   │   │
│  │                 (huge green)                            │   │
│  │                                                         │   │
│  │        Application Completed & Locked                  │   │
│  │                                                         │   │
│  │  Your application has been successfully submitted      │   │
│  │  and locked.                                           │   │
│  │                                                         │   │
│  │  You can now proceed to submit your documents and      │   │
│  │  grades in the "Submission of Requirements" section.   │   │
│  │                                                         │   │
│  │  ┌──────────────────────────────────────────────┐      │   │
│  │  │  School Year: S.Y 2025-2026                  │      │   │
│  │  │  Semester: 1ST SEMESTER                      │      │   │
│  │  └──────────────────────────────────────────────┘      │   │
│  │                                                         │   │
│  │  ┌────────────────────────────────────────────┐        │   │
│  │  │  Go to Submission of Requirements           │        │   │
│  │  └────────────────────────────────────────────┘        │   │
│  │                                                         │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ User clicks "Submission of Requirements"
┌─────────────────────────────────────────────────────────────────┐
│            SUBMISSION OF REQUIREMENTS PAGE                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │        SUBMISSION OF REQUIREMENTS                       │   │
│  │  ┌───────────────────────────────────────────────┐     │   │
│  │  │ 📅 School Year: S.Y 2025-2026                │     │   │
│  │  │ | 📚 Semester: 1ST SEMESTER                   │     │   │
│  │  └───────────────────────────────────────────────┘     │   │
│  │                                                         │   │
│  │  ━━━━ DOCUMENTS TO BE SUBMITTED ━━━━                   │   │
│  │                                                         │   │
│  │  ☐ School ID or Valid Government-issued ID             │   │
│  │  ☐ Proof that ONE parent is an active Taguig Voter    │   │
│  │  ☐ Birth Certificate                                   │   │
│  │  ... (all document requirements)                        │   │
│  │                                                         │   │
│  │  [Add Requirement]                                      │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## State Transitions

### Application Section States

**STATE 1: INITIAL (Not Started)**
```
┌─────────────────────────────────┐
│   Complete Basic Qualification  │
│                                  │
│   [Start Application Process]   │
└─────────────────────────────────┘
```

**STATE 2: QUALIFIED (In Progress)**
```
┌─────────────────────────────────┐
│   ✓ Basic qualification complete│
│                                  │
│   Next step: Complete the full  │
│   application form              │
│                                  │
│   [Complete Application Form]   │
└─────────────────────────────────┘
```

**STATE 3: COMPLETED & LOCKED** 🔒
```
┌─────────────────────────────────┐
│            ✓                     │
│     (large green checkmark)      │
│                                  │
│   Application Completed & Locked │
│                                  │
│   ┌──────────────────────────┐  │
│   │ School Year: 2025-2026   │  │
│   │ Semester: 1ST SEMESTER   │  │
│   └──────────────────────────┘  │
│                                  │
│   [Go to Submission of          │
│    Requirements]                 │
└─────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  FullApplicationForm                         │
│                                                              │
│  User enters:                                                │
│  • school_year: "S.Y 2025-2026"                             │
│  • semester: "1ST SEMESTER"                                  │
│  • + 60 other fields                                         │
│                                                              │
│  onComplete({                                                │
│    school_year: "S.Y 2025-2026",                            │
│    semester: "1ST SEMESTER"                                  │
│  })                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  StudentDashboard                            │
│                                                              │
│  handleApplicationComplete(data) {                           │
│    setApplicationData(data);  // Store in state             │
│    setHasCompletedApplication(true);                        │
│    setActiveSection('requirements');                        │
│  }                                                           │
│                                                              │
│  State:                                                      │
│  • applicationData: {                                        │
│      school_year: "S.Y 2025-2026",                          │
│      semester: "1ST SEMESTER"                                │
│    }                                                         │
│  • hasCompletedApplication: true                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              DocumentRequirements Component                  │
│                                                              │
│  Props received:                                             │
│  • schoolYear: "S.Y 2025-2026"                              │
│  • semester: "1ST SEMESTER"                                  │
│  • darkMode: false                                           │
│                                                              │
│  Displays in header:                                         │
│  ┌────────────────────────────────────┐                     │
│  │ 📅 School Year: S.Y 2025-2026     │                     │
│  │ | 📚 Semester: 1ST SEMESTER        │                     │
│  └────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## Lock/Unlock States

```
┌──────────────┬─────────────┬──────────────┬─────────────┐
│ Section      │ Before Qual │ After Qual   │ After App   │
├──────────────┼─────────────┼──────────────┼─────────────┤
│ Application  │ 🔓 Open     │ 🔓 Open      │ 🔒 LOCKED   │
│ Submission   │ 🔒 Locked   │ 🔒 Locked    │ 🔓 Open     │
│ Grades       │ 🔒 Locked   │ 🔒 Locked    │ 🔓 Open     │
└──────────────┴─────────────┴──────────────┴─────────────┘
```

## Color Coding

```
┌──────────────────────────────────────────────────────────┐
│  Application States                                       │
├──────────────────────────────────────────────────────────┤
│  🔴 Not Started        → Red gradient button             │
│  🟡 In Progress        → Purple/Blue UI                  │
│  🟢 Completed & Locked → Green checkmark, success colors │
├──────────────────────────────────────────────────────────┤
│  Purple Gradient (#667eea → #764ba2)                     │
│    • Application form header                             │
│    • Semester/Year banner in Submission of Requirements │
├──────────────────────────────────────────────────────────┤
│  Red Gradient (#dc2626 → #b91c1c) - TCU Colors          │
│    • Action buttons                                      │
│    • Start/Continue buttons                              │
├──────────────────────────────────────────────────────────┤
│  Green (#10b981)                                         │
│    • Success checkmarks                                  │
│    • Completed status                                    │
│    • Submit buttons                                      │
├──────────────────────────────────────────────────────────┤
│  Orange (#f59e0b)                                        │
│    • Lock icons                                          │
│    • Warning messages                                    │
└──────────────────────────────────────────────────────────┘
```

