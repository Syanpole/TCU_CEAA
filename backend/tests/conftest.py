"""
Pytest configuration for Django tests
This file is automatically loaded by pytest before any tests are collected.
"""
import os
import sys
import django
from pathlib import Path

# Get the backend directory
backend_dir = Path(__file__).parent.parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

# Setup Django
django.setup()
