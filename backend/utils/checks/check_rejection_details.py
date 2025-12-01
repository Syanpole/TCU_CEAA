"""
Check audit logs for document rejection details
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import AuditLog, DocumentSubmission
from django.utils import timezone
from datetime import timedelta
import json

print("=" * 80)
print("🔍 AUDIT LOG ANALYSIS - DOCUMENT ID: 5")
print("=" * 80)

# Get document
try:
    doc = DocumentSubmission.objects.get(id=5)
    print(f"\n📄 Document Details:")
    print(f"   ID: {doc.id}")
    print(f"   Student: {doc.student.get_full_name()} ({doc.student.student_id})")
    print(f"   Type: {doc.get_document_type_display()}")
    print(f"   Status: {doc.status}")
    print(f"   Submitted: {doc.submitted_at}")
    print(f"   File: {doc.document_file.name}")
except DocumentSubmission.DoesNotExist:
    print("\n❌ Document ID 5 not found")
    exit()

# Get audit logs related to this document
audit_logs = AuditLog.objects.filter(
    target_model='DocumentSubmission',
    target_object_id=5
).order_by('timestamp')

print(f"\n📊 Found {audit_logs.count()} audit log entries\n")

for log in audit_logs:
    print(f"\n{'=' * 80}")
    print(f"⏰ Timestamp: {log.timestamp}")
    print(f"👤 User: {log.user.username if log.user else 'System'}")
    print(f"🎯 Action: {log.action_type}")
    print(f"📝 Description: {log.action_description}")
    print(f"⚠️ Severity: {log.severity}")
    
    if log.metadata:
        print(f"\n📋 Metadata:")
        metadata = log.metadata
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                pass
        
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                if key == 'verification_result' and isinstance(value, dict):
                    print(f"\n   🤖 Verification Result:")
                    for vkey, vvalue in value.items():
                        print(f"      {vkey}: {vvalue}")
                elif key == 'algorithms_results' and isinstance(value, dict):
                    print(f"\n   🧠 Algorithm Results:")
                    for algo_name, algo_data in value.items():
                        if isinstance(algo_data, dict):
                            print(f"\n      {algo_data.get('name', algo_name)}:")
                            for akey, avalue in algo_data.items():
                                if akey != 'name':
                                    print(f"         {akey}: {avalue}")
                else:
                    print(f"   {key}: {value}")

# Also check for AI analysis logs
print(f"\n\n{'=' * 80}")
print("🤖 AI ANALYSIS LOGS")
print("=" * 80)

ai_logs = AuditLog.objects.filter(
    action_type='ai_analysis',
    target_object_id=5
).order_by('-timestamp')

if ai_logs.exists():
    for log in ai_logs:
        print(f"\n⏰ {log.timestamp}")
        print(f"📝 {log.action_description}")
        
        if log.metadata:
            metadata = log.metadata
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    pass
            
            if isinstance(metadata, dict):
                print(f"\n   AI Analysis Details:")
                for key, value in metadata.items():
                    if key not in ['algorithms_results', 'verification_result']:
                        print(f"   {key}: {value}")
else:
    print("\n❌ No AI analysis logs found")

print("\n" + "=" * 80)
