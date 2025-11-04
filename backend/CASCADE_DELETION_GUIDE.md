# 🗑️ User Account Deletion & Cascade System

## Overview
When an admin deletes a user account in the TCU-CEAA system, all related records are automatically handled to maintain data integrity while preserving important audit trails.

---

## 🔄 Automatic Cascade Deletion (Related Records Deleted)

When a user account is deleted, the following records are **automatically deleted** due to `on_delete=models.CASCADE`:

### 1. **Document Submissions** (`DocumentSubmission`)
- **Field**: `student` (ForeignKey to CustomUser)
- **Action**: ALL documents submitted by the student are deleted
- **Includes**: 
  - Document files (PDFs, images, etc.)
  - AI analysis data
  - Submission metadata

### 2. **Grade Submissions** (`GradeSubmission`)
- **Field**: `student` (ForeignKey to CustomUser)
- **Action**: ALL grade submissions by the student are deleted
- **Includes**:
  - Grade sheets (uploaded files)
  - AI evaluation results
  - Academic records

### 3. **Allowance Applications** (`AllowanceApplication`)
- **Field**: `student` (ForeignKey to CustomUser)
- **Field**: `grade_submission` (ForeignKey to GradeSubmission)
- **Action**: ALL applications by the student are deleted
- **Includes**:
  - Application history
  - Disbursement records
  - Email notification logs

### 4. **Email Verifications** (`EmailVerification`)
- **Field**: `user` (ForeignKey to CustomUser)
- **Action**: ALL verification codes for the user are deleted
- **Includes**:
  - Verification codes
  - Verification history

### 5. **Auth Tokens** (Django REST Framework)
- **Field**: `user` (ForeignKey to CustomUser)
- **Action**: Authentication token is deleted
- **Effect**: User is immediately logged out

---

## 🔒 Preserved Records (Audit Trail)

The following records are **preserved** to maintain system integrity and audit trails using `on_delete=models.SET_NULL`:

### 1. **Audit Logs** (`AuditLog`)
- **Fields**: 
  - `user` (who performed the action) → SET_NULL
  - `target_user` (who was affected) → SET_NULL
- **Preserved**: All audit log entries remain in the database
- **Effect**: Admin can still see historical actions even after user deletion
- **Display**: Shows as "[Deleted User]" in logs

### 2. **Admin Review Records**
- **DocumentSubmission.reviewed_by** → SET_NULL
- **GradeSubmission.reviewed_by** → SET_NULL
- **AllowanceApplication.processed_by** → SET_NULL
- **Preserved**: History of who reviewed/processed items
- **Effect**: Documents/grades/applications remain linked to students, but reviewer info is nullified

### 3. **Verified Student Records** (`VerifiedStudent`)
- **Field**: `registered_user` → SET_NULL
- **Action**: Link is removed but record is preserved
- **Effect**: Student can register again in the future
- **Additional**: `has_registered` flag is reset to `False`

---

## 📊 Deletion Process Flow

```
┌─────────────────────────────────────────────────────┐
│ ADMIN INITIATES USER DELETION                       │
│ (Via Django Admin or Management Command)            │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 1: Count Related Records                       │
│ • Documents                                          │
│ • Grades                                             │
│ • Applications                                       │
│ • Verifications                                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 2: Display Deletion Summary                    │
│ • Show all records to be deleted                    │
│ • Request confirmation                               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 3: Begin Transaction                           │
│ (All-or-nothing operation)                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 4: Delete Auth Token                           │
│ • Immediately log out user                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 5: Reset VerifiedStudent                       │
│ • Set has_registered = False                         │
│ • Set registered_user = NULL                         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 6: Delete User Account                         │
│ • Triggers CASCADE deletion                          │
│ • Automatically deletes:                             │
│   - DocumentSubmission records                       │
│   - GradeSubmission records                          │
│   - AllowanceApplication records                     │
│   - EmailVerification records                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 7: Preserve Audit Records                      │
│ • AuditLog.user = NULL (preserved)                   │
│ • Review records = NULL (preserved)                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ STEP 8: Commit Transaction                          │
│ • All changes saved atomically                       │
│ • Success confirmation shown                         │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ How to Delete User Accounts

### Method 1: Django Admin Interface

1. **Login** to Django Admin at `/admin/`
2. **Navigate** to "Users" section
3. **Select** the user(s) to delete
4. **Choose Action**: "🗑️ Delete selected users and ALL their records"
5. **Click** "Go"
6. **Confirm** the deletion

**Features**:
- ✅ Shows count of records to be deleted
- ✅ Batch deletion support
- ✅ Transaction safety
- ✅ Automatic VerifiedStudent reset
- ✅ Only superusers can delete

### Method 2: Management Command (Recommended for Single Users)

```bash
# Interactive mode (with confirmation prompt)
python manage.py delete_user_account <username>

# Non-interactive mode (auto-confirm)
python manage.py delete_user_account <username> --confirm
```

**Example**:
```bash
$ python manage.py delete_user_account john_doe

============================================================
USER ACCOUNT DELETION SUMMARY
============================================================

👤 User: john_doe (John Doe)
   Email: john.doe@example.com
   Role: student
   Student ID: 22-00001
   Joined: 2024-09-15

📊 RECORDS TO BE DELETED:
   • 3 Document Submissions
   • 2 Grade Submissions
   • 2 Allowance Applications
   • 5 Email Verifications
   • 1 User Account

   TOTAL: 13 records will be permanently deleted

📝 VERIFIED STUDENT RECORD:
   • VerifiedStudent record will be PRESERVED
   • Status will be reset to allow re-registration
   • Student: John Doe

🔒 PRESERVED RECORDS (Audit Trail):
   • AuditLog entries (admin actions/reviews)
   • Documents reviewed by this user (if admin)
   • Grades reviewed by this user (if admin)
   • Applications processed by this user (if admin)

⚠️  WARNING: This action CANNOT be undone!

Type the username to confirm deletion: john_doe

✅ Reset VerifiedStudent record for 22-00001
============================================================
✅ USER ACCOUNT SUCCESSFULLY DELETED
============================================================

✅ Deleted 3 document submissions
✅ Deleted 2 grade submissions
✅ Deleted 2 allowance applications
✅ Deleted 5 email verifications
✅ Deleted user account: john_doe
✅ Reset VerifiedStudent record (can register again)

✨ Total: 13 records deleted successfully
```

---

## 📋 Database Schema Reference

### CASCADE Relationships
```sql
-- DocumentSubmission
student_id → CustomUser.id [CASCADE]

-- GradeSubmission
student_id → CustomUser.id [CASCADE]

-- AllowanceApplication
student_id → CustomUser.id [CASCADE]
grade_submission_id → GradeSubmission.id [CASCADE]

-- EmailVerification
user_id → CustomUser.id [CASCADE]

-- Token (DRF)
user_id → CustomUser.id [CASCADE]
```

### SET_NULL Relationships (Preserved)
```sql
-- AuditLog
user_id → CustomUser.id [SET_NULL]
target_user_id → CustomUser.id [SET_NULL]

-- DocumentSubmission
reviewed_by_id → CustomUser.id [SET_NULL]

-- GradeSubmission
reviewed_by_id → CustomUser.id [SET_NULL]

-- AllowanceApplication
processed_by_id → CustomUser.id [SET_NULL]

-- VerifiedStudent
registered_user_id → CustomUser.id [SET_NULL]
added_by_id → CustomUser.id [SET_NULL]
```

---

## ⚠️ Important Considerations

### 1. **Irreversible Action**
- User deletion is **PERMANENT**
- No undo functionality
- Always double-check before confirming

### 2. **Data Loss**
When you delete a user, you lose:
- ❌ All submitted documents
- ❌ All grade records
- ❌ All applications
- ❌ User's profile information
- ❌ Upload history

### 3. **Preserved Data**
You keep:
- ✅ Audit trail (who did what, when)
- ✅ VerifiedStudent record (for re-registration)
- ✅ System analytics aggregates
- ✅ Review history metadata

### 4. **Re-registration**
After deletion:
- Student can register again with same Student ID
- VerifiedStudent record is automatically reset
- New account will have fresh start (no old data)

### 5. **Admin Accounts**
Deleting an admin account:
- Their review decisions remain in the system
- Reviewed documents/grades show "[Deleted Admin]"
- Audit logs preserve their actions

---

## 🔍 Verification After Deletion

To verify a user was deleted properly:

```bash
# Check user doesn't exist
python manage.py shell
>>> from myapp.models import CustomUser
>>> CustomUser.objects.filter(username='john_doe').exists()
False

# Check VerifiedStudent was reset
>>> from myapp.models import VerifiedStudent
>>> vs = VerifiedStudent.objects.get(student_id='22-00001')
>>> vs.has_registered
False
>>> vs.registered_user
None

# Check audit logs are preserved
>>> from myapp.models import AuditLog
>>> AuditLog.objects.filter(user__isnull=True).count()
# Shows preserved logs from deleted users
```

---

## 🆘 Recovery Options

**There is NO automatic recovery** once a user is deleted. However:

### Manual Recovery (If caught immediately):
1. Restore from database backup
2. Re-import from backup dump
3. Contact database administrator

### Prevention:
1. **Always use staging environment** for testing deletions
2. **Take database backups** before bulk deletions
3. **Use the management command** for better visibility
4. **Review deletion summary** carefully before confirming

---

## 🔐 Security & Permissions

### Who Can Delete Users?

1. **Django Admin**: Only **superusers** can delete user accounts
2. **Management Command**: Requires server/database access
3. **API**: No direct deletion endpoint (must use admin interface)

### Audit Trail

Every deletion creates audit log entries:
- Who deleted the account
- When it was deleted
- IP address of admin
- Browser/user agent
- Count of records affected

---

## 📝 Best Practices

1. ✅ **Always review** deletion summary before confirming
2. ✅ **Use management command** for single deletions (better visibility)
3. ✅ **Use admin interface** for batch deletions
4. ✅ **Take database backup** before mass deletions
5. ✅ **Document reason** for deletion in notes
6. ✅ **Notify affected parties** before deletion if appropriate
7. ✅ **Test in staging** environment first
8. ✅ **Verify VerifiedStudent** reset if student should re-register

---

## 🐛 Troubleshooting

### Issue: "Cannot delete user, foreign key constraint"
**Solution**: This shouldn't happen with CASCADE setup. Check database migrations are up to date:
```bash
python manage.py migrate
```

### Issue: "VerifiedStudent not reset"
**Solution**: Manually reset:
```python
from myapp.models import VerifiedStudent
vs = VerifiedStudent.objects.get(student_id='XX-XXXXX')
vs.has_registered = False
vs.registered_user = None
vs.save()
```

### Issue: "Audit logs showing wrong user"
**Solution**: This is expected behavior. Deleted users show as `None` or "[Deleted User]" in audit logs.

---

## 📚 Related Documentation

- **User Management**: See `ADMIN_AI_GUIDE.md`
- **Audit System**: See `AUDIT_LOGGING_SYSTEM.md`
- **Security**: See `AI_NAME_VERIFICATION_SECURITY.md`
- **Database Models**: See `backend/myapp/models.py`

---

## ✅ Implementation Complete

The cascade deletion system is fully implemented and production-ready:
- ✅ All models configured with proper `on_delete` behavior
- ✅ Management command created for safe deletion
- ✅ Admin action added for bulk operations
- ✅ Audit trail preservation implemented
- ✅ VerifiedStudent reset logic in place
- ✅ Transaction safety ensured
- ✅ Comprehensive documentation provided

**Status**: 🟢 Ready for Production Use
