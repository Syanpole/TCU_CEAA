"""
Populate verified students from CSV directly to GCP Cloud SQL database
This script connects to the GCP PostgreSQL database and imports verified students
Run with: python populate_gcp_verified_students.py
"""

import csv
import psycopg2
from pathlib import Path

# GCP Cloud SQL Connection Details
DB_CONFIG = {
    'dbname': 'tcu_ceaa_db',
    'user': 'postgres',
    'password': 'TCU_CEAA_2024_SecureDB!',
    'host': '34.63.119.130',  # Public IP of tcu-ceaa-postgres
    'port': '5432'
}

# Path to CSV file
CSV_FILE = Path(__file__).parent.parent / 'verified_students.csv'

def check_table_exists(cursor):
    """Check if verified_students table exists"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'myapp_verifiedstudent'
        );
    """)
    exists = cursor.fetchone()[0]
    if exists:
        print("✅ Table 'myapp_verifiedstudent' found")
    else:
        print("❌ Table 'myapp_verifiedstudent' not found!")
        print("   Please ensure Django migrations have been run on the GCP database")
        return False
    return True

def populate_verified_students():
    """Read CSV and populate verified students table in GCP database"""
    
    if not CSV_FILE.exists():
        print(f"❌ Error: CSV file not found at {CSV_FILE}")
        return
    
    print(f"📄 Reading verified students from: {CSV_FILE}")
    print(f"🔌 Connecting to GCP Cloud SQL: {DB_CONFIG['host']}")
    print("=" * 80)
    
    try:
        # Connect to GCP database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if table exists
        if not check_table_exists(cursor):
            cursor.close()
            conn.close()
            return
        conn.commit()
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Try multiple encodings to handle special characters
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        file_content = None
        
        for encoding in encodings:
            try:
                with open(CSV_FILE, 'r', encoding=encoding) as f:
                    file_content = f.read()
                    print(f"✅ Successfully read file with {encoding} encoding")
                    break
            except UnicodeDecodeError:
                continue
        
        if not file_content:
            print("❌ Could not read CSV file with any encoding")
            return
        
        # Parse CSV from string
        from io import StringIO
        csv_file = StringIO(file_content)
        
        with csv_file as file:
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
                    
                    # Try to insert, update if exists
                    insert_sql = """
                    INSERT INTO myapp_verifiedstudent 
                        (student_id, first_name, last_name, middle_initial, sex, course, year_level, is_active, has_registered, notes, added_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (student_id) 
                    DO UPDATE SET 
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        middle_initial = EXCLUDED.middle_initial,
                        sex = EXCLUDED.sex,
                        course = EXCLUDED.course,
                        year_level = EXCLUDED.year_level,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING (xmax = 0) AS inserted
                    """
                    
                    cursor.execute(insert_sql, (
                        student_number,
                        first_name,
                        last_name,
                        middle_initial,
                        sex,
                        course,
                        year_level,
                        True,
                        False,
                        'Imported from verified_students.csv'
                    ))
                    
                    was_inserted = cursor.fetchone()[0]
                    
                    if was_inserted:
                        created_count += 1
                        print(f"✅ Created: {first_name} {last_name} ({student_number})")
                    else:
                        updated_count += 1
                        print(f"🔄 Updated: {first_name} {last_name} ({student_number})")
                    
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error processing {row.get('Student Number', 'Unknown')}: {str(e)}")
        
        # Commit all changes
        conn.commit()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM myapp_verifiedstudent")
        total_count = cursor.fetchone()[0]
        
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   ✅ Created: {created_count}")
        print(f"   🔄 Updated: {updated_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📈 Total in GCP database: {total_count}")
        print(f"\n✅ Done!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ Database connection error: {str(e)}")
        print(f"\n💡 Tip: Make sure your IP is whitelisted in GCP Cloud SQL")
        print(f"   Run: gcloud sql instances patch tcu-ceaa-postgres --authorized-networks=YOUR_IP")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    populate_verified_students()
