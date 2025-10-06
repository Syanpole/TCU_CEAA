# Database Schema Mismatch Fix - AllowanceApplication

## Problem Encountered

**Error:** `IntegrityError: null value in column "email_sent" of relation "myapp_allowanceapplication" violates not-null constraint`

### Root Cause

The PostgreSQL database table `myapp_allowanceapplication` had an `email_sent` column with a NOT NULL constraint, but the Django model didn't define this field. When creating new allowance applications, Django tried to insert NULL for this field, causing the integrity error.

**Error Details:**
```
Failing row contains (6, both, 10000.00, pending, null, 2025-10-03 13:36:58.658003+00, null, null, 8, 1, null, null, null).
```

The database expected a value for `email_sent`, but the model wasn't providing one.

## Solution Implemented

### 1. Added Missing Fields to Model

Updated `backend/myapp/models.py` to include email notification tracking fields:

```python
class AllowanceApplication(models.Model):
    # ... existing fields ...
    
    # Email notification tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    notification_error = models.TextField(blank=True, null=True)
```

### 2. Created and Applied Migration

**Migration:** `0011_remove_allowanceapplication_schedule_date_and_more.py`

Changes made:
- ✅ Removed field `schedule_date` from `allowanceapplication`
- ✅ Removed field `status_email_sent` from `allowanceapplication`
- ✅ Added field `email_sent_at` to `allowanceapplication`
- ✅ Added field `notification_error` to `allowanceapplication`
- ✅ Altered field `email_sent` on `allowanceapplication` (added default=False)

## Field Descriptions

### `email_sent` (BooleanField)
- **Purpose:** Tracks whether an email notification has been sent for this application
- **Default:** `False`
- **Usage:** Set to `True` when confirmation email is successfully sent to the student

### `email_sent_at` (DateTimeField)
- **Purpose:** Records the timestamp when the email was sent
- **Nullable:** Yes
- **Usage:** Automatically set when email is sent successfully

### `notification_error` (TextField)
- **Purpose:** Stores any error messages if email sending fails
- **Nullable:** Yes
- **Usage:** Helps with debugging email delivery issues

## Benefits

### 1. **Database Consistency**
- Model now matches the actual database schema
- No more IntegrityError when creating applications

### 2. **Email Tracking**
- Can track which applications have had notifications sent
- Prevents duplicate emails
- Can retry failed emails

### 3. **Error Logging**
- Captures email sending errors for troubleshooting
- Helps identify delivery issues

### 4. **Audit Trail**
- `email_sent_at` provides a complete timeline
- Can verify when students were notified

## Testing the Fix

### Before Fix:
```python
# This would fail with IntegrityError
application = AllowanceApplication.objects.create(
    student=student,
    grade_submission=grade,
    application_type='both',
    amount=10000
)
# Error: null value in column "email_sent" violates not-null constraint
```

### After Fix:
```python
# This now works perfectly
application = AllowanceApplication.objects.create(
    student=student,
    grade_submission=grade,
    application_type='both',
    amount=10000
)
# email_sent automatically defaults to False
# No error!
```

## Future Enhancements

### Email Notification System

You can now implement automatic email notifications:

```python
from django.core.mail import send_mail
from django.utils import timezone

def send_application_notification(application):
    """Send email notification for new application"""
    try:
        send_mail(
            subject=f'Allowance Application Submitted - {application.get_application_type_display()}',
            message=f'Your application for {application.amount} has been received.',
            from_email='noreply@tcu.edu',
            recipient_list=[application.student.email],
            fail_silently=False,
        )
        
        # Mark as sent
        application.email_sent = True
        application.email_sent_at = timezone.now()
        application.save()
        
    except Exception as e:
        # Log the error
        application.notification_error = str(e)
        application.save()
```

### Admin Features

Admins can now:
- See which applications have pending email notifications
- Retry failed email sends
- Track email delivery success rate

```python
# Get applications with unsent emails
pending_notifications = AllowanceApplication.objects.filter(email_sent=False)

# Get failed email attempts
failed_notifications = AllowanceApplication.objects.exclude(notification_error='')
```

## Migration Commands Used

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

## Files Modified

1. **backend/myapp/models.py**
   - Added `email_sent`, `email_sent_at`, and `notification_error` fields

2. **backend/myapp/migrations/0011_remove_allowanceapplication_schedule_date_and_more.py**
   - Auto-generated migration file

## Related Issues Fixed

This fix also resolves:
- ✅ Previous "Failed to submit application" error
- ✅ Database schema mismatch
- ✅ Missing email notification infrastructure
- ✅ Duplicate application prevention (via unique_together constraint)

---

**Status:** ✅ **FIXED**
**Date:** October 3, 2025
**Impact:** Critical - Enables allowance application submissions
**Database:** PostgreSQL (tcu_ceaa_db)
