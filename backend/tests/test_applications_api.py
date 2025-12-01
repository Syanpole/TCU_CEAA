#!/usr/bin/env python
"""Test the applications endpoint directly"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import AllowanceApplication, CustomUser
from myapp.serializers import AllowanceApplicationSerializer

try:
    # Test getting all applications
    apps = AllowanceApplication.objects.all()
    print(f"✅ Total applications: {apps.count()}")
    
    # Try to serialize
    serializer = AllowanceApplicationSerializer(apps, many=True)
    print(f"✅ Serialization successful")
    print(f"✅ Data: {len(serializer.data)} records")
    
    for app in serializer.data[:2]:
        print(f"  - App {app.get('id')}: {app.get('status')}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
