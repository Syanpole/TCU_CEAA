#!/usr/bin/env python
"""
Script to fix the email_verified_at column issue in the database.
This script checks if the column exists and adds it if it doesn't.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.db import connection

def check_and_fix_columns():
    """Check if email_verified_at column exists and add it if it doesn't"""
    with connection.cursor() as cursor:
        # Check existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'myapp_customuser' 
            ORDER BY ordinal_position
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print("Existing columns in myapp_customuser:")
        for col in existing_columns:
            print(f"  - {col}")
        
        # Check if email_verified_at exists
        if 'email_verified_at' not in existing_columns:
            print("\n❌ email_verified_at column is missing!")
            print("✅ Adding email_verified_at column...")
            
            try:
                cursor.execute("""
                    ALTER TABLE myapp_customuser 
                    ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE NULL
                """)
                print("✅ Successfully added email_verified_at column!")
            except Exception as e:
                print(f"❌ Error adding column: {e}")
                return False
        else:
            print("\n✅ email_verified_at column already exists!")
        
        # Check if is_email_verified exists
        if 'is_email_verified' not in existing_columns:
            print("\n❌ is_email_verified column is missing!")
            print("✅ Adding is_email_verified column...")
            
            try:
                cursor.execute("""
                    ALTER TABLE myapp_customuser 
                    ADD COLUMN is_email_verified BOOLEAN NOT NULL DEFAULT FALSE
                """)
                print("✅ Successfully added is_email_verified column!")
            except Exception as e:
                print(f"❌ Error adding column: {e}")
                return False
        else:
            print("✅ is_email_verified column already exists!")
        
        # Verify the columns are now present
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'myapp_customuser' 
            AND column_name IN ('email_verified_at', 'is_email_verified')
        """)
        final_check = [row[0] for row in cursor.fetchall()]
        
        print("\n📋 Final verification:")
        print(f"  - email_verified_at: {'✅ Present' if 'email_verified_at' in final_check else '❌ Missing'}")
        print(f"  - is_email_verified: {'✅ Present' if 'is_email_verified' in final_check else '❌ Missing'}")
        
        return True

if __name__ == '__main__':
    print("=" * 60)
    print("Fixing email verification columns in database")
    print("=" * 60)
    
    try:
        success = check_and_fix_columns()
        if success:
            print("\n" + "=" * 60)
            print("✅ Database schema fix completed successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Run: python manage.py migrate --fake")
            print("2. Restart your Django development server")
            print("3. Try logging in again")
        else:
            print("\n" + "=" * 60)
            print("❌ Database schema fix failed!")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
