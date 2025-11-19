#!/usr/bin/env python
"""Test the grouped_by_semester endpoint response"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser
from myapp.semester_grouping_service import SemesterGroupingService

# Get all students with grades
students_with_grades = CustomUser.objects.filter(
    gradesubmission__isnull=False,
    role='student'
).distinct()

print(f"✅ Students with grades: {students_with_grades.count()}")

# Test the service for each student
service = SemesterGroupingService()

for student in students_with_grades[:3]:
    print(f"\n📊 Student: {student.first_name} {student.last_name} (ID: {student.id})")
    grouped_data = service.group_student_grades_by_semester(student)
    
    if grouped_data:
        for group in grouped_data:
            print(f"   - {group['semester_label']}: {len(group['subjects'])} subjects, GWA: {group['gwa']}")
    else:
        print(f"   - No grouped data")

# Now test what the admin endpoint would return
print(f"\n🔄 Testing admin endpoint response format:")
grouped_all = service.get_grouped_grades_for_admin()
print(f"   Total students in result: {len(grouped_all)}")

# Build response like the endpoint does
response_data = []
for student_id, groups in grouped_all.items():
    try:
        student = CustomUser.objects.get(id=student_id)
        response_data.append({
            'student_id': student_id,
            'student_name': f"{student.first_name} {student.last_name}",
            'semester_groups': groups
        })
    except CustomUser.DoesNotExist:
        pass

print(f"   Response items: {len(response_data)}")
print(f"   First item keys: {list(response_data[0].keys()) if response_data else 'None'}")
if response_data:
    print(f"   First student: {response_data[0]['student_name']}")
    print(f"   Semester groups: {len(response_data[0]['semester_groups'])}")
