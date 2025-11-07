# Student Verification System - CSV Import Guide

## Overview
This system automatically verifies students during registration based on their Student Number. Students listed in the CSV file will be able to register in the system.

## Files Created

1. **`import_verified_students.ps1`** - PowerShell script to import students from CSV
2. **`backend/add_verified_students.py`** - Python script that reads CSV and adds students to database
3. **CSV File**: `BSCS_4th_Year_List-1.csv` (should be in Downloads folder)

## How It Works

### 1. CSV Import Process
When you run the import script:
- The CSV file is copied from Downloads to the backend directory
- Each student in the CSV is added to the `VerifiedStudent` table in the database
- Students with matching Student Numbers can now register

### 2. Registration Process
When a student registers:
1. They enter their **Student Number** (e.g., `22-00001`)
2. The system checks if that Student Number exists in the `VerifiedStudent` table
3. If found, they can complete registration
4. If not found, registration is blocked

### 3. Student Verification
The system verifies students by checking:
- ✅ **Student Number** (from CSV) - Primary verification
- First Name, Last Name, Middle Initial (optional additional verification)

## How to Import Students

### Step 1: Ensure CSV File Exists
Make sure `BSCS_4th_Year_List-1.csv` is located at:
```
C:\Users\acer\Downloads\BSCS_4th_Year_List-1.csv
```

### Step 2: Run the Import Script
Open PowerShell in the project root directory and run:
```powershell
.\import_verified_students.ps1
```

### Step 3: Verify Import
The script will show:
- ✅ Number of students created
- ⚠️ Number of students that already existed
- 📊 Total verified students in database

## CSV File Format

The CSV file should have these columns:
```csv
Student Number,Last Name,First Name,Middle Initial,Sex,Course,Year
22-00001,Abaigar,Vennee Jones,R,M,BSCS,4
21-00274,Abayon,Kenneth,A,M,BSCS,4
```

### Column Details:
- **Student Number**: Format `YY-XXXXX` (e.g., `22-00001`)
- **Last Name**: Student's last name
- **First Name**: Student's first name
- **Middle Initial**: Middle initial or `N/A` if none
- **Sex**: `M` or `F`
- **Course**: Course code (e.g., `BSCS`, `BSIT`)
- **Year**: Year level (1-6)

## Adding More Students

### Option 1: Update CSV and Re-import
1. Add new students to the CSV file
2. Run `.\import_verified_students.ps1` again
3. Only new students will be added (existing ones will be skipped)

### Option 2: Manual Addition via Django Admin
1. Log in to Django Admin panel
2. Go to "Verified Students"
3. Click "Add Verified Student"
4. Fill in the student information

## Checking Verified Students

### Via Django Shell
```python
python manage.py shell

from myapp.models import VerifiedStudent

# Count total verified students
print(VerifiedStudent.objects.count())

# List all verified students
for student in VerifiedStudent.objects.all():
    print(f"{student.student_id} - {student.first_name} {student.last_name}")

# Check if specific student exists
student = VerifiedStudent.objects.filter(student_id='22-00001').first()
if student:
    print(f"Found: {student}")
```

### Via Database Script
Run the existing script:
```powershell
cd backend
python show_database_contents.py
```

## Security Notes

🔒 **Important Security Features:**
- Only students in the VerifiedStudent table can register
- Each student can only register once (`has_registered` flag)
- Student Number must match exactly
- System prevents duplicate registrations

## Troubleshooting

### Problem: "CSV file not found"
**Solution:** Make sure the CSV file is at `C:\Users\acer\Downloads\BSCS_4th_Year_List-1.csv`

### Problem: "Student already exists"
**Solution:** This is normal - the student was imported previously. The script skips existing students.

### Problem: Students can't register
**Possible causes:**
1. Student Number not in database - run import script
2. Student already registered - check `has_registered` flag
3. Student marked as inactive - check `is_active` flag

### Problem: Import script fails
**Solution:**
1. Make sure backend server is not running
2. Check database is accessible
3. Verify Python environment is activated
4. Check CSV file format is correct

## Current CSV Students (50 students)

The current CSV file contains **50 BSCS 4th Year students** with Student Numbers:
- 22-00001 through 22-00914
- 21-00274, 21-05075, 21-02223
- 20-02192
- 19-00677, 19-00648
- Jul-51 (note: unusual format)

All these students will be automatically verified when they register using their Student Number.

## Related Files

- **Models**: `backend/myapp/models.py` - `VerifiedStudent` model definition
- **Views**: `backend/myapp/views.py` - `verify_student_view` function
- **Registration**: Frontend registration form checks student verification

## Questions?

If students have issues registering:
1. Verify their Student Number is in the CSV file
2. Check they haven't already registered
3. Ensure they're entering the exact Student Number format (e.g., `22-00001`)
