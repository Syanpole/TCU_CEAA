import psycopg
import subprocess
import time

print("=" * 60)
print("PostgreSQL Password Discovery & Reset Tool")
print("=" * 60)

pg_bin = r"C:\Program Files\PostgreSQL\17\bin"

# Method 1: Try to find the working password
print("\n[Method 1] Attempting to find current password...")
passwords_to_try = [
    "postgres123",     # Server password
    "postgre123",      # .env password
    "postgres",        # Default
    "admin",           # Common
    "password",        # Common
    "root",            # Common
    "123456",          # Common
    "",                # Empty password
]

working_password = None
for pwd in passwords_to_try:
    try:
        print(f"  Trying: '{pwd}'...")
        conn = psycopg.connect(
            dbname='postgres',
            user='postgres',
            password=pwd,
            host='127.0.0.1',
            port='5432',
            connect_timeout=3
        )
        print(f"  ✓ SUCCESS! Current password is: '{pwd}'")
        working_password = pwd
        conn.close()
        break
    except psycopg.OperationalError as e:
        if "password authentication failed" in str(e):
            print(f"  ✗ Wrong password")
        else:
            print(f"  ✗ Connection error: {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

if working_password:
    print(f"\n✓ Found working password: '{working_password}'")
    
    # Try to change it to postgre123
    new_password = "postgre123"
    if working_password != new_password:
        print(f"\n[Method 2] Changing password to '{new_password}'...")
        try:
            conn = psycopg.connect(
                dbname='postgres',
                user='postgres',
                password=working_password,
                host='127.0.0.1',
                port='5432'
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"ALTER USER postgres WITH PASSWORD '{new_password}'")
            print(f"✓ Password changed to: '{new_password}'")
            cur.close()
            conn.close()
            
            # Verify new password
            print(f"\n[Verification] Testing new password...")
            conn = psycopg.connect(
                dbname='postgres',
                user='postgres',
                password=new_password,
                host='127.0.0.1',
                port='5432'
            )
            print(f"✓ New password verified!")
            conn.close()
            
        except Exception as e:
            print(f"✗ Failed to change password: {e}")
    else:
        print(f"✓ Password is already set to '{new_password}'")
        
else:
    print("\n✗ Could not find working password with standard attempts")
    print("\n[Method 3] Checking authentication method...")
    
    # Check pg_hba.conf
    pg_hba_path = r"C:\Program Files\PostgreSQL\17\data\pg_hba.conf"
    try:
        with open(pg_hba_path, 'r') as f:
            print(f"\nReading {pg_hba_path}...")
            lines = f.readlines()
            print("\nHost-based authentication rules:")
            for line in lines:
                if line.strip().startswith('host') and not line.strip().startswith('#'):
                    print(f"  {line.strip()}")
    except Exception as e:
        print(f"✗ Cannot read pg_hba.conf: {e}")
        print("  You may need to run this script as Administrator")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
if working_password and working_password == "postgre123":
    print("✓ Password is correctly set to 'postgre123'")
    print("\nFor pgAdmin:")
    print("  1. Completely close pgAdmin")
    print("  2. Delete the server connection")
    print("  3. Create a new server with:")
    print("     - Host: 127.0.0.1")
    print("     - Port: 5432")
    print("     - Username: postgres")
    print("     - Password: postgre123")
    print("     - Database: postgres")
elif working_password:
    print(f"Current password: {working_password}")
    print("Run this script as Administrator to change it")
else:
    print("Run: reset_password_admin.ps1 as Administrator")
    print("This will reset the password properly")

input("\nPress Enter to exit...")
