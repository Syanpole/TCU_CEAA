"""
Direct import script for verified students
Run this directly with: python import_students_from_csv.py

This will sync the BSCS_4th_Year_List-1.csv file with the database.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

import csv
from myapp.models import VerifiedStudent

def import_students():
    """Import students from CSV file"""
    
    # CSV file path (in backend directory)
    csv_file = os.path.join(os.path.dirname(__file__), 'BSCS_4th_Year_List-1.csv')
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file not found at {csv_file}")
        print("Please make sure BSCS_4th_Year_List-1.csv is in the backend directory.")
        return False
    
    print("="*70)
    print("  📋 TCU-CEAA: Import Verified Students from CSV")
    print("="*70)
    print(f"\n📄 Reading from: {csv_file}\n")
    
    verified_students = []
    
    # Read CSV file
    try:
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
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
        
        print(f"✅ Read {len(verified_students)} students from CSV file\n")
    
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return False
    
    # Add students to database
    print("🔄 Adding students to database...\n")
    created_count = 0
    existing_count = 0
    updated_count = 0
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
                # Check if any data needs updating
                needs_update = False
                update_fields = []
                
                if student.first_name != student_data['first_name']:
                    student.first_name = student_data['first_name']
                    needs_update = True
                    update_fields.append('first_name')
                
                if student.last_name != student_data['last_name']:
                    student.last_name = student_data['last_name']
                    needs_update = True
                    update_fields.append('last_name')
                
                if student.middle_initial != student_data['middle_initial']:
                    student.middle_initial = student_data['middle_initial']
                    needs_update = True
                    update_fields.append('middle_initial')
                
                if student.sex != student_data['sex']:
                    student.sex = student_data['sex']
                    needs_update = True
                    update_fields.append('sex')
                
                if student.course != student_data['course']:
                    student.course = student_data['course']
                    needs_update = True
                    update_fields.append('course')
                
                if student.year_level != student_data['year_level']:
                    student.year_level = student_data['year_level']
                    needs_update = True
                    update_fields.append('year_level')
                
                if needs_update:
                    student.save()
                    updated_count += 1
                    print(f"🔄 Updated: {student.first_name} {student.last_name} ({student.student_id}) - Fields: {', '.join(update_fields)}")
                else:
                    existing_count += 1
                    print(f"⏭️  Unchanged: {student.first_name} {student.last_name} ({student.student_id})")
                    
        except Exception as e:
            error_count += 1
            print(f"❌ Error processing {student_data.get('student_id', 'unknown')}: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("  📊 IMPORT SUMMARY")
    print("="*70)
    print(f"✅ New students created:     {created_count}")
    print(f"🔄 Existing students updated: {updated_count}")
    print(f"⏭️  Unchanged students:        {existing_count}")
    print(f"❌ Errors:                    {error_count}")
    print(f"📊 Total in database:         {VerifiedStudent.objects.count()}")
    print("="*70)
    
    print("\n✨ Students from the CSV can now register using their Student Number!")
    print("   Example: Student 22-00001 (Vennee Jones Abaigar) can register\n")
    
    return True

if __name__ == '__main__':
    import_students()
