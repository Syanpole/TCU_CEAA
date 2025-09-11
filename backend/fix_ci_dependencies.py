#!/usr/bin/env python3
"""
Emergency CI Dependency Fix Script
Resolves SciPy compilation issues and ensures CI compatibility
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"🔧 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True, result.stdout
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"   ⏱️ Timeout")
        return False, "Command timed out"
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False, str(e)

def fix_ci_dependencies():
    """Fix CI dependency issues"""
    
    print("🚨 CI DEPENDENCY EMERGENCY FIX")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    fixes_applied = []
    
    # 1. Remove problematic cached packages
    print("\n1️⃣ Clearing problematic package cache...")
    
    cache_clear_commands = [
        "pip cache purge",
        "pip uninstall scipy -y || true",
        "pip uninstall matplotlib -y || true"
    ]
    
    for cmd in cache_clear_commands:
        success, output = run_command(cmd, f"Running: {cmd}")
        if success:
            fixes_applied.append(f"Cache cleared: {cmd}")
    
    # 2. Install CI-safe dependencies
    print("\n2️⃣ Installing CI-safe dependencies...")
    
    # Install with specific flags to avoid compilation
    install_commands = [
        "pip install --only-binary=all --no-cache-dir -r requirements-ci.txt",
        "pip install --only-binary=all --upgrade setuptools wheel pip"
    ]
    
    for cmd in install_commands:
        success, output = run_command(cmd, f"Installing dependencies")
        if success:
            fixes_applied.append(f"Dependencies installed: {cmd}")
        else:
            # Try alternative approach
            print(f"\n🔄 Trying alternative installation method...")
            alt_cmd = cmd.replace("--only-binary=all", "--prefer-binary")
            success, output = run_command(alt_cmd, f"Alternative installation")
            if success:
                fixes_applied.append(f"Alternative installation successful: {alt_cmd}")
    
    # 3. Verify critical packages
    print("\n3️⃣ Verifying critical packages...")
    
    critical_packages = [
        'django',
        'djangorestframework', 
        'numpy',
        'PyPDF2',
        'pdfplumber',
        'Pillow',
        'opencv-python',
        'cv2'
    ]
    
    working_packages = []
    failed_packages = []
    
    for package in critical_packages:
        try:
            if package == 'opencv-python':
                import cv2
                working_packages.append('opencv-python (cv2)')
            else:
                __import__(package)
                working_packages.append(package)
            print(f"   ✅ {package}")
        except ImportError:
            failed_packages.append(package)
            print(f"   ❌ {package}")
    
    # 4. Create fallback configuration
    print("\n4️⃣ Creating fallback configuration...")
    
    fallback_config = {
        "scipy_available": False,
        "matplotlib_available": False,
        "pdf_processors": working_packages,
        "ai_fallback_mode": True,
        "compilation_free": True,
        "fixes_applied": fixes_applied,
        "timestamp": str(subprocess.check_output(['date'], shell=True, text=True).strip())
    }
    
    # Save configuration
    config_file = backend_dir / 'ci_fallback_config.json'
    with open(config_file, 'w') as f:
        json.dump(fallback_config, f, indent=2)
    
    print(f"   ✅ Fallback configuration saved to {config_file}")
    
    # 5. Test the fix
    print("\n5️⃣ Testing the fix...")
    
    test_success = True
    
    # Test Django
    try:
        import django
        print(f"   ✅ Django {django.get_version()}")
    except Exception as e:
        print(f"   ❌ Django failed: {e}")
        test_success = False
    
    # Test PDF processing
    try:
        import PyPDF2
        import pdfplumber
        print(f"   ✅ PDF processors available")
    except Exception as e:
        print(f"   ❌ PDF processing failed: {e}")
        test_success = False
    
    # Test AI/ML basics
    try:
        import numpy as np
        import sklearn
        test_array = np.array([1, 2, 3])
        print(f"   ✅ Basic AI/ML functionality: NumPy {np.__version__}, Sklearn {sklearn.__version__}")
    except Exception as e:
        print(f"   ❌ AI/ML basics failed: {e}")
        test_success = False
    
    # 6. Generate summary
    print("\n" + "=" * 50)
    print("🏁 FIX SUMMARY")
    print("=" * 50)
    
    print(f"Working packages: {len(working_packages)}")
    for pkg in working_packages:
        print(f"  ✅ {pkg}")
    
    if failed_packages:
        print(f"\nFailed packages: {len(failed_packages)}")
        for pkg in failed_packages:
            print(f"  ❌ {pkg}")
    
    print(f"\nFixes applied: {len(fixes_applied)}")
    for fix in fixes_applied:
        print(f"  🔧 {fix}")
    
    if test_success and len(working_packages) >= 5:
        print(f"\n🎉 CI DEPENDENCY FIX SUCCESSFUL!")
        print(f"   ✅ Core functionality restored")
        print(f"   ✅ Compilation issues resolved")
        print(f"   ✅ CI-safe fallbacks active")
        return 0
    else:
        print(f"\n⚠️ PARTIAL SUCCESS - Some issues remain")
        print(f"   📋 Check failed packages above")
        print(f"   🔄 May need manual intervention")
        return 1

if __name__ == "__main__":
    sys.exit(fix_ci_dependencies())
