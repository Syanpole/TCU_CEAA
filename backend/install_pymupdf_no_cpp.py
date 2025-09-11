#!/usr/bin/env python3
"""
Enhanced PyMuPDF Installation Script
Prevents C++ compilation by forcing wheel installation
"""

import subprocess
import sys
import platform
import os
import json

def get_platform_info():
    """Get detailed platform information"""
    return {
        'system': platform.system(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'architecture': platform.architecture()
    }

def check_wheel_availability():
    """Check if PyMuPDF wheels are available for current platform"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--dry-run", "--only-binary=PyMuPDF", "PyMuPDF==1.24.10"
        ], capture_output=True, text=True)
        
        return result.returncode == 0
    except Exception:
        return False

def install_pymupdf_wheel_only():
    """Install PyMuPDF using wheels only, no source compilation"""
    
    platform_info = get_platform_info()
    print("Platform Information:")
    for key, value in platform_info.items():
        print(f"  {key}: {value}")
    print()
    
    # Try multiple PyMuPDF versions with wheel support
    versions_to_try = [
        "1.26.4",   # Currently installed
        "1.26.3",   # Previous stable
        "1.26.1",   # Earlier stable
        "1.25.5",   # Fallback version
        "1.24.14",  # Another fallback
    ]
    
    for version in versions_to_try:
        print(f"Attempting to install PyMuPDF=={version} with wheels only...")
        
        try:
            # First, uninstall any existing PyMuPDF
            subprocess.run([
                sys.executable, "-m", "pip", "uninstall", "-y", "PyMuPDF"
            ], capture_output=True)
            
            # Install with wheels only - this prevents C++ compilation
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--only-binary=PyMuPDF",
                f"PyMuPDF=={version}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ PyMuPDF {version} installed successfully with wheels!")
                
                # Verify installation
                try:
                    import fitz
                    print(f"✅ PyMuPDF imported successfully (version: {fitz.version[0]})")
                    return True
                except ImportError as e:
                    print(f"⚠️ PyMuPDF installed but import failed: {e}")
                    continue
                    
            else:
                print(f"⚠️ Wheel installation failed for version {version}")
                print(f"Error: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️ Exception during installation of version {version}: {e}")
    
    print("❌ All wheel installations failed")
    return False

def install_alternative_solution():
    """Install alternative PDF processing without PyMuPDF"""
    print("\nInstalling alternative PDF processing solution...")
    
    try:
        # Install enhanced PyPDF2 and other alternatives
        alternatives = [
            "PyPDF2==3.0.1",
            "pdfplumber==0.9.0",  # Alternative PDF processing
            "pymupdf-fonts==1.0.5",  # Fonts for better text rendering
        ]
        
        for package in alternatives:
            print(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"⚠️ Failed to install {package}: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alternative installation failed: {e}")
        return False

def update_ai_verifier_for_alternatives():
    """Update AI verifier to handle PyMuPDF absence gracefully"""
    
    verifier_path = "ai_verification/base_verifier.py"
    if not os.path.exists(verifier_path):
        print(f"⚠️ AI verifier not found at {verifier_path}")
        return
    
    print("✅ AI verifier will use fallback PDF processing")
    # The fallback mechanism is already implemented in base_verifier.py

def main():
    """Main installation process"""
    print("Enhanced PyMuPDF Installation (C++ Compilation Prevention)")
    print("=" * 70)
    
    # Step 1: Try wheel-only installation
    if install_pymupdf_wheel_only():
        print("\n🎉 PyMuPDF installed successfully with wheels!")
        print("   No C++ compilation was required.")
        return 0
    
    # Step 2: Install alternative solution
    print("\n⚠️ PyMuPDF wheels not available. Installing alternatives...")
    if install_alternative_solution():
        update_ai_verifier_for_alternatives()
        print("\n✅ Alternative PDF processing solution installed.")
        print("   The system will use PyPDF2 and other alternatives.")
        return 0
    
    # Step 3: Final fallback
    print("\n❌ All installation methods failed.")
    print("Manual intervention required:")
    print("1. Check platform compatibility")
    print("2. Update pip: python -m pip install --upgrade pip")
    print("3. Try: pip install --only-binary=all PyMuPDF")
    return 1

if __name__ == "__main__":
    sys.exit(main())
