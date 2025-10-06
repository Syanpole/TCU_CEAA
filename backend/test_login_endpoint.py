#!/usr/bin/env python
"""
Test the actual login API endpoint to simulate frontend request
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

import json
from django.test import RequestFactory
from myapp.views import login_view
from rest_framework.test import force_authenticate

def test_login_endpoint():
    print("=" * 60)
    print("🧪 TESTING LOGIN API ENDPOINT")
    print("=" * 60)
    
    factory = RequestFactory()
    
    # Test 1: salagubang with password
    print("\n📝 Test 1: Login as salagubang")
    print("-" * 60)
    
    request = factory.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'salagubang', 'password': 'password'}),
        content_type='application/json'
    )
    
    response = login_view(request)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2)}")
    
    # Test 2: admin with password
    print("\n📝 Test 2: Login as admin")
    print("-" * 60)
    
    request = factory.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'admin', 'password': 'password'}),
        content_type='application/json'
    )
    
    response = login_view(request)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2)}")
    
    # Test 3: Wrong password
    print("\n📝 Test 3: Wrong password")
    print("-" * 60)
    
    request = factory.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'salagubang', 'password': 'wrongpassword'}),
        content_type='application/json'
    )
    
    response = login_view(request)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2)}")
    
    print("\n" + "=" * 60)
    print("✅ ENDPOINT TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_login_endpoint()
