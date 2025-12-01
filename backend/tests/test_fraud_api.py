"""
Test script for Fraud Management API Endpoints

Tests all fraud management endpoints with authentication.
"""

import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from myapp.models import FraudReport, FraudNotification
from rest_framework.authtoken.models import Token

User = get_user_model()

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def create_test_admin():
    """Create and authenticate admin user"""
    try:
        admin = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin = User.objects.create_user(
            username='admin',
            email='admin@tcu.edu',
            password='admin123',
            role='admin',
            is_staff=True
        )
    
    # Get or create token
    token, _ = Token.objects.get_or_create(user=admin)
    
    return admin, token.key

def test_get_fraud_reports(client, token):
    """Test GET /api/fraud-reports/"""
    print_header("Test: Get Fraud Reports List")
    
    response = client.get(
        '/api/fraud-reports/',
        HTTP_AUTHORIZATION=f'Token {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"   • Total Reports: {data.get('statistics', {}).get('total', 0)}")
        print(f"   • Pending: {data.get('statistics', {}).get('pending', 0)}")
        print(f"   • Critical: {data.get('statistics', {}).get('critical', 0)}")
        print(f"   • Reports Returned: {len(data.get('reports', []))}")
        
        if data.get('reports'):
            report = data['reports'][0]
            print(f"\n   First Report:")
            print(f"   • ID: {report.get('report_id')}")
            print(f"   • Type: {report.get('fraud_type')}")
            print(f"   • Severity: {report.get('severity')}")
            print(f"   • Status: {report.get('status')}")
    else:
        print(f"❌ Failed: {response.content}")

def test_get_fraud_report_detail(client, token, report_id):
    """Test GET /api/fraud-reports/<id>/"""
    print_header("Test: Get Fraud Report Detail")
    
    response = client.get(
        f'/api/fraud-reports/{report_id}/',
        HTTP_AUTHORIZATION=f'Token {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"   • Report ID: {data.get('report_id')}")
        print(f"   • User: {data.get('suspected_user', {}).get('email')}")
        print(f"   • Type: {data.get('fraud_type')}")
        print(f"   • Severity: {data.get('severity')}")
        print(f"   • Status: {data.get('status')}")
        print(f"   • Score: {data.get('face_match_score')}")
        print(f"   • Liveness Passed: {data.get('liveness_verification_passed')}")
        print(f"   • Created: {data.get('created_at')}")
        
        # Show liveness data
        if data.get('liveness_data'):
            print(f"\n   Liveness Checks:")
            liveness = data['liveness_data']
            print(f"   • Color Flash: {liveness.get('colorFlash')}")
            print(f"   • Blink: {liveness.get('blink')}")
            print(f"   • Movement: {liveness.get('movement')}")
    else:
        print(f"❌ Failed: {response.content}")

def test_update_fraud_report(client, token, report_id):
    """Test POST /api/fraud-reports/<id>/update/"""
    print_header("Test: Update Fraud Report")
    
    data = {
        'status': 'investigating',
        'admin_notes': 'Reviewing evidence and user history. Checking for old ID photos that might explain low similarity score.'
    }
    
    response = client.post(
        f'/api/fraud-reports/{report_id}/update/',
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Token {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"   • New Status: {result.get('status')}")
        print(f"   • Notes Added: {len(result.get('admin_notes', ''))} characters")
    else:
        print(f"❌ Failed: {response.content}")

def test_get_fraud_notifications(client, token):
    """Test GET /api/fraud-notifications/"""
    print_header("Test: Get Fraud Notifications")
    
    response = client.get(
        '/api/fraud-notifications/',
        HTTP_AUTHORIZATION=f'Token {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"   • Total Notifications: {len(data.get('notifications', []))}")
        print(f"   • Unread Count: {data.get('unread_count', 0)}")
        
        if data.get('notifications'):
            notif = data['notifications'][0]
            print(f"\n   First Notification:")
            print(f"   • Title: {notif.get('title')}")
            print(f"   • Priority: {notif.get('priority')}")
            print(f"   • Read: {notif.get('is_read')}")
            
            return notif.get('id')
    else:
        print(f"❌ Failed: {response.content}")
    
    return None

def test_mark_notification_read(client, token, notification_id):
    """Test POST /api/fraud-notifications/<id>/mark-read/"""
    if not notification_id:
        print("⏩ Skipping: No notification ID available")
        return
    
    print_header("Test: Mark Notification as Read")
    
    response = client.post(
        f'/api/fraud-notifications/{notification_id}/mark-read/',
        HTTP_AUTHORIZATION=f'Token {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"   • Read Status: {result.get('is_read')}")
        print(f"   • Read At: {result.get('read_at')}")
    else:
        print(f"❌ Failed: {response.content}")

def test_resolve_fraud_report(client, token, report_id):
    """Test POST /api/fraud-reports/<id>/resolve/"""
    print_header("Test: Resolve Fraud Report")
    
    # First, test with 'dismissed' resolution
    data = {
        'resolution': 'dismissed',
        'admin_notes': 'False positive - verified that similarity score of 0.28 was due to very old ID photo (5+ years). User provided updated photo with score of 0.78. Natural aging and weight changes confirmed.'
    }
    
    response = client.post(
        f'/api/fraud-reports/{report_id}/resolve/',
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Token {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"   • Resolution: {data['resolution']}")
        print(f"   • New Status: {result.get('status')}")
        print(f"   • User Reinstated: {result.get('message')}")
    else:
        print(f"❌ Failed: {response.content}")

def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("  FRAUD MANAGEMENT API TEST SUITE")
    print("="*60)
    
    # Create admin and get token
    admin, token = create_test_admin()
    print(f"\n✓ Admin user ready: {admin.username}")
    print(f"✓ Auth token: {token[:20]}...")
    
    # Create test client
    client = Client()
    
    # Get a fraud report to test with
    fraud_report = FraudReport.objects.first()
    if not fraud_report:
        print("\n❌ No fraud reports found. Run test_fraud_detection.py first.")
        return
    
    report_id = fraud_report.id
    print(f"✓ Using fraud report: {fraud_report.report_id}")
    
    # Run tests
    test_get_fraud_reports(client, token)
    test_get_fraud_report_detail(client, token, report_id)
    test_update_fraud_report(client, token, report_id)
    notification_id = test_get_fraud_notifications(client, token)
    test_mark_notification_read(client, token, notification_id)
    test_resolve_fraud_report(client, token, report_id)
    
    print_header("TEST SUMMARY")
    print("✅ Get Fraud Reports: Tested")
    print("✅ Get Report Detail: Tested")
    print("✅ Update Report: Tested")
    print("✅ Get Notifications: Tested")
    print("✅ Mark Notification Read: Tested")
    print("✅ Resolve Fraud Report: Tested")
    print("\n✨ All API tests completed!\n")

if __name__ == "__main__":
    main()
