# Quick Reference: Managing Verified Students

## 📍 CSV File Location
```
backend/BSCS_4th_Year_List-1.csv
```

## 🔄 How to Add/Update Students

### Option 1: Edit CSV File (Recommended)
1. Open `backend/BSCS_4th_Year_List-1.csv` in Excel or text editor
2. Add new rows or edit existing ones:
   ```csv
   Student Number,Last Name,First Name,Middle Initial,Sex,Course,Year
   22-00001,Abaigar,Vennee Jones,R,M,BSCS,4
   22-12345,NewStudent,John,A,M,BSCS,4
   ```
3. Save the CSV file
4. Run the import script:
   ```powershell
   .\import_verified_students.ps1
   ```

### Option 2: Direct Python Script (From Backend Directory)
```powershell
cd backend
python import_students_from_csv.py
```

## ✨ What Happens When You Import

- **New students**: Added to database (✅ Created)
- **Existing students with changes**: Updated (🔄 Updated)
- **Existing students unchanged**: Skipped (⏭️ Unchanged)
- **Errors**: Displayed with details (❌ Error)

## 📋 CSV Format Rules

| Column | Required | Format | Example |
|--------|----------|--------|---------|
| Student Number | ✅ Yes | YY-XXXXX | 22-00001 |
| Last Name | ✅ Yes | Text | Abaigar |
| First Name | ✅ Yes | Text | Vennee Jones |
| Middle Initial | ⚠️ Optional | Letter or N/A | R |
| Sex | ✅ Yes | M or F | M |
| Course | ✅ Yes | BSCS, BSIT, etc. | BSCS |
| Year | ✅ Yes | 1-6 | 4 |

## 🎯 Common Tasks

### Add a Single Student
1. Open `backend/BSCS_4th_Year_List-1.csv`
2. Add new row at the bottom:
   ```csv
   22-99999,Doe,Jane,M,F,BSCS,4
   ```
3. Save file
4. Run: `.\import_verified_students.ps1`

### Update Student Information
1. Open `backend/BSCS_4th_Year_List-1.csv`
2. Find the student's row by Student Number
3. Edit the information (name, year, etc.)
4. Save file
5. Run: `.\import_verified_students.ps1`

### Remove a Student
1. Open `backend/BSCS_4th_Year_List-1.csv`
2. Delete the student's row
3. Save file
4. **Note**: Student won't be deleted from database, but won't be updated
5. To fully remove, use Django admin or database script

### Check Who's in the Database
```powershell
cd backend
python show_database_contents.py
```

Or in Django shell:
```python
python manage.py shell

from myapp.models import VerifiedStudent
print(f"Total students: {VerifiedStudent.objects.count()}")
for s in VerifiedStudent.objects.all():
    print(f"{s.student_id} - {s.first_name} {s.last_name}")
```

## 🔒 Student Registration Flow

1. Student goes to registration page
2. Enters Student Number (e.g., `22-00001`)
3. System checks `VerifiedStudent` table
4. If found → ✅ Can register
5. If not found → ❌ Registration blocked

## 📊 Current Students (50 total)

Your CSV has 50 BSCS 4th Year students:
- Student Numbers: 22-00001 through 22-00914
- Plus older batches: 21-xxxxx, 20-02192, 19-xxxxx
- Special case: Jul-51 (Soriano, Isaac)

## 🚨 Important Notes

1. **Student Number is the unique identifier** - Don't change it for existing students
2. **CSV must have headers** - First row must be column names
3. **Middle Initial**: Use "N/A" if student has no middle initial
4. **Already registered students**: Won't be affected by CSV updates
5. **Backup recommended**: Keep a backup of CSV before major changes

## 🛠️ Files in System

| File | Purpose |
|------|---------|
| `backend/BSCS_4th_Year_List-1.csv` | Master list of students (EDIT THIS) |
| `backend/import_students_from_csv.py` | Python script that reads CSV |
| `import_verified_students.ps1` | Easy-to-run PowerShell script |
| `backend/add_verified_students.py` | Django shell alternative |

## ⚡ Quick Commands

```powershell
# Import students from CSV
.\import_verified_students.ps1

# Import from backend directory
cd backend
python import_students_from_csv.py

# View database contents
cd backend
python show_database_contents.py

# Django shell method
cd backend
Get-Content add_verified_students.py | python manage.py shell
```

## 🎓 Example Workflow

**Scenario**: New batch of students needs to be added

1. Receive student list from registrar
2. Open `backend/BSCS_4th_Year_List-1.csv`
3. Copy/paste student data (or type manually)
4. Save file
5. Run: `.\import_verified_students.ps1`
6. Verify in output: "✅ Students created: X"
7. Students can now register!

## ❓ Troubleshooting

**Problem**: "CSV file not found"
- **Solution**: Make sure file is at `backend/BSCS_4th_Year_List-1.csv`

**Problem**: "Error reading CSV file"
- **Solution**: Check CSV format, ensure no missing commas, proper encoding (UTF-8)

**Problem**: "Student already exists"
- **Solution**: Normal - student was previously imported. Check if update is needed.

**Problem**: Student can't register
- **Solution**: 
  1. Check if Student Number is in CSV (exact match required)
  2. Run import script again
  3. Verify with `show_database_contents.py`

**Problem**: Import shows "Updated" but no changes
- **Solution**: Script detected a difference and updated the record (this is normal)

---

**Ready to use!** Just edit the CSV and run the import script. 🚀
