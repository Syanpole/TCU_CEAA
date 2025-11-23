from myapp.models import DocumentSubmission

docs = DocumentSubmission.objects.all().order_by('-submitted_at')[:3]
print('Recent documents:')
for d in docs:
    print(f'\nDoc {d.id}: {d.document_type}')
    print(f'Status: {d.status}')
    print(f'AI Completed: {d.ai_analysis_completed}')
    print(f'Confidence: {d.ai_confidence_score}')
    print(f'AI Notes: {d.ai_analysis_notes[:300] if d.ai_analysis_notes else "None"}')
