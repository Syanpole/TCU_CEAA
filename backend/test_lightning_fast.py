#!/usr/bin/env python3
"""
Test Lightning-Fast AI Document Verification
Demonstrates ultra-fast processing for impatient students
"""
import os
import sys
import time
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from ai_verification.ultra_fast_verifier import UltraFastDocumentVerifier
from ai_verification.performance_monitor import performance_monitor
import tempfile
from PIL import Image
import io

def create_test_document(width=800, height=600, filename="test_doc.jpg"):
    """Create a test document image"""
    # Create a simple document-like image
    img = Image.new('RGB', (width, height), color='white')
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    img.save(temp_file.name, 'JPEG')
    temp_file.close()
    
    return temp_file.name

class MockDocumentSubmission:
    """Mock document submission for testing"""
    def __init__(self, doc_type='birth_certificate'):
        self.document_type = doc_type
        self.id = 'test_123'

class MockUploadedFile:
    """Mock uploaded file for testing"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = os.path.basename(file_path)
        self.size = os.path.getsize(file_path)
    
    def temporary_file_path(self):
        return self.file_path
    
    def chunks(self):
        with open(self.file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk

def test_lightning_fast_verification():
    """Test the lightning-fast verification system"""
    print("🚀 Testing Lightning-Fast AI Document Verification")
    print("=" * 60)
    
    # Initialize the ultra-fast verifier
    verifier = UltraFastDocumentVerifier()
    
    # Test scenarios
    test_scenarios = [
        {"name": "Small Phone Photo", "size": (400, 300)},
        {"name": "Standard Scan", "size": (800, 600)}, 
        {"name": "High Resolution", "size": (1200, 900)},
        {"name": "Very Small Image", "size": (200, 150)},
        {"name": "Large File", "size": (2000, 1500)}
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"\n📄 Testing: {scenario['name']} ({scenario['size'][0]}x{scenario['size'][1]})")
        
        # Create test document
        test_file_path = create_test_document(
            width=scenario['size'][0], 
            height=scenario['size'][1]
        )
        
        try:
            # Create mock objects
            mock_submission = MockDocumentSubmission()
            mock_file = MockUploadedFile(test_file_path)
            
            # Perform verification
            start_time = time.time()
            result = verifier.instant_verify(mock_submission, mock_file)
            processing_time = time.time() - start_time
            
            # Record performance
            performance_monitor.record_processing_time(
                processing_time=processing_time,
                document_type='test_document',
                file_size=mock_file.size,
                success=result['is_valid_document']
            )
            
            # Display results
            print(f"   ⚡ Processing Time: {processing_time:.3f} seconds")
            print(f"   ✅ Status: {'APPROVED' if result['is_valid_document'] else 'REJECTED'}")
            print(f"   📊 Confidence: {result['confidence_score']:.1%}")
            print(f"   🎯 Quality Rating: {result.get('quality_rating', 'N/A')}")
            print(f"   📈 Speed Rating: {get_speed_rating(processing_time)}")
            
            if result.get('quality_issues'):
                print(f"   ⚠️  Issues: {len(result['quality_issues'])} minor issues detected")
            
            if result.get('from_cache'):
                print(f"   💾 Cache: Retrieved from cache (instant!)")
            
            results.append({
                'scenario': scenario['name'],
                'processing_time': processing_time,
                'success': result['is_valid_document'],
                'confidence': result['confidence_score'],
                'file_size': mock_file.size
            })
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                'scenario': scenario['name'],
                'processing_time': 0,
                'success': False,
                'error': str(e)
            })
        
        finally:
            # Clean up test file
            try:
                os.unlink(test_file_path)
            except:
                pass
    
    # Performance summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    successful_results = [r for r in results if r['success']]
    if successful_results:
        avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
        fastest = min(r['processing_time'] for r in successful_results)
        slowest = max(r['processing_time'] for r in successful_results)
        
        print(f"✅ Success Rate: {len(successful_results)}/{len(results)} ({len(successful_results)/len(results)*100:.1f}%)")
        print(f"⚡ Average Time: {avg_time:.3f} seconds")
        print(f"🏃 Fastest Time: {fastest:.3f} seconds")
        print(f"🐌 Slowest Time: {slowest:.3f} seconds")
        
        # Speed analysis
        instant_count = len([r for r in successful_results if r['processing_time'] < 0.2])
        fast_count = len([r for r in successful_results if r['processing_time'] < 0.5])
        
        print(f"\n🎯 STUDENT EXPERIENCE:")
        print(f"   ⚡ Feels Instant (< 0.2s): {instant_count}/{len(successful_results)} ({instant_count/len(successful_results)*100:.1f}%)")
        print(f"   🚀 Fast Enough (< 0.5s): {fast_count}/{len(successful_results)} ({fast_count/len(successful_results)*100:.1f}%)")
        
        if avg_time < 0.5:
            print(f"\n🎉 EXCELLENT! Students will love this speed!")
        elif avg_time < 1.0:
            print(f"\n✅ Good performance for student patience")
        else:
            print(f"\n⚠️  May need optimization for better student experience")
    
    # Get performance report
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE REPORT")
    print("=" * 60)
    
    report = performance_monitor.get_performance_report()
    if 'error' not in report:
        overall = report['overall_performance']
        print(f"📊 Overall Rating: {overall['performance_rating'].upper()}")
        print(f"⏱️  Average Processing: {overall['average_processing_time']:.3f}s")
        print(f"✅ Success Rate: {overall['success_rate']:.1%}")
        
        student_exp = report['student_experience']
        print(f"\n👨‍🎓 STUDENT EXPERIENCE:")
        print(f"   Feels Instant: {student_exp['feels_instant']:.1%}")
        print(f"   Acceptable Speed: {student_exp['acceptable_speed']:.1%}")
        print(f"   Needs Improvement: {student_exp['needs_improvement']:.1%}")
        
        if report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   • {rec}")

def get_speed_rating(processing_time: float) -> str:
    """Get human-readable speed rating"""
    if processing_time < 0.1:
        return "⚡ Lightning Fast"
    elif processing_time < 0.3:
        return "🚀 Super Fast" 
    elif processing_time < 0.5:
        return "⭐ Very Fast"
    elif processing_time < 1.0:
        return "✅ Fast"
    else:
        return "📈 Normal"

def test_cache_performance():
    """Test cache performance for repeated documents"""
    print("\n" + "=" * 60)
    print("💾 TESTING CACHE PERFORMANCE")
    print("=" * 60)
    
    verifier = UltraFastDocumentVerifier()
    
    # Create test document
    test_file_path = create_test_document(800, 600)
    mock_submission = MockDocumentSubmission()
    mock_file = MockUploadedFile(test_file_path)
    
    try:
        # First verification (no cache)
        print("🔄 First verification (no cache):")
        start_time = time.time()
        result1 = verifier.instant_verify(mock_submission, mock_file)
        time1 = time.time() - start_time
        print(f"   Time: {time1:.3f} seconds")
        print(f"   From cache: {result1.get('from_cache', False)}")
        
        # Second verification (should use cache)
        print("\n💾 Second verification (with cache):")
        start_time = time.time()
        result2 = verifier.instant_verify(mock_submission, mock_file)
        time2 = time.time() - start_time
        print(f"   Time: {time2:.3f} seconds")
        print(f"   From cache: {result2.get('from_cache', False)}")
        
        # Cache performance improvement
        if time1 > 0:
            improvement = ((time1 - time2) / time1) * 100
            print(f"\n📈 Cache Performance:")
            print(f"   Speed improvement: {improvement:.1f}%")
            if improvement > 50:
                print(f"   🎉 Excellent cache performance!")
            elif improvement > 20:
                print(f"   ✅ Good cache performance")
            else:
                print(f"   📊 Cache working but minimal improvement")
    
    finally:
        try:
            os.unlink(test_file_path)
        except:
            pass

if __name__ == "__main__":
    try:
        test_lightning_fast_verification()
        test_cache_performance()
        
        print("\n" + "=" * 60)
        print("🎯 RECOMMENDATIONS FOR STUDENTS")
        print("=" * 60)
        print("1. 📱 Use JPG or PNG format for fastest processing")
        print("2. 📏 Keep images between 400x300 and 1200x900 pixels")
        print("3. 💡 Take photos in good lighting")
        print("4. 📷 Keep images under 5MB for best speed")
        print("5. 🔄 If processing seems slow, try uploading again")
        print("\n✨ Expected processing time: Under 0.5 seconds!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
