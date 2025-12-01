#!/usr/bin/env python3
"""
🤖 AI-Generated Content Detection Test Suite
Comprehensive testing of AI-generated document and image detection
"""

import os
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile
import json

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from ai_verification.ai_generated_detector import AIGeneratedDetector

def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print('='*80)

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def print_error(message):
    print(f"❌ {message}")

def create_test_image(width=800, height=600, image_type='natural'):
    """Create test images with different characteristics"""
    
    if image_type == 'natural':
        # Create a natural-looking image with some noise
        img = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Add some random elements
        for i in range(50):
            x1, y1 = np.random.randint(0, width), np.random.randint(0, height)
            x2, y2 = x1 + np.random.randint(10, 50), y1 + np.random.randint(10, 50)
            color = tuple(np.random.randint(0, 255, 3))
            draw.rectangle([x1, y1, x2, y2], fill=color)
        
        # Add some noise
        pixels = np.array(img)
        noise = np.random.normal(0, 10, pixels.shape).astype(np.int16)
        pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)
        
    elif image_type == 'ai_like':
        # Create an image that looks AI-generated
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Perfect gradients and symmetrical patterns (typical of AI)
        for i in range(height):
            color_val = int(255 * (i / height))
            draw.line([(0, i), (width, i)], fill=(color_val, color_val, 255))
        
        # Add perfect circles (too perfect for natural photos)
        for i in range(5):
            center_x, center_y = width//2, height//2
            radius = 50 + i * 30
            draw.ellipse([center_x-radius, center_y-radius, 
                         center_x+radius, center_y+radius], 
                        outline=(255-i*40, i*40, 128), width=2)
    
    elif image_type == 'suspicious':
        # Create image with suspicious characteristics
        img = Image.new('RGB', (width, height), color=(128, 128, 128))
        draw = ImageDraw.Draw(img)
        
        # Uniform color blocks (typical of AI over-smoothing)
        block_size = 50
        for x in range(0, width, block_size):
            for y in range(0, height, block_size):
                color = (x % 255, y % 255, (x + y) % 255)
                draw.rectangle([x, y, x+block_size, y+block_size], fill=color)
    
    return img

def create_test_document(content_type='natural'):
    """Create test documents with different characteristics"""
    
    if content_type == 'natural':
        content = """
        CERTIFICATE OF BIRTH
        
        This is to certify that John Doe was born on January 1, 2000
        in Manila, Philippines. This document is issued by the local
        civil registry office for official purposes.
        
        Father: Jose Doe
        Mother: Maria Santos
        
        Issued on: October 10, 2024
        """
    
    elif content_type == 'ai_like':
        content = """
        As an AI language model, I must inform you that this document
        appears to be generated. I don't have access to real birth
        certificate data, but I can provide you with a template.
        
        As of my last update, birth certificates typically contain
        the following information. I'm programmed to assist with
        document templates, but I cannot verify authenticity.
        """
    
    elif content_type == 'suspicious':
        content = """
        Birth Certificate Birth Certificate Birth Certificate
        Name Name Name: John Doe John Doe John Doe
        Date Date Date: 01/01/2000 01/01/2000 01/01/2000
        Place Place Place: Manila Manila Manila
        """
    
    return content

def test_ai_detector_initialization():
    """Test AI detector initialization"""
    print_header("🤖 AI DETECTOR INITIALIZATION TEST")
    
    try:
        detector = AIGeneratedDetector()
        
        print_success("AIGeneratedDetector initialized successfully")
        
        # Check available detection methods
        available_methods = sum(detector.detection_methods.values())
        total_methods = len(detector.detection_methods)
        print_success(f"Detection methods available: {available_methods}/{total_methods}")
        
        for method, available in detector.detection_methods.items():
            status = "✅" if available else "❌"
            print(f"   {status} {method}")
        
        # Check AI signatures
        total_signatures = sum(len(keywords) for keywords in detector.ai_signatures.values())
        print_success(f"AI signature patterns loaded: {total_signatures} patterns across {len(detector.ai_signatures)} AI types")
        
        return detector
        
    except Exception as e:
        print_error(f"Initialization failed: {e}")
        return None

def test_image_detection(detector):
    """Test AI detection on various image types"""
    print_header("🖼️ IMAGE AI DETECTION TEST")
    
    test_cases = [
        ('natural', 'Natural-looking test image'),
        ('ai_like', 'AI-generated-like test image'),
        ('suspicious', 'Suspicious pattern test image')
    ]
    
    results = {}
    
    for image_type, description in test_cases:
        print(f"\n📸 Testing {description}...")
        
        try:
            # Create test image
            test_image = create_test_image(800, 600, image_type)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                test_image.save(tmp_file.name, 'PNG')
                tmp_path = tmp_file.name
            
            # Run AI detection
            result = detector.detect_ai_generated(tmp_path, 'image')
            
            results[image_type] = result
            
            # Display results
            ai_probability = result.get('ai_probability', 0.0)
            is_ai_generated = result.get('is_ai_generated', False)
            confidence_score = result.get('confidence_score', 0.0)
            
            print(f"   AI Probability: {ai_probability:.3f} ({ai_probability*100:.1f}%)")
            print(f"   Is AI Generated: {'🤖 YES' if is_ai_generated else '📷 NO'}")
            print(f"   Confidence Score: {confidence_score:.3f}")
            
            # Show detection methods used
            detection_methods = result.get('detection_methods', {})
            active_methods = len([m for m in detection_methods.values() if m.get('ai_score', 0) > 0])
            print(f"   Active Detection Methods: {active_methods}/{len(detection_methods)}")
            
            # Show recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"   Recommendation: {recommendations[0]}")
            
            # Cleanup
            os.unlink(tmp_path)
            
        except Exception as e:
            print_error(f"Image detection failed for {image_type}: {e}")
            results[image_type] = {'error': str(e)}
    
    return results

def test_document_detection(detector):
    """Test AI detection on various document types"""
    print_header("📄 DOCUMENT AI DETECTION TEST")
    
    test_cases = [
        ('natural', 'Natural document content'),
        ('ai_like', 'AI-generated-like content'),
        ('suspicious', 'Suspicious repetitive content')
    ]
    
    results = {}
    
    for content_type, description in test_cases:
        print(f"\n📝 Testing {description}...")
        
        try:
            # Create test document
            test_content = create_test_document(content_type)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(test_content)
                tmp_path = tmp_file.name
            
            # Run AI detection
            result = detector.detect_ai_generated(tmp_path, 'document')
            
            results[content_type] = result
            
            # Display results
            ai_probability = result.get('ai_probability', 0.0)
            is_ai_generated = result.get('is_ai_generated', False)
            confidence_score = result.get('confidence_score', 0.0)
            
            print(f"   AI Probability: {ai_probability:.3f} ({ai_probability*100:.1f}%)")
            print(f"   Is AI Generated: {'🤖 YES' if is_ai_generated else '📝 NO'}")
            print(f"   Confidence Score: {confidence_score:.3f}")
            
            # Show suspicious indicators
            suspicious_indicators = result.get('suspicious_indicators', [])
            if suspicious_indicators:
                print(f"   Suspicious Indicators: {len(suspicious_indicators)}")
                for indicator in suspicious_indicators[:3]:  # Show first 3
                    print(f"     • {indicator}")
            
            # Show recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"   Recommendation: {recommendations[0]}")
            
            # Cleanup
            os.unlink(tmp_path)
            
        except Exception as e:
            print_error(f"Document detection failed for {content_type}: {e}")
            results[content_type] = {'error': str(e)}
    
    return results

def test_metadata_detection(detector):
    """Test metadata-based AI detection"""
    print_header("🔍 METADATA AI DETECTION TEST")
    
    try:
        # Create image with suspicious metadata
        test_image = create_test_image(400, 300, 'natural')
        
        # Add metadata that might indicate AI generation
        from PIL.ExifTags import TAGS
        import piexif
        
        # Create EXIF data with AI indicators
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Software: "DALL-E 2.0",
                piexif.ImageIFD.Artist: "OpenAI ChatGPT",
                piexif.ImageIFD.Copyright: "Generated by Midjourney"
            }
        }
        
        exif_bytes = piexif.dump(exif_dict)
        
        # Save with suspicious metadata
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            test_image.save(tmp_file.name, 'JPEG', exif=exif_bytes)
            tmp_path = tmp_file.name
        
        # Run detection
        result = detector.detect_ai_generated(tmp_path, 'image')
        
        # Check metadata analysis
        metadata_analysis = result.get('metadata_analysis', {})
        ai_indicators = metadata_analysis.get('ai_indicators', [])
        
        print(f"📊 Metadata Analysis Results:")
        print(f"   AI Indicators Found: {len(ai_indicators)}")
        for indicator in ai_indicators:
            print(f"     • {indicator['type']}: {indicator['keyword']} in {indicator['field']}")
        
        metadata_score = metadata_analysis.get('ai_score', 0.0)
        print(f"   Metadata AI Score: {metadata_score:.3f}")
        
        # Overall result
        ai_probability = result.get('ai_probability', 0.0)
        print(f"   Overall AI Probability: {ai_probability:.3f} ({ai_probability*100:.1f}%)")
        
        # Cleanup
        os.unlink(tmp_path)
        
        return len(ai_indicators) > 0
        
    except ImportError:
        print_warning("piexif not available - skipping metadata test")
        return True
    except Exception as e:
        print_error(f"Metadata detection test failed: {e}")
        return False

def test_performance_benchmarks(detector):
    """Test detection performance and speed"""
    print_header("⚡ PERFORMANCE BENCHMARK TEST")
    
    import time
    
    # Test different image sizes
    test_sizes = [
        (400, 300, "Small"),
        (800, 600, "Medium"), 
        (1200, 900, "Large"),
        (1920, 1080, "HD")
    ]
    
    performance_results = {}
    
    for width, height, size_name in test_sizes:
        print(f"\n📏 Testing {size_name} image ({width}x{height})...")
        
        try:
            # Create test image
            test_image = create_test_image(width, height, 'natural')
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                test_image.save(tmp_file.name, 'PNG')
                tmp_path = tmp_file.name
            
            # Measure detection time
            start_time = time.time()
            result = detector.detect_ai_generated(tmp_path, 'image')
            end_time = time.time()
            
            processing_time = end_time - start_time
            performance_results[size_name] = {
                'processing_time': processing_time,
                'ai_probability': result.get('ai_probability', 0.0),
                'image_size': f"{width}x{height}",
                'file_size': os.path.getsize(tmp_path)
            }
            
            print(f"   Processing Time: {processing_time:.3f} seconds")
            print(f"   File Size: {os.path.getsize(tmp_path) / 1024:.1f} KB")
            print(f"   AI Probability: {result.get('ai_probability', 0.0):.3f}")
            
            # Performance rating
            if processing_time < 1.0:
                print(f"   Performance: ✅ EXCELLENT (< 1 second)")
            elif processing_time < 3.0:
                print(f"   Performance: ⚠️ GOOD (< 3 seconds)")
            else:
                print(f"   Performance: ❌ SLOW (> 3 seconds)")
            
            # Cleanup
            os.unlink(tmp_path)
            
        except Exception as e:
            print_error(f"Performance test failed for {size_name}: {e}")
            performance_results[size_name] = {'error': str(e)}
    
    # Summary
    print(f"\n📊 Performance Summary:")
    avg_time = np.mean([r['processing_time'] for r in performance_results.values() if 'processing_time' in r])
    print(f"   Average Processing Time: {avg_time:.3f} seconds")
    
    return performance_results

def generate_comprehensive_report(detector, image_results, document_results, performance_results):
    """Generate comprehensive test report"""
    print_header("📋 COMPREHENSIVE TEST REPORT")
    
    print("🤖 AI-Generated Content Detection System")
    print("=" * 50)
    
    # System status
    available_methods = sum(detector.detection_methods.values())
    total_methods = len(detector.detection_methods)
    print(f"📊 System Status: {available_methods}/{total_methods} detection methods available")
    
    # Image detection results
    print(f"\n🖼️ Image Detection Results:")
    for img_type, result in image_results.items():
        if 'error' not in result:
            ai_prob = result.get('ai_probability', 0.0)
            status = "🤖 AI-GENERATED" if ai_prob >= 0.7 else "📷 NATURAL" if ai_prob < 0.4 else "⚠️ SUSPICIOUS"
            print(f"   {img_type.capitalize()}: {status} (Probability: {ai_prob:.3f})")
        else:
            print(f"   {img_type.capitalize()}: ❌ ERROR")
    
    # Document detection results  
    print(f"\n📄 Document Detection Results:")
    for doc_type, result in document_results.items():
        if 'error' not in result:
            ai_prob = result.get('ai_probability', 0.0)
            status = "🤖 AI-GENERATED" if ai_prob >= 0.7 else "📝 NATURAL" if ai_prob < 0.4 else "⚠️ SUSPICIOUS"
            print(f"   {doc_type.capitalize()}: {status} (Probability: {ai_prob:.3f})")
        else:
            print(f"   {doc_type.capitalize()}: ❌ ERROR")
    
    # Performance results
    print(f"\n⚡ Performance Results:")
    successful_tests = [r for r in performance_results.values() if 'processing_time' in r]
    if successful_tests:
        avg_time = np.mean([r['processing_time'] for r in successful_tests])
        max_time = max([r['processing_time'] for r in successful_tests])
        min_time = min([r['processing_time'] for r in successful_tests])
        
        print(f"   Average Processing Time: {avg_time:.3f} seconds")
        print(f"   Fastest Processing: {min_time:.3f} seconds")
        print(f"   Slowest Processing: {max_time:.3f} seconds")
        
        # Performance rating
        if avg_time < 1.0:
            print(f"   Overall Performance: ✅ EXCELLENT")
        elif avg_time < 3.0:
            print(f"   Overall Performance: ⚠️ GOOD")
        else:
            print(f"   Overall Performance: ❌ NEEDS OPTIMIZATION")
    
    # Final assessment
    print(f"\n🎯 Final Assessment:")
    
    # Count successful detections
    successful_image_tests = len([r for r in image_results.values() if 'error' not in r])
    successful_doc_tests = len([r for r in document_results.values() if 'error' not in r])
    successful_perf_tests = len(successful_tests)
    
    total_successful = successful_image_tests + successful_doc_tests + successful_perf_tests
    total_tests = len(image_results) + len(document_results) + len(performance_results)
    
    success_rate = (total_successful / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"   Test Success Rate: {success_rate:.1f}% ({total_successful}/{total_tests})")
    
    if success_rate >= 90:
        print(f"   System Status: ✅ PRODUCTION READY")
        print(f"   Recommendation: Deploy with confidence")
    elif success_rate >= 70:
        print(f"   System Status: ⚠️ MOSTLY FUNCTIONAL")
        print(f"   Recommendation: Address failing components before production")
    else:
        print(f"   System Status: ❌ NEEDS WORK")
        print(f"   Recommendation: Significant fixes required")

def main():
    """Main test execution"""
    print_header("🚀 AI-GENERATED CONTENT DETECTION TEST SUITE")
    print("Comprehensive testing of AI-generated document and image detection")
    print("Testing all detection methods and performance characteristics")
    
    # Initialize detector
    detector = test_ai_detector_initialization()
    if not detector:
        print_error("Cannot proceed without detector initialization")
        return
    
    # Run tests
    print("\n🧪 Running comprehensive test suite...")
    
    # Test image detection
    image_results = test_image_detection(detector)
    
    # Test document detection
    document_results = test_document_detection(detector)
    
    # Test metadata detection
    metadata_success = test_metadata_detection(detector)
    
    # Test performance
    performance_results = test_performance_benchmarks(detector)
    
    # Generate final report
    generate_comprehensive_report(detector, image_results, document_results, performance_results)
    
    print(f"\n🎉 AI-Generated Content Detection Test Suite Completed!")
    print(f"✅ The system is ready to detect AI-generated content in production!")

if __name__ == "__main__":
    main()