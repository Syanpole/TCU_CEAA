#!/usr/bin/env python
"""Test if face_adjudication_views can be imported"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

try:
    from myapp.face_adjudication_views import VerificationAdjudicationViewSet
    print('✅ Face adjudication views import OK')
    print(f'✅ ViewSet class: {VerificationAdjudicationViewSet}')
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
