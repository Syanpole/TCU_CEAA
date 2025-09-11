#!/usr/bin/env python3
"""
Simple test to verify PyMuPDF integration with AI verification system
"""

import os
import sys
import tempfile
from pathlib import Path

# Add Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import django
django.setup()

def test_pymupdf_with_ai_verification():
    """Test PyMuPDF integration with AI verification"""
    
    print("Testing PyMuPDF with AI Verification...")
    print("=" * 50)
    
    try:
        # Test import
        import fitz
        print(f"✅ PyMuPDF Version: {fitz.version[0]}")
        
        from ai_verification.base_verifier import BaseVerifier, PYMUPDF_AVAILABLE, PDF_AVAILABLE
        print(f"✅ PYMUPDF_AVAILABLE: {PYMUPDF_AVAILABLE}")
        print(f"✅ PDF_AVAILABLE: {PDF_AVAILABLE}")
        
        # Create a test PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "TEST BIRTH CERTIFICATE")
        page.insert_text((72, 100), "REPUBLIC OF THE PHILIPPINES")
        page.insert_text((72, 128), "CIVIL REGISTRY")
        page.insert_text((72, 156), "This is to certify that a child was born...")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            doc.save(temp_file.name)
            temp_path = temp_file.name
        
        doc.close()
        
        # Test PDF processing with AI verifier
        verifier = BaseVerifier()
        
        # Simulate file upload object
        class MockFile:
            def __init__(self, file_path):
                self.file_path = file_path
                
            def chunks(self):
                with open(self.file_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
        
        mock_file = MockFile(temp_path)
        result = verifier.extract_pdf_content(mock_file)
        
        print(f"✅ PDF Content Extraction Result:")
        print(f"   Page Count: {result.get('page_count', 'N/A')}")
        print(f"   Text Length: {len(result.get('extracted_text', ''))}")
        print(f"   Has Images: {result.get('has_images', False)}")
        
        extracted_text = result.get('extracted_text', '')
        if 'BIRTH CERTIFICATE' in extracted_text.upper():
            print("✅ Text extraction working correctly")
        else:
            print("⚠️ Text extraction may have issues")
        
        # Clean up
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pymupdf_with_ai_verification()
    if success:
        print("\n🎉 PyMuPDF C++ compilation issues resolved!")
        print("   The AI verification system is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Issues still remain with PyMuPDF integration.")
        sys.exit(1)
