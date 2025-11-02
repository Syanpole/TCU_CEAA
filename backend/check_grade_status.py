import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

g = GradeSubmission.objects.latest('id')
print(f'Grade ID: {g.id}')
print(f'Status: {g.status}')
print(f'Confidence: {g.ai_confidence_score}')
print(f'\nAdmin Notes:')
print(g.admin_notes if g.admin_notes else 'None')
print(f'\nAI Evaluation Notes:')
print(g.ai_evaluation_notes if g.ai_evaluation_notes else 'None')
