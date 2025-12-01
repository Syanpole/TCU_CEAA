"""
Test script to check Face Adjudication Dashboard endpoint
Run this to verify the backend endpoint is working
"""

import requests
import json

# Test the dashboard endpoint
url = "http://127.0.0.1:8000/api/admin/face-adjudications/dashboard/"

try:
    # You'll need to be authenticated - this test assumes you're logged in
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Dashboard endpoint is working!")
        data = response.json()
        if 'stats' in data:
            print(f"\nStats found:")
            print(f"  - Pending: {data['stats'].get('total_pending', 0)}")
            print(f"  - Completed: {data['stats'].get('total_completed', 0)}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend server")
    print("   Make sure Django server is running at http://127.0.0.1:8000")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "="*50)
print("If you see authentication errors, the endpoint exists but requires login.")
print("If you see 404, the URL routing may need to be checked.")
print("If you see 500, there's a server error in the view.")
