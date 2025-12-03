"""
Populate verified students from CSV to GCP database
Run with: python populate_verified_students_gcp.py
"""

import os
import sys
import django
import csv
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from myapp.models import VerifiedStudent

# Path to CSV file
CSV_FILE = project_root.parent / 'verified_students.csv'

def populate_verified_students():
    """Read CSV and populate verified students table"""
    
    if not CSV_FILE.exists():
        print(f"❌ Error: CSV file not found at {CSV_FILE}")
        return
    
    print(f"📄 Reading verified students from: {CSV_FILE}")
    print("=" * 80)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # Clean the data
                student_number = row['Student Number'].strip()
                last_name = row['Last Name'].strip()
                first_name = row['First Name'].strip()
                middle_initial = row['Middle Initial'].strip()
                sex = row['Sex'].strip().upper()
                course = row['Course'].strip().upper()
                year_level = int(row['Year'].strip())
                
                # Handle N/A middle initials
                if middle_initial.upper() == 'N/A':
                    middle_initial = ''
                
                # Create or update student
                student, created = VerifiedStudent.objects.update_or_create(
                    student_id=student_number,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'middle_initial': middle_initial,
                        'sex': sex,
                        'course': course,
                        'year_level': year_level,
                        'is_active': True,
                        'notes': 'Imported from verified_students.csv'
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"✅ Created: {first_name} {last_name} ({student_number})")
                else:
                    updated_count += 1
                    print(f"🔄 Updated: {first_name} {last_name} ({student_number})")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error processing {row.get('Student Number', 'Unknown')}: {str(e)}")
    
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created_count}")
    print(f"   🔄 Updated: {updated_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📈 Total in database: {VerifiedStudent.objects.count()}")
    print(f"\n✅ Done!")

if __name__ == '__main__':
    populate_verified_students()
