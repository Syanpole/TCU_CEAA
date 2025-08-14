import requests
import json

print("Starting login API test...")

# Test login endpoint
url = "http://127.0.0.1:8000/api/auth/login/"
data = {
    "username": "admin",
    "password": "admin123"
}

print(f"Testing URL: {url}")
print(f"Data: {data}")

try:
    print("Sending request...")
    response = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login successful!")
        print(f"Token: {result.get('token')}")
        print(f"User: {result.get('user')}")
    else:
        print("❌ Login failed!")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: {e}")
    print("Make sure Django server is running on http://127.0.0.1:8000/")
except Exception as e:
    print(f"❌ Error: {e}")

print("Test completed.")
