#!/usr/bin/env python3
"""
Python 3.12+ Compatibility Checker for TCU-CEAA
Checks for common compatibility issues with Python 3.12+
"""

import sys
import importlib.util
import warnings

def check_python_version():
    """Check if Python version is compatible"""
    print(f"🐍 Python Version: {sys.version}")
    
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 12:
        print("✅ Python 3.12+ detected - checking compatibility...")
        return True
    else:
        print("⚠️ Python version < 3.12 - some checks may not apply")
        return False

def check_pkgutil_compatibility():
    """Check for pkgutil.ImpImporter usage"""
    print("\n🔍 Checking pkgutil compatibility...")
    
    try:
        import pkgutil
        
        # Try to access ImpImporter (should fail in Python 3.12+)
        if hasattr(pkgutil, 'ImpImporter'):
            print("⚠️ pkgutil.ImpImporter found - this may cause issues in Python 3.12+")
            return False
        else:
            print("✅ pkgutil.ImpImporter not found - compatibility OK")
            return True
            
    except Exception as e:
        print(f"❌ Error checking pkgutil: {e}")
        return False

def check_dependencies():
    """Check if all dependencies can be imported"""
    print("\n📦 Checking dependency imports...")
    
    dependencies = [
        ('Django', 'django'),
        ('Django REST Framework', 'rest_framework'),
        ('CORS Headers', 'corsheaders'),
        ('Pillow', 'PIL'),
        ('PyPDF2', 'PyPDF2'),
        ('OpenCV', 'cv2'),
        ('NumPy', 'numpy'),
        ('Pytesseract', 'pytesseract'),
        ('Scikit-learn', 'sklearn'),
        ('NLTK', 'nltk'),
        ('Python-docx', 'docx'),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for name, module in dependencies:
        try:
            spec = importlib.util.find_spec(module)
            if spec is not None:
                # Try to actually import it
                importlib.import_module(module)
                print(f"✅ {name}")
                success_count += 1
            else:
                print(f"❌ {name} - Module not found")
        except ImportError as e:
            print(f"❌ {name} - Import error: {e}")
        except Exception as e:
            print(f"⚠️ {name} - Other error: {e}")
    
    print(f"\n📊 Dependencies: {success_count}/{total_count} successfully imported")
    return success_count == total_count

def check_wheel_compatibility():
    """Check wheel and setuptools versions"""
    print("\n🛠️ Checking build tools...")
    
    try:
        import setuptools
        print(f"✅ setuptools: {setuptools.__version__}")
    except ImportError:
        print("❌ setuptools not found")
    
    try:
        import wheel
        print(f"✅ wheel: {wheel.__version__}")
    except ImportError:
        print("❌ wheel not found")

def main():
    """Run all compatibility checks"""
    print("🚀 TCU-CEAA Python 3.12+ Compatibility Checker")
    print("=" * 50)
    
    is_python_312_plus = check_python_version()
    pkgutil_ok = check_pkgutil_compatibility()
    deps_ok = check_dependencies()
    check_wheel_compatibility()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    
    if is_python_312_plus and pkgutil_ok and deps_ok:
        print("✅ All compatibility checks passed!")
        print("🎉 Ready for Python 3.12+ deployment")
        return True
    else:
        print("⚠️ Some compatibility issues found")
        if not pkgutil_ok:
            print("❌ pkgutil compatibility issues detected")
        if not deps_ok:
            print("❌ Dependency import issues detected")
        
        print("\n🔧 Suggested fixes:")
        print("1. Update dependencies: pip install -U -r requirements.txt")
        print("2. Install build tools: pip install -U setuptools wheel")
        print("3. Check for deprecated package usage")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Compatibility check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
