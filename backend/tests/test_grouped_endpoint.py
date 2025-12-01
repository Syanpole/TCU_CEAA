#!/usr/bin/env python
"""Test the grouped_by_semester endpoint"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.semester_grouping_service import SemesterGroupingService

student = CustomUser.objects.get(id=25)

# Test the service
service = SemesterGroupingService()
grouped_data = service.group_student_grades_by_semester(student)

print("✅ Grouped Data Response:")
print("=" * 80)
print(json.dumps(grouped_data, indent=2, default=str))
