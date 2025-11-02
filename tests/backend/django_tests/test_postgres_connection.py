"""
Quick PostgreSQL Connection Test
Tests the connection with credentials from .env file
"""
import os
from dotenv import load_dotenv
import psycopg

# Load environment variables
load_dotenv()

DB_NAME = os.getenv('DB_NAME', 'tcu_ceaa_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

print("=" * 60)
print("PostgreSQL Connection Test")
print("=" * 60)
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}")
print(f"Password: {'*' * len(DB_PASSWORD)}")
print(f"Host: {DB_HOST}")
print(f"Port: {DB_PORT}")
print("=" * 60)

try:
    # Try to connect
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("✅ SUCCESS! Connection established successfully!")
    print("Django should work with these credentials.")
    
    # Get PostgreSQL version
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\nPostgreSQL Version: {version[0]}")
    
    cursor.close()
    conn.close()
    
except psycopg.OperationalError as e:
    print("❌ FAILED! Connection failed!")
    print(f"Error: {e}")
    print("\nPossible solutions:")
    print("1. Check if PostgreSQL service is running")
    print("2. Verify the password is correct")
    print("3. Update the .env file with correct credentials")
    print("\nTo reset PostgreSQL password, run:")
    print("   .\\reset_postgres_password.ps1")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("=" * 60)
