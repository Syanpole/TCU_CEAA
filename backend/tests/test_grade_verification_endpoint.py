"""
Test script for the new grade submission identity verification endpoint.
This simulates the frontend calling the API.
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/face-verification/grade-submission/"

# Test data
TEST_USER = {
    "username": "test_student",
    "password": "testpass123"
}

LIVENESS_DATA = {
    "colorFlash": {"passed": True, "results": [
        {"color": "#FF0000", "detected": True},
        {"color": "#00FF00", "detected": True},
        {"color": "#0000FF", "detected": True}
    ]},
    "blink": {"passed": True, "frames": 5},
    "movement": {"passed": True}
}


def login_user():
    """Login and get authentication token"""
    login_url = f"{BASE_URL}/api/auth/login/"
    response = requests.post(login_url, json=TEST_USER)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful for user: {data.get('username')}")
        return data.get('token')
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_endpoint_without_auth():
    """Test that endpoint requires authentication"""
    print("\n🔒 Testing authentication requirement...")
    
    response = requests.post(API_URL)
    
    if response.status_code == 401:
        print("✅ Endpoint correctly requires authentication (401)")
        return True
    else:
        print(f"❌ Expected 401, got {response.status_code}")
        return False


def test_endpoint_missing_photo(token):
    """Test validation when photo is missing"""
    print("\n📸 Testing missing photo validation...")
    
    headers = {"Authorization": f"Token {token}"}
    data = {
        "liveness_data": json.dumps(LIVENESS_DATA),
        "grade_submission_id": "1"
    }
    
    response = requests.post(API_URL, headers=headers, data=data)
    
    if response.status_code == 400:
        error = response.json()
        if "photo" in error.get("error", "").lower():
            print(f"✅ Correctly validates missing photo: {error.get('error')}")
            return True
    
    print(f"❌ Expected 400 with photo error, got {response.status_code}: {response.text}")
    return False


def test_endpoint_missing_liveness(token):
    """Test validation when liveness data is missing"""
    print("\n🎭 Testing missing liveness data validation...")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Create a minimal test image
    test_image_path = Path("test_selfie.jpg")
    if not test_image_path.exists():
        # Create a 1x1 black pixel image for testing
        from PIL import Image
        img = Image.new('RGB', (1, 1), color='black')
        img.save(test_image_path)
        print("  Created test image")
    
    with open(test_image_path, 'rb') as f:
        files = {"photo": f}
        data = {"grade_submission_id": "1"}
        
        response = requests.post(API_URL, headers=headers, files=files, data=data)
    
    if response.status_code == 400:
        error = response.json()
        if "liveness" in error.get("error", "").lower():
            print(f"✅ Correctly validates missing liveness data: {error.get('error')}")
            return True
    
    print(f"❌ Expected 400 with liveness error, got {response.status_code}: {response.text}")
    return False


def test_endpoint_structure():
    """Test that endpoint is accessible (route exists)"""
    print("\n🌐 Testing endpoint accessibility...")
    
    response = requests.post(API_URL)
    
    # We expect either 401 (auth required) or 400 (validation error)
    # NOT 404 (not found) or 500 (server error)
    if response.status_code in [400, 401]:
        print(f"✅ Endpoint exists and responds (status: {response.status_code})")
        return True
    elif response.status_code == 404:
        print(f"❌ Endpoint not found (404) - check URL routing")
        return False
    else:
        print(f"⚠️ Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return False


def cleanup():
    """Clean up test files"""
    test_image = Path("test_selfie.jpg")
    if test_image.exists():
        test_image.unlink()
        print("\n🧹 Cleaned up test files")


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Testing Grade Submission Identity Verification Endpoint")
    print("=" * 60)
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    # Test 1: Endpoint structure
    results["total"] += 1
    if test_endpoint_structure():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 2: Authentication
    results["total"] += 1
    if test_endpoint_without_auth():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Try to login for authenticated tests
    print("\n🔑 Attempting to login...")
    token = login_user()
    
    if token:
        # Test 3: Missing photo
        results["total"] += 1
        if test_endpoint_missing_photo(token):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 4: Missing liveness data
        results["total"] += 1
        if test_endpoint_missing_liveness(token):
            results["passed"] += 1
        else:
            results["failed"] += 1
    else:
        print("\n⚠️ Skipping authenticated tests (login failed)")
        print("   Note: This is expected if test user doesn't exist")
    
    # Cleanup
    cleanup()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    print("=" * 60)
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {results['failed']} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        cleanup()
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Test script error: {str(e)}")
        import traceback
        traceback.print_exc()
        cleanup()
        exit(1)
