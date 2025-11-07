import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import FullApplication

apps = FullApplication.objects.all().order_by('-created_at')
print(f'Total applications: {apps.count()}\n')

for app in apps:
    print(f'ID: {app.id}')
    print(f'User: {app.user.username} ({app.user.student_id})')
    print(f'Name: {app.first_name} {app.last_name}')
    print(f'Is Submitted: {app.is_submitted}')
    print(f'Is Locked: {app.is_locked}')
    print(f'Submitted At: {app.submitted_at}')
    print(f'Created At: {app.created_at}')
    print('-' * 50)
