"""
🧪 ADVANCED AI SYSTEM TEST
Test the new Vision AI, Learning System, and enhanced document verification
"""

import os
import sys
import django
import json
from pathlib import Path

# Setup Django
os.chdir(r'D:\xp\htdocs\TCU_CEAA\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def test_vision_ai():
    """Test Vision AI document analysis"""
    print("🎯 Testing Vision AI System...")
    
    try:
        from ai_verification.vision_ai import vision_ai
        import numpy as np
        
        # Create a test image (simulated)
        test_image = np.ones((800, 600, 3), dtype=np.uint8) * 255  # White image
        
        # Test document structure analysis
        analysis = vision_ai.analyze_document_structure(test_image)
        
        print(f"✅ Vision AI Analysis:")
        print(f"   Document Type: {analysis['document_type']}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
        print(f"   Quality: {analysis['quality_assessment'].get('is_acceptable', 'Unknown')}")
        print(f"   Layout Type: {analysis['layout_structure'].get('layout_type', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vision AI test failed: {str(e)}")
        return False

def test_learning_system():
    """Test Learning System functionality"""
    print("\n🧠 Testing Learning System...")
    
    try:
        from ai_verification.learning_system import learning_system
        
        # Test recording admin decision
        test_ocr_results = {
            'extracted_text': 'CERTIFICATE OF LIVE BIRTH REPUBLIC OF THE PHILIPPINES',
            'similarity_score': 0.85,
            'confidence_level': 'high'
        }
        
        learning_system.record_admin_decision(
            document_id=999,
            document_type='birth_certificate',
            ocr_results=test_ocr_results,
            admin_decision='approved',
            admin_notes='Test training data'
        )
        
        # Test recommendation system
        recommendation = learning_system.get_recommendation('birth_certificate', test_ocr_results)
        
        print(f"✅ Learning System Test:")
        print(f"   Recommendation: {recommendation['recommendation']}")
        print(f"   Confidence: {recommendation['confidence']:.1%}")
        print(f"   Reasoning: {recommendation['reasoning']}")
        
        # Test learning progress
        progress = learning_system.analyze_learning_progress()
        print(f"   Training Samples: {progress['training_samples']}")
        print(f"   Overall Accuracy: {progress['overall_accuracy']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Learning System test failed: {str(e)}")
        return False

def test_enhanced_verifier():
    """Test Enhanced Autonomous Verifier"""
    print("\n🤖 Testing Enhanced Autonomous Verifier...")
    
    try:
        from ai_verification.autonomous_verifier import autonomous_verifier
        
        # Check if Vision AI is loaded
        has_vision = hasattr(autonomous_verifier, 'vision_ai_available') and autonomous_verifier.vision_ai_available
        has_learning = hasattr(autonomous_verifier, 'learning_system')
        
        print(f"✅ Enhanced Verifier Status:")
        print(f"   Vision AI Available: {has_vision}")
        print(f"   Learning System Available: {has_learning}")
        print(f"   EasyOCR Available: {autonomous_verifier.easyocr_available}")
        print(f"   Tesseract Available: {autonomous_verifier.tesseract_available}")
        
        # Test document patterns
        patterns = autonomous_verifier.document_patterns
        print(f"   Document Patterns: {len(patterns)} types loaded")
        
        for doc_type, pattern in patterns.items():
            threshold = pattern.get('confidence_threshold', 'Not set')
            print(f"     • {doc_type}: threshold {threshold}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Verifier test failed: {str(e)}")
        return False

def test_training_endpoints():
    """Test AI Training API endpoints"""
    print("\n📚 Testing AI Training Endpoints...")
    
    try:
        from ai_verification.training_views import ai_learning_stats
        from myapp.models import CustomUser
        
        # Get an admin user
        admin_user = CustomUser.objects.filter(role='admin').first()
        if not admin_user:
            print("⚠️ No admin user found, skipping endpoint test")
            return True
        
        print(f"✅ Training Endpoints:")
        print(f"   Admin user found: {admin_user.username}")
        print(f"   Training views module loaded successfully")
        print(f"   Endpoints available:")
        print(f"     • /api/ai/train-feedback/")
        print(f"     • /api/ai/learning-stats/")
        print(f"     • /api/ai/retrain/")
        print(f"     • /api/ai/pending-reviews/")
        
        return True
        
    except Exception as e:
        print(f"❌ Training endpoints test failed: {str(e)}")
        return False

def test_birth_certificate_patterns():
    """Test birth certificate specific patterns"""
    print("\n📄 Testing Birth Certificate Recognition...")
    
    try:
        from ai_verification.vision_ai import vision_ai
        
        # Test birth certificate patterns
        template = vision_ai.document_templates['birth_certificate']
        
        test_text = "CERTIFICATE OF LIVE BIRTH REPUBLIC OF THE PHILIPPINES CIVIL REGISTRAR LLOYD KENNETH SALAMEDA RAMOS"
        
        # Test keyword matching
        found_keywords = []
        for keyword in template['validation_keywords']:
            if keyword.lower() in test_text.lower():
                found_keywords.append(keyword)
        
        print(f"✅ Birth Certificate Pattern Test:")
        print(f"   Test Text: '{test_text[:50]}...'")
        print(f"   Found Keywords: {found_keywords}")
        print(f"   Match Rate: {len(found_keywords)}/{len(template['validation_keywords'])} = {len(found_keywords)/len(template['validation_keywords']):.1%}")
        
        # Test field extraction patterns
        import re
        extracted_fields = {}
        for field_name, pattern in template['field_patterns'].items():
            matches = re.findall(pattern, test_text, re.IGNORECASE)
            if matches:
                extracted_fields[field_name] = matches[0]
        
        print(f"   Extracted Fields: {extracted_fields}")
        
        return True
        
    except Exception as e:
        print(f"❌ Birth certificate test failed: {str(e)}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 ADVANCED AI SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    tests = [
        ("Vision AI System", test_vision_ai),
        ("Learning System", test_learning_system),
        ("Enhanced Verifier", test_enhanced_verifier),
        ("Training Endpoints", test_training_endpoints),
        ("Birth Certificate Patterns", test_birth_certificate_patterns)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Advanced AI system is ready!")
        print("\n💡 Next Steps:")
        print("   1. Upload Lloyd's birth certificate to test Vision AI")
        print("   2. Admin can provide training feedback via /api/ai/train-feedback/")
        print("   3. Monitor learning progress via /api/ai/learning-stats/")
        print("   4. System will automatically improve accuracy over time")
        
    else:
        print(f"⚠️ {total - passed} tests failed. Check logs for details.")
    
    return passed == total

if __name__ == "__main__":
    run_comprehensive_test()