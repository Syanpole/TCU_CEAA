#!/usr/bin/env python
"""Clear Django cache and force refresh"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.core.cache import cache

# Clear all cache
cache.clear()
print("✅ Django cache cleared")

# Also verify database state one more time
from myapp.models import GradeSubmission, CustomUser

student = CustomUser.objects.get(id=25)
grades = GradeSubmission.objects.filter(student=student, academic_year='2025-2026', semester='1st')

print("\nFinal Database Verification:")
print("=" * 80)
print(f"✅ Student: {student.first_name} {student.last_name}")
print(f"✅ Subjects: {grades.count()}")
print(f"✅ Approved: {grades.filter(status='approved').count()}")
print(f"✅ Pending: {grades.filter(status='pending').count()}")
print()

for grade in grades.order_by('subject_code'):
    print(f"   ✅ {grade.subject_code}: {grade.status.upper()} - {grade.ai_confidence_score:.0%}")

print("\n✅ Ready for frontend refresh")
