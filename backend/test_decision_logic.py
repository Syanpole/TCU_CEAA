#!/usr/bin/env python3
"""
Simple test to verify the updated (more lenient) verification system
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from ai_verification.base_verifier import DocumentTypeDetector
from PIL import Image
import tempfile

def test_decision_logic():
    """Test the updated decision logic directly"""
    print("🧪 Testing Updated Decision Logic")
    print("=" * 50)
    
    detector = DocumentTypeDetector()
    
    # Test scenarios with different confidence and fraud levels
    test_scenarios = [
        {
            'name': 'Low confidence, low fraud (should approve)',
            'verification_result': {
                'confidence_score': 0.15,
                'fraud_risk_score': 0.2,
                'is_acceptable_quality': True,
                'document_type_match': False
            }
        },
        {
            'name': 'Medium confidence, medium fraud (should approve)',
            'verification_result': {
                'confidence_score': 0.35,
                'fraud_risk_score': 0.4,
                'is_acceptable_quality': True,
                'document_type_match': True
            }
        },
        {
            'name': 'Very high fraud (should reject)',
            'verification_result': {
                'confidence_score': 0.5,
                'fraud_risk_score': 0.85,
                'is_acceptable_quality': True,
                'document_type_match': True
            }
        },
        {
            'name': 'High fraud + very low confidence (should reject)',
            'verification_result': {
                'confidence_score': 0.05,
                'fraud_risk_score': 0.65,
                'is_acceptable_quality': True,
                'document_type_match': False
            }
        },
        {
            'name': 'Poor quality + very low confidence (should manual review)',
            'verification_result': {
                'confidence_score': 0.05,
                'fraud_risk_score': 0.3,
                'is_acceptable_quality': False,
                'document_type_match': False
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}:")
        
        decision = detector._make_final_decision(
            scenario['verification_result'], 
            'birth_certificate'
        )
        
        print(f"   Confidence: {scenario['verification_result']['confidence_score']:.2f}")
        print(f"   Fraud Risk: {scenario['verification_result']['fraud_risk_score']:.2f}")
        print(f"   Quality OK: {scenario['verification_result']['is_acceptable_quality']}")
        print(f"   Type Match: {scenario['verification_result']['document_type_match']}")
        print(f"   → Decision: {decision['recommendation']}")
        print(f"   → Final Confidence: {decision['final_confidence']:.2f}")
        print(f"   → Reasoning: {', '.join(decision['decision_reasoning'])}")
        
        # Check if the decision matches expectation
        if 'should approve' in scenario['name'] and decision['recommendation'] == 'auto_approve':
            print("   ✅ CORRECT: Approved as expected")
        elif 'should reject' in scenario['name'] and decision['recommendation'] == 'reject':
            print("   ✅ CORRECT: Rejected as expected")
        elif 'should manual' in scenario['name'] and decision['recommendation'] == 'manual_review':
            print("   ✅ CORRECT: Manual review as expected")
        else:
            print(f"   ⚠️ UNEXPECTED: Got {decision['recommendation']}")

def test_default_behavior():
    """Test default behavior with minimal scores"""
    print("\n🔧 Testing Default Behavior")
    print("=" * 50)
    
    detector = DocumentTypeDetector()
    
    # Minimal legitimate document scenario
    minimal_result = {
        'confidence_score': 0.1,
        'fraud_risk_score': 0.1,
        'is_acceptable_quality': True,
        'document_type_match': False
    }
    
    decision = detector._make_final_decision(minimal_result, 'birth_certificate')
    
    print(f"Minimal legitimate document:")
    print(f"   Confidence: {minimal_result['confidence_score']:.2f}")
    print(f"   Fraud Risk: {minimal_result['fraud_risk_score']:.2f}")
    print(f"   → Decision: {decision['recommendation']}")
    
    if decision['recommendation'] == 'auto_approve':
        print("   ✅ GOOD: System is now more lenient!")
    else:
        print("   ❌ ISSUE: Still too strict")

if __name__ == '__main__':
    test_decision_logic()
    test_default_behavior()
    print("\n🎯 Decision Logic Test Complete!")
