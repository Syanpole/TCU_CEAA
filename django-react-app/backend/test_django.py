#!/usr/bin/env python
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)

try:
    import django
    print("Django version:", django.get_version())
except ImportError as e:
    print("Django import error:", e)

try:
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
    print("Environment variable set")
    
    django.setup()
    print("Django setup completed successfully!")
    
    from django.core.management import execute_from_command_line
    print("Django management module imported successfully!")
    
except Exception as e:
    print("Error during Django setup:", e)
    import traceback
    traceback.print_exc()
