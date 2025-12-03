"""
Verify verified students in GCP database
"""
import psycopg2

DB_CONFIG = {
    'dbname': 'tcu_ceaa_db',
    'user': 'postgres',
    'password': 'TCU_CEAA_2024_SecureDB!',
    'host': '34.63.119.130',
    'port': '5432'
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Get count by course
cursor.execute("""
    SELECT course, COUNT(*) as count
    FROM myapp_verifiedstudent
    GROUP BY course
    ORDER BY course;
""")

print("Verified Students by Course:")
print("=" * 50)
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} students")

# Get count by year level
cursor.execute("""
    SELECT year_level, COUNT(*) as count
    FROM myapp_verifiedstudent
    GROUP BY year_level
    ORDER BY year_level;
""")

print("\nVerified Students by Year Level:")
print("=" * 50)
for row in cursor.fetchall():
    print(f"  Year {row[0]}: {row[1]} students")

# Get sample records
cursor.execute("""
    SELECT student_id, first_name, last_name, course, year_level
    FROM myapp_verifiedstudent
    ORDER BY last_name
    LIMIT 10;
""")

print("\nSample Records (First 10):")
print("=" * 80)
print(f"{'Student ID':<15} {'Name':<35} {'Course':<8} {'Year':<5}")
print("-" * 80)
for row in cursor.fetchall():
    full_name = f"{row[1]} {row[2]}"
    print(f"{row[0]:<15} {full_name:<35} {row[3]:<8} {row[4]:<5}")

# Total count
cursor.execute("SELECT COUNT(*) FROM myapp_verifiedstudent")
total = cursor.fetchone()[0]
print("\n" + "=" * 80)
print(f"Total Verified Students: {total}")

cursor.close()
conn.close()
