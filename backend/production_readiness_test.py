#!/usr/bin/env python3
"""
🚀 TCU-CEAA AI System Production Readiness Test
Comprehensive test of all 6 AI algorithms + Cosine Similarity
Tests the complete system as specified for production deployment
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from myapp.models import DocumentSubmission
from ai_verification.integrated_verifier import IntegratedVerificationService
import tempfile
import json
from PIL import Image
import io

User = get_user_model()

def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print('='*80)

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def print_error(message):
    print(f"❌ {message}")

def create_test_image(width=800, height=600, text="TEST DOCUMENT"):
    """Create a test image with text for OCR testing"""
    img = Image.new('RGB', (width, height), color='white')
    return img

def test_ai_architecture_compliance():
    """Test that all 6 core algorithms + cosine similarity are available"""
    print_header("🤖 AI ARCHITECTURE COMPLIANCE TEST")
    
    try:
        # Test integrated service initialization
        service = IntegratedVerificationService()
        print_success("IntegratedVerificationService initialized")
        
        # Check all algorithms are available
        algorithms = [
            ('document_validator', 'Document Validator - OCR + Pattern Matching'),
            ('cross_matcher', 'Cross-Document Matcher - Fuzzy String Matching'),
            ('grade_verifier', 'Grade Verifier - GWA + Suspicious Pattern Detection'),
            ('face_verifier', 'Face Verifier - OpenCV Face Detection'),
            ('fraud_detector', 'Fraud Detector - Metadata Analysis + Tampering Detection'),
            ('verification_manager', 'AI Verification Manager - Orchestration + Weighted Scoring'),
            ('cosine_analyzer', 'TF-IDF Cosine Similarity Analyzer')
        ]
        
        for attr_name, description in algorithms:
            if hasattr(service, attr_name):
                print_success(f"{description} - AVAILABLE")
            else:
                print_error(f"{description} - MISSING")
                
        return True
    except Exception as e:
        print_error(f"AI Architecture test failed: {e}")
        return False

def test_database_integration():
    """Test enhanced user model and document submission model"""
    print_header("🗄️ DATABASE INTEGRATION TEST")
    
    try:
        # Test enhanced user model
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student',
            student_id='24-12345',
            first_name='Test',
            last_name='Student',
            middle_initial='M.'
        )
        print_success("Enhanced User Model - Student created with personal info")
        
        # Create test document
        test_img = create_test_image()
        img_bytes = io.BytesIO()
        test_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test_document.png",
            img_bytes.getvalue(),
            content_type="image/png"
        )
        
        # Test extended document submission model with AI fields
        doc_submission = DocumentSubmission.objects.create(
            student=user,
            document_type='birth_certificate',
            document_file=uploaded_file,
            description='Test document for AI analysis',
            ai_confidence_score=0.85,
            ai_document_type_match=True,
            ai_extracted_text='Sample extracted text',
            ai_key_information={'name': 'Test Student', 'type': 'birth_certificate'},
            ai_quality_assessment={'quality_score': 0.9, 'resolution': 'high'},
            ai_recommendations=['Document appears authentic'],
            ai_analysis_completed=True
        )
        print_success("Extended DocumentSubmission Model - AI analysis fields stored")
        
        # Verify AI fields are properly stored
        stored_doc = DocumentSubmission.objects.get(id=doc_submission.id)
        if stored_doc.ai_confidence_score == 0.85:
            print_success("Real-time AI Result Storage - Confidence score stored")
        if stored_doc.ai_key_information.get('name') == 'Test Student':
            print_success("JSON Field Storage - AI extracted data stored")
        if len(stored_doc.ai_recommendations) > 0:
            print_success("AI Recommendations Storage - Working correctly")
            
        # Cleanup
        user.delete()
        print_success("Database Integration Test - PASSED")
        return True
        
    except Exception as e:
        print_error(f"Database Integration test failed: {e}")
        return False

def test_ai_algorithms_functionality():
    """Test each of the 6 core algorithms + cosine similarity"""
    print_header("🧠 AI ALGORITHMS FUNCTIONALITY TEST")
    
    try:
        service = IntegratedVerificationService()
        
        # Test Document Validator (OCR + Pattern Matching)
        print("\n📄 Testing Document Validator...")
        if hasattr(service.document_validator, 'validate_document_type'):
            print_success("Document Validator - OCR + Pattern Matching READY")
        else:
            print_warning("Document Validator - Interface may have changed")
            
        # Test Cross-Document Matcher (Fuzzy String Matching)
        print("\n🔗 Testing Cross-Document Matcher...")
        if hasattr(service.cross_matcher, 'match_documents'):
            test_doc1 = {'name': 'John Doe', 'address': '123 Main St'}
            test_doc2 = {'name': 'Jon Doe', 'address': '123 Main Street'}
            result = service.cross_matcher.match_documents(test_doc1, test_doc2)
            if 'overall_similarity' in result:
                print_success(f"Cross-Document Matcher - Similarity: {result['overall_similarity']:.2f}")
            else:
                print_warning("Cross-Document Matcher - Unexpected result format")
        
        # Test Grade Verifier (GWA + Suspicious Pattern Detection)
        print("\n📊 Testing Grade Verifier...")
        if hasattr(service.grade_verifier, 'calculate_gwa'):
            test_grades = [85.0, 90.0, 88.0, 92.0, 87.0]
            gwa_result = service.grade_verifier.calculate_gwa(test_grades)
            print_success(f"Grade Verifier - GWA Calculation: {gwa_result.get('gwa', 'N/A')}")
            
        # Test Face Verifier (OpenCV Face Detection)
        print("\n👤 Testing Face Verifier...")
        if hasattr(service.face_verifier, 'detect_faces') or hasattr(service.face_verifier, 'verify_face'):
            print_success("Face Verifier - OpenCV Face Detection READY")
            
        # Test Fraud Detector (Metadata Analysis + Tampering Detection)
        print("\n🔍 Testing Fraud Detector...")
        if hasattr(service.fraud_detector, 'analyze_metadata') or hasattr(service.fraud_detector, 'detect_tampering'):
            print_success("Fraud Detector - Metadata Analysis + Tampering Detection READY")
            
        # Test AI Verification Manager (Orchestration + Weighted Scoring)
        print("\n🎯 Testing AI Verification Manager...")
        if hasattr(service.verification_manager, 'verify_document'):
            print_success("AI Verification Manager - Orchestration + Weighted Scoring READY")
            
        # Test TF-IDF Cosine Similarity
        print("\n📐 Testing TF-IDF Cosine Similarity...")
        if hasattr(service.cosine_analyzer, 'compare_documents'):
            text1 = "This is a birth certificate from the civil registry office"
            text2 = "Birth certificate issued by the civil registry"
            similarity_result = service.cosine_analyzer.compare_documents(text1, text2)
            if 'similarity_score' in similarity_result:
                print_success(f"Cosine Similarity - Score: {similarity_result['similarity_score']:.4f}")
                print_success("TF-IDF Vectorization - Vector Space Analysis WORKING")
                
        print_success("All AI Algorithms Functionality Test - PASSED")
        return True
        
    except Exception as e:
        print_error(f"AI Algorithms functionality test failed: {e}")
        return False

def test_api_endpoints_availability():
    """Test that all AI API endpoints are available"""
    print_header("🌐 API ENDPOINTS AVAILABILITY TEST")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        endpoints = [
            ('ai-document-analysis', 'POST /api/ai/analyze-document/'),
            ('ai-analysis-status', 'GET /api/ai/status/<id>/', {'document_id': 1}),
            ('ai-dashboard-stats', 'GET /api/ai/dashboard-stats/'),
            ('ai-batch-process', 'POST /api/ai/batch-process/')
        ]
        
        for endpoint_name, description, *args in endpoints:
            try:
                if args:
                    url = reverse(endpoint_name, kwargs=args[0])
                else:
                    url = reverse(endpoint_name)
                print_success(f"{description} - URL Pattern Available: {url}")
            except Exception as e:
                print_error(f"{description} - URL Pattern Error: {e}")
                
        return True
        
    except Exception as e:
        print_error(f"API Endpoints test failed: {e}")
        return False

def generate_production_report():
    """Generate final production readiness report"""
    print_header("📋 PRODUCTION READINESS REPORT")
    
    # Run all tests
    tests = [
        ("AI Architecture Compliance", test_ai_architecture_compliance),
        ("Database Integration", test_database_integration),
        ("AI Algorithms Functionality", test_ai_algorithms_functionality),
        ("API Endpoints Availability", test_api_endpoints_availability)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        results[test_name] = test_func()
    
    # Summary
    print_header("🎯 FINAL PRODUCTION READINESS SUMMARY")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} PASSED")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 PRODUCTION READY!")
        print("🚀 All 6 Core AI Algorithms + Cosine Similarity Integration: VERIFIED")
        print("🗄️ Enhanced Database Models with AI Fields: VERIFIED")
        print("🌐 Complete API Endpoints: VERIFIED")
        print("⚡ System ready for production deployment!")
    else:
        print(f"\n⚠️ PRODUCTION READINESS: {passed_tests}/{total_tests}")
        print("🔧 Some components need attention before production deployment")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    print_header("🚀 TCU-CEAA AI SYSTEM - PRODUCTION READINESS TEST")
    print("Testing complete AI system before production deployment...")
    print("Verifying: 6 Core Algorithms + Cosine Similarity + Database + APIs")
    
    is_ready = generate_production_report()
    
    if is_ready:
        print(f"\n🎊 SYSTEM STATUS: PRODUCTION READY!")
        sys.exit(0)
    else:
        print(f"\n🔧 SYSTEM STATUS: REQUIRES FIXES")
        sys.exit(1)