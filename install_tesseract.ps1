# Enhanced AI Document Verification - Tesseract OCR Installation
# This script installs Tesseract OCR for Windows

Write-Host "🤖 Installing Tesseract OCR for Enhanced AI Document Verification" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  This script should be run as Administrator for best results" -ForegroundColor Yellow
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
}

# Method 1: Try Chocolatey installation
Write-Host "1. Attempting Chocolatey installation..." -ForegroundColor Green

try {
    # Check if Chocolatey is installed
    $chocoPath = Get-Command choco -ErrorAction SilentlyContinue
    
    if ($chocoPath) {
        Write-Host "   ✅ Chocolatey found, installing Tesseract..." -ForegroundColor Green
        choco install tesseract -y
        
        # Verify installation
        $tesseractPath = Get-Command tesseract -ErrorAction SilentlyContinue
        if ($tesseractPath) {
            Write-Host "   ✅ Tesseract installed successfully via Chocolatey!" -ForegroundColor Green
            tesseract --version
            exit 0
        }
    } else {
        Write-Host "   ❌ Chocolatey not found" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Chocolatey installation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 2: Manual download and installation
Write-Host ""
Write-Host "2. Manual installation method..." -ForegroundColor Green

$tesseractUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$downloadPath = "$env:TEMP\tesseract-installer.exe"

try {
    Write-Host "   📥 Downloading Tesseract installer..." -ForegroundColor Yellow
    
    # Download the installer
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($tesseractUrl, $downloadPath)
    
    Write-Host "   ✅ Download completed" -ForegroundColor Green
    
    # Check if file exists and has reasonable size
    if ((Test-Path $downloadPath) -and ((Get-Item $downloadPath).Length -gt 1MB)) {
        Write-Host "   🚀 Starting installation..." -ForegroundColor Yellow
        Write-Host "   📝 Please follow the installation wizard" -ForegroundColor Yellow
        Write-Host "   ⚠️  Make sure to check 'Add to PATH' during installation" -ForegroundColor Yellow
        
        # Start the installer
        Start-Process -FilePath $downloadPath -Wait
        
        # Clean up
        Remove-Item $downloadPath -ErrorAction SilentlyContinue
        
        Write-Host "   ✅ Installation completed!" -ForegroundColor Green
        
    } else {
        Write-Host "   ❌ Download failed or file corrupted" -ForegroundColor Red
    }
    
} catch {
    Write-Host "   ❌ Manual installation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 3: Provide manual instructions
Write-Host ""
Write-Host "3. Manual Installation Instructions" -ForegroundColor Green
Write-Host "   If automatic installation failed, please:" -ForegroundColor Yellow
Write-Host "   1. Go to: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
Write-Host "   2. Download the Windows installer" -ForegroundColor White
Write-Host "   3. Run the installer as Administrator" -ForegroundColor White
Write-Host "   4. During installation, make sure to:" -ForegroundColor White
Write-Host "      • Check 'Add tesseract to your PATH environment variable'" -ForegroundColor White
Write-Host "      • Install additional language data if needed" -ForegroundColor White
Write-Host "   5. Restart your PowerShell/Command Prompt" -ForegroundColor White
Write-Host "   6. Test with: tesseract --version" -ForegroundColor White

# Verification
Write-Host ""
Write-Host "4. Testing Tesseract installation..." -ForegroundColor Green

try {
    $tesseractPath = Get-Command tesseract -ErrorAction SilentlyContinue
    if ($tesseractPath) {
        Write-Host "   ✅ Tesseract is available in PATH!" -ForegroundColor Green
        Write-Host "   📍 Location: $($tesseractPath.Source)" -ForegroundColor White
        tesseract --version
        
        Write-Host ""
        Write-Host "🎉 SUCCESS: Tesseract OCR is ready!" -ForegroundColor Green
        Write-Host "   The Enhanced AI Document Verification system can now:" -ForegroundColor White
        Write-Host "   • Extract text from images using OCR" -ForegroundColor White
        Write-Host "   • Analyze document content for fraud detection" -ForegroundColor White
        Write-Host "   • Verify document authenticity with high accuracy" -ForegroundColor White
        
    } else {
        Write-Host "   ❌ Tesseract not found in PATH" -ForegroundColor Red
        Write-Host "   Please add Tesseract to your PATH environment variable" -ForegroundColor Yellow
        Write-Host "   Or restart your PowerShell session after installation" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error testing Tesseract: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "   1. Close and reopen PowerShell/Command Prompt" -ForegroundColor White
Write-Host "   2. Run: tesseract --version (to verify)" -ForegroundColor White
Write-Host "   3. Run: python test_ai_verification.py (to test full system)" -ForegroundColor White
Write-Host "   4. Start your Django server: python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "🛡️  Your document verification system will now detect and reject:" -ForegroundColor Green
Write-Host "   • Random photos submitted as official documents" -ForegroundColor White
Write-Host "   • Screenshots or fake documents" -ForegroundColor White
Write-Host "   • Wrong document types" -ForegroundColor White
Write-Host "   • Poor quality or suspicious files" -ForegroundColor White
