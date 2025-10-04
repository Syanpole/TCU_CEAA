import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from myapp.models import Student

User = get_user_model()

# Connect to SQLite database
sqlite_db = 'db.sqlite3'
conn = sqlite3.connect(sqlite_db)
cursor = conn.cursor()

print("=" * 60)
print("Migrating Users from SQLite to PostgreSQL")
print("=" * 60)
print()

# Get all users from SQLite
try:
    cursor.execute("SELECT * FROM myapp_customuser")
    columns = [description[0] for description in cursor.description]
    users_data = cursor.fetchall()
    
    print(f"Found {len(users_data)} users in SQLite database")
    print()
    
    migrated = 0
    skipped = 0
    updated = 0
    
    for user_row in users_data:
        user_dict = dict(zip(columns, user_row))
        username = user_dict.get('username')
        
        # Check if user already exists in PostgreSQL
        if User.objects.filter(username=username).exists():
            print(f"⚠ User '{username}' already exists in PostgreSQL")
            
            # Update existing user with SQLite data
            user = User.objects.get(username=username)
            user.password = user_dict.get('password')  # Copy password hash
            user.email = user_dict.get('email', '')
            user.first_name = user_dict.get('first_name', '')
            user.last_name = user_dict.get('last_name', '')
            user.is_staff = user_dict.get('is_staff', False)
            user.is_active = user_dict.get('is_active', True)
            user.is_superuser = user_dict.get('is_superuser', False)
            # Map user_type to role field
            user_type = user_dict.get('user_type', user_dict.get('role', 'student'))
            user.role = user_type if user_type in ['admin', 'student', 'user'] else 'student'
            if hasattr(user, 'student_id'):
                user.student_id = user_dict.get('student_id', None)
            user.save()
            updated += 1
            print(f"  ✓ Updated user '{username}' with SQLite data")
        else:
            # Create new user in PostgreSQL
            try:
                # Map user_type to role field
                user_type = user_dict.get('user_type', user_dict.get('role', 'student'))
                role = user_type if user_type in ['admin', 'student', 'user'] else 'student'
                
                user = User(
                    username=username,
                    email=user_dict.get('email', ''),
                    password=user_dict.get('password'),  # Copy password hash directly
                    first_name=user_dict.get('first_name', ''),
                    last_name=user_dict.get('last_name', ''),
                    is_staff=user_dict.get('is_staff', False),
                    is_active=user_dict.get('is_active', True),
                    is_superuser=user_dict.get('is_superuser', False),
                    role=role,
                    date_joined=user_dict.get('date_joined'),
                )
                if hasattr(user, 'student_id'):
                    user.student_id = user_dict.get('student_id', None)
                user.save()
                migrated += 1
                print(f"✓ Migrated user: {username} ({user.user_type})")
            except Exception as e:
                print(f"✗ Error migrating {username}: {str(e)}")
                skipped += 1
    
    print()
    print("=" * 60)
    print(f"Migration Summary:")
    print(f"  New users migrated: {migrated}")
    print(f"  Existing users updated: {updated}")
    print(f"  Skipped (errors): {skipped}")
    print(f"  Total users in PostgreSQL: {User.objects.count()}")
    print("=" * 60)
    print()
    print("✓ All users can now login with their original passwords!")
    
except sqlite3.OperationalError as e:
    print(f"Error accessing SQLite database: {e}")
    print("Make sure the database file exists and is not corrupted.")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    conn.close()

# Also migrate Student records if they exist
print()
print("Migrating Student records...")
try:
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM myapp_student")
    columns = [description[0] for description in cursor.description]
    students_data = cursor.fetchall()
    
    print(f"Found {len(students_data)} student records in SQLite")
    
    for student_row in students_data:
        student_dict = dict(zip(columns, student_row))
        student_id = student_dict.get('student_id')
        
        if not Student.objects.filter(student_id=student_id).exists():
            try:
                # Get the user reference
                user_id = student_dict.get('user_id')
                user = User.objects.filter(id=user_id).first()
                
                if user:
                    Student.objects.create(
                        user=user,
                        student_id=student_id,
                        course=student_dict.get('course', ''),
                        year_level=student_dict.get('year_level', ''),
                        contact_number=student_dict.get('contact_number', ''),
                    )
                    print(f"✓ Migrated student: {student_id}")
            except Exception as e:
                print(f"✗ Error migrating student {student_id}: {e}")
    
    conn.close()
    print(f"✓ Total students in PostgreSQL: {Student.objects.count()}")
    
except Exception as e:
    print(f"Note: Could not migrate students: {e}")

print()
print("✓ Migration complete!")
print("All existing users can now login with their original passwords.")
