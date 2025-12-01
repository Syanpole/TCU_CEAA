"""
Create PostgreSQL Database for TCU_CEAA
This script will create the tcu_ceaa_db database if it doesn't exist
"""

import psycopg
import sys

# Database connection parameters
DB_PARAMS = {
    'user': 'postgres',
    'password': 'admin123',
    'host': 'localhost',
    'port': '5432',
}

DB_NAME = 'tcu_ceaa_db'

def check_and_create_database():
    """Check if database exists and create it if it doesn't"""
    
    print("="*60)
    print("PostgreSQL Database Setup for TCU_CEAA")
    print("="*60)
    print()
    
    try:
        # Connect to PostgreSQL (default postgres database)
        print(f"[1/4] Connecting to PostgreSQL server...")
        conn = psycopg.connect(**DB_PARAMS, dbname='postgres', autocommit=True)
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        print()
        
        # Check if database exists
        print(f"[2/4] Checking if database '{DB_NAME}' exists...")
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{DB_NAME}' already exists!")
        else:
            print(f"⚠ Database '{DB_NAME}' not found. Creating...")
            
            # Create the database
            print(f"[3/4] Creating database '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"✓ Database '{DB_NAME}' created successfully!")
        
        print()
        
        # List all databases
        print("[4/4] Listing all databases:")
        cursor.execute(
            "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname"
        )
        databases = cursor.fetchall()
        
        for db in databases:
            marker = " ← YOUR APP DATABASE" if db[0] == DB_NAME else ""
            print(f"  • {db[0]}{marker}")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("✅ SUCCESS! Database is ready!")
        print("="*60)
        print()
        print("Next steps:")
        print("1. Refresh pgAdmin4 (right-click on 'Databases' → Refresh)")
        print("2. You should now see 'tcu_ceaa_db' in the database list")
        print("3. Run: python manage.py migrate")
        print("4. Run: python manage.py runserver")
        print()
        
        return True
        
    except psycopg.OperationalError as e:
        print()
        print("="*60)
        print("❌ CONNECTION FAILED!")
        print("="*60)
        print()
        print(f"Error: {e}")
        print()
        print("Common issues:")
        print("1. PostgreSQL service is not running")
        print("   → Open Services and start 'postgresql-x64-XX'")
        print()
        print("2. Wrong password")
        print("   → Check your pgAdmin4 password")
        print("   → Current password in script: admin123")
        print()
        print("3. Wrong port")
        print("   → Default is 5432, check your PostgreSQL configuration")
        print()
        return False
        
    except Exception as e:
        print()
        print("="*60)
        print("❌ ERROR!")
        print("="*60)
        print()
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print()
        return False

if __name__ == '__main__':
    success = check_and_create_database()
    sys.exit(0 if success else 1)
