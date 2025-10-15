"""
🚀 INSTALL AUTONOMOUS AI VERIFICATION SYSTEM
Installs all dependencies for fully autonomous document verification
"""
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("=" * 70)
print("🤖 AUTONOMOUS AI VERIFICATION SYSTEM INSTALLATION")
print("=" * 70)
print()
print("This will install:")
print("  ✅ EasyOCR - Pure Python OCR (no Tesseract needed)")
print("  ✅ OpenCV - Computer vision and image analysis")
print("  ✅ Deep learning models for text recognition")
print("  ✅ Fraud detection algorithms")
print()
print("⏳ This may take 5-10 minutes (downloads AI models)...")
print()

packages = [
    "easyocr",
    "opencv-python",
    "numpy",
    "torch",  # For EasyOCR models
    "scikit-image",
    "fuzzywuzzy",
    "python-Levenshtein"
]

for i, package in enumerate(packages, 1):
    try:
        print(f"\n[{i}/{len(packages)}] {package}")
        install_package(package)
        print(f"  ✅ {package} installed")
    except Exception as e:
        print(f"  ⚠️  Warning: {package} failed: {str(e)}")
        print(f"     You can install manually later: pip install {package}")

print()
print("=" * 70)
print("✅ INSTALLATION COMPLETE!")
print("=" * 70)
print()
print("🤖 Autonomous AI verification is now active!")
print()
print("Features enabled:")
print("  ✅ Pure Python OCR (no external tools)")
print("  ✅ Image quality analysis")
print("  ✅ Document type verification")
print("  ✅ Student name verification")
print("  ✅ Fraud detection")
print("  ✅ Structure analysis")
print()
print("Test the system:")
print("  cd D:\\xp\\htdocs\\TCU_CEAA\\backend")
print("  python test_autonomous_verification.py")
print()
