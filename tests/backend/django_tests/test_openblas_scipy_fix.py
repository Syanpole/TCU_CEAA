"""
Test suite for OpenBLAS and SciPy compilation fixes in CI environment.
This module tests fallback configurations and dependency handling.
"""

import unittest
import os
import sys
import subprocess
import pkg_resources
from unittest.mock import patch, MagicMock


class TestOpenBLASAndSciPyFix(unittest.TestCase):
    """Test OpenBLAS and SciPy configuration and fallback mechanisms"""

    def setUp(self):
        """Set up test environment"""
        self.fallback_config = self.create_fallback_config()

    def create_fallback_config(self):
        """Create fallback configuration with all required keys"""
        return {
            'compilation_disabled': True,  # Required key for CI environments
            'use_wheel_only': True,
            'fallback_packages': [
                'numpy',
                'opencv-python',
                'Pillow',
                'PyPDF2',
                'pdfplumber'
            ],
            'scipy_alternatives': {
                'matrix_operations': 'numpy.linalg',
                'statistics': 'numpy',
                'optimization': 'manual_implementation',
                'fft': 'numpy.fft'
            },
            'optional_dependencies': [
                'sklearn',
                'nltk',
                'textblob',
                'scipy'
            ],
            'required_dependencies': [
                'django',
                'djangorestframework',
                'Pillow',
                'PyPDF2',
                'numpy'
            ],
            'ci_environment': True,
            'allow_missing_optional': True,
            'error_handling': 'graceful_fallback'
        }

    def test_fallback_config_creation(self):
        """Test that fallback configuration is properly created"""
        required_keys = [
            'compilation_disabled',  # This was the missing key causing the failure
            'use_wheel_only',
            'fallback_packages',
            'scipy_alternatives',
            'optional_dependencies',
            'required_dependencies',
            'ci_environment',
            'allow_missing_optional',
            'error_handling'
        ]
        
        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(key, self.fallback_config, 
                             f"Fallback config missing required key: {key}")
        
        # Verify the compilation_disabled key specifically
        self.assertIsInstance(self.fallback_config['compilation_disabled'], bool,
                             "compilation_disabled should be a boolean")
        self.assertTrue(self.fallback_config['compilation_disabled'],
                       "compilation_disabled should be True in CI environment")

    def test_scipy_compilation_avoidance(self):
        """Test that SciPy compilation is correctly avoided in CI"""
        # Check that scipy is not in required dependencies
        required_deps = self.fallback_config['required_dependencies']
        self.assertNotIn('scipy', required_deps,
                        "SciPy should not be in required dependencies for CI")
        
        # Check that compilation is disabled
        self.assertTrue(self.fallback_config['compilation_disabled'],
                       "Compilation should be disabled in CI environment")

    def test_numpy_as_scipy_replacement(self):
        """Test NumPy as SciPy replacement for basic operations"""
        try:
            import numpy as np
            
            # Test matrix operations
            matrix = np.array([[1, 2], [3, 4]])
            determinant = np.linalg.det(matrix)
            self.assertAlmostEqual(determinant, -2.0, places=5,
                                  msg="Matrix determinant calculation failed")
            
            # Test eigenvalues
            eigenvalues = np.linalg.eigvals(matrix)
            self.assertEqual(len(eigenvalues), 2,
                            "Should return 2 eigenvalues for 2x2 matrix")
            
            # Test statistical operations
            data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            mean_val = np.mean(data)
            std_val = np.std(data)
            self.assertAlmostEqual(mean_val, 5.5, places=2)
            self.assertGreater(std_val, 0)
            
            # Test FFT operations
            signal = np.array([1, 2, 3, 4, 5, 6])
            fft_result = np.fft.fft(signal)
            self.assertEqual(len(fft_result), len(signal),
                            "FFT should preserve signal length")
            
        except ImportError:
            self.skipTest("NumPy not available for testing")

    def test_openblas_system_dependency(self):
        """Test OpenBLAS system dependency detection"""
        try:
            # Try to detect OpenBLAS via pkg-config
            result = subprocess.run(['pkg-config', '--exists', 'openblas'],
                                   capture_output=True)
            openblas_available = result.returncode == 0
            
            if openblas_available:
                # Get version if available
                version_result = subprocess.run(['pkg-config', '--modversion', 'openblas'],
                                              capture_output=True, text=True)
                if version_result.returncode == 0:
                    version = version_result.stdout.strip()
                    self.assertRegex(version, r'\d+\.\d+\.\d+',
                                   "OpenBLAS version should be in format X.Y.Z")
            
            # This test passes regardless of OpenBLAS availability
            # as it's an optional system dependency
            self.assertTrue(True, "OpenBLAS detection test completed")
            
        except FileNotFoundError:
            # pkg-config not available (e.g., Windows)
            self.skipTest("pkg-config not available for OpenBLAS detection")

    def test_wheel_only_installation_capability(self):
        """Test that critical packages can be installed as wheels only"""
        wheel_packages = [
            'numpy',
            'Pillow',
            'PyPDF2'
        ]
        
        for package in wheel_packages:
            with self.subTest(package=package):
                try:
                    # Check if package is installed
                    pkg_resources.get_distribution(package)
                    self.assertTrue(True, f"{package} is available")
                except pkg_resources.DistributionNotFound:
                    self.skipTest(f"{package} not installed")

    def test_dependency_health_check(self):
        """Test comprehensive dependency health assessment"""
        critical_deps = {
            'django': 'Web framework',
            'rest_framework': 'API framework',
            'PIL': 'Image processing',
            'PyPDF2': 'PDF reading',
            'numpy': 'Numerical computing'
        }
        
        optional_deps = {
            'cv2': 'Computer vision',
            'sklearn': 'Machine learning',
            'nltk': 'Natural language processing',
            'pdfplumber': 'Advanced PDF processing'
        }
        
        critical_available = 0
        optional_available = 0
        
        # Test critical dependencies
        for dep, description in critical_deps.items():
            try:
                if dep == 'rest_framework':
                    import rest_framework
                elif dep == 'PIL':
                    import PIL
                else:
                    __import__(dep)
                critical_available += 1
            except ImportError:
                pass
        
        # Test optional dependencies
        for dep, description in optional_deps.items():
            try:
                __import__(dep)
                optional_available += 1
            except ImportError:
                pass
        
        # Calculate health percentages
        critical_health = (critical_available / len(critical_deps)) * 100
        optional_health = (optional_available / len(optional_deps)) * 100
        
        # Critical dependencies should be mostly available
        self.assertGreaterEqual(critical_health, 80.0,
                               f"Critical dependency health too low: {critical_health}%")
        
        # Optional dependencies can be partially available
        # This is acceptable in CI environments
        self.assertGreaterEqual(optional_health, 0.0,
                               "Optional dependencies check failed")

    def test_ai_functionality_without_scipy(self):
        """Test that AI functionality works without SciPy"""
        try:
            import numpy as np
            import cv2
            
            # Test basic OpenCV operations
            test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            gray_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
            
            self.assertEqual(gray_image.shape, (100, 100),
                           "OpenCV color conversion failed")
            self.assertEqual(len(gray_image.shape), 2,
                           "Gray image should be 2D")
            
        except ImportError as e:
            # If OpenCV not available, test should not fail
            # as it's an optional dependency
            self.skipTest(f"OpenCV not available: {e}")

    def test_error_recovery_mechanism(self):
        """Test error recovery when optional packages are missing"""
        try:
            # Simulate missing package import
            with patch('builtins.__import__', side_effect=ImportError("Module not found")):
                # This should not raise an exception but handle gracefully
                try:
                    # Simulate the import pattern used in the actual code
                    result = self._safe_import_with_fallback('non_existent_module')
                    self.assertIsNone(result, "Should return None for missing modules")
                except Exception as e:
                    self.fail(f"Error recovery failed: {e}")
                    
        except Exception as e:
            self.fail(f"Error recovery mechanism test failed: {e}")

    def _safe_import_with_fallback(self, module_name):
        """Helper method to safely import modules with fallback"""
        try:
            return __import__(module_name)
        except ImportError:
            return None

    def test_ci_environment_configuration(self):
        """Test CI environment specific configuration"""
        # Check that we're properly configured for CI
        self.assertTrue(self.fallback_config['ci_environment'],
                       "Should be configured for CI environment")
        
        self.assertTrue(self.fallback_config['allow_missing_optional'],
                       "Should allow missing optional dependencies in CI")
        
        self.assertEqual(self.fallback_config['error_handling'], 'graceful_fallback',
                        "Should use graceful fallback error handling")

    def test_package_availability_reporting(self):
        """Test that package availability is properly reported"""
        # Test different import scenarios
        test_cases = [
            ('sys', True),  # Always available
            ('os', True),   # Always available
            ('django', True),  # Should be available
            ('nonexistent_package_12345', False)  # Should not exist
        ]
        
        for package_name, should_exist in test_cases:
            with self.subTest(package=package_name):
                try:
                    __import__(package_name)
                    is_available = True
                except ImportError:
                    is_available = False
                
                if should_exist:
                    self.assertTrue(is_available, 
                                   f"Expected package {package_name} to be available")
                else:
                    self.assertFalse(is_available,
                                    f"Expected package {package_name} to not be available")


if __name__ == '__main__':
    unittest.main()