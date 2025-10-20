# ============================================================================
# TCU-CEAA Backend Dependencies Installation Script (Windows PowerShell)
# ============================================================================
# This script ensures optimal installation of Python dependencies, especially
# NumPy and SciPy which require prebuilt binary wheels to avoid compilation.
# ============================================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TCU-CEAA Backend Dependencies Installation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  WARNING: No virtual environment detected!" -ForegroundColor Yellow
    Write-Host "It's recommended to use a virtual environment (.venv)" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Installation cancelled. Activate .venv first:" -ForegroundColor Red
        Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "✅ Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

# Step 1: Upgrade pip, setuptools, and wheel
Write-Host "📦 Step 1/4: Upgrading pip, setuptools, and wheel..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upgrade pip tools" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Pip tools upgraded successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Install NumPy and SciPy with binary-only flag (avoids compilation)
Write-Host "📊 Step 2/4: Installing NumPy and SciPy (prebuilt wheels only)..." -ForegroundColor Cyan
Write-Host "   This ensures fast installation without compilation" -ForegroundColor Gray
python -m pip install --only-binary=:all: "numpy==1.26.4" "scipy==1.14.1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install NumPy/SciPy" -ForegroundColor Red
    Write-Host "⚠️  If you see 'no matching distribution', your Python version may not have prebuilt wheels." -ForegroundColor Yellow
    Write-Host "   Solutions:" -ForegroundColor Yellow
    Write-Host "   1. Use Python 3.11 or 3.12 (recommended)" -ForegroundColor Yellow
    Write-Host "   2. Try: pip install numpy scipy (allows compilation, slower)" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ NumPy and SciPy installed successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Install remaining requirements
Write-Host "📚 Step 3/4: Installing remaining dependencies..." -ForegroundColor Cyan
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install requirements" -ForegroundColor Red
    exit 1
}
Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Step 4: Verify critical packages
Write-Host "🔍 Step 4/4: Verifying critical AI packages..." -ForegroundColor Cyan
$packages = @("django", "numpy", "scipy", "opencv-python", "pytesseract", "scikit-learn")
$allInstalled = $true

foreach ($pkg in $packages) {
    python -c "import $($pkg.Replace('-', '_')); print('✅ $pkg')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to import $pkg" -ForegroundColor Red
        $allInstalled = $false
    }
}

Write-Host ""
if ($allInstalled) {
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✅ Installation Complete!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run migrations: python manage.py migrate" -ForegroundColor Yellow
    Write-Host "  2. Start server: python manage.py runserver" -ForegroundColor Yellow
} else {
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "⚠️  Installation completed with some issues" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "Please check the errors above and retry." -ForegroundColor Yellow
    exit 1
}
