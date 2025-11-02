#!/usr/bin/env python3
"""
Test Runner for Organized Test Suite
Run this from the project root directory to execute tests in their new organized structure.
"""

import sys
import os
import subprocess

# Add backend to Python path for Django imports
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def run_test_category(category):
    """Run tests from a specific category directory"""
    test_path = os.path.join('tests', 'backend', category)
    if not os.path.exists(test_path):
        print(f"❌ Test directory {test_path} does not exist")
        return False
    
    print(f"🧪 Running {category} tests from {test_path}")
    
    # Change to backend directory for Django context
    original_dir = os.getcwd()
    os.chdir('backend')
    
    try:
        # Run each test file in the category
        for test_file in os.listdir(os.path.join('..', test_path)):
            if test_file.startswith('test_') and test_file.endswith('.py'):
                test_file_path = os.path.join('..', test_path, test_file)
                print(f"  → Running {test_file}")
                
                # Use subprocess to run the test with proper Python path
                result = subprocess.run([
                    sys.executable, test_file_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"    ✅ PASSED")
                else:
                    print(f"    ❌ FAILED: {result.stderr[:200]}")
    
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    finally:
        os.chdir(original_dir)
    
    return True

def main():
    print("🚀 TCU CEAA Test Suite Runner")
    print("=" * 50)
    
    categories = ['ai_tests', 'django_tests', 'integration_tests']
    
    if len(sys.argv) > 1:
        # Run specific category
        category = sys.argv[1]
        if category in categories:
            run_test_category(category)
        else:
            print(f"❌ Unknown category: {category}")
            print(f"Available categories: {', '.join(categories)}")
    else:
        # Run all categories
        print("Running all test categories...")
        for category in categories:
            print(f"\n📁 {category.upper()}")
            print("-" * 30)
            run_test_category(category)

if __name__ == '__main__':
    main()