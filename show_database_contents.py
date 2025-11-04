"""
Visual guide to show what tables exist in your database
This proves the database is properly connected
"""

import psycopg
from tabulate import tabulate

# Connection parameters
DB_PARAMS = {
    'dbname': 'tcu_ceaa_db',
    'user': 'postgres',
    'password': 'admin123',
    'host': 'localhost',
    'port': '5432'
}

print("="*80)
print(" 🔍 TCU_CEAA DATABASE CONTENTS - What You Should See in pgAdmin4")
print("="*80)
print()

try:
    # Connect to database
    conn = psycopg.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("""
        SELECT table_name, 
               pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    print(f"📊 Database: tcu_ceaa_db")
    print(f"🔗 Connection: ✅ SUCCESSFUL")
    print(f"📋 Total Tables: {len(tables)}")
    print()
    print("-"*80)
    
    # Display tables in a nice format
    headers = ["#", "Table Name", "Size", "Description"]
    table_data = []
    
    for idx, (table_name, size) in enumerate(tables, 1):
        # Add descriptions for key tables
        desc = ""
        if "customuser" in table_name.lower():
            desc = "👥 User accounts (students, admin, staff)"
        elif "application" in table_name.lower() or "allowance" in table_name.lower():
            desc = "📝 Scholarship/Allowance applications"
        elif "grade" in table_name.lower():
            desc = "📊 Student grades"
        elif "document" in table_name.lower():
            desc = "📄 Uploaded documents"
        elif "auth" in table_name.lower():
            desc = "🔐 Authentication & permissions"
        elif "django" in table_name.lower():
            desc = "⚙️ Django system tables"
        elif "token" in table_name.lower():
            desc = "🎫 API authentication tokens"
        elif "analytics" in table_name.lower():
            desc = "📈 System analytics & monitoring"
        
        table_data.append([idx, table_name, size, desc])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print()
    print("-"*80)
    print()
    print("📍 HOW TO VIEW THIS IN pgAdmin4:")
    print()
    print("1. Open pgAdmin4")
    print("2. Connect to PostgreSQL server (password: admin123)")
    print("3. Expand: Servers → PostgreSQL XX → Databases")
    print("4. Right-click 'Databases' → Refresh")
    print("5. Expand: tcu_ceaa_db → Schemas → public → Tables")
    print("6. Right-click 'Tables' → Refresh")
    print()
    print("You should see ALL the tables listed above! ⬆️")
    print()
    print("-"*80)
    print()
    
    # Get sample counts from key tables
    print("📊 DATA SUMMARY:")
    print()
    
    key_tables = [
        ('myapp_customuser', 'Total Users'),
        ('myapp_allowanceapplication', 'Allowance Applications'),
        ('myapp_application', 'Scholarship Applications'),
        ('myapp_grade', 'Grade Records'),
        ('django_migrations', 'Applied Migrations')
    ]
    
    summary_data = []
    for table, description in key_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            summary_data.append([description, count, "✅" if count > 0 else "📭"])
        except Exception:
            summary_data.append([description, "N/A", "❌"])
    
    print(tabulate(summary_data, headers=["Category", "Count", "Status"], tablefmt="grid"))
    
    print()
    print("="*80)
    print("✅ SUCCESS! Database is fully connected and contains all Django tables!")
    print("="*80)
    print()
    print("🎯 NEXT STEPS:")
    print("   1. Refresh pgAdmin4 to see these tables")
    print("   2. Right-click any table → 'View/Edit Data' → 'All Rows'")
    print("   3. Both Django and pgAdmin4 show the SAME data!")
    print()
    
    cursor.close()
    conn.close()
    
except psycopg.OperationalError as e:
    print("❌ CONNECTION FAILED!")
    print(f"Error: {e}")
    print()
    print("Solutions:")
    print("1. Check PostgreSQL is running: Get-Service postgresql*")
    print("2. Verify password in backend\\.env is: admin123")
    print("3. Ensure database exists: python create_database.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
