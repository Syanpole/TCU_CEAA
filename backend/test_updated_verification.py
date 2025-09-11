#!/usr/bin/env python3
"""
Test the updated (more lenient) verification system
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from ai_verification.base_verifier import DocumentTypeDetector
from ai_verification.verification_manager import DocumentVerificationManager
from PIL import Image
import tempfile
import json

def create_test_image():
    """Create a simple test image"""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Create a simple white image
        img = Image.new('RGB', (800, 600), 'white')
        img.save(f.name, 'JPEG')
        return f.name

def test_verification_leniency():
    """Test that the verification system is now more lenient"""
    print("🧪 Testing Updated (More Lenient) Verification System")
    print("=" * 60)
    
    # Create test image
    test_image_path = create_test_image()
    
    try:
        # Initialize verifier
        detector = DocumentTypeDetector()
        manager = DocumentVerificationManager()
        
        # Test with various document types
        test_types = ['birth_certificate', 'school_id', 'grades', 'voters_certificate']
        
        for doc_type in test_types:
            print(f"\n📄 Testing {doc_type}:")
            
            # Run verification
            result = detector.verify_document_type(test_image_path, doc_type)
            decision = manager.autonomous_verification(test_image_path, doc_type)
            
            print(f"   Confidence: {result.get('confidence_score', 0.0):.2f}")
            print(f"   Fraud Risk: {result.get('fraud_risk_score', 1.0):.2f}")
            print(f"   Quality OK: {result.get('is_acceptable_quality', False)}")
            print(f"   Type Match: {result.get('document_type_match', False)}")
            print(f"   Decision: {decision.get('recommendation', 'unknown')}")
            print(f"   Final Confidence: {decision.get('final_confidence', 0.0):.2f}")
            print(f"   Reasoning: {', '.join(decision.get('decision_reasoning', []))}")
            
            # Check if more lenient
            if decision.get('recommendation') in ['auto_approve', 'manual_review']:
                print(f"   ✅ IMPROVED: Now more lenient!")
            else:
                print(f"   ❌ Still rejecting")
    
    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

def test_fraud_detection_still_works():
    """Test that fraud detection still works for obvious fraud"""
    print("\n🛡️ Testing Fraud Detection Still Works")
    print("=" * 60)
    
    # Test with obviously wrong content
    test_image_path = create_test_image()
    
    try:
        detector = DocumentTypeDetector()
        manager = DocumentVerificationManager()
        
        # Force high fraud risk by simulating bad content
        # Test with obviously wrong content
        result = detector.verify_document_type(test_image_path, 'birth_certificate')
        
        # Manually set high fraud risk to test fraud detection
        result['fraud_risk_score'] = 0.9  # Very high fraud
        result['confidence_score'] = 0.05  # Very low confidence
        
        decision = detector._make_final_decision(result, 'birth_certificate')
        
        print(f"High Fraud Test:")
        print(f"   Fraud Risk: {result['fraud_risk_score']:.2f}")
        print(f"   Confidence: {result['confidence_score']:.2f}")
        print(f"   Decision: {decision.get('recommendation', 'unknown')}")
        
        if decision.get('recommendation') == 'reject':
            print("   ✅ GOOD: Still rejects obvious fraud!")
        else:
            print("   ⚠️ WARNING: May be too lenient for fraud")
            
    finally:
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

if __name__ == '__main__':
    test_verification_leniency()
    test_fraud_detection_still_works()
    print("\n🎯 Test Complete!")
