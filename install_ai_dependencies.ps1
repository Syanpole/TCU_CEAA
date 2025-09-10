# AI Dependencies Installation Script for TCU-CEAA (Windows PowerShell)
Write-Host "Installing AI dependencies for TCU-CEAA backend..." -ForegroundColor Green

# Navigate to backend directory
Set-Location backend

# Install Python dependencies
Write-Host "Installing Python packages..." -ForegroundColor Yellow
pip install PyPDF2==3.0.1
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pytesseract==0.3.10
pip install scikit-learn==1.3.0
pip install nltk==3.8.1
pip install python-docx==0.8.11

Write-Host ""
Write-Host "⚠️  IMPORTANT INSTALLATION NOTES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Tesseract OCR Engine:" -ForegroundColor Cyan
Write-Host "   - Download from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
Write-Host "   - Install the Windows installer (tesseract-ocr-w64-setup-v5.x.x.exe)" -ForegroundColor White
Write-Host "   - Default installation path: C:\Program Files\Tesseract-OCR\" -ForegroundColor White
Write-Host ""
Write-Host "2. Add Tesseract to System PATH:" -ForegroundColor Cyan
Write-Host "   - Add 'C:\Program Files\Tesseract-OCR' to your system PATH" -ForegroundColor White
Write-Host "   - Or set TESSDATA_PREFIX environment variable" -ForegroundColor White
Write-Host ""
Write-Host "3. Verify Installation:" -ForegroundColor Cyan
Write-Host "   - Open new command prompt and run: tesseract --version" -ForegroundColor White
Write-Host ""

# Run Django migrations
Write-Host "Running Django migrations for AI fields..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "✅ AI dependencies installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🤖 Your TCU-CEAA system now includes:" -ForegroundColor Magenta
Write-Host "   • Advanced document analysis with OCR" -ForegroundColor White
Write-Host "   • Intelligent grade validation and cross-checking" -ForegroundColor White
Write-Host "   • Automated allowance eligibility calculation" -ForegroundColor White
Write-Host "   • Quality assessment and recommendation system" -ForegroundColor White
Write-Host "   • Confidence scoring for all AI operations" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Start your server with: python manage.py runserver" -ForegroundColor Green
Write-Host ""

# Go back to root directory
Set-Location ..
