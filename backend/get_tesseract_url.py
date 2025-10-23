"""
Fetch latest Tesseract release info from GitHub API
"""
import urllib.request
import json

try:
    url = "https://api.github.com/repos/UB-Mannheim/tesseract/releases/latest"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        
    print("=" * 70)
    print("LATEST TESSERACT OCR RELEASE")
    print("=" * 70)
    print(f"Version: {data['tag_name']}")
    print(f"Released: {data['published_at'][:10]}")
    print()
    print("Available Downloads:")
    print()
    
    for asset in data['assets']:
        if 'w64-setup' in asset['name'] and asset['name'].endswith('.exe'):
            print(f"✅ Windows 64-bit Installer:")
            print(f"   Name: {asset['name']}")
            print(f"   Size: {asset['size'] / (1024*1024):.1f} MB")
            print(f"   Download URL:")
            print(f"   {asset['browser_download_url']}")
            print()
            
            # Save URL to file for easy access
            with open('tesseract_download_url.txt', 'w') as f:
                f.write(asset['browser_download_url'])
            print("✅ URL saved to: tesseract_download_url.txt")
            break
    
except Exception as e:
    print(f"Error: {e}")
    print()
    print("Manual download link:")
    print("https://github.com/UB-Mannheim/tesseract/releases")
