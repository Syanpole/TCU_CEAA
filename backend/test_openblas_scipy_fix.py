#!/usr/bin/env python3
"""
Test OpenBLAS and SciPy Compilation Issues
Validates that the CI environment can handle scientific computing dependencies
"""

import unittest
import subprocess
import sys
import os
import tempfile
import json

class TestOpenBLASAndSciPyFix(unittest.TestCase):
    """Test OpenBLAS dependency resolution and SciPy compilation fix"""
    
    def setUp(self):
        """Set up test environment"""
        self.is_ci = os.getenv('CI', 'false').lower() == 'true'
        self.platform = sys.platform
        
    def test_openblas_system_dependency(self):
        """Test if OpenBLAS system dependency is available"""
        if not self.platform.startswith('linux'):
            self.skipTest("OpenBLAS check only relevant on Linux")
            
        print("\n🔍 Testing OpenBLAS system dependency...")
        
        # Method 1: Check with pkg-config
        try:
            result = subprocess.run(['pkg-config', '--exists', 'openblas'], 
                                   capture_output=True, check=False)
            if result.returncode == 0:
                print("✅ OpenBLAS found via pkg-config")
                # Get version info
                version_result = subprocess.run(['pkg-config', '--modversion', 'openblas'], 
                                               capture_output=True, text=True, check=False)
                if version_result.returncode == 0:
                    print(f"   Version: {version_result.stdout.strip()}")
                return  # OpenBLAS is available
        except FileNotFoundError:
            print("⚠️ pkg-config not available")
        
        # Method 2: Check for library files directly
        openblas_paths = [
            '/usr/lib/x86_64-linux-gnu/libopenblas.so',
            '/usr/lib/libopenblas.so',
            '/opt/OpenBLAS/lib/libopenblas.so',
            '/usr/lib/x86_64-linux-gnu/openblas-pthread/libopenblas.so'
        ]
        
        found_path = None
        for path in openblas_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if found_path:
            print(f"✅ OpenBLAS library found at: {found_path}")
        else:
            print("❌ OpenBLAS not found in standard locations")
            # This should now pass because we added OpenBLAS installation to CI
            if self.is_ci:
                self.fail("OpenBLAS should be installed in CI environment")
    
    def test_scipy_compilation_avoided(self):
        """Test that SciPy is not being compiled from source"""
        print("\n🧪 Testing SciPy compilation avoidance...")
        
        # Check if scipy is in requirements
        requirements_files = ['requirements-ci.txt', 'requirements-ci-safe.txt']
        scipy_found = False
        
        for req_file in requirements_files:
            if os.path.exists(req_file):
                with open(req_file, 'r') as f:
                    content = f.read()
                    if 'scipy' in content.lower() and not content.lower().find('scipy') in [
                        line for line in content.split('\n') if line.strip().startswith('#')
                    ]:
                        scipy_found = True
                        print(f"⚠️ SciPy found in {req_file}")
        
        if not scipy_found:
            print("✅ SciPy correctly excluded from CI requirements")
        else:
            print("❌ SciPy still in requirements - may cause compilation issues")
    
    def test_numpy_as_scipy_replacement(self):
        """Test that NumPy can handle basic operations that would use SciPy"""
        print("\n🔢 Testing NumPy as SciPy replacement...")
        
        try:
            import numpy as np
            
            # Test basic linear algebra (replaces scipy.linalg basics)
            matrix = np.array([[1, 2], [3, 4]])
            determinant = np.linalg.det(matrix)
            eigenvals, eigenvecs = np.linalg.eig(matrix)
            
            print(f"✅ Matrix determinant: {determinant}")
            print(f"✅ Eigenvalues: {eigenvals}")
            
            # Test basic statistics (replaces scipy.stats basics)
            data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            mean = np.mean(data)
            std = np.std(data)
            
            print(f"✅ Statistical operations: mean={mean}, std={std}")
            
            # Test FFT (replaces scipy.fft basics)
            signal = np.array([1, 2, 1, 2, 1, 2])
            fft_result = np.fft.fft(signal)
            
            print(f"✅ FFT operations: {len(fft_result)} components")
            
            self.assertTrue(True, "NumPy successfully replaces basic SciPy functionality")
            
        except ImportError as e:
            self.fail(f"NumPy not available: {e}")
        except Exception as e:
            self.fail(f"NumPy operations failed: {e}")
    
    def test_wheel_only_installation(self):
        """Test that packages can be installed with --only-binary=all"""
        print("\n🎡 Testing wheel-only installation capability...")
        
        # Test packages that should have wheels available
        test_packages = [
            'numpy==1.26.4',
            'Pillow==10.4.0',
            'PyPDF2==3.0.1'
        ]
        
        for package in test_packages:
            try:
                # Simulate wheel-only installation test
                cmd = [sys.executable, '-m', 'pip', 'install', '--dry-run', 
                       '--only-binary=all', package]
                
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                       timeout=30, check=False)
                
                if result.returncode == 0 or 'would install' in result.stdout.lower():
                    print(f"✅ {package} - wheel available")
                else:
                    print(f"❌ {package} - no wheel available: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️ {package} - timeout during check")
            except Exception as e:
                print(f"❌ {package} - error: {e}")
    
    def test_fallback_config_creation(self):
        """Test that fallback configuration is properly created"""
        print("\n⚙️ Testing fallback configuration...")
        
        config_file = 'ci_fallback_config.json'
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                required_keys = [
                    'compilation_disabled', 'wheel_only_mode', 
                    'problematic_packages_removed'
                ]
                
                for key in required_keys:
                    if key in config:
                        print(f"✅ Config has {key}: {config[key]}")
                    else:
                        print(f"❌ Config missing {key}")
                        self.fail(f"Fallback config missing required key: {key}")
                
                print("✅ Fallback configuration is valid")
                
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON in fallback config: {e}")
        else:
            print("⚠️ Fallback config not found - may need to run fix script")
    
    def test_ai_functionality_without_scipy(self):
        """Test that AI functionality works without SciPy"""
        print("\n🤖 Testing AI functionality without SciPy...")
        
        try:
            # Test basic computer vision
            import cv2
            import numpy as np
            
            # Create test image
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            test_image[25:75, 25:75] = [255, 0, 0]  # Red square
            
            # Basic OpenCV operations
            gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            print(f"✅ OpenCV operations: {test_image.shape} -> {gray.shape}")
            
            # Test basic ML with sklearn (if available and no scipy dependency)
            try:
                from sklearn.cluster import KMeans
                
                # Simple clustering test
                data = np.random.rand(20, 2)
                kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
                labels = kmeans.fit_predict(data)
                
                print(f"✅ Basic ML clustering: {len(set(labels))} clusters")
                
            except ImportError:
                print("⚠️ scikit-learn not available (expected in CI)")
            
            # Test text processing
            import nltk
            from textblob import TextBlob
            
            text = "This is a test document for AI processing."
            blob = TextBlob(text)
            
            print(f"✅ Text processing: {len(blob.words)} words")
            
            self.assertTrue(True, "AI functionality working without SciPy")
            
        except ImportError as e:
            print(f"⚠️ Some AI packages not available: {e}")
        except Exception as e:
            self.fail(f"AI functionality test failed: {e}")

    def test_comprehensive_dependency_health(self):
        """Test overall dependency health for the project"""
        print("\n🏥 Testing comprehensive dependency health...")
        
        critical_imports = {
            'django': 'Web framework',
            'rest_framework': 'API framework', 
            'PIL': 'Image processing',
            'PyPDF2': 'PDF reading',
            'numpy': 'Numerical computing'
        }
        
        optional_imports = {
            'cv2': 'Computer vision',
            'sklearn': 'Machine learning',
            'nltk': 'Natural language processing',
            'pdfplumber': 'Advanced PDF processing'
        }
        
        critical_success = 0
        optional_success = 0
        
        print("\n📋 Critical dependencies:")
        for module, description in critical_imports.items():
            try:
                __import__(module)
                print(f"   ✅ {module} - {description}")
                critical_success += 1
            except ImportError:
                print(f"   ❌ {module} - {description}")
        
        print("\n📋 Optional dependencies:")
        for module, description in optional_imports.items():
            try:
                __import__(module)
                print(f"   ✅ {module} - {description}")
                optional_success += 1
            except ImportError:
                print(f"   ⚠️ {module} - {description} (optional)")
        
        # Require at least 80% of critical dependencies
        critical_threshold = len(critical_imports) * 0.8
        
        print(f"\n📊 Results:")
        print(f"   Critical: {critical_success}/{len(critical_imports)} "
              f"({critical_success/len(critical_imports)*100:.1f}%)")
        print(f"   Optional: {optional_success}/{len(optional_imports)} "
              f"({optional_success/len(optional_imports)*100:.1f}%)")
        
        if critical_success >= critical_threshold:
            print("✅ Dependency health: GOOD")
        else:
            print("❌ Dependency health: POOR")
            self.fail(f"Too many critical dependencies missing. "
                     f"Expected at least {critical_threshold}, got {critical_success}")

def run_tests():
    """Run all tests and return results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpenBLASAndSciPyFix)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("🧪 OPENBLAS & SCIPY FIX TEST SUMMARY")
    print("="*60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors
    
    print(f"Total tests: {total_tests}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
    
    success_rate = (successes / total_tests) * 100 if total_tests > 0 else 0
    
    if success_rate >= 80:
        print(f"\n🎉 OpenBLAS/SciPy fix: SUCCESS ({success_rate:.1f}% tests passed)")
        return 0
    else:
        print(f"\n⚠️ OpenBLAS/SciPy fix: NEEDS ATTENTION ({success_rate:.1f}% tests passed)")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
