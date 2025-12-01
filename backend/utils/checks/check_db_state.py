#!/usr/bin/env python
"""Check current database state"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission, CustomUser

student = CustomUser.objects.get(id=25)
grades = GradeSubmission.objects.filter(student=student, academic_year='2025-2026', semester='1st')

print('Current Database State:')
print('=' * 80)
print(f'Total Subjects: {grades.count()}')
print(f'Approved: {grades.filter(status="approved").count()}')
print(f'Pending: {grades.filter(status="pending").count()}')
print()
for grade in grades.order_by('subject_code'):
    print(f'{grade.subject_code}: {grade.status.upper()} - {grade.ai_confidence_score:.0%} confidence')
