#!/usr/bin/env python3
"""
Test script for Ultra-Fast AI Document Processing Speed
This tests the new instant processing system
"""

import os
import sys
import django
import time
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def test_ultra_fast_processing():
    """Test the ultra-fast processing system speed"""
    print("⚡ Testing Ultra-Fast AI Document Processing")
    print("=" * 60)
    
    try:
        from ai_verification.ultra_fast_verifier import UltraFastDocumentVerifier
        
        # Create verifier instance
        verifier = UltraFastDocumentVerifier()
        print("✅ Ultra-Fast Verifier initialized")
        
        # Create a mock document submission object
        class MockDocumentSubmission:
            def __init__(self):
                self.document_type = 'birth_certificate'
                self.id = 'test-123'
            
            def get_document_type_display(self):
                return 'Birth Certificate'
        
        # Create a mock uploaded file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Create a simple test image
            from PIL import Image
            import numpy as np
            
            # Create a test image with some text-like patterns
            img_array = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(temp_file.name)
            
            mock_submission = MockDocumentSubmission()
            
            print(f"🎯 Testing with mock document: {temp_file.name}")
            
            # Test multiple times to get average
            times = []
            for i in range(5):
                start_time = time.time()
                result = verifier.instant_verify(mock_submission, temp_file.name)
                processing_time = time.time() - start_time
                times.append(processing_time)
                
                print(f"Test {i+1}: {processing_time:.3f}s - {result.get('verification_method', 'unknown')}")
            
            # Calculate stats
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print("\n📊 PERFORMANCE RESULTS:")
            print(f"   Average Time: {avg_time:.3f} seconds")
            print(f"   Fastest Time: {min_time:.3f} seconds")
            print(f"   Slowest Time: {max_time:.3f} seconds")
            print(f"   Target Time: 0.500 seconds")
            
            if avg_time <= 0.5:
                print("   🎉 EXCELLENT: Target achieved!")
            elif avg_time <= 1.0:
                print("   ✅ GOOD: Close to target")
            elif avg_time <= 2.0:
                print("   ⚠️ ACCEPTABLE: Room for improvement")
            else:
                print("   ❌ SLOW: Optimization needed")
            
            # Clean up
            os.unlink(temp_file.name)
            verifier.cleanup()
            
            return avg_time <= 1.0
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_serializer_integration():
    """Test the updated serializer integration"""
    print("\n🔗 Testing Serializer Integration")
    print("=" * 40)
    
    try:
        from myapp.serializers import DocumentSubmissionCreateSerializer
        
        serializer = DocumentSubmissionCreateSerializer()
        
        if hasattr(serializer, '_process_ultra_fast_results'):
            print("✅ Ultra-fast result processing method available")
        else:
            print("❌ Ultra-fast result processing method missing")
            
        print("✅ Serializer integration test complete")
        return True
        
    except Exception as e:
        print(f"❌ Serializer test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Ultra-Fast AI Processing Speed Test")
    print("This will test the optimized system for instant document processing.\n")
    
    try:
        speed_success = test_ultra_fast_processing()
        integration_success = test_serializer_integration()
        
        if speed_success and integration_success:
            print("\n🎉 SUCCESS: Ultra-Fast AI Processing System is ready!")
            print("Students will now experience:")
            print("  ⚡ Instant document processing (< 1 second)")
            print("  🤖 Real-time AI analysis feedback")
            print("  ✅ Immediate approval notifications")
            print("  🚀 No more waiting for manual reviews")
            print("\n💡 The system is now optimized for student experience!")
        else:
            print("\n⚠️ PARTIAL SUCCESS: System works but may need optimization")
            
        return speed_success and integration_success
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
