"""
Test script for COE and ID Verification Admin Features
Tests all new admin endpoints and functionality
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@tcu.edu.ph"
ADMIN_PASSWORD = "admin123"
STUDENT_EMAIL = "student@tcu.edu.ph"
STUDENT_PASSWORD = "student123"

# Test file paths
COE_FILE = Path(__file__).parent / "media" / "documents" / "2025" / "11" / "Certificate_of_Enrollment.jpg"


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)


def print_result(success, message, data=None):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if data and isinstance(data, dict):
        print(f"   Data: {json.dumps(data, indent=2)[:200]}...")


def login(email, password):
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    return None


def test_student_upload():
    """Test student document upload"""
    print_section("Test 1: Student Document Upload")
    
    # Login as student
    token = login(STUDENT_EMAIL, STUDENT_PASSWORD)
    if not token:
        print_result(False, "Student login failed")
        return None
    
    print_result(True, "Student logged in successfully")
    
    # Upload COE document
    headers = {"Authorization": f"Bearer {token}"}
    
    if not COE_FILE.exists():
        print_result(False, f"Test file not found: {COE_FILE}")
        return None
    
    with open(COE_FILE, 'rb') as f:
        files = {'file': f}
        data = {
            'document_type': 'certificate_of_enrollment',
            'description': 'Test COE upload for verification'
        }
        response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code in [200, 201]:
        doc_data = response.json()
        print_result(True, f"Document uploaded successfully (ID: {doc_data.get('id')})")
        return doc_data.get('id')
    else:
        print_result(False, f"Upload failed: {response.status_code} - {response.text}")
        return None


def test_ai_analysis(document_id):
    """Test AI document analysis"""
    print_section("Test 2: AI Document Analysis")
    
    # Login as student
    token = login(STUDENT_EMAIL, STUDENT_PASSWORD)
    if not token:
        print_result(False, "Student login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Trigger AI analysis
    response = requests.post(
        f"{BASE_URL}/api/ai/analyze-document/",
        headers=headers,
        json={"document_id": document_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, "AI analysis completed")
        print(f"   Confidence: {result.get('results', {}).get('overall_analysis', {}).get('overall_confidence', 0):.2%}")
        print(f"   Status: {result.get('document_status')}")
        print(f"   Auto-approved: {result.get('auto_approved')}")
        
        # Check COE verification results
        coe_result = result.get('results', {}).get('algorithms_results', {}).get('coe_verification', {})
        if coe_result:
            print(f"\n   COE Verification:")
            print(f"      Status: {coe_result.get('status')}")
            print(f"      Confidence: {coe_result.get('confidence', 0):.2%}")
            print(f"      Checks Passed: {coe_result.get('checks_passed')}/{coe_result.get('total_checks')}")
        
        return True
    else:
        print_result(False, f"AI analysis failed: {response.status_code} - {response.text}")
        return False


def test_student_check_status(document_id):
    """Test student checking document status"""
    print_section("Test 3: Student Check Document Status")
    
    token = login(STUDENT_EMAIL, STUDENT_PASSWORD)
    if not token:
        print_result(False, "Student login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check status
    response = requests.get(
        f"{BASE_URL}/api/ai/status/{document_id}/",
        headers=headers
    )
    
    if response.status_code == 200:
        status_data = response.json()
        print_result(True, "Status retrieved successfully")
        print(f"   Status: {status_data.get('status')}")
        print(f"   AI Completed: {status_data.get('ai_completed')}")
        print(f"   Confidence: {status_data.get('confidence_score', 0):.2%}")
        print(f"   Auto-approved: {status_data.get('auto_approved')}")
    else:
        print_result(False, f"Status check failed: {response.status_code}")


def test_admin_dashboard():
    """Test admin document dashboard"""
    print_section("Test 4: Admin Document Dashboard")
    
    token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print_result(False, "Admin login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get dashboard data
    response = requests.get(
        f"{BASE_URL}/api/admin/documents/dashboard/",
        headers=headers
    )
    
    if response.status_code == 200:
        dashboard = response.json()
        print_result(True, "Admin dashboard loaded successfully")
        print(f"   Total Documents: {dashboard.get('summary', {}).get('total_documents')}")
        
        ai_stats = dashboard.get('ai_statistics', {})
        print(f"\n   AI Statistics:")
        print(f"      Total Analyzed: {ai_stats.get('total_analyzed')}")
        print(f"      Auto-approved: {ai_stats.get('auto_approved')}")
        print(f"      Avg Confidence: {ai_stats.get('avg_confidence', 0):.2%}")
        
        coe_stats = dashboard.get('coe_statistics', {})
        print(f"\n   COE Statistics:")
        print(f"      Total: {coe_stats.get('total')}")
        print(f"      Valid: {coe_stats.get('valid')}")
        print(f"      Invalid: {coe_stats.get('invalid')}")
        
        id_stats = dashboard.get('id_verification_statistics', {})
        print(f"\n   ID Verification Statistics:")
        print(f"      Total: {id_stats.get('total')}")
        print(f"      Identity Verified: {id_stats.get('identity_verified')}")
        print(f"      Identity Failed: {id_stats.get('identity_failed')}")
        
        print(f"\n   Documents Needing Attention: {len(dashboard.get('attention_needed', []))}")
    else:
        print_result(False, f"Dashboard failed: {response.status_code}")


def test_admin_view_ai_details(document_id):
    """Test admin viewing AI analysis details"""
    print_section("Test 5: Admin View AI Details")
    
    token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print_result(False, "Admin login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get AI details
    response = requests.get(
        f"{BASE_URL}/api/documents/{document_id}/ai_details/",
        headers=headers
    )
    
    if response.status_code == 200:
        details = response.json()
        print_result(True, "AI details retrieved successfully")
        
        student = details.get('student', {})
        print(f"\n   Student: {student.get('name')} ({student.get('student_id')})")
        print(f"   Document: {details.get('document_type_display')}")
        
        ai_analysis = details.get('ai_analysis', {})
        print(f"\n   AI Analysis:")
        print(f"      Confidence: {ai_analysis.get('confidence_score', 0):.2%}")
        print(f"      Auto-approved: {ai_analysis.get('auto_approved')}")
        
        # Show COE verification details
        algorithms = ai_analysis.get('algorithms_results', {})
        if 'coe_verification' in algorithms:
            coe = algorithms['coe_verification']
            print(f"\n   COE Verification:")
            print(f"      Status: {coe.get('status')}")
            print(f"      Valid: {coe.get('is_valid')}")
            print(f"      Checks Passed: {coe.get('checks_passed')}/{coe.get('total_checks')}")
            
            detected = coe.get('detected_elements', {})
            print(f"\n   Detected Elements:")
            for element, data in detected.items():
                if isinstance(data, dict) and data.get('present'):
                    print(f"      ✅ {element}: {data.get('confidence', 0):.2%}")
    else:
        print_result(False, f"AI details failed: {response.status_code}")


def test_admin_review(document_id):
    """Test admin reviewing document"""
    print_section("Test 6: Admin Review Document")
    
    token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print_result(False, "Admin login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Review document
    response = requests.post(
        f"{BASE_URL}/api/documents/{document_id}/review/",
        headers=headers,
        json={
            "status": "approved",
            "admin_notes": "COE verified successfully. All elements detected with high confidence. Approved via admin review."
        }
    )
    
    if response.status_code == 200:
        review_data = response.json()
        print_result(True, "Document reviewed successfully")
        print(f"   Status: {review_data.get('status')}")
        print(f"   Reviewed by: {review_data.get('reviewed_by_name')}")
    else:
        print_result(False, f"Review failed: {response.status_code}")


def test_admin_reanalyze(document_id):
    """Test admin triggering re-analysis"""
    print_section("Test 7: Admin Re-analyze Document")
    
    token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print_result(False, "Admin login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Trigger re-analysis
    response = requests.post(
        f"{BASE_URL}/api/documents/{document_id}/reanalyze/",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, "Re-analysis completed successfully")
        print(f"   New Confidence: {result.get('new_confidence', 0):.2%}")
        print(f"   New Status: {result.get('new_status')}")
    else:
        print_result(False, f"Re-analysis failed: {response.status_code}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " " * 15 + "🎓 COE & ID VERIFICATION SYSTEM - INTEGRATION TEST" + " " * 13 + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print(f"\n📍 Testing against: {BASE_URL}")
    print(f"📁 Test file: {COE_FILE}")
    
    # Test 1: Student uploads document
    document_id = test_student_upload()
    
    if document_id:
        # Test 2: AI analyzes document
        ai_success = test_ai_analysis(document_id)
        
        if ai_success:
            # Test 3: Student checks status
            test_student_check_status(document_id)
            
            # Test 4: Admin views dashboard
            test_admin_dashboard()
            
            # Test 5: Admin views AI details
            test_admin_view_ai_details(document_id)
            
            # Test 6: Admin reviews document
            test_admin_review(document_id)
            
            # Test 7: Admin re-analyzes (optional)
            # test_admin_reanalyze(document_id)
    
    print("\n" + "=" * 80)
    print("✅ Integration tests completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
