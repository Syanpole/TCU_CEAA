#!/usr/bin/env python3
"""
CI Test Runner for TCU-CEAA
This script helps run tests from the reorganized repository structure
"""

import os
import sys
import subprocess


def run_ci_dependency_test():
    """Run the CI dependency resolution test"""
    print("🧪 Running CI dependency resolution test...")
    
    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the test file in the reorganized structure
    test_file = os.path.join(script_dir, 'tests', 'backend', 'integration_tests', 'test_ci_dependency_resolution.py')
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Run the test from the backend directory for proper Django setup
        backend_dir = os.path.join(script_dir, 'backend')
        os.chdir(backend_dir)
        
        result = subprocess.run([
            sys.executable, 
            os.path.relpath(test_file, backend_dir)
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def run_all_backend_tests():
    """Run Django tests"""
    print("🧪 Running Django application tests...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, 'backend')
    
    try:
        os.chdir(backend_dir)
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', 'myapp', '--verbosity=2'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running Django tests: {e}")
        return False


def main():
    """Main test runner"""
    print("🚀 TCU-CEAA CI Test Runner")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    all_passed = True
    
    # Run dependency tests
    if not run_ci_dependency_test():
        all_passed = False
    
    print("\n" + "=" * 50)
    
    # Run Django tests
    if not run_all_backend_tests():
        all_passed = False
    
    print("\n" + "=" * 50)
    print("📊 Final Result:")
    
    if all_passed:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()