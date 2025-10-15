import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import GradeSubmission

g = GradeSubmission.objects.get(id=6)
print(f'Grade ID: {g.id}')
print(f'Status: {g.status}')
print(f'Confidence: {g.ai_confidence_score}')
print(f'Reviewed: {g.reviewed_at}')
print(f'\n=== ADMIN NOTES ===')
print(g.admin_notes if g.admin_notes else 'None')
print(f'\n=== AI EVALUATION NOTES ===')
print(g.ai_evaluation_notes if g.ai_evaluation_notes else 'None')
