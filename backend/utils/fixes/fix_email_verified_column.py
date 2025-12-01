"""
Script to add is_email_verified column to CustomUser table in PostgreSQL
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.db import connection

def add_is_email_verified_column():
    """Add is_email_verified column if it doesn't exist"""
    with connection.cursor() as cursor:
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='myapp_customuser' AND column_name='is_email_verified';
        """)
        
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Column 'is_email_verified' already exists!")
        else:
            print("⚠️ Column 'is_email_verified' is missing. Adding it now...")
            
            # Add the column with default value False
            cursor.execute("""
                ALTER TABLE myapp_customuser 
                ADD COLUMN is_email_verified BOOLEAN DEFAULT FALSE NOT NULL;
            """)
            
            print("✅ Successfully added 'is_email_verified' column!")
            
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name='myapp_customuser' AND column_name='is_email_verified';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"\n📋 Column details:")
            print(f"   Name: {result[0]}")
            print(f"   Type: {result[1]}")
            print(f"   Default: {result[2]}")
        
        # Show all columns in the table
        print("\n📊 All columns in myapp_customuser table:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='myapp_customuser'
            ORDER BY ordinal_position;
        """)
        
        for row in cursor.fetchall():
            print(f"   - {row[0]} ({row[1]})")

if __name__ == '__main__':
    print("🔧 Fixing is_email_verified column in PostgreSQL...\n")
    add_is_email_verified_column()
    print("\n✅ Done! You can now login as a student.")
