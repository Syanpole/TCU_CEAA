#!/usr/bin/env python3
"""
Performance test for AI document verification system
"""
import os
import sys
import django
import time
from PIL import Image
import tempfile

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from ai_verification.base_verifier import DocumentTypeDetector
from ai_verification.verification_manager import DocumentVerificationManager

def create_test_image(size=(800, 600)):
    """Create a test image of specified size"""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        img = Image.new('RGB', size, 'white')
        # Add some text-like patterns
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "BIRTH CERTIFICATE", fill='black')
        draw.text((50, 100), "Date of Birth: 01/01/2000", fill='black')
        draw.text((50, 150), "Name: Test Person", fill='black')
        img.save(f.name, 'JPEG')
        return f.name

def benchmark_ai_processing():
    """Benchmark the AI processing speed"""
    print("⏱️ AI Document Verification Performance Test")
    print("=" * 60)
    
    # Test different image sizes
    test_sizes = [
        (400, 300, "Small (400x300)"),
        (800, 600, "Medium (800x600)"),
        (1200, 900, "Large (1200x900)"),
        (1920, 1080, "HD (1920x1080)")
    ]
    
    detector = DocumentTypeDetector()
    
    for width, height, size_name in test_sizes:
        print(f"\n📊 Testing {size_name} image:")
        
        # Create test image
        test_image = create_test_image((width, height))
        
        try:
            # Time the AI processing
            start_time = time.time()
            
            # Mock document submission object
            class MockDocumentSubmission:
                def __init__(self, doc_type):
                    self.document_type = doc_type
            
            mock_submission = MockDocumentSubmission('birth_certificate')
            
            # Run verification
            result = detector.verify_document_type(mock_submission, test_image)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"   Processing Time: {processing_time:.2f} seconds")
            print(f"   Confidence: {result.get('confidence_score', 0.0):.2f}")
            print(f"   Quality OK: {result.get('is_acceptable_quality', False)}")
            
            # Performance assessment
            if processing_time < 1.0:
                print("   ✅ EXCELLENT: Under 1 second")
            elif processing_time < 3.0:
                print("   ✅ GOOD: Under 3 seconds")
            elif processing_time < 5.0:
                print("   ⚠️ ACCEPTABLE: Under 5 seconds")
            else:
                print("   ❌ SLOW: Over 5 seconds - needs optimization")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        finally:
            if os.path.exists(test_image):
                os.unlink(test_image)

def test_processing_bottlenecks():
    """Identify processing bottlenecks"""
    print("\n🔍 Identifying Processing Bottlenecks")
    print("=" * 60)
    
    test_image = create_test_image()
    detector = DocumentTypeDetector()
    
    try:
        class MockDocumentSubmission:
            def __init__(self, doc_type):
                self.document_type = doc_type
        
        mock_submission = MockDocumentSubmission('birth_certificate')
        
        # Test individual components
        components = [
            ("File reading", lambda: Image.open(test_image)),
            ("Image analysis", lambda: detector._analyze_image_content(test_image)),
            ("OCR processing", lambda: detector._extract_text_content(test_image)),
            ("Quality assessment", lambda: detector._assess_document_quality(test_image)),
            ("Fraud detection", lambda: detector._detect_fraud_indicators(test_image, mock_submission.document_type))
        ]
        
        for component_name, component_func in components:
            start_time = time.time()
            try:
                component_func()
                end_time = time.time()
                component_time = end_time - start_time
                print(f"   {component_name}: {component_time:.3f}s")
                
                if component_time > 2.0:
                    print(f"      ⚠️ BOTTLENECK: {component_name} is slow")
            except Exception as e:
                print(f"   {component_name}: ERROR - {str(e)}")
                
    finally:
        if os.path.exists(test_image):
            os.unlink(test_image)

def suggest_optimizations():
    """Suggest performance optimizations"""
    print("\n💡 Performance Optimization Suggestions")
    print("=" * 60)
    
    suggestions = [
        "1. Image Preprocessing:",
        "   - Resize large images to max 1024x768 before processing",
        "   - Convert to grayscale for faster OCR",
        "   - Use JPEG compression for faster loading",
        "",
        "2. Caching Optimizations:",
        "   - Cache document signatures and models",
        "   - Implement result caching for identical files",
        "   - Pre-load ML models at startup",
        "",
        "3. Processing Optimizations:",
        "   - Use asynchronous processing for non-blocking UI",
        "   - Implement progressive loading (quick scan → detailed analysis)",
        "   - Skip expensive operations for obvious fraud cases",
        "",
        "4. Infrastructure Optimizations:",
        "   - Use GPU acceleration for OpenCV operations",
        "   - Implement multi-threading for parallel processing",
        "   - Consider cloud-based AI services for heavy workloads"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

if __name__ == '__main__':
    benchmark_ai_processing()
    test_processing_bottlenecks()
    suggest_optimizations()
    print("\n🎯 Performance Analysis Complete!")
