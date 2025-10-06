import psycopg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials from .env
db_name = os.getenv('DB_NAME', 'tcu_ceaa_db')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgre123')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = os.getenv('DB_PORT', '5432')

print(f"Testing PostgreSQL connection...")
print(f"Database: {db_name}")
print(f"User: {db_user}")
print(f"Password: {'*' * len(db_password)}")
print(f"Host: {db_host}")
print(f"Port: {db_port}")
print("-" * 50)

# Try different passwords
passwords_to_try = [
    db_password,  # From .env
    'postgres',   # Default
    'admin',      # Common
    'root',       # Common
    '123456',     # Common
    'password',   # Common
    'postgre',    # Variant
]

for pwd in passwords_to_try:
    try:
        print(f"\nTrying password: {'*' * len(pwd)} ({pwd[:3]}...)")
        conn = psycopg.connect(
            dbname='postgres',  # Connect to default postgres database first
            user=db_user,
            password=pwd,
            host=db_host,
            port=db_port
        )
        print(f"✓ SUCCESS! Password is: {pwd}")
        
        # Check if our database exists
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cur.fetchone()
        
        if db_exists:
            print(f"✓ Database '{db_name}' exists")
        else:
            print(f"✗ Database '{db_name}' does NOT exist")
            print(f"  Creating database '{db_name}'...")
            conn.autocommit = True
            cur.execute(f'CREATE DATABASE {db_name}')
            print(f"✓ Database '{db_name}' created successfully")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("CORRECT PASSWORD FOUND!")
        print("=" * 50)
        print(f"\nUpdate your .env file with:")
        print(f"DB_PASSWORD={pwd}")
        break
        
    except psycopg.OperationalError as e:
        print(f"✗ Failed: {e}")
        continue
    except Exception as e:
        print(f"✗ Error: {e}")
        continue
else:
    print("\n" + "=" * 50)
    print("NONE OF THE PASSWORDS WORKED")
    print("=" * 50)
    print("\nYou may need to:")
    print("1. Reset the PostgreSQL password")
    print("2. Check if PostgreSQL is configured for password authentication")
    print("3. Check pg_hba.conf file for authentication method")
