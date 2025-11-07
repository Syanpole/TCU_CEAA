"""
Quick script to check full applications data
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import FullApplication

print("📊 Full Applications in Database:\n")
applications = FullApplication.objects.all().select_related('user')

for app in applications:
    status = "✅ Submitted" if app.is_submitted else "📝 Draft"
    locked = "🔒 Locked" if app.is_locked else "🔓 Unlocked"
    print(f"  {app.id}. {app.user.first_name} {app.user.last_name}")
    print(f"     Student ID: {app.user.student_id}")
    print(f"     School Year: {app.school_year}, Semester: {app.semester}")
    print(f"     Barangay: {app.barangay}")
    print(f"     Status: {status} {locked}")
    print(f"     Created: {app.created_at.strftime('%Y-%m-%d %H:%M')}")
    print()

print(f"Total: {applications.count()} applications")
