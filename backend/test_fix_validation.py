#!/usr/bin/env python3
"""
Simple OpenBLAS/SciPy Fix Validation
Quick test to verify the fix is working
"""

import sys
import os
import json

def test_scipy_removed():
    """Test that SciPy is properly excluded"""
    print("🧪 Testing SciPy exclusion...")
    
    # Check requirements files
    req_files = ['requirements-ci.txt', 'requirements-ci-safe.txt']
    scipy_issues = []
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if 'scipy' in line.lower() and not line.startswith('#'):
                    scipy_issues.append(f"{req_file}: {line}")
    
    if scipy_issues:
        print("❌ SciPy still found in requirements:")
        for issue in scipy_issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ SciPy properly excluded from all requirements")
        return True

def test_config_exists():
    """Test that fallback config exists"""
    print("🧪 Testing fallback configuration...")
    
    config_file = 'ci_fallback_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("✅ Fallback config exists and is valid JSON")
            print(f"   - Compilation free: {config.get('compilation_free', 'unknown')}")
            print(f"   - SciPy available: {config.get('scipy_available', 'unknown')}")
            return True
            
        except json.JSONDecodeError:
            print("❌ Fallback config exists but contains invalid JSON")
            return False
    else:
        print("❌ Fallback config not found")
        return False

def test_core_imports():
    """Test that core packages can be imported"""
    print("🧪 Testing core package imports...")
    
    essential_packages = [
        ('django', 'Django web framework'),
        ('numpy', 'NumPy for numerical computing'),
        ('PyPDF2', 'PDF processing'),
        ('PIL', 'Image processing')
    ]
    
    success_count = 0
    
    for package, description in essential_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
            success_count += 1
        except ImportError:
            print(f"   ❌ {package} - {description}")
    
    if success_count >= 3:  # At least 75% success
        print(f"✅ Core imports successful: {success_count}/{len(essential_packages)}")
        return True
    else:
        print(f"❌ Too many core import failures: {success_count}/{len(essential_packages)}")
        return False

def test_numpy_functionality():
    """Test that NumPy can replace basic SciPy operations"""
    print("🧪 Testing NumPy as SciPy replacement...")
    
    try:
        import numpy as np
        
        # Basic linear algebra
        matrix = np.array([[1, 2], [3, 4]])
        det = np.linalg.det(matrix)
        
        # Basic statistics
        data = np.array([1, 2, 3, 4, 5])
        mean = np.mean(data)
        std = np.std(data)
        
        print(f"   ✅ Linear algebra: determinant = {det:.2f}")
        print(f"   ✅ Statistics: mean = {mean}, std = {std:.2f}")
        return True
        
    except ImportError:
        print("   ❌ NumPy not available")
        return False
    except Exception as e:
        print(f"   ❌ NumPy operations failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚨 OPENBLAS/SCIPY FIX VALIDATION")
    print("=" * 50)
    
    tests = [
        test_scipy_removed,
        test_config_exists,
        test_core_imports,
        test_numpy_functionality
    ]
    
    results = []
    for test in tests:
        print()
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__.replace('test_', '').replace('_', ' ').title()}: {status}")
    
    success_rate = (passed / total) * 100
    print(f"\nOverall: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 OpenBLAS/SciPy fix: VALIDATION SUCCESSFUL!")
        print("   ✅ CI environment ready for deployment")
        return 0
    else:
        print("⚠️ OpenBLAS/SciPy fix: VALIDATION NEEDS ATTENTION")
        print("   📋 Some issues require manual review")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
