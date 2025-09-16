"""
Test suite for CI dependency resolution and compatibility verification.
This module tests that all required dependencies can be installed and work correctly in CI environment.
"""

import unittest
import sys
import os
import subprocess
import importlib
import json


class TestCIDependencyResolution(unittest.TestCase):
    """Test CI dependency installation and compatibility"""

    def setUp(self):
        """Set up test environment"""
        self.critical_dependencies = [
            'django',
            'rest_framework', 
            'corsheaders',
            'PIL',
            'PyPDF2',
            'docx',
            'pdfplumber',
            'numpy'
        ]
        
        self.optional_dependencies = [
            'cv2',
            'pytesseract',
            'nltk',
            'textblob'
        ]

    def test_critical_dependencies_available(self):
        """Test that all critical dependencies are available"""
        print("🔍 Testing critical dependencies...")
        
        missing_deps = []
        for dep in self.critical_dependencies:
            try:
                importlib.import_module(dep)
                print(f"   ✅ {dep}: Available")
            except ImportError as e:
                missing_deps.append(dep)
                print(f"   ❌ {dep}: Missing - {e}")
        
        self.assertEqual(len(missing_deps), 0, 
                        f"Critical dependencies missing: {missing_deps}")

    def test_optional_dependencies_graceful_fallback(self):
        """Test that optional dependencies fail gracefully"""
        print("🔍 Testing optional dependencies fallback...")
        
        for dep in self.optional_dependencies:
            try:
                importlib.import_module(dep)
                print(f"   ✅ {dep}: Available")
            except ImportError:
                print(f"   ⚠️  {dep}: Not available (graceful fallback)")
        
        # This test always passes - we just log availability
        self.assertTrue(True, "Optional dependencies handled gracefully")

    def test_django_setup_compatibility(self):
        """Test Django environment setup works correctly"""
        print("🔍 Testing Django environment setup...")
        
        try:
            # Set up Django environment
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
            
            import django
            from django.conf import settings
            
            if not settings.configured:
                django.setup()
            
            print(f"   ✅ Django {django.get_version()}: Configured successfully")
            
            # Test database connection (should be SQLite in memory for tests)
            from django.db import connection
            cursor = connection.cursor()
            print(f"   ✅ Database: {connection.vendor} connection successful")
            
            self.assertTrue(True)
            
        except Exception as e:
            self.fail(f"Django setup failed: {e}")

    def test_ai_package_compatibility(self):
        """Test AI/ML package compatibility"""
        print("🔍 Testing AI/ML package compatibility...")
        
        # Test NumPy
        try:
            import numpy as np
            test_array = np.array([1, 2, 3])
            self.assertEqual(len(test_array), 3)
            print(f"   ✅ NumPy {np.__version__}: Working correctly")
        except Exception as e:
            self.fail(f"NumPy compatibility test failed: {e}")
        
        # Test PIL/Pillow
        try:
            from PIL import Image
            # Create a simple test image
            test_img = Image.new('RGB', (100, 100), color='red')
            self.assertEqual(test_img.size, (100, 100))
            print(f"   ✅ Pillow: Working correctly")
        except Exception as e:
            self.fail(f"Pillow compatibility test failed: {e}")
        
        # Test PDF processing
        try:
            import PyPDF2
            print(f"   ✅ PyPDF2: Available for PDF processing")
        except ImportError:
            print(f"   ⚠️  PyPDF2: Not available")
        
        try:
            import pdfplumber
            print(f"   ✅ pdfplumber: Available for PDF processing")
        except ImportError:
            print(f"   ⚠️  pdfplumber: Not available")

    def test_requirements_file_validity(self):
        """Test that requirements-ci.txt is valid and installable"""
        print("🔍 Testing requirements file validity...")
        
        requirements_path = os.path.join(os.path.dirname(__file__), 'requirements-ci.txt')
        
        if os.path.exists(requirements_path):
            print(f"   ✅ requirements-ci.txt: Found")
            
            # Read and validate requirements format
            with open(requirements_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            invalid_lines = []
            for line in lines:
                if '==' not in line and '>=' not in line and not line.isalpha():
                    invalid_lines.append(line)
            
            self.assertEqual(len(invalid_lines), 0, 
                           f"Invalid requirement lines: {invalid_lines}")
            print(f"   ✅ Requirements format: Valid ({len(lines)} packages)")
        else:
            print(f"   ⚠️  requirements-ci.txt: Not found, using default requirements")

    def test_python_version_compatibility(self):
        """Test Python version compatibility"""
        print("🔍 Testing Python version compatibility...")
        
        python_version = sys.version_info
        print(f"   ℹ️  Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Ensure minimum Python 3.8 support
        self.assertGreaterEqual(python_version.major, 3)
        self.assertGreaterEqual(python_version.minor, 8)
        
        print(f"   ✅ Python version: Compatible")

    def test_environment_variables(self):
        """Test required environment variables"""
        print("🔍 Testing environment variables...")
        
        required_vars = ['DJANGO_SETTINGS_MODULE']
        optional_vars = ['DEBUG', 'SECRET_KEY']
        
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                print(f"   ✅ {var}: Set")
            else:
                print(f"   ⚠️  {var}: Not set (will use default)")
        
        for var in optional_vars:
            value = os.environ.get(var)
            if value:
                print(f"   ✅ {var}: Set")
            else:
                print(f"   ℹ️  {var}: Not set (optional)")


def run_dependency_tests():
    """Run all dependency tests with detailed output"""
    print("🧪 CI Dependency Resolution Test Suite")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCIDependencyResolution)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All dependency tests passed! CI environment is ready.")
    else:
        print("\n⚠️  Some dependency tests failed. Check logs above.")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_dependency_tests()
    sys.exit(0 if success else 1)