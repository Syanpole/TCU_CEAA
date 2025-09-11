#!/usr/bin/env python3
"""
Real-world performance test for AI verification system
Tests how long verification takes for actual documents
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

def test_real_world_performance():
    """Test performance with realistic scenarios"""
    print("🚀 Real-World AI Verification Performance Test")
    print("=" * 60)
    print("Testing processing speed for impatient students...")
    print()
    
    try:
        from ai_verification.fast_verifier import FastDocumentTypeDetector
        fast_detector = FastDocumentTypeDetector()
        
        # Test scenarios students might encounter
        scenarios = [
            {
                'name': 'Phone photo of birth certificate',
                'size': (1080, 1920),
                'expected_time': '< 1 second',
                'target': 1.0
            },
            {
                'name': 'Scanned school ID (medium quality)',
                'size': (800, 600),
                'expected_time': '< 0.5 seconds',
                'target': 0.5
            },
            {
                'name': 'High-res transcript scan',
                'size': (1200, 1600),
                'expected_time': '< 1.5 seconds',
                'target': 1.5
            },
            {
                'name': 'Quick selfie with document',
                'size': (640, 480),
                'expected_time': '< 0.3 seconds',
                'target': 0.3
            }
        ]
        
        total_tests = len(scenarios)
        passed_tests = 0
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"📱 Test {i}/{total_tests}: {scenario['name']}")
            
            # Create test image
            test_image = create_realistic_test_image(scenario['size'])
            
            try:
                # Mock document submission
                class MockSubmission:
                    def __init__(self):
                        self.document_type = 'birth_certificate'
                
                mock_submission = MockSubmission()
                
                # Time the verification
                start_time = time.time()
                result = fast_detector.fast_verify_document(
                    mock_submission, 
                    test_image,
                    max_time=scenario['target'] + 0.5
                )
                processing_time = time.time() - start_time
                
                # Check performance
                performance = "✅ EXCELLENT" if processing_time <= scenario['target'] else "⚠️ SLOW"
                if processing_time <= scenario['target']:
                    passed_tests += 1
                
                print(f"   Expected: {scenario['expected_time']}")
                print(f"   Actual: {processing_time:.2f}s {performance}")
                print(f"   Confidence: {result.get('confidence_score', 0.0):.2f}")
                print(f"   Status: {'✅ Approved' if result.get('is_valid_document') else '❌ Rejected'}")
                
                # Student experience feedback
                if processing_time <= 0.5:
                    print(f"   📱 Student Experience: ⚡ Instant verification!")
                elif processing_time <= 1.0:
                    print(f"   📱 Student Experience: ✅ Quick and smooth")
                elif processing_time <= 2.0:
                    print(f"   📱 Student Experience: ⏳ Acceptable wait time")
                else:
                    print(f"   📱 Student Experience: 😴 Students might get impatient")
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
            finally:
                if os.path.exists(test_image):
                    os.unlink(test_image)
            
            print()
        
        # Overall performance assessment
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 EXCELLENT: All performance targets met!")
            print("Students will be happy with the verification speed! 😊")
        elif passed_tests >= total_tests * 0.75:
            print("✅ GOOD: Most performance targets met")
            print("Most students will find this acceptable")
        else:
            print("⚠️ NEEDS OPTIMIZATION: Performance targets not met")
            print("Students might get impatient - consider optimizations")
        
        print()
        print("💡 STUDENT EXPERIENCE TIPS:")
        print("   • Processing times under 1 second feel instant")
        print("   • 1-2 seconds is acceptable for most students")
        print("   • Over 3 seconds and students start getting impatient")
        print("   • Show progress indicators for longer processing")
        
    except ImportError as e:
        print(f"❌ Fast verifier not available: {e}")
        print("Using fallback performance estimates...")
        
        # Estimate performance based on typical operations
        print()
        print("📊 ESTIMATED PERFORMANCE (without fast verifier):")
        print("   • Basic file validation: ~0.1s")
        print("   • Image loading and resizing: ~0.3s")
        print("   • OCR text extraction: ~1-3s")
        print("   • AI analysis: ~0.5-1s")
        print("   • Total estimated time: 2-5 seconds")
        print()
        print("⚠️ Recommendation: Use the FastDocumentTypeDetector for better performance!")

def create_realistic_test_image(size):
    """Create a realistic test document image"""
    width, height = size
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Create image with document-like content
        img = Image.new('RGB', (width, height), 'white')
        
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Add text that looks like a document
            y_pos = 50
            lines = [
                "BIRTH CERTIFICATE",
                "Certificate No: BC-2024-001234",
                "Full Name: STUDENT TEST PERSON",
                "Date of Birth: January 15, 2000",
                "Place of Birth: Sample City",
                "Father's Name: Father Test Person",
                "Mother's Name: Mother Test Person",
                "Date Issued: March 15, 2024",
                "Registrar: Sample Civil Registry"
            ]
            
            for line in lines:
                draw.text((50, y_pos), line, fill='black')
                y_pos += 30
                
        except Exception:
            # Fallback if font operations fail
            pass
        
        img.save(f.name, 'JPEG', quality=85)
        return f.name

def suggest_performance_improvements():
    """Suggest specific performance improvements for impatient students"""
    print()
    print("🔧 PERFORMANCE IMPROVEMENT SUGGESTIONS")
    print("=" * 60)
    
    improvements = [
        "1. Frontend Optimizations:",
        "   • Show upload progress bar during file upload",
        "   • Display 'Analyzing...' spinner immediately",
        "   • Use WebSocket for real-time status updates",
        "   • Implement client-side image compression",
        "",
        "2. Backend Optimizations:",
        "   • Pre-resize images before AI processing",
        "   • Use async processing with immediate response",
        "   • Cache AI models to avoid loading time",
        "   • Implement result caching for duplicate files",
        "",
        "3. User Experience:",
        "   • Quick file validation (< 0.1s) with immediate feedback",
        "   • Progressive disclosure: 'Quick check passed, running full analysis...'",
        "   • Estimated time remaining: 'About 2 seconds remaining...'",
        "   • Fun loading messages: 'AI is examining your document...'",
        "",
        "4. Performance Monitoring:",
        "   • Track processing times in database",
        "   • Alert when processing > 3 seconds",
        "   • A/B test different timeout values",
        "   • Monitor student abandonment rates"
    ]
    
    for improvement in improvements:
        print(improvement)

if __name__ == '__main__':
    test_real_world_performance()
    suggest_performance_improvements()
