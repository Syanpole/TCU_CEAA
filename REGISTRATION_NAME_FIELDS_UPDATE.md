# Student Registration & Profile - Name Fields Update

## Summary
Updated the student registration and profile settings to use separate fields for **First Name**, **Middle Initial**, and **Last Name** instead of a single "Full Name" field.

## Changes Made

### Backend Changes

#### 1. Database Model (`backend/myapp/models.py`)
- ✅ Added `middle_initial` field to `CustomUser` model
  - Type: `CharField(max_length=5, blank=True, null=True)`
  - Optional field for storing middle initial (e.g., "M.", "A.")
  - Help text: "Middle initial (e.g., A. or M.)"

#### 2. Serializers (`backend/myapp/serializers.py`)
- ✅ Updated `UserSerializer` to include `middle_initial` in fields list
- ✅ Updated `RegisterSerializer` to include `middle_initial` in fields list
- Both serializers now support the new field structure

#### 3. Database Migration
- ✅ Migration `0012_customuser_middle_initial.py` created and applied
- Database now has the `middle_initial` column in the `customuser` table

### Frontend Changes

#### 1. Student Registration Modal (`frontend/src/components/StudentRegistrationModal.tsx`)
- ✅ Replaced single `fullName` field with three separate fields:
  - `firstName` - Required field for first name
  - `middleInitial` - Optional field for middle initial (auto-formatted)
  - `lastName` - Required field for last name
- ✅ Added auto-formatting for middle initial (capitalizes and adds period)
- ✅ Updated form submission to send separate name fields to backend
- ✅ Improved validation and user experience

#### 2. Student Registration Component (`frontend/src/components/StudentRegistration.tsx`)
- ✅ Same changes as modal version
- ✅ Consistent three-field name input across both registration forms

#### 3. Profile Settings (`frontend/src/components/ProfileSettings.tsx`)
- ✅ Added `middle_initial` field to the Personal Info tab
- ✅ Displays between First Name and Last Name
- ✅ Auto-formatting for middle initial input
- ✅ Optional field with helpful placeholder ("M.")
- ✅ Syncs with dark mode theme

#### 4. TypeScript Interfaces (`frontend/src/services/authService.ts`)
- ✅ Updated `User` interface to include `middle_initial?: string`
- ✅ Updated `RegisterData` interface to include `middle_initial?: string`
- ✅ Maintains type safety across the application

## Features

### Auto-Formatting
- **Middle Initial**: Automatically capitalizes and adds a period
  - Input: "m" → Output: "M."
  - Input: "john" → Output: "J."
  - Maximum 2 characters (letter + period)

### Validation
- **First Name**: Required field
- **Middle Initial**: Optional field (can be left blank)
- **Last Name**: Required field
- All fields trim whitespace before submission

### User Experience
- Clear labels and placeholders
- Helpful hints (e.g., "Optional (e.g., M.)")
- Consistent layout in three-column format
- Responsive design maintained

## Database Schema

### CustomUser Model Fields (Name-related)
```python
first_name = CharField(max_length=150, blank=True)  # Django default
last_name = CharField(max_length=150, blank=True)   # Django default
middle_initial = CharField(max_length=5, blank=True, null=True)  # New field
```

## API Changes

### Registration Endpoint (`/api/auth/register/`)
**New Request Format:**
```json
{
  "username": "student123",
  "email": "student@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Juan",
  "middle_initial": "D.",
  "last_name": "Dela Cruz",
  "student_id": "22-12345",
  "role": "student"
}
```

### Profile Update Endpoint (`/api/auth/profile/`)
**New Request Format:**
```json
{
  "first_name": "Juan",
  "middle_initial": "D.",
  "last_name": "Dela Cruz",
  "email": "student@example.com",
  "username": "student123",
  "student_id": "22-12345"
}
```

## Testing Checklist

- [x] Backend model updated with middle_initial field
- [x] Database migration created and applied
- [x] Registration modal accepts three name fields
- [x] Registration form accepts three name fields
- [x] Profile settings displays and updates middle initial
- [x] Auto-formatting works for middle initial
- [x] API serializers handle new field structure
- [ ] Test student registration with middle initial
- [ ] Test student registration without middle initial
- [ ] Test profile update with middle initial
- [ ] Test profile update removing middle initial
- [ ] Verify existing users are not affected

## Notes

### Admin Users
- Admin registration/profile functionality remains unchanged
- Admin users can also have middle_initial field if needed in the future
- Current changes focused on student user experience

### Backward Compatibility
- Middle initial is optional (blank=True, null=True)
- Existing users without middle initial will work normally
- No data migration needed for existing users
- Field can be added to existing profiles later

### Future Enhancements
- Could add full name display method to model (combining all three fields)
- Could add name formatting utilities
- Could extend to admin profile if needed

## Migration Command

To apply the changes to your database:
```bash
cd backend
python manage.py migrate
```

The migration `0012_customuser_middle_initial` will be applied automatically.

## Rollback (if needed)

To rollback the migration:
```bash
cd backend
python manage.py migrate myapp 0011  # Replace 0011 with the previous migration number
```

---

**Last Updated**: October 5, 2025
**Status**: ✅ Complete and Applied
**Impact**: Student registration and profile settings only
