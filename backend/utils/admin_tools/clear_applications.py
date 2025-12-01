"""
Clear all existing full applications so we can test fresh
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import FullApplication

print("🗑️  Clearing existing full applications...")
count = FullApplication.objects.all().count()
FullApplication.objects.all().delete()
print(f"✅ Deleted {count} old application(s)")
print("\n💡 Now you can submit a NEW application from the student form and it will save ALL fields!")
