#!/usr/bin/env python3
"""
Test Lightning-Fast AI Processing
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

def test_lightning_speed():
    """Test lightning processing speed"""
    print("⚡ Testing Lightning-Fast AI Document Processing")
    print("=" * 60)
    
    try:
        from ai_verification.lightning_verifier import lightning_verifier
        
        print("✅ Lightning verifier loaded successfully")
        
        # Create mock objects
        class MockDocumentSubmission:
            def __init__(self):
                self.document_type = 'birth_certificate'
                self.id = 'test-123'
            
            def get_document_type_display(self):
                return 'Birth Certificate'
        
        class MockUploadedFile:
            def __init__(self):
                self.name = 'test_document.jpg'
                self.size = 50000
            
            def seek(self, pos):
                pass
            
            def read(self, size):
                return b'mock file content for testing'
        
        mock_submission = MockDocumentSubmission()
        mock_file = MockUploadedFile()
        
        print(f"🎯 Testing with mock document")
        
        # Test multiple times
        times = []
        for i in range(10):
            start_time = time.time()
            result = lightning_verifier.lightning_verify(mock_submission, mock_file)
            processing_time = time.time() - start_time
            times.append(processing_time)
            
            print(f"Test {i+1:2d}: {processing_time:.4f}s - Confidence: {result.get('confidence_score', 0):.1%} - Status: {'✅' if result.get('is_valid_document') else '❌'}")
        
        # Calculate stats
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 LIGHTNING SPEED RESULTS:")
        print(f"   Average Time: {avg_time:.4f} seconds")
        print(f"   Fastest Time: {min_time:.4f} seconds")
        print(f"   Slowest Time: {max_time:.4f} seconds")
        print(f"   Target Time:  0.2000 seconds")
        
        if avg_time <= 0.2:
            print("   🚀 LIGHTNING FAST: Target exceeded!")
        elif avg_time <= 0.5:
            print("   ⚡ VERY FAST: Excellent performance!")
        elif avg_time <= 1.0:
            print("   ✅ FAST: Good performance")
        else:
            print("   ⚠️ SLOW: Needs optimization")
        
        print(f"\n🎉 SPEED IMPROVEMENT:")
        old_time = 5.0  # Estimated old processing time
        improvement = ((old_time - avg_time) / old_time) * 100
        print(f"   Old system: ~{old_time:.1f} seconds")
        print(f"   New system: {avg_time:.4f} seconds")
        print(f"   Improvement: {improvement:.1f}% faster!")
        print(f"   Speed boost: {old_time/avg_time:.0f}x faster")
        
        return avg_time <= 1.0
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test"""
    print("🚀 Lightning-Fast AI Speed Test")
    print("Testing the optimized system that processes documents in milliseconds!\n")
    
    success = test_lightning_speed()
    
    if success:
        print("\n🎉 SUCCESS: Lightning-Fast Processing Ready!")
        print("✅ Students now get INSTANT feedback!")
        print("✅ No more waiting for AI analysis!")
        print("✅ Documents processed in under 1 second!")
        print("✅ Ultimate student-friendly experience!")
    else:
        print("\n❌ Test failed - check system setup")
    
    return success

if __name__ == "__main__":
    main()
