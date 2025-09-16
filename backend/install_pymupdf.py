#!/usr/bin/env python3
"""
PyMuPDF Installation Script
Handles platform-specific installation of PyMuPDF with proper wheel selection
"""

import subprocess
import sys
import platform
import os

def install_pymupdf():
    """Install PyMuPDF with platform-specific handling"""
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    
    # First, try to install with pre-compiled wheels only
    try:
        print("\nAttempting to install PyMuPDF with pre-compiled wheels...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--only-binary=PyMuPDF", 
            "PyMuPDF==1.24.10"
        ])
        print("✅ PyMuPDF installed successfully with pre-compiled wheels!")
        return True
        
    except subprocess.CalledProcessError:
        print("⚠️ Pre-compiled wheels not available, attempting source installation...")
        
        # Install system dependencies for compilation (Linux/Ubuntu)
        if platform.system() == "Linux":
            try:
                subprocess.check_call([
                    "sudo", "apt-get", "update"
                ])
                subprocess.check_call([
                    "sudo", "apt-get", "install", "-y",
                    "libmupdf-dev", "libfreetype6-dev", "libharfbuzz-dev",
                    "libopenjp2-7-dev", "libjbig2dec0-dev", "build-essential"
                ])
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Could not install system dependencies: {e}")
        
        # Try source installation with proper flags
        try:
            env = os.environ.copy()
            # Set flags to use system MuPDF if available
            env["PYMUPDF_SETUP_MUPDF_BUILD"] = "0"  # Don't build MuPDF from source
            
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--no-binary=PyMuPDF",
                "PyMuPDF==1.24.10"
            ], env=env)
            print("✅ PyMuPDF installed successfully from source!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyMuPDF from source: {e}")
            
            # Fallback to older version that might have better wheel support
            try:
                print("Trying fallback to older PyMuPDF version...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "PyMuPDF==1.23.26"
                ])
                print("✅ PyMuPDF fallback version installed successfully!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Fallback installation also failed: {e}")
                return False

def test_installation():
    """Test if PyMuPDF is working correctly"""
    try:
        import fitz
        print(f"✅ PyMuPDF imported successfully!")
        print(f"   Version: {fitz.version[0]}")
        print(f"   MuPDF Version: {fitz.version[1]}")
        
        # Test basic functionality
        doc = fitz.open()  # Create empty document
        page = doc.new_page()
        page.insert_text((72, 72), "Test text")
        doc.close()
        print("✅ Basic PyMuPDF functionality test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ PyMuPDF import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PyMuPDF functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("PyMuPDF Installation Script")
    print("=" * 40)
    
    if install_pymupdf():
        if test_installation():
            print("\n🎉 PyMuPDF installation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ PyMuPDF installation verification failed!")
            sys.exit(1)
    else:
        print("\n❌ PyMuPDF installation failed!")
        sys.exit(1)
