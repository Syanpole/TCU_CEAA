# Document Submission Form - Visual Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Submit Required Documents                       │
│           Upload required documents for TCU-CEAA scholarship         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Document Type *      [Select document type...              ▼]       │
│                       • Birth Certificate / PSA                       │
│                       • School ID                                     │
│                       • Certificate of Enrollment                     │
│                       • Grade 10 Report Card                          │
│                       • Grade 12 Report Card                          │
│                       • Diploma                                       │
│                       • Others                                        │
│                                                                       │
│  Description          ┌────────────────────────────────────┐         │
│  (Optional)           │ Add any notes or additional        │         │
│                       │ information about this document... │         │
│                       └────────────────────────────────────┘         │
│                                                                       │
│  Upload File *        [Choose File] No file chosen                   │
│                       Accepted formats: PDF, JPG, PNG, DOC, DOCX     │
│                       (Max 10MB)                                      │
│                                                                       │
│                       Document Submission Guidelines:                 │
│                       • Name your file clearly                        │
│                       • Ensure text is clear and readable             │
│                       • PDF format is preferred                       │
│                       • For IDs: Submit back-to-back on one page     │
│                       • Submit high-quality scans                     │
│                                                                       │
│                                                          [ Cancel ]    │
│                          [ ⚡ Submit for Instant AI Processing ]      │
└─────────────────────────────────────────────────────────────────────┘
```

# Grade Submission Form - Visual Structure

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Submit Grades                                │
│        Upload your grade sheet for TCU-CEAA allowance evaluation     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  📋 Document Verification Status                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ ✅ Birth Certificate / PSA              Approved               │  │
│  │ ✅ School ID                             Approved               │  │
│  │ ⏳ Certificate of Enrollment            Under Review           │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌─────────────────────────┬────────────────────────────────────┐    │
│  │ Semester *   [1st ▼]    │ Academic Year *  [2024-2025]       │    │
│  └─────────────────────────┴────────────────────────────────────┘    │
│                                                                        │
│  ┌─────────────────────────┬────────────────────────────────────┐    │
│  │ Total Units *  [21]     │ GWA (%) *        [85.50]           │    │
│  └─────────────────────────┴────────────────────────────────────┘    │
│                                                                        │
│  ┌─────────────────────────┬────────────────────────────────────┐    │
│  │ SWA (%) *    [87.25]    │ Grade Status Indicators            │    │
│  │                         │ ☐ Has failing grades               │    │
│  │                         │ ☐ Has incomplete grades (INC)      │    │
│  │                         │ ☐ Has dropped subjects (DROP)      │    │
│  └─────────────────────────┴────────────────────────────────────┘    │
│                                                                        │
│  Upload Grade    [Choose File] grade_sheet.pdf                        │
│  Sheet *         Upload your official grade sheet.                    │
│                  AI will automatically evaluate your grades.           │
│                                                                        │
│  🤖 Fully Autonomous AI Processing System                             │
│  • INSTANT AUTO-APPROVAL - No waiting for manual review              │
│  • Comprehensive document analysis with OCR                           │
│  • Intelligent cross-validation and verification                      │
│  • Advanced quality assessment                                        │
│  • Automatic allowance eligibility calculation                        │
│  • Complete autonomous processing                                     │
│                                                                        │
│                                                      [ Cancel ]        │
│                            [ Submit for Instant AI Approval ]         │
└──────────────────────────────────────────────────────────────────────┘
```

# Modal Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│ BROWSER WINDOW                                                  ╳    │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Dashboard Background (Blurred)                                  │ │
│ │                                                                 │ │
│ │   ┌───────────────────────────────────────────────────────┐ ✕  │ │
│ │   │                                                       │    │ │
│ │   │        DOCUMENT SUBMISSION FORM                      │    │ │
│ │   │        (Enhanced with gradient background)           │    │ │
│ │   │                                                       │    │ │
│ │   │  • White to gray gradient background                 │    │ │
│ │   │  • 24px rounded corners                              │    │ │
│ │   │  • Soft shadow for depth                             │    │ │
│ │   │  • Max width: 700-750px                              │    │ │
│ │   │  • Smooth slide-up animation                         │    │ │
│ │   │                                                       │    │ │
│ │   │  Labels (180px)    Inputs (Remaining space)          │    │ │
│ │   │  ─────────────────────────────────────────────       │    │ │
│ │   │  Document Type     [Dropdown Select Menu     ▼]      │    │ │
│ │   │  Description       [Text Area                  ]      │    │ │
│ │   │  Upload File       [File Input                 ]      │    │ │
│ │   │                                                       │    │ │
│ │   │                            [Cancel] [Submit]          │    │ │
│ │   └───────────────────────────────────────────────────────┘    │ │
│ │                                                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

Legend:
✕ = Close button (circular, red on hover, rotates 90°)
╳ = Browser close button
```

# Color Scheme

## Modal & Form Colors
- **Modal Overlay**: rgba(15, 23, 42, 0.7) with 8px backdrop blur
- **Form Background**: Linear gradient #ffffff → #f8f9fa
- **Border**: rgba(226, 232, 240, 0.6)
- **Shadow**: Multi-layer (0 20px 60px + 0 4px 16px)

## Text Colors
- **Headings**: #1e293b (dark slate)
- **Labels**: #334155 (slate gray)
- **Body Text**: #64748b (light slate)
- **Gradient Text**: Linear gradient #667eea → #764ba2

## Interactive Elements
- **Primary Button**: Linear gradient #667eea → #764ba2
- **Secondary Button**: Red gradient for cancel
- **Focus Ring**: rgba(102, 126, 234, 0.15) with 4px spread
- **Hover State**: Lighter gradient with scale transform

## Status Indicators
- **Approved**: Green (#22c55e) background with checkmark
- **Pending**: Amber (#f59e0b) background with clock
- **Missing**: Red (#ef4444) background with X mark
- **Error**: Red gradient background for alerts

# Typography

## Font Sizes
- **H3 (Main Title)**: 28px, weight 800
- **Paragraph**: 15px, weight 500
- **Labels**: 14px, weight 600
- **Input Text**: 14px, weight 500
- **Helper Text**: 12-13px

## Font Weights
- **Bold**: 800 (headings)
- **Semi-bold**: 600 (labels)
- **Medium**: 500 (body text)

# Spacing & Layout

## Form Spacing
- **Form Padding**: 32px
- **Group Margin**: 24px bottom
- **Label-Input Gap**: 16px horizontal
- **Button Gap**: 12px

## Grid Columns
- **Document Form**: 180px (label) | 1fr (input)
- **Grade Form**: 160px (label) | 1fr (input)
- **Two-Column Row**: 1fr | 1fr

## Border Radius
- **Modal**: 24px
- **Form Elements**: 12px
- **Buttons**: 12px
- **Close Button**: 50% (circular)

# Animations

## Modal Animations
- **Fade In**: 0.3s ease-out (overlay)
- **Slide Up**: 0.4s cubic-bezier(0.4, 0, 0.2, 1) (content)
- **Scale**: From 0.95 to 1.0 on open

## Button Animations
- **Close Button**: 90° rotation on hover, 0.3s
- **Submit Button**: translateY(-2px) on hover, 0.4s
- **Ripple Effect**: Expanding circle from center

## Form Element Animations
- **Focus**: translateY(-1px) with shadow expansion
- **Selected File**: Slide-in from top
- **Loading Spinner**: 1s linear rotation
