"""
Test the full-application API endpoint
"""
import requests

# Test the API endpoint
url = "http://localhost:8000/api/full-application/"

print("🧪 Testing Full Application API Endpoint")
print(f"📡 URL: {url}\n")

# You'll need to be authenticated to access this
# For now, let's just test if the endpoint exists
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {len(data)} applications")
        for app in data:
            print(f"   - {app['user']['first_name']} {app['user']['last_name']} ({app['school_year']} {app['semester']})")
    elif response.status_code == 401:
        print("⚠️  Endpoint exists but requires authentication (expected)")
    elif response.status_code == 403:
        print("⚠️  Endpoint exists but access forbidden (expected for non-admin)")
    else:
        print(f"❌ Response: {response.text}")
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to the server. Make sure Django is running on localhost:8000")
except Exception as e:
    print(f"❌ Error: {str(e)}")
