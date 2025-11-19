#!/usr/bin/env python
"""Test the exact API response"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser
from myapp.semester_grouping_service import SemesterGroupingService
from rest_framework.response import Response

# Simulate what the endpoint does
grouping_service = SemesterGroupingService()

# Call with no filters (admin request)
grouped_all = grouping_service.get_grouped_grades_for_admin(
    academic_year=None,
    semester=None,
    status=None
)

print(f"✅ Grouped all result type: {type(grouped_all)}")
print(f"✅ Keys: {list(grouped_all.keys())}")

# Convert to list format like the endpoint does
response_data = []
for student_id, groups in grouped_all.items():
    try:
        student = CustomUser.objects.get(id=student_id)
        item = {
            'student_id': student_id,
            'student_name': f"{student.first_name} {student.last_name}",
            'semester_groups': groups
        }
        response_data.append(item)
        print(f"\n✅ Item for student {student_id}:")
        print(f"   - semester_groups count: {len(groups)}")
        if groups:
            print(f"   - First group keys: {list(groups[0].keys())}")
            print(f"   - First group subjects: {len(groups[0].get('subjects', []))}")
            print(f"   - First group GWA: {groups[0].get('gwa')}")
    except CustomUser.DoesNotExist:
        pass

print(f"\n📤 Final Response:")
print(json.dumps(response_data, indent=2, default=str))
