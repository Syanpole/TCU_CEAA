# 🎨 Audit Logging Visual Guide

## 📊 System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TCU-CEAA AUDIT LOGGING SYSTEM                  │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   STUDENT    │        │    ADMIN     │        │  AI SYSTEM   │
│   Actions    │        │   Actions    │        │   Actions    │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │                       │                       │
       │                       │                       │
       ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    AUDIT LOGGER UTILITY                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  • Captures action details                            │  │
│  │  • Records user information                           │  │
│  │  • Logs IP address & user agent                       │  │
│  │  • Stores metadata in JSON format                     │  │
│  │  • Assigns severity level                             │  │
│  │  • Adds timestamp automatically                       │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  DATABASE       │
                    │  AuditLog Table │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  ADMIN DASHBOARD│
                    │  Audit Logs Tab │
                    └─────────────────┘
```

---

## 🔄 Action Flow Examples

### **Example 1: Student Submits Document**

```
1. STUDENT ACTION
   ┌────────────────────────────────────────┐
   │ Student uploads Birth Certificate PDF  │
   └────────────────┬───────────────────────┘
                    │
2. SYSTEM PROCESSES │
                    ▼
   ┌────────────────────────────────────────┐
   │ DocumentSubmissionCreateSerializer     │
   │ • Validates file                       │
   │ • Creates document record              │
   │ • Calls audit_logger.log_document_     │
   │   submitted()                          │
   └────────────────┬───────────────────────┘
                    │
3. AUDIT LOG #1     ▼
   ┌────────────────────────────────────────┐
   │ LOG: document_submitted                │
   │ User: john.doe                         │
   │ Document Type: Birth Certificate       │
   │ IP: 192.168.1.100                      │
   │ Time: 2025-10-15 14:30:00             │
   └────────────────┬───────────────────────┘
                    │
4. AI ANALYSIS      │
                    ▼
   ┌────────────────────────────────────────┐
   │ Lightning Verifier analyzes document   │
   │ • Confidence: 95%                      │
   │ • Status: APPROVED                     │
   │ • Processing: 0.45s                    │
   └────────────────┬───────────────────────┘
                    │
5. AUDIT LOG #2     ▼
   ┌────────────────────────────────────────┐
   │ LOG: ai_analysis                       │
   │ Analysis Type: document_verification   │
   │ Confidence: 0.95                       │
   │ Status: approved                       │
   │ Algorithms: [lightning_verifier]       │
   └────────────────┬───────────────────────┘
                    │
6. AUDIT LOG #3     ▼
   ┌────────────────────────────────────────┐
   │ LOG: ai_auto_approve                   │
   │ Document auto-approved                 │
   │ Confidence: 95%                        │
   │ Quality Rating: excellent              │
   └────────────────────────────────────────┘

RESULT: 3 audit logs created for single document submission!
```

---

### **Example 2: Admin Reviews Grade Submission**

```
1. STUDENT ACTION
   ┌────────────────────────────────────────┐
   │ Student submits grades                 │
   └────────────────┬───────────────────────┘
                    │
2. AUDIT LOG #1     ▼
   ┌────────────────────────────────────────┐
   │ LOG: grade_submitted                   │
   │ Academic Year: 2024-2025               │
   │ GWA: 1.50                              │
   └────────────────┬───────────────────────┘
                    │
3. AI EVALUATES     │
                    ▼
   ┌────────────────────────────────────────┐
   │ Grade Analyzer runs                    │
   │ • Qualifies for Basic: Yes             │
   │ • Qualifies for Merit: Yes             │
   │ • Auto-approves                        │
   └────────────────┬───────────────────────┘
                    │
4. AUDIT LOG #2     ▼
   ┌────────────────────────────────────────┐
   │ LOG: ai_analysis (grade_evaluation)    │
   │ Confidence: 0.85                       │
   │ Status: approved                       │
   └────────────────┬───────────────────────┘
                    │
5. AUDIT LOG #3     ▼
   ┌────────────────────────────────────────┐
   │ LOG: grade_approved                    │
   │ Auto-approved: true                    │
   │ Qualifies Basic: true                  │
   │ Qualifies Merit: true                  │
   └────────────────────────────────────────┘
```

---

## 📈 Audit Log Timeline View

```
Time: 14:30:00  ┌─────────────────────────────────────┐
                │ 🔐 john.doe logged in               │
                │    IP: 192.168.1.100                │
                │    Device: Chrome on Windows        │
                └─────────────────────────────────────┘
                        │
Time: 14:30:15          ▼
                ┌─────────────────────────────────────┐
                │ 📄 john.doe submitted Birth Cert    │
                │    Status: Processing               │
                │    File: birth_cert.pdf             │
                └─────────────────────────────────────┘
                        │
Time: 14:30:16          ▼
                ┌─────────────────────────────────────┐
                │ 🤖 AI analyzed Birth Certificate    │
                │    Confidence: 95%                  │
                │    Algorithm: lightning_verifier    │
                │    Processing Time: 0.45s           │
                └─────────────────────────────────────┘
                        │
Time: 14:30:16          ▼
                ┌─────────────────────────────────────┐
                │ ✅ AI auto-approved Birth Cert      │
                │    Quality Rating: Excellent        │
                │    Decision: Approved               │
                └─────────────────────────────────────┘
                        │
Time: 14:35:20          ▼
                ┌─────────────────────────────────────┐
                │ 🎓 john.doe submitted grades        │
                │    AY: 2024-2025, Semester: 1st     │
                │    GWA: 1.50                        │
                └─────────────────────────────────────┘
                        │
Time: 14:35:21          ▼
                ┌─────────────────────────────────────┐
                │ 🤖 AI evaluated grades              │
                │    Confidence: 85%                  │
                │    Basic: Eligible                  │
                │    Merit: Eligible                  │
                └─────────────────────────────────────┘
                        │
Time: 14:40:00          ▼
                ┌─────────────────────────────────────┐
                │ 🚪 john.doe logged out              │
                │    Session Duration: 10 minutes     │
                └─────────────────────────────────────┘
```

---

## 🎯 Severity Level Colors

```
┌──────────────────────────────────────────────────────────────┐
│  INFO (ℹ️)    │  Blue    │  Normal operations               │
│───────────────┼──────────┼──────────────────────────────────│
│  SUCCESS (✅) │  Green   │  Successful completions          │
│───────────────┼──────────┼──────────────────────────────────│
│  WARNING (⚠️) │  Yellow  │  Issues or rejections            │
│───────────────┼──────────┼──────────────────────────────────│
│  CRITICAL (🚨)│  Red     │  Security or system errors       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔍 Filter View in Admin Dashboard

```
╔════════════════════════════════════════════════════════════════╗
║                      AUDIT LOGS                                 ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  Filters:  [Action Type ▼] [Severity ▼] [Date Range]          ║
║            [User: ________] [Search: ____________] [Apply]     ║
║                                                                 ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  ✅ 14:30:16 | john.doe | AI auto-approved Birth Certificate  ║
║     Confidence: 95% | Quality: Excellent                       ║
║     [View Details] [View Document]                             ║
║                                                                 ║
║  ───────────────────────────────────────────────────────────   ║
║                                                                 ║
║  ℹ️  14:30:15 | john.doe | Submitted Birth Certificate        ║
║     Status: Approved | Document ID: 123                        ║
║     [View Details] [View Document]                             ║
║                                                                 ║
║  ───────────────────────────────────────────────────────────   ║
║                                                                 ║
║  ✅ 14:30:00 | john.doe | User Login                          ║
║     IP: 192.168.1.100 | Device: Chrome                         ║
║     [View Details] [View Session]                              ║
║                                                                 ║
║  ───────────────────────────────────────────────────────────   ║
║                                                                 ║
║  Showing 3 of 150 logs | [Previous] [1] [2] [3] ... [Next]   ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🎨 Metadata Expansion View

```
┌─────────────────────────────────────────────────────────────────┐
│ LOG ENTRY #123                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Action Type:     ai_analysis                                    │
│ Description:     AI document_verification analysis completed    │
│                  for DocumentSubmission ID:123 (Conf: 95.0%)   │
│ User:            john.doe (Student)                             │
│ Severity:        Info                                           │
│ Timestamp:       2025-10-15 14:30:16                           │
│ IP Address:      192.168.1.100                                 │
│ User Agent:      Mozilla/5.0 (Windows NT 10.0)...              │
├─────────────────────────────────────────────────────────────────┤
│ METADATA:                                                       │
│ {                                                               │
│   "analysis_type": "document_verification",                     │
│   "confidence_score": 0.95,                                     │
│   "status": "approved",                                         │
│   "algorithms_used": ["lightning_verifier"],                    │
│   "processing_time": 0.45,                                      │
│   "additional_metadata": {                                      │
│     "document_type": "birth_certificate",                       │
│     "auto_approved": true,                                      │
│     "quality_rating": "excellent",                              │
│     "matched_keywords": ["birth", "certificate", "psa"],        │
│     "ocr_confidence": 0.98                                      │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Analytics Dashboard View

```
╔════════════════════════════════════════════════════════════════╗
║              AUDIT LOG ANALYTICS (Last 30 Days)                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  Total Actions:        1,234                                   ║
║  Unique Users:         45                                      ║
║  AI Actions:           856 (69%)                               ║
║  Admin Actions:        123 (10%)                               ║
║  Student Actions:      255 (21%)                               ║
║                                                                 ║
║  ────────────────────────────────────────────────────────────  ║
║                                                                 ║
║  Top Action Types:                                             ║
║    1. ai_analysis          345                                 ║
║    2. document_submitted   234                                 ║
║    3. user_login           189                                 ║
║    4. ai_auto_approve      156                                 ║
║    5. grade_submitted       89                                 ║
║                                                                 ║
║  ────────────────────────────────────────────────────────────  ║
║                                                                 ║
║  AI Performance:                                               ║
║    Average Confidence:     87.5%                               ║
║    Auto-Approval Rate:     78%                                 ║
║    Average Process Time:   0.52s                               ║
║                                                                 ║
║  ────────────────────────────────────────────────────────────  ║
║                                                                 ║
║  Security Alerts:                                              ║
║    Failed Logins:          12                                  ║
║    Suspicious IPs:         2                                   ║
║    Critical Events:        0                                   ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🔐 Security Monitoring View

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY AUDIT LOG                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚠️  14:25:30 | unknown_user | Failed Login Attempt           │
│      Username: admin | IP: 203.45.67.89                        │
│      Reason: Invalid password                                  │
│      [Block IP] [Investigate]                                  │
│                                                                 │
│  ⚠️  14:25:25 | unknown_user | Failed Login Attempt           │
│      Username: admin | IP: 203.45.67.89                        │
│      Reason: Invalid password                                  │
│      [Block IP] [Investigate]                                  │
│                                                                 │
│  ⚠️  14:25:20 | unknown_user | Failed Login Attempt           │
│      Username: admin | IP: 203.45.67.89                        │
│      Reason: Invalid password                                  │
│      ⚠️ ALERT: 3 attempts from same IP!                        │
│      [Block IP] [Investigate]                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📱 Mobile View Concept

```
┌─────────────────────────┐
│   AUDIT LOGS            │
├─────────────────────────┤
│                         │
│ 🔍 [Search...]          │
│                         │
│ ┌─────────────────────┐ │
│ │ ✅ AI Auto-Approved │ │
│ │ Birth Certificate   │ │
│ │ 14:30:16            │ │
│ │ Conf: 95%           │ │
│ │ [Details ▼]         │ │
│ └─────────────────────┘ │
│                         │
│ ┌─────────────────────┐ │
│ │ ℹ️  Document Submit │ │
│ │ Birth Certificate   │ │
│ │ 14:30:15            │ │
│ │ [Details ▼]         │ │
│ └─────────────────────┘ │
│                         │
│ ┌─────────────────────┐ │
│ │ ✅ User Login       │ │
│ │ john.doe            │ │
│ │ 14:30:00            │ │
│ │ [Details ▼]         │ │
│ └─────────────────────┘ │
│                         │
│ [Load More...]          │
│                         │
└─────────────────────────┘
```

---

## 🎯 Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║          AUDIT LOG QUICK REFERENCE                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  🔐 Authentication                                        ║
║     user_login, user_logout, user_registered             ║
║                                                           ║
║  📄 Documents                                             ║
║     document_submitted, document_approved,                ║
║     document_rejected, document_revised                   ║
║                                                           ║
║  🎓 Grades                                                ║
║     grade_submitted, grade_approved,                      ║
║     grade_rejected, grade_processed                       ║
║                                                           ║
║  💰 Applications                                          ║
║     application_submitted, application_approved,          ║
║     application_rejected, application_disbursed           ║
║                                                           ║
║  🤖 AI System                                             ║
║     ai_analysis, ai_auto_approve                          ║
║                                                           ║
║  👤 Profile                                               ║
║     user_updated, password_changed                        ║
║                                                           ║
║  ⚙️  Admin                                                ║
║     admin_review, admin_action, system_config             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

**Created**: October 15, 2025  
**Purpose**: Visual guide for understanding audit logging system  
**Audience**: Admins, Developers, System Administrators  
**Status**: Complete and Active
