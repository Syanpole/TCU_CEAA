"""
Quick script to add verified students to the database from CSV file
Run: python manage.py shell < add_verified_students.py

CSV file location: backend/BSCS_4th_Year_List-1.csv
Format: Student Number,Last Name,First Name,Middle Initial,Sex,Course,Year

USAGE:
1. Edit backend/BSCS_4th_Year_List-1.csv to add/update students
2. Run: cd backend && Get-Content add_verified_students.py | python manage.py shell
3. Students will be automatically added/updated in the database

This script will automatically verify students whose student numbers match the CSV
when they register in the system.
"""

import csv
import os
from myapp.models import VerifiedStudent

# CSV file paths (tries multiple locations, prioritizes backend directory)
CSV_FILE_PATHS = [
    os.path.join(os.path.dirname(__file__), 'BSCS_4th_Year_List-1.csv'),  # Backend directory (PREFERRED)
    r'BSCS_4th_Year_List-1.csv',  # Current directory
    r'C:\Users\acer\Downloads\BSCS_4th_Year_List-1.csv',  # Downloads folder (fallback)
]

# Find the CSV file
CSV_FILE_PATH = None
for path in CSV_FILE_PATHS:
    if os.path.exists(path):
        CSV_FILE_PATH = path
        break

print(f"Reading students from: {CSV_FILE_PATH}")

if not os.path.exists(CSV_FILE_PATH):
    print(f"❌ Error: CSV file not found at {CSV_FILE_PATH}")
    print("Please make sure the CSV file is in the correct location.")
    exit(1)

verified_students = []

# Read CSV file
try:
    with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Parse CSV row
            student_data = {
                'student_id': row['Student Number'].strip(),
                'first_name': row['First Name'].strip(),
                'last_name': row['Last Name'].strip(),
                'middle_initial': row['Middle Initial'].strip() if row['Middle Initial'].strip() else 'N/A',
                'sex': row['Sex'].strip().upper(),
                'course': row['Course'].strip().upper(),
                'year_level': int(row['Year'].strip()),
                'is_active': True,
                'notes': 'Imported from BSCS 4th Year List CSV'
            }
            verified_students.append(student_data)
    
    print(f"📄 Read {len(verified_students)} students from CSV file\n")

except Exception as e:
    print(f"❌ Error reading CSV file: {e}")
    exit(1)

# Add students to database
print("Adding verified students to database...")
created_count = 0
existing_count = 0
error_count = 0

for student_data in verified_students:
    try:
        student, created = VerifiedStudent.objects.get_or_create(
            student_id=student_data['student_id'],
            defaults=student_data
        )
        if created:
            created_count += 1
            print(f"✅ Created: {student.first_name} {student.last_name} ({student.student_id})")
        else:
            existing_count += 1
            print(f"⚠️  Already exists: {student.first_name} {student.last_name} ({student.student_id})")
    except Exception as e:
        error_count += 1
        print(f"❌ Error adding {student_data.get('student_id', 'unknown')}: {e}")

print("\n" + "="*60)
print(f"✅ Students created: {created_count}")
print(f"⚠️  Students already existed: {existing_count}")
print(f"❌ Errors: {error_count}")
print(f"📊 Total verified students in database: {VerifiedStudent.objects.count()}")
print("="*60)
