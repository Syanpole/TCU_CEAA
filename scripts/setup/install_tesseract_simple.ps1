# Simple Tesseract OCR Installation Script for Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tesseract OCR Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Tesseract is already installed
Write-Host "Checking if Tesseract is already installed..." -ForegroundColor Yellow
try {
    $existing = Get-Command tesseract -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "✅ Tesseract is already installed!" -ForegroundColor Green
        Write-Host "Location: $($existing.Source)" -ForegroundColor White
        tesseract --version
        exit 0
    }
} catch {
    Write-Host "Tesseract not found in PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📥 Downloading Tesseract installer..." -ForegroundColor Yellow
Write-Host ""

$url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$output = "$env:TEMP\tesseract-installer.exe"

try {
    # Download the installer
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    
    if (Test-Path $output) {
        Write-Host "✅ Download completed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🚀 Starting installer..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "IMPORTANT: During installation:" -ForegroundColor Red
        Write-Host "  ✓ Check the box: 'Add tesseract to PATH'" -ForegroundColor Yellow
        Write-Host "  ✓ Install to default location" -ForegroundColor Yellow
        Write-Host ""
        
        # Start the installer and wait for it to complete
        Start-Process -FilePath $output -Wait
        
        Write-Host ""
        Write-Host "✅ Installation completed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️ IMPORTANT: Please restart PowerShell" -ForegroundColor Yellow
        Write-Host "   Then test with: tesseract --version" -ForegroundColor White
        
        # Clean up
        Remove-Item $output -ErrorAction SilentlyContinue
        
    } else {
        Write-Host "❌ Download failed" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install manually:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "  2. Download Windows installer" -ForegroundColor White
    Write-Host "  3. Run as Administrator" -ForegroundColor White
    Write-Host "  4. Check 'Add to PATH' during installation" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
