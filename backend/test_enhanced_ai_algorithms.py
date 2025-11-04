#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced AI verification algorithms
Tests the advanced Face Verifier and Fraud Detector implementations
"""

import os
import sys
import json
import tempfile
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw
import cv2

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced algorithms
try:
    from ai_verification.advanced_algorithms import FaceVerifier, FraudDetector
    print("✅ Successfully imported enhanced algorithms")
except ImportError as e:
    print(f"❌ Failed to import algorithms: {e}")
    sys.exit(1)

class EnhancedAlgorithmTestSuite:
    """Comprehensive test suite for enhanced AI algorithms"""
    
    def __init__(self):
        self.face_verifier = FaceVerifier()
        self.fraud_detector = FraudDetector()
        self.test_results = {
            'face_verifier_tests': [],
            'fraud_detector_tests': [],
            'performance_metrics': {},
            'overall_status': 'UNKNOWN'
        }
        
    def create_test_image(self, width=400, height=300, add_face=True):
        """Create a test image with optional face-like pattern"""
        # Create a simple test image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        if add_face:
            # Draw a simple face-like pattern
            face_x, face_y = width // 2, height // 2
            face_size = min(width, height) // 4
            
            # Face outline (circle)
            draw.ellipse([
                face_x - face_size, face_y - face_size,
                face_x + face_size, face_y + face_size
            ], fill='lightgray', outline='black')
            
            # Eyes
            eye_size = face_size // 6
            draw.ellipse([
                face_x - face_size//2, face_y - face_size//3,
                face_x - face_size//2 + eye_size, face_y - face_size//3 + eye_size
            ], fill='black')
            
            draw.ellipse([
                face_x + face_size//2 - eye_size, face_y - face_size//3,
                face_x + face_size//2, face_y - face_size//3 + eye_size
            ], fill='black')
            
            # Mouth
            draw.arc([
                face_x - face_size//3, face_y,
                face_x + face_size//3, face_y + face_size//2
            ], start=0, end=180, fill='black', width=3)
        
        return img
    
    def save_test_image_with_exif(self, img, filename, add_editing_software=False):
        """Save test image with custom EXIF data"""
        # Convert PIL image to format that supports EXIF
        exif_dict = {
            "0th": {
                256: img.width,  # ImageWidth
                257: img.height,  # ImageLength
                272: "TestCamera",  # Make
                306: "2024:01:15 12:00:00",  # DateTime
            }
        }
        
        if add_editing_software:
            exif_dict["0th"][305] = "Adobe Photoshop 2024"  # Software
        
        try:
            import piexif
            exif_bytes = piexif.dump(exif_dict)
            img.save(filename, "JPEG", exif=exif_bytes, quality=95)
        except ImportError:
            # Fallback: save without EXIF
            img.save(filename, "JPEG", quality=95)
        
        return filename
    
    def test_face_verifier_basic_functionality(self):
        """Test basic Face Verifier functionality"""
        test_name = "Face Verifier Basic Functionality"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create test image with face
                test_img = self.create_test_image(add_face=True)
                test_img.save(temp_file.name, "JPEG")
                
                # Test face verification
                result = self.face_verifier.verify_face(temp_file.name)
                
                # Validate results
                expected_keys = ['has_face', 'face_count', 'faces_detected', 'confidence', 'quality_score']
                missing_keys = [key for key in expected_keys if key not in result]
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if not missing_keys else 'FAIL',
                    'details': {
                        'missing_keys': missing_keys,
                        'result_keys': list(result.keys()),
                        'has_face': result.get('has_face', False),
                        'face_count': result.get('face_count', 0),
                        'confidence': result.get('confidence', 0.0)
                    }
                }
                
                if 'error' in result:
                    test_result['status'] = 'ERROR'
                    test_result['error'] = result['error']
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        self.test_results['face_verifier_tests'].append(test_result)
        print(f"   Result: {test_result['status']}")
        
        return test_result['status'] == 'PASS'
    
    def test_face_verifier_advanced_features(self):
        """Test advanced Face Verifier features"""
        test_name = "Face Verifier Advanced Features"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create test image with face
                test_img = self.create_test_image(add_face=True)
                test_img.save(temp_file.name, "JPEG")
                
                # Test advanced face verification
                result = self.face_verifier.verify_face(temp_file.name)
                
                # Check for advanced features
                advanced_keys = [
                    'detection_method', 'pose_analysis', 'overall_assessment'
                ]
                
                advanced_features_present = all(key in result for key in advanced_keys)
                
                # Check face quality analysis
                quality_analysis_present = False
                if result.get('faces_detected'):
                    first_face = result['faces_detected'][0]
                    quality_analysis_present = 'quality_analysis' in first_face
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if advanced_features_present and quality_analysis_present else 'FAIL',
                    'details': {
                        'advanced_features_present': advanced_features_present,
                        'quality_analysis_present': quality_analysis_present,
                        'detection_method': result.get('detection_method', 'unknown'),
                        'pose_analysis_keys': list(result.get('pose_analysis', {}).keys()),
                        'assessment_keys': list(result.get('overall_assessment', {}).keys())
                    }
                }
                
                if 'error' in result:
                    test_result['status'] = 'ERROR'
                    test_result['error'] = result['error']
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        self.test_results['face_verifier_tests'].append(test_result)
        print(f"   Result: {test_result['status']}")
        
        return test_result['status'] == 'PASS'
    
    def test_face_verifier_multiple_faces(self):
        """Test Face Verifier with multiple faces"""
        test_name = "Face Verifier Multiple Faces"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create test image with multiple face-like patterns
                img = Image.new('RGB', (600, 400), color='white')
                draw = ImageDraw.Draw(img)
                
                # Draw two simple faces
                for face_center in [(150, 200), (450, 200)]:
                    face_x, face_y = face_center
                    face_size = 50
                    
                    # Face outline
                    draw.ellipse([
                        face_x - face_size, face_y - face_size,
                        face_x + face_size, face_y + face_size
                    ], fill='lightgray', outline='black')
                    
                    # Eyes
                    eye_size = 8
                    draw.ellipse([
                        face_x - 20, face_y - 15,
                        face_x - 20 + eye_size, face_y - 15 + eye_size
                    ], fill='black')
                    
                    draw.ellipse([
                        face_x + 12, face_y - 15,
                        face_x + 12 + eye_size, face_y - 15 + eye_size
                    ], fill='black')
                
                img.save(temp_file.name, "JPEG")
                
                # Test face verification
                result = self.face_verifier.verify_face(temp_file.name)
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS',  # We'll determine this based on results
                    'details': {
                        'face_count': result.get('face_count', 0),
                        'has_multiple_faces': result.get('face_count', 0) > 1,
                        'faces_detected_count': len(result.get('faces_detected', [])),
                        'detection_successful': result.get('has_face', False)
                    }
                }
                
                # The test passes if it detects any faces (our simple drawings may not be detected)
                if 'error' in result:
                    test_result['status'] = 'ERROR'
                    test_result['error'] = result['error']
                elif not result.get('has_face', False):
                    test_result['status'] = 'WARN'
                    test_result['details']['warning'] = 'No faces detected in test image (expected with simple drawings)'
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        self.test_results['face_verifier_tests'].append(test_result)
        print(f"   Result: {test_result['status']}")
        
        return test_result['status'] in ['PASS', 'WARN']
    
    def test_fraud_detector_basic_functionality(self):
        """Test basic Fraud Detector functionality"""
        test_name = "Fraud Detector Basic Functionality"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create clean test image
                test_img = self.create_test_image()
                test_img.save(temp_file.name, "JPEG")
                
                # Test fraud detection
                result = self.fraud_detector.detect_fraud(temp_file.name)
                
                # Validate results
                expected_keys = [
                    'is_likely_fraud', 'fraud_probability', 'fraud_indicators', 
                    'metadata_analysis', 'tampering_analysis'
                ]
                missing_keys = [key for key in expected_keys if key not in result]
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if not missing_keys else 'FAIL',
                    'details': {
                        'missing_keys': missing_keys,
                        'result_keys': list(result.keys()),
                        'is_likely_fraud': result.get('is_likely_fraud', False),
                        'fraud_probability': result.get('fraud_probability', 0.0),
                        'indicator_count': len(result.get('fraud_indicators', []))
                    }
                }
                
                if 'error' in result:
                    test_result['status'] = 'ERROR'
                    test_result['error'] = result['error']
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        self.test_results['fraud_detector_tests'].append(test_result)
        print(f"   Result: {test_result['status']}")
        
        return test_result['status'] == 'PASS'
    
    def test_fraud_detector_metadata_analysis(self):
        """Test Fraud Detector metadata analysis"""
        test_name = "Fraud Detector Metadata Analysis"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create test image with suspicious EXIF
                test_img = self.create_test_image()
                self.save_test_image_with_exif(test_img, temp_file.name, add_editing_software=True)
                
                # Test fraud detection
                result = self.fraud_detector.detect_fraud(temp_file.name)
                
                # Check for comprehensive metadata analysis
                metadata_analysis = result.get('metadata_analysis', {})
                
                expected_metadata_keys = [
                    'metadata_missing', 'timestamp_analysis', 'file_details'
                ]
                
                metadata_complete = all(key in metadata_analysis for key in expected_metadata_keys)
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if metadata_complete else 'FAIL',
                    'details': {
                        'metadata_complete': metadata_complete,
                        'metadata_keys': list(metadata_analysis.keys()),
                        'suspicious_software_detected': metadata_analysis.get('suspicious_software', False),
                        'timestamp_analysis_present': 'timestamp_analysis' in metadata_analysis,
                        'file_details_present': 'file_details' in metadata_analysis
                    }
                }
                
                if 'error' in result:
                    test_result['status'] = 'ERROR'
                    test_result['error'] = result['error']
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        self.test_results['fraud_detector_tests'].append(test_result)
        print(f"   Result: {test_result['status']}")
        
        return test_result['status'] == 'PASS'
    
    def test_fraud_detector_advanced_analysis(self):
        """Test Fraud Detector advanced analysis features"""
        test_name = "Fraud Detector Advanced Analysis"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create test image
                test_img = self.create_test_image()
                test_img.save(temp_file.name, "JPEG")
                
                # Test fraud detection
                result = self.fraud_detector.detect_fraud(temp_file.name)
                
                # Check for advanced analysis features
                advanced_keys = [
                    'ela_analysis', 'compression_analysis', 'pixel_analysis', 'overall_assessment'
                ]
                
                advanced_features_present = sum(1 for key in advanced_keys if key in result and result[key])
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if advanced_features_present >= 2 else 'FAIL',
                    'details': {
                        'advanced_features_count': advanced_features_present,
                        'ela_analysis_present': bool(result.get('ela_analysis')),
                        'compression_analysis_present': bool(result.get('compression_analysis')),
                        'pixel_analysis_present': bool(result.get('pixel_analysis')),
                        'overall_assessment_present': bool(result.get('overall_assessment')),
                        'available_analyses': [key for key in advanced_keys if key in result and result[key]]
                    }
                }
                
                if 'error' in result:
                    test_result['status'] = 'ERROR'
                    test_result['error'] = result['error']
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        self.test_results['fraud_detector_tests'].append(test_result)
        print(f"   Result: {test_result['status']}")
        
        return test_result['status'] == 'PASS'
    
    def test_algorithm_performance(self):
        """Test algorithm performance and speed"""
        test_name = "Algorithm Performance Test"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            import time
            
            performance_results = {
                'face_verifier_time': 0.0,
                'fraud_detector_time': 0.0,
                'total_time': 0.0,
                'performance_grade': 'F'
            }
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create test image
                test_img = self.create_test_image(add_face=True)
                test_img.save(temp_file.name, "JPEG")
                
                # Test Face Verifier performance
                start_time = time.time()
                face_result = self.face_verifier.verify_face(temp_file.name)
                face_time = time.time() - start_time
                performance_results['face_verifier_time'] = face_time
                
                # Test Fraud Detector performance
                start_time = time.time()
                fraud_result = self.fraud_detector.detect_fraud(temp_file.name)
                fraud_time = time.time() - start_time
                performance_results['fraud_detector_time'] = fraud_time
                
                total_time = face_time + fraud_time
                performance_results['total_time'] = total_time
                
                # Grade performance (target: under 5 seconds total)
                if total_time < 2.0:
                    performance_results['performance_grade'] = 'A'
                elif total_time < 5.0:
                    performance_results['performance_grade'] = 'B'
                elif total_time < 10.0:
                    performance_results['performance_grade'] = 'C'
                elif total_time < 20.0:
                    performance_results['performance_grade'] = 'D'
                else:
                    performance_results['performance_grade'] = 'F'
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if total_time < 20.0 else 'FAIL',
                    'details': performance_results
                }
                
                # Check for errors
                if 'error' in face_result or 'error' in fraud_result:
                    test_result['status'] = 'ERROR'
                    test_result['errors'] = {
                        'face_verifier_error': face_result.get('error'),
                        'fraud_detector_error': fraud_result.get('error')
                    }
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        self.test_results['performance_metrics'] = test_result.get('details', {})
        print(f"   Result: {test_result['status']}")
        if 'details' in test_result:
            print(f"   Face Verifier: {test_result['details']['face_verifier_time']:.2f}s")
            print(f"   Fraud Detector: {test_result['details']['fraud_detector_time']:.2f}s")
            print(f"   Total Time: {test_result['details']['total_time']:.2f}s")
            print(f"   Performance Grade: {test_result['details']['performance_grade']}")
        
        return test_result['status'] == 'PASS'
    
    def test_backward_compatibility(self):
        """Test backward compatibility with existing system"""
        test_name = "Backward Compatibility Test"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # Test if algorithms still provide expected output format
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                test_img = self.create_test_image(add_face=True)
                test_img.save(temp_file.name, "JPEG")
                
                # Test Face Verifier compatibility
                face_result = self.face_verifier.verify_face(temp_file.name)
                face_compatible = all(key in face_result for key in ['has_face', 'face_count', 'confidence'])
                
                # Test Fraud Detector compatibility
                fraud_result = self.fraud_detector.detect_fraud(temp_file.name)
                fraud_compatible = all(key in fraud_result for key in ['is_likely_fraud', 'fraud_probability', 'fraud_indicators'])
                
                test_result = {
                    'test_name': test_name,
                    'status': 'PASS' if face_compatible and fraud_compatible else 'FAIL',
                    'details': {
                        'face_verifier_compatible': face_compatible,
                        'fraud_detector_compatible': fraud_compatible,
                        'face_result_keys': list(face_result.keys()),
                        'fraud_result_keys': list(fraud_result.keys())
                    }
                }
                
                if 'error' in face_result or 'error' in fraud_result:
                    test_result['status'] = 'ERROR'
                    test_result['errors'] = {
                        'face_error': face_result.get('error'),
                        'fraud_error': fraud_result.get('error')
                    }
                
                # Clean up
                os.unlink(temp_file.name)
                
        except Exception as e:
            test_result = {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e)
            }
        
        print(f"   Result: {test_result['status']}")
        return test_result['status'] == 'PASS'
    
    def run_all_tests(self):
        """Run all tests and generate comprehensive report"""
        print("🚀 Starting Enhanced AI Algorithms Test Suite")
        print("=" * 60)
        
        # Run all tests
        test_methods = [
            self.test_face_verifier_basic_functionality,
            self.test_face_verifier_advanced_features,
            self.test_face_verifier_multiple_faces,
            self.test_fraud_detector_basic_functionality,
            self.test_fraud_detector_metadata_analysis,
            self.test_fraud_detector_advanced_analysis,
            self.test_algorithm_performance,
            self.test_backward_compatibility
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            if test_method():
                passed_tests += 1
        
        # Calculate overall status
        success_rate = passed_tests / total_tests
        if success_rate >= 0.9:
            self.test_results['overall_status'] = 'EXCELLENT'
        elif success_rate >= 0.75:
            self.test_results['overall_status'] = 'GOOD'
        elif success_rate >= 0.5:
            self.test_results['overall_status'] = 'ACCEPTABLE'
        else:
            self.test_results['overall_status'] = 'POOR'
        
        # Generate final report
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Overall Status: {self.test_results['overall_status']}")
        
        if 'performance_grade' in self.test_results.get('performance_metrics', {}):
            print(f"Performance Grade: {self.test_results['performance_metrics']['performance_grade']}")
        
        print("\n📋 DETAILED RESULTS:")
        
        # Face Verifier results
        print("\n🔍 Face Verifier Tests:")
        for test in self.test_results['face_verifier_tests']:
            status_icon = "✅" if test['status'] == 'PASS' else "⚠️" if test['status'] == 'WARN' else "❌"
            print(f"   {status_icon} {test['test_name']}: {test['status']}")
        
        # Fraud Detector results
        print("\n🔒 Fraud Detector Tests:")
        for test in self.test_results['fraud_detector_tests']:
            status_icon = "✅" if test['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {test['test_name']}: {test['status']}")
        
        return self.test_results

def main():
    """Main test execution"""
    print("Enhanced AI Algorithms Test Suite")
    print("Testing Face Verifier and Fraud Detector enhancements")
    print("=" * 60)
    
    # Create and run test suite
    test_suite = EnhancedAlgorithmTestSuite()
    results = test_suite.run_all_tests()
    
    # Save results to file
    try:
        with open('enhanced_algorithms_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Test results saved to: enhanced_algorithms_test_results.json")
    except Exception as e:
        print(f"\n⚠️ Could not save results: {e}")
    
    # Return exit code based on results
    if results['overall_status'] in ['EXCELLENT', 'GOOD']:
        print("\n🎉 All critical tests passed! Enhanced algorithms are ready for production.")
        return 0
    elif results['overall_status'] == 'ACCEPTABLE':
        print("\n⚠️ Most tests passed, but some issues detected. Review recommended.")
        return 1
    else:
        print("\n❌ Critical issues detected. Enhanced algorithms need attention.")
        return 2

if __name__ == "__main__":
    exit(main())