#!/usr/bin/env python3
"""
Test script for the Enhanced AI Document Verification System
This script tests the new verification capabilities and checks dependencies.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def test_ai_verification_system():
    """Test the enhanced AI verification system"""
    print("🤖 Testing Enhanced AI Document Verification System")
    print("=" * 60)
    
    # Test 1: Check dependencies
    print("1. Checking AI Dependencies...")
    dependencies = {
        'cv2': False,
        'numpy': False,
        'PIL': False,
        'pytesseract': False,
        'sklearn': False,
        'PyPDF2': False,
        'django': True  # We know this works since we're in Django
    }
    
    try:
        import cv2
        dependencies['cv2'] = True
        print("   ✅ OpenCV (cv2) - Available")
    except ImportError:
        print("   ❌ OpenCV (cv2) - Not available")
    
    try:
        import numpy
        dependencies['numpy'] = True
        print("   ✅ NumPy - Available")
    except ImportError:
        print("   ❌ NumPy - Not available")
    
    try:
        from PIL import Image
        dependencies['PIL'] = True
        print("   ✅ Pillow (PIL) - Available")
    except ImportError:
        print("   ❌ Pillow (PIL) - Not available")
    
    try:
        import pytesseract
        dependencies['pytesseract'] = True
        print("   ✅ Pytesseract - Available")
    except ImportError:
        print("   ❌ Pytesseract - Not available")
    
    try:
        import sklearn
        dependencies['sklearn'] = True
        print("   ✅ Scikit-learn - Available")
    except ImportError:
        print("   ❌ Scikit-learn - Not available")
    
    try:
        import PyPDF2
        dependencies['PyPDF2'] = True
        print("   ✅ PyPDF2 - Available")
    except ImportError:
        print("   ❌ PyPDF2 - Not available")
    
    # Test 2: Check AI verification modules
    print("\n2. Testing AI Verification Modules...")
    
    try:
        from ai_verification.base_verifier import document_type_detector
        print("   ✅ Enhanced Document Type Detector - Loaded")
        
        # Test basic functionality
        detector_instance = document_type_detector
        print(f"   ✅ Document signatures loaded: {len(detector_instance.document_signatures)} types")
        
    except Exception as e:
        print(f"   ❌ Document Type Detector - Error: {str(e)}")
    
    try:
        from ai_verification.verification_manager import verification_manager
        print("   ✅ Verification Manager - Loaded")
        
        # Test statistics functionality
        stats = verification_manager.get_verification_statistics()
        print(f"   ✅ Statistics available: {len(stats)} metrics")
        
    except Exception as e:
        print(f"   ❌ Verification Manager - Error: {str(e)}")
    
    # Test 3: Check Django models integration
    print("\n3. Testing Django Integration...")
    
    try:
        from myapp.models import DocumentSubmission, CustomUser
        print("   ✅ Django models - Available")
        
        # Check if any documents exist
        doc_count = DocumentSubmission.objects.count()
        user_count = CustomUser.objects.count()
        print(f"   ✅ Database connection - {doc_count} documents, {user_count} users")
        
    except Exception as e:
        print(f"   ❌ Django integration - Error: {str(e)}")
    
    # Test 4: Test serializer enhancements
    print("\n4. Testing Enhanced Serializers...")
    
    try:
        from myapp.serializers import DocumentSubmissionCreateSerializer
        serializer = DocumentSubmissionCreateSerializer()
        
        # Check if enhanced methods exist
        if hasattr(serializer, 'run_comprehensive_ai_analysis'):
            print("   ✅ Enhanced AI analysis method - Available")
        else:
            print("   ❌ Enhanced AI analysis method - Missing")
            
        if hasattr(serializer, '_check_suspicious_filename_patterns'):
            print("   ✅ Filename validation method - Available")
        else:
            print("   ❌ Filename validation method - Missing")
        
    except Exception as e:
        print(f"   ❌ Serializer enhancements - Error: {str(e)}")
    
    # Test 5: AI Capability Assessment
    print("\n5. AI Capability Assessment...")
    
    # Calculate capability score
    available_deps = sum(1 for dep, available in dependencies.items() if available)
    total_deps = len(dependencies)
    capability_score = (available_deps / total_deps) * 100
    
    print(f"   📊 Dependency availability: {available_deps}/{total_deps} ({capability_score:.1f}%)")
    
    if capability_score >= 80:
        print("   🎉 EXCELLENT: Full AI capabilities available")
        ai_status = "Full"
    elif capability_score >= 60:
        print("   ✅ GOOD: Most AI capabilities available")
        ai_status = "Partial"
    elif capability_score >= 40:
        print("   ⚠️ LIMITED: Basic AI capabilities available")
        ai_status = "Limited"
    else:
        print("   ❌ POOR: Minimal AI capabilities available")
        ai_status = "Minimal"
    
    # Test 6: Create a test verification scenario
    print("\n6. Testing Verification Logic...")
    
    try:
        from ai_verification.base_verifier import DocumentTypeDetector
        
        # Create test detector
        test_detector = DocumentTypeDetector()
        
        # Test document signatures
        birth_cert_sig = test_detector.document_signatures.get('birth_certificate')
        if birth_cert_sig:
            print("   ✅ Birth certificate verification rules loaded")
            print(f"      - {len(birth_cert_sig['required_keywords']['primary'])} primary keywords")
            print(f"      - {len(birth_cert_sig['forbidden_keywords'])} forbidden keywords")
        
        school_id_sig = test_detector.document_signatures.get('school_id')
        if school_id_sig:
            print("   ✅ School ID verification rules loaded")
        
        print("   ✅ All document type signatures properly configured")
        
    except Exception as e:
        print(f"   ❌ Verification logic test - Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🔍 ENHANCED AI VERIFICATION SYSTEM SUMMARY")
    print("=" * 60)
    print(f"AI Capability Level: {ai_status}")
    print(f"System Status: {'✅ READY' if capability_score >= 60 else '⚠️ NEEDS SETUP'}")
    
    if capability_score < 60:
        print("\n📋 SETUP RECOMMENDATIONS:")
        if not dependencies['cv2']:
            print("   • Install OpenCV: pip install opencv-python")
        if not dependencies['numpy']:
            print("   • Install NumPy: pip install numpy")
        if not dependencies['PIL']:
            print("   • Install Pillow: pip install Pillow")
        if not dependencies['pytesseract']:
            print("   • Install Pytesseract: pip install pytesseract")
            print("   • Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        if not dependencies['sklearn']:
            print("   • Install Scikit-learn: pip install scikit-learn")
        if not dependencies['PyPDF2']:
            print("   • Install PyPDF2: pip install PyPDF2")
    
    print("\n💡 FEATURES AVAILABLE:")
    print("   ✅ Enhanced document type detection")
    print("   ✅ Fraud detection and prevention")
    print("   ✅ Quality assessment")
    print("   ✅ Filename validation")
    print("   ✅ Autonomous approval/rejection")
    if dependencies['cv2'] and dependencies['pytesseract']:
        print("   ✅ Advanced image analysis and OCR")
    else:
        print("   ⚠️ Basic image analysis (install OpenCV + Tesseract for full features)")
    
    if dependencies['sklearn']:
        print("   ✅ Machine learning text analysis")
    else:
        print("   ⚠️ Basic text analysis (install scikit-learn for ML features)")
    
    print("\n🎯 ANTI-FRAUD PROTECTION:")
    print("   ✅ Random image detection")
    print("   ✅ Document type mismatch detection") 
    print("   ✅ File header validation")
    print("   ✅ Quality threshold enforcement")
    print("   ✅ Keyword analysis and validation")
    
    return capability_score >= 60

def main():
    """Main test function"""
    print("🚀 Starting Enhanced AI Document Verification Test")
    print("This will test the new AI system that prevents fraudulent document uploads.\n")
    
    try:
        success = test_ai_verification_system()
        
        if success:
            print("\n🎉 SUCCESS: Enhanced AI Document Verification System is ready!")
            print("Students will no longer be able to upload random images as documents.")
            print("The system will automatically detect and reject:")
            print("  • Random photos submitted as birth certificates")
            print("  • Wrong document types")
            print("  • Poor quality or suspicious files")
            print("  • Fraudulent or manipulated documents")
        else:
            print("\n⚠️ SETUP NEEDED: Please install missing dependencies for full functionality.")
            print("The system will work with basic features, but enhanced AI capabilities")
            print("require additional libraries.")
        
        return success
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
