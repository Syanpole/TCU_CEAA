# AI/OCR Libraries Installation Script
# Run this in PowerShell from the TCU_CEAA directory

Write-Host "🤖 TCU-CEAA AI Document Verification - OCR Installation" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run this script from the TCU_CEAA directory" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Check Python version
Write-Host "🐍 Checking Python version..." -ForegroundColor Yellow
python --version

Write-Host ""
Write-Host "Choose installation option:" -ForegroundColor Cyan
Write-Host "1. Full Installation (EasyOCR + Pytesseract + OpenCV) - Recommended" -ForegroundColor Green
Write-Host "2. Lightweight (OpenCV only) - Faster, limited AI" -ForegroundColor Yellow
Write-Host "3. EasyOCR only - Best quality, slower" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Enter choice (1-3)"

Write-Host ""

switch ($choice) {
    "1" {
        Write-Host "📥 Installing Full AI/OCR Stack..." -ForegroundColor Green
        Write-Host "This will download ~600MB of packages and AI models" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "Installing EasyOCR..." -ForegroundColor Cyan
        pip install easyocr --quiet
        
        Write-Host "Installing Pytesseract..." -ForegroundColor Cyan
        pip install pytesseract --quiet
        
        Write-Host "Installing OpenCV..." -ForegroundColor Cyan
        pip install opencv-python --quiet
        
        Write-Host "Installing Pillow..." -ForegroundColor Cyan
        pip install pillow --quiet
        
        Write-Host ""
        Write-Host "✅ Full installation complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  Note: For Pytesseract to work, you also need to:" -ForegroundColor Yellow
        Write-Host "   1. Download Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
        Write-Host "   2. Install it to C:\Program Files\Tesseract-OCR" -ForegroundColor White
        Write-Host "   3. Add to PATH or it will use EasyOCR only" -ForegroundColor White
    }
    
    "2" {
        Write-Host "📥 Installing Lightweight Stack..." -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Installing OpenCV..." -ForegroundColor Cyan
        pip install opencv-python --quiet
        
        Write-Host "Installing Pillow..." -ForegroundColor Cyan
        pip install pillow --quiet
        
        Write-Host ""
        Write-Host "✅ Lightweight installation complete!" -ForegroundColor Green
        Write-Host "⚠️  Note: No OCR available - AI confidence scores will be lower" -ForegroundColor Yellow
    }
    
    "3" {
        Write-Host "📥 Installing EasyOCR..." -ForegroundColor Green
        Write-Host "This will download ~500MB of packages and AI models" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "Installing EasyOCR..." -ForegroundColor Cyan
        pip install easyocr --quiet
        
        Write-Host "Installing OpenCV..." -ForegroundColor Cyan
        pip install opencv-python --quiet
        
        Write-Host "Installing Pillow..." -ForegroundColor Cyan
        pip install pillow --quiet
        
        Write-Host ""
        Write-Host "✅ EasyOCR installation complete!" -ForegroundColor Green
    }
    
    default {
        Write-Host "❌ Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔍 Verifying installation..." -ForegroundColor Cyan
Write-Host ""

# Test imports
python -c "
try:
    import easyocr
    print('✅ EasyOCR: Installed')
except ImportError:
    print('❌ EasyOCR: Not installed')

try:
    import pytesseract
    print('✅ Pytesseract: Installed')
except ImportError:
    print('❌ Pytesseract: Not installed')

try:
    import cv2
    print('✅ OpenCV: Installed')
except ImportError:
    print('❌ OpenCV: Not installed')

try:
    from PIL import Image
    print('✅ Pillow: Installed')
except ImportError:
    print('❌ Pillow: Not installed')
"

Write-Host ""
Write-Host "🎯 Testing AI Vision system..." -ForegroundColor Cyan

cd backend

python -c "
from ai_verification.vision_ai import default_vision_ai

print('')
print('Available OCR Engines:', ', '.join(default_vision_ai.get_available_engines()) or 'None')
print('Vision AI Available:', default_vision_ai.is_available())
print('')

if default_vision_ai.is_available():
    print('✅ AI Document Verification is READY!')
    print('')
    print('Next steps:')
    print('1. Restart Django server: python manage.py runserver')
    print('2. Upload a test document')
    print('3. Check AI confidence scores')
else:
    print('⚠️  No OCR engines available')
    print('AI will work with limited functionality')
"

cd ..

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Installation Complete! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Read INSTALL_OCR_LIBRARIES.md for troubleshooting" -ForegroundColor Yellow
Write-Host ""
