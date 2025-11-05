#!/usr/bin/env python
"""
Check database tables related to email verification
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Get all tables with 'email' in the name
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname='public' AND tablename LIKE '%email%' 
        ORDER BY tablename
    """)
    tables = cursor.fetchall()
    
    print("=" * 60)
    print("Email-related tables in database:")
    print("=" * 60)
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check columns in myapp_customuser related to email
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'myapp_customuser'
        AND (column_name LIKE '%email%' OR column_name LIKE '%verified%')
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    
    print("\n" + "=" * 60)
    print("Email/verification columns in myapp_customuser:")
    print("=" * 60)
    for col_name, data_type, is_nullable in columns:
        nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
        print(f"  - {col_name}: {data_type} ({nullable})")
    
    print("\n" + "=" * 60)
    print("✅ Database check completed!")
    print("=" * 60)
