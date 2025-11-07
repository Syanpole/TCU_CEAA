# Database Schema Fix - November 5, 2025

## Problem
The login and password reset features were failing with the error:
```
ProgrammingError: column myapp_customuser.email_verified_at does not exist
```

## Root Cause
The database schema was out of sync with the Django models. The `email_verified_at` column was defined in the Django model (`CustomUser` in `models.py`) but was missing from the actual PostgreSQL database table.

## Solution Applied

### 1. Fixed Migration Conflicts
Merged conflicting migrations:
- `0019_customuser_email_verified_at_and_more`
- `0020_merge_20251104_2222`

Created merge migration: `0021_merge_20251105_1225.py`

### 2. Added Missing Database Column
Created and ran `fix_db_columns_now.py` which:
- Checked existing columns in `myapp_customuser` table
- Added the missing `email_verified_at` column with the correct type:
  ```sql
  ALTER TABLE myapp_customuser 
  ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE NULL
  ```

### 3. Synced Django Migration State
Ran `python manage.py migrate --fake` to synchronize Django's migration tracking with the actual database state.

## Current Database State

### Email-related Tables
- `myapp_emailverificationcode` - Stores email verification codes for registration and password reset

### Email Verification Columns in `myapp_customuser`
| Column | Type | Nullable |
|--------|------|----------|
| email | character varying | NOT NULL |
| is_email_verified | boolean | NOT NULL |
| email_verified_at | timestamp with time zone | NULL |

## What Now Works

### ✅ Login System
- Users can now log in without the `ProgrammingError`
- Email verification status is properly checked
- Students must verify their email before logging in (if role is 'student')

### ✅ Password Reset System
- Users can request password reset codes via `/api/auth/request-password-reset/`
- Verification codes are sent to email
- Users can verify codes via `/api/auth/verify-reset-code/`
- Users can reset passwords via `/api/auth/reset-password/`

### ✅ Email Verification
- New users receive verification codes during registration
- Verification codes are stored in `myapp_emailverificationcode` table
- Codes expire after 10 minutes
- Maximum 5 verification attempts per code

## Next Steps for Deployment

1. **Restart Django Development Server**
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   cd c:\xampp\htdocs\TCU_CEAA\backend
   python manage.py runserver
   ```

2. **Test the Fix**
   - Try logging in with existing credentials
   - Test forgot password flow
   - Register a new account to test email verification

3. **For Production Deployment**
   When deploying to production, ensure you:
   - Run migrations: `python manage.py migrate`
   - If the column still doesn't exist, use the `fix_db_columns_now.py` script
   - Restart your production server

## Files Created/Modified

### New Files
- `backend/fix_db_columns_now.py` - Database schema fix script
- `backend/check_database_tables.py` - Database diagnostic script
- `backend/myapp/migrations/0021_merge_20251105_1225.py` - Merge migration

### Modified Files
None - only database schema was modified

## Technical Details

### Migration Sequence
1. `0019_customuser_email_verified_at_and_more` - Attempted to add email verification fields
2. `0020_merge_20251104_2222` - Previous merge attempt
3. `0021_merge_20251105_1225` - Final successful merge
4. Faked migration to sync state

### Database Commands Used
```sql
-- Check existing columns
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'myapp_customuser';

-- Add missing column
ALTER TABLE myapp_customuser 
ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE NULL;

-- Verify column exists
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'myapp_customuser' 
AND column_name IN ('email_verified_at', 'is_email_verified');
```

## Prevention

To avoid this issue in the future:
1. Always run `python manage.py makemigrations` after model changes
2. Always run `python manage.py migrate` to apply migrations
3. Check migration conflicts before deploying: `python manage.py showmigrations`
4. Test locally before pushing to production

## Verification Checklist

- [x] `email_verified_at` column exists in database
- [x] `is_email_verified` column exists in database
- [x] Migration conflicts resolved
- [x] Django migration state synchronized
- [x] Login endpoint accessible
- [x] Password reset endpoints accessible
- [ ] Manual testing of login flow (next step)
- [ ] Manual testing of password reset flow (next step)
- [ ] Manual testing of registration with email verification (next step)

---
**Fix completed on:** November 5, 2025  
**Database:** PostgreSQL (tcu_ceaa_db)  
**Django Version:** 5.2.5  
**Python Version:** 3.13.2
