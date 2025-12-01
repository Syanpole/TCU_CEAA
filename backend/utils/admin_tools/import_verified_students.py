"""
Script to import verified students from CSV file into the database
These students are pre-verified by TCU and can create accounts.

Run: python import_verified_students.py
"""

import os
import sys
import django
import csv

# Setup Django environment
if __name__ == '__main__':
    # Add the backend directory to the path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
    django.setup()

from myapp.models import VerifiedStudent

# BSCS 4th Year Students from CSV
verified_students_data = [
    {'student_id': '22-00001', 'last_name': 'Abaigar', 'first_name': 'Vennee Jones', 'middle_initial': 'R', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '21-00274', 'last_name': 'Abayon', 'first_name': 'Kenneth', 'middle_initial': 'A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00319', 'last_name': 'Alejandro', 'first_name': 'Adrian', 'middle_initial': 'N/A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00327', 'last_name': 'Arcilla', 'first_name': 'Stephen Jay', 'middle_initial': 'B', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00005', 'last_name': 'Aspan', 'first_name': 'Khesler John', 'middle_initial': 'V', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00007', 'last_name': 'Bacon', 'first_name': 'Jhon Lorenz', 'middle_initial': 'G', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00330', 'last_name': 'Balmoja', 'first_name': 'Dorothy Zoe', 'middle_initial': 'L', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00009', 'last_name': 'Bentulan', 'first_name': 'Paul Marco', 'middle_initial': 'Y', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '19-00677', 'last_name': 'Bermas', 'first_name': 'Jonathan', 'middle_initial': 'B', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00011', 'last_name': 'Cabalse', 'first_name': 'Christopher Julian', 'middle_initial': 'R', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00013', 'last_name': 'Catalan', 'first_name': 'Fritz John Josh', 'middle_initial': 'F', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00312', 'last_name': 'Curias', 'first_name': 'Jeremiah James', 'middle_initial': 'A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '21-05075', 'last_name': 'Dacera', 'first_name': 'Oliver', 'middle_initial': 'D', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00006', 'last_name': 'Dejaro', 'first_name': 'Dee-Yam Mark', 'middle_initial': 'B', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00363', 'last_name': 'Dela Cruz', 'first_name': 'Angelo', 'middle_initial': 'A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00373', 'last_name': 'Delica', 'first_name': 'Riu', 'middle_initial': 'L', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00379', 'last_name': 'Deocariza', 'first_name': 'Laurence Jade', 'middle_initial': 'A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00384', 'last_name': 'Divina', 'first_name': 'John Jordan', 'middle_initial': 'E', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00390', 'last_name': 'Dungao', 'first_name': 'Justine Zyrie', 'middle_initial': 'N/A', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00396', 'last_name': 'Eborde', 'first_name': 'Christian', 'middle_initial': 'N', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00402', 'last_name': 'Enriquez', 'first_name': 'Timothy Jhon', 'middle_initial': 'N/A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00410', 'last_name': 'Esteban', 'first_name': 'Sean Lloyd', 'middle_initial': 'D', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00417', 'last_name': 'Feliciano', 'first_name': 'Sean Paul', 'middle_initial': 'C', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00462', 'last_name': 'Galauran', 'first_name': 'Mariano', 'middle_initial': 'R', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00466', 'last_name': 'Gonzales', 'first_name': 'Hannah Vine', 'middle_initial': 'D', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00472', 'last_name': 'Ita-As', 'first_name': 'Geniel', 'middle_initial': 'G', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00476', 'last_name': 'Jimenez', 'first_name': 'Althea Jasmine', 'middle_initial': 'J', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00482', 'last_name': 'Laure', 'first_name': 'Shane', 'middle_initial': 'N/A', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00484', 'last_name': 'Libay', 'first_name': 'Jet', 'middle_initial': 'D', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00494', 'last_name': 'Magat', 'first_name': 'Alfred', 'middle_initial': 'M', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00503', 'last_name': 'Malanog Jr', 'first_name': 'Malbert', 'middle_initial': 'S', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00512', 'last_name': 'Molina', 'first_name': 'Kim Alfred', 'middle_initial': 'A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00519', 'last_name': 'Montañez', 'first_name': 'Joseph Anthony', 'middle_initial': 'N/A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00528', 'last_name': 'Morales', 'first_name': 'Justin', 'middle_initial': 'F', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00534', 'last_name': 'Orcales', 'first_name': 'Marianne', 'middle_initial': 'V', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00540', 'last_name': 'Peñaflor', 'first_name': 'Jonel', 'middle_initial': 'P', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00548', 'last_name': 'Porras', 'first_name': 'Kenneth', 'middle_initial': 'N/A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '19-00648', 'last_name': 'Ramos', 'first_name': 'Lloyd Kenneth', 'middle_initial': 'S', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00551', 'last_name': 'Rapal', 'first_name': 'Jalil', 'middle_initial': 'R', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00332', 'last_name': 'Relon', 'first_name': 'Jave Allah', 'middle_initial': 'C', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00566', 'last_name': 'Reyes', 'first_name': 'Benedict', 'middle_initial': 'S', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '20-02192', 'last_name': 'Reyes', 'first_name': 'Kerwin', 'middle_initial': 'F', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00914', 'last_name': 'Salivio', 'first_name': 'Chester John', 'middle_initial': 'C', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00334', 'last_name': 'Sambitan', 'first_name': 'John Rafael', 'middle_initial': 'L', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00568', 'last_name': 'San Gabriel', 'first_name': 'Yrael Nikko', 'middle_initial': 'D', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '21-02223', 'last_name': 'Solero', 'first_name': 'Jeffrey', 'middle_initial': 'J', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': 'Jul-51', 'last_name': 'Soriano', 'first_name': 'Isaac', 'middle_initial': 'A', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00570', 'last_name': 'Tanabe', 'first_name': 'Denise Koyasha', 'middle_initial': 'H', 'sex': 'F', 'course': 'BSCS', 'year_level': 4},
    {'student_id': '22-00574', 'last_name': 'Villaruel', 'first_name': 'Ken Cedric', 'middle_initial': 'S', 'sex': 'M', 'course': 'BSCS', 'year_level': 4},
]

print("=" * 80)
print("IMPORTING VERIFIED STUDENTS - BSCS 4th Year")
print("=" * 80)
print(f"Total students to process: {len(verified_students_data)}")
print("=" * 80)

added_count = 0
updated_count = 0
skipped_count = 0
error_count = 0

for student_data in verified_students_data:
    try:
        student_id = student_data['student_id']
        
        # Check if student already exists
        existing_student = VerifiedStudent.objects.filter(student_id=student_id).first()
        
        if existing_student:
            # Update existing student if needed
            updated = False
            if not existing_student.is_active:
                existing_student.is_active = True
                updated = True
            
            # Update other fields if they're different
            if existing_student.first_name != student_data['first_name']:
                existing_student.first_name = student_data['first_name']
                updated = True
            if existing_student.last_name != student_data['last_name']:
                existing_student.last_name = student_data['last_name']
                updated = True
            if existing_student.middle_initial != student_data['middle_initial']:
                existing_student.middle_initial = student_data['middle_initial']
                updated = True
            if existing_student.sex != student_data['sex']:
                existing_student.sex = student_data['sex']
                updated = True
            if existing_student.course != student_data['course']:
                existing_student.course = student_data['course']
                updated = True
            if existing_student.year_level != student_data['year_level']:
                existing_student.year_level = student_data['year_level']
                updated = True
            
            if updated:
                existing_student.notes = (existing_student.notes or '') + '\n[Updated: November 6, 2025 - BSCS 4th Year import]'
                existing_student.save()
                print(f"🔄 Updated: {student_id} - {student_data['first_name']} {student_data['last_name']}")
                updated_count += 1
            else:
                print(f"⚠️  Skipped (already exists): {student_id} - {student_data['first_name']} {student_data['last_name']}")
                skipped_count += 1
        else:
            # Create new verified student
            new_student = VerifiedStudent.objects.create(
                student_id=student_id,
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                middle_initial=student_data['middle_initial'] if student_data['middle_initial'] != 'N/A' else '',
                sex=student_data['sex'],
                course=student_data['course'],
                year_level=student_data['year_level'],
                is_active=True,
                has_registered=False,
                notes='Imported from BSCS 4th Year list on November 6, 2025. Pre-verified by TCU.'
            )
            print(f"✅ Created: {student_id} - {student_data['first_name']} {student_data['last_name']}")
            added_count += 1
            
    except Exception as e:
        print(f"❌ Error processing {student_data.get('student_id', 'UNKNOWN')}: {str(e)}")
        error_count += 1

print("\n" + "=" * 80)
print("IMPORT SUMMARY")
print("=" * 80)
print(f"✅ Newly created: {added_count}")
print(f"🔄 Updated: {updated_count}")
print(f"⚠️  Skipped (no changes): {skipped_count}")
print(f"❌ Errors: {error_count}")
print("-" * 80)
print(f"📊 Total verified students in database: {VerifiedStudent.objects.count()}")
print(f"📊 Active verified students: {VerifiedStudent.objects.filter(is_active=True).count()}")
print(f"📊 Students who have registered: {VerifiedStudent.objects.filter(has_registered=True).count()}")
print(f"📊 Students pending registration: {VerifiedStudent.objects.filter(is_active=True, has_registered=False).count()}")
print("=" * 80)
print("\n✅ These students can now create accounts in the TCU-CEAA system!")
print("=" * 80)
