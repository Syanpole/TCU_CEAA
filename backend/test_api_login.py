"""
API Login Test - Manual Test Script
This is NOT a Django test case - it's a manual testing script for running server.
Rename to avoid Django test discovery.
"""
try:
    import requests
except ImportError:
    print("❌ 'requests' module not installed. Install it with: pip install requests")
    exit(1)

import json

def run_manual_test():
    """Manual test function - only runs when script is executed directly"""
    print("=" * 60)
    print("Testing API Login Endpoint")
    print("=" * 60)
    print()

    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/api/auth/login/"

    # Test admin login
    print("1. Testing ADMIN login:")
    print(f"   URL: {login_url}")
    print(f"   Username: admin")
    print(f"   Password: admin@123")
    print()

    try:
        response = requests.post(login_url, json={
            "username": "admin",
            "password": "admin@123"
        })
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("   ✓ ADMIN LOGIN SUCCESSFUL!")
            token = response.json().get('token')
            print(f"   Token: {token[:20]}...")
    else:
        print("   ✗ ADMIN LOGIN FAILED!")
        
except requests.exceptions.ConnectionError:
    print("   ✗ ERROR: Cannot connect to Django server!")
    print("   Make sure server is running: python manage.py runserver")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print()
print("-" * 60)
print()

# Test student login
print("2. Testing STUDENT login:")
print(f"   URL: {login_url}")
print(f"   Username: kyoti")
print(f"   Password: student@123")
print()

try:
    response = requests.post(login_url, json={
        "username": "kyoti",
        "password": "student@123"
    })
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("   ✓ STUDENT LOGIN SUCCESSFUL!")
    else:
        print("   ✗ STUDENT LOGIN FAILED!")
        
except requests.exceptions.ConnectionError:
    print("   ✗ ERROR: Cannot connect to Django server!")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print()
print("=" * 60)
print("Test Complete")
print("=" * 60)
