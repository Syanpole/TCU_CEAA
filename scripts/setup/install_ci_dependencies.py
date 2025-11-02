#!/usr/bin/env python3
"""
CI-friendly dependency installer for TCU_CEAA project
Handles problematic packages that might fail compilation in CI environments
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run command and handle errors gracefully"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def install_ci_dependencies():
    """Install dependencies in CI-friendly way"""
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
        print(f"Changed to directory: {os.getcwd()}")
    
    # Install basic dependencies first
    basic_deps = [
        "pip install --upgrade pip wheel setuptools",
        "pip install Django==5.2.5",
        "pip install djangorestframework==3.15.2", 
        "pip install django-cors-headers==4.4.0",
        "pip install psycopg[binary]==3.2.3",
        "pip install Pillow==10.4.0"
    ]
    
    print("Installing basic Django dependencies...")
    for cmd in basic_deps:
        if not run_command(cmd, f"Installing {cmd.split('==')[0].split()[-1]}"):
            print(f"Failed to install {cmd}, but continuing...")
    
    # Install document processing
    doc_deps = [
        "pip install PyPDF2==3.0.1",
        "pip install python-docx==1.1.2", 
        "pip install pdfplumber==0.9.0"
    ]
    
    print("\nInstalling document processing dependencies...")
    for cmd in doc_deps:
        run_command(cmd, f"Installing {cmd.split('==')[0].split()[-1]}")
    
    # Install AI/ML dependencies with fallbacks
    ai_deps = [
        ("pip install numpy==1.26.4", "numpy"),
        ("pip install --only-binary=all scikit-learn==1.5.2", "scikit-learn"),
        ("pip install --only-binary=all opencv-python-headless==4.10.0.84", "opencv"),
        ("pip install pytesseract==0.3.13", "pytesseract"),
        ("pip install nltk==3.9.1", "nltk"),
        ("pip install textblob==0.18.0", "textblob")
    ]
    
    print("\nInstalling AI/ML dependencies...")
    for cmd, name in ai_deps:
        if not run_command(cmd, f"Installing {name}"):
            # Try alternative installation
            alt_cmd = f"pip install --no-deps {name}"
            print(f"Trying alternative installation for {name}...")
            run_command(alt_cmd, f"Alternative install {name}")
    
    # Try to install matplotlib (optional)
    print("\nInstalling optional visualization dependencies...")
    run_command("pip install --only-binary=all matplotlib==3.8.4", "matplotlib (optional)")
    
    # Try scipy with specific options
    print("\nTrying to install scipy...")
    scipy_commands = [
        "pip install --only-binary=all scipy==1.11.4",
        "pip install --no-build-isolation scipy==1.11.4", 
        "pip install scipy"  # Latest version
    ]
    
    scipy_installed = False
    for cmd in scipy_commands:
        if run_command(cmd, "scipy"):
            scipy_installed = True
            break
        print("Scipy installation failed, trying next method...")
    
    if not scipy_installed:
        print("⚠️  Warning: scipy could not be installed. Some advanced features may not work.")
    
    # Show final status
    print("\n" + "="*70)
    print("INSTALLATION SUMMARY")
    print("="*70)
    
    # Check what's actually installed
    result = subprocess.run("pip list", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        installed_packages = result.stdout
        key_packages = ['Django', 'numpy', 'opencv', 'scikit-learn', 'nltk', 'textblob', 'PIL', 'PyPDF2']
        
        for package in key_packages:
            if package.lower() in installed_packages.lower():
                print(f"✅ {package} - Installed")
            else:
                print(f"❌ {package} - Not found")
    
    print("\n🎉 Installation complete! Some packages may have failed in CI, but core functionality should work.")
    print("💡 If running locally, you can install missing packages manually.")

if __name__ == "__main__":
    install_ci_dependencies()
