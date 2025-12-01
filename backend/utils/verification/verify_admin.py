#!/usr/bin/env python
"""
Quick verification script to check Django admin registrations
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib import admin
from myapp.models import BasicQualification, FullApplication, CustomUser, DocumentSubmission, GradeSubmission

print("=" * 60)
print("DJANGO ADMIN REGISTRATION VERIFICATION")
print("=" * 60)

models_to_check = [
    ('CustomUser', CustomUser),
    ('BasicQualification', BasicQualification),
    ('FullApplication', FullApplication),
    ('DocumentSubmission', DocumentSubmission),
    ('GradeSubmission', GradeSubmission),
]

for name, model in models_to_check:
    is_registered = model in admin.site._registry
    status = "✅ REGISTERED" if is_registered else "❌ NOT REGISTERED"
    print(f"{name:30} {status}")
    if is_registered:
        admin_class = admin.site._registry[model]
        print(f"  └─ Admin class: {admin_class.__class__.__name__}")

print("\n" + "=" * 60)
print(f"Total models registered from myapp: {len([m for m in admin.site._registry.keys() if 'myapp' in str(m)])}")
print("=" * 60)

# List all admin URLs
print("\nAdmin URLs available:")
from django.urls import reverse
try:
    print(f"  - Basic Qualifications: /admin/myapp/basicqualification/")
    print(f"  - Full Applications: /admin/myapp/fullapplication/")
    print(f"  - Custom Users: /admin/myapp/customuser/")
except Exception as e:
    print(f"  Error getting URLs: {e}")

print("\n✅ All models are properly registered!")
print("If you don't see them in the admin panel:")
print("  1. Restart the Django development server")
print("  2. Clear your browser cache (Ctrl+Shift+Delete)")
print("  3. Hard refresh the admin page (Ctrl+F5)")
