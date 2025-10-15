"""
Download and install Tesseract OCR for Windows
"""
import os
import sys
import urllib.request
import subprocess

def download_tesseract():
    """Download Tesseract installer"""
    urls = [
        "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe",
        "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    ]
    
    output_path = os.path.join(os.environ['TEMP'], 'tesseract-setup.exe')
    
    print("=" * 70)
    print("TESSERACT OCR INSTALLER DOWNLOAD")
    print("=" * 70)
    print()
    
    for url in urls:
        try:
            print(f"Trying to download from: {url[:50]}...")
            urllib.request.urlretrieve(url, output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:  # > 1MB
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Download successful!")
                print(f"   File: {output_path}")
                print(f"   Size: {size_mb:.2f} MB")
                print()
                print("=" * 70)
                print("INSTALLATION INSTRUCTIONS")
                print("=" * 70)
                print()
                print("1. Run the installer:")
                print(f"   {output_path}")
                print()
                print("2. During installation:")
                print("   ✅ Install to: C:\\Program Files\\Tesseract-OCR")
                print("   ✅ Check 'Add to PATH' option")
                print()
                print("3. After installation, restart your terminal and run:")
                print("   tesseract --version")
                print()
                print("4. Then test with:")
                print("   cd D:\\xp\\htdocs\\TCU_CEAA\\backend")
                print("   python test_grade_name_verification.py")
                print()
                
                # Try to open the installer
                print("Attempting to open installer...")
                try:
                    os.startfile(output_path)
                    print("✅ Installer opened! Follow the on-screen instructions.")
                except Exception as e:
                    print(f"⚠️ Could not auto-open installer: {e}")
                    print(f"Please manually run: {output_path}")
                
                return True
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            continue
    
    print()
    print("=" * 70)
    print("⚠️ AUTOMATIC DOWNLOAD FAILED")
    print("=" * 70)
    print()
    print("Please download Tesseract manually:")
    print()
    print("1. Go to: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Click on 'tesseract-ocr-w64-setup-5.3.3.20231005.exe'")
    print("3. Run the downloaded installer")
    print("4. Install to: C:\\Program Files\\Tesseract-OCR")
    print("5. Make sure to check 'Add to PATH' during installation")
    print()
    return False

if __name__ == "__main__":
    download_tesseract()
