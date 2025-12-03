"""
Check the actual structure of the verified_students table in GCP
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

# Get table structure
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'myapp_verifiedstudent'
    ORDER BY ordinal_position;
""")

print("Table: myapp_verifiedstudent")
print("=" * 80)
for row in cursor.fetchall():
    print(f"  {row[0]:<30} {row[1]:<20} {row[2] if row[2] else ''}")

cursor.close()
conn.close()
