import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import FullApplication
from django.utils import timezone

# Find all submitted applications without submitted_at timestamp
apps = FullApplication.objects.filter(is_submitted=True, submitted_at__isnull=True)

print(f'Found {apps.count()} applications that need fixing...\n')

for app in apps:
    # Set submitted_at to created_at (approximate submission time)
    app.submitted_at = app.created_at
    app.save()
    print(f'✅ Fixed application ID {app.id} - {app.user.username}')
    print(f'   Set submitted_at to: {app.submitted_at}')

print(f'\n✅ Fixed {apps.count()} applications!')
