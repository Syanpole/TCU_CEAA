#!/usr/bin/env python3
"""
Test script to verify PyMuPDF installation and C++ compilation fixes
"""

import sys
import os
import traceback
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_pymupdf_installation():
    """Test PyMuPDF installation and basic functionality"""
    print("Testing PyMuPDF Installation...")
    print("=" * 50)
    
    try:
        import fitz
        print(f"✅ PyMuPDF imported successfully!")
        print(f"   PyMuPDF Version: {fitz.version[0]}")
        print(f"   MuPDF Library Version: {fitz.version[1]}")
        print(f"   PyMuPDF Build Date: {fitz.version[2]}")
        
        # Test basic document creation
        doc = fitz.open()  # Create empty document
        page = doc.new_page()
        page.insert_text((72, 72), "Test text for C++ type verification")
        
        # Test text extraction
        text = page.get_text()
        if "Test text for C++ type verification" in text:
            print("✅ Basic text insertion and extraction working")
        else:
            print("⚠️ Text extraction may have issues")
        
        doc.close()
        print("✅ Document creation and manipulation successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ PyMuPDF import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PyMuPDF functionality test failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False

def test_ai_verification_fallback():
    """Test AI verification with PDF processing fallback"""
    print("\nTesting AI Verification System...")
    print("=" * 50)
    
    try:
        from ai_verification.base_verifier import BaseVerifier, PDF_AVAILABLE, PYMUPDF_AVAILABLE
        
        print(f"PDF_AVAILABLE: {PDF_AVAILABLE}")
        print(f"PYMUPDF_AVAILABLE: {PYMUPDF_AVAILABLE}")
        
        if PYMUPDF_AVAILABLE:
            print("✅ PyMuPDF available for AI verification")
        elif PDF_AVAILABLE:
            print("⚠️ Using PyPDF2 fallback for AI verification")
        else:
            print("❌ No PDF processing libraries available")
            return False
        
        # Test verifier initialization
        verifier = BaseVerifier()
        print("✅ BaseVerifier initialized successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ AI verification import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ AI verification test failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False

def test_django_integration():
    """Test Django integration with fixed dependencies"""
    print("\nTesting Django Integration...")
    print("=" * 50)
    
    try:
        import django
        from django.conf import settings
        
        # Configure Django if not already configured
        if not settings.configured:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
            django.setup()
        
        print(f"✅ Django version: {django.get_version()}")
        
        # Test model imports
        from myapp.models import User, Application
        print("✅ Django models imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Django import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Django integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("PyMuPDF C++ Compilation Fix Verification")
    print("=" * 60)
    
    tests = [
        ("PyMuPDF Installation", test_pymupdf_installation),
        ("AI Verification Fallback", test_ai_verification_fallback),
        ("Django Integration", test_django_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! PyMuPDF C++ compilation issues resolved.")
        return 0
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
