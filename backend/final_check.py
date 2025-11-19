#!/usr/bin/env python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()
from myapp.models import GradeSubmission, CustomUser
student = CustomUser.objects.get(id=25)
grades = GradeSubmission.objects.filter(student=student, academic_year='2025-2026', semester='1st')
print('FINAL DASHBOARD DATA')
print('=' * 60)
print(f'Total: {grades.count()} | Approved: {grades.filter(status="approved").count()} | Pending: {grades.filter(status="pending").count()}')
for g in grades.order_by('subject_code'):
    print(f'{g.subject_code:12} {g.status:10} {g.ai_confidence_score*100:5.0f}%')
