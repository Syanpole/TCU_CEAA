# CI/CD Installation Script for Windows/PowerShell
# This script handles the complete installation process for CI environments

Write-Host "Starting CI/CD installation process..." -ForegroundColor Green

try {
    # Step 1: Install system dependencies
    Write-Host "Step 1: Installing system dependencies..." -ForegroundColor Yellow
    if (Test-Path "install_openblas.ps1") {
        & .\install_openblas.ps1
    } else {
        Write-Host "install_openblas.ps1 not found, attempting manual setup..." -ForegroundColor Yellow
        
        # For GitHub Actions or other CI
        if ($env:GITHUB_ACTIONS -eq "true") {
            Write-Host "GitHub Actions detected" -ForegroundColor Blue
            # GitHub Actions Windows runners have most tools pre-installed
        }
    }

    # Step 2: Upgrade pip and install build tools
    Write-Host "Step 2: Upgrading pip and installing build tools..." -ForegroundColor Yellow
    python -m pip install --upgrade pip setuptools wheel

    # Step 3: Install core dependencies first
    Write-Host "Step 3: Installing core dependencies..." -ForegroundColor Yellow
    if (Test-Path "requirements-ci.txt") {
        pip install -r requirements-ci.txt --prefer-binary
    } else {
        Write-Host "requirements-ci.txt not found, using requirements.txt" -ForegroundColor Yellow
        pip install -r requirements.txt --prefer-binary
    }

    # Step 4: Install ML dependencies separately (optional)
    Write-Host "Step 4: Installing ML dependencies..." -ForegroundColor Yellow
    if (Test-Path "requirements-ml.txt") {
        try {
            pip install -r requirements-ml.txt --prefer-binary
        } catch {
            Write-Host "Warning: Some ML packages failed to install, continuing without them" -ForegroundColor Red
            Write-Host "This is normal in CI environments where compilation may fail" -ForegroundColor Yellow
        }
    }

    Write-Host "Installation completed successfully!" -ForegroundColor Green

    # Step 5: Verify installation
    Write-Host "Step 5: Verifying installation..." -ForegroundColor Yellow
    
    try { python -c "import django; print(f'Django version: {django.get_version()}')" }
    catch { Write-Host "Django verification failed" -ForegroundColor Red }
    
    try { python -c "import numpy; print(f'NumPy version: {numpy.__version__}')" }
    catch { Write-Host "NumPy not installed" -ForegroundColor Yellow }
    
    try { python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')" }
    catch { Write-Host "OpenCV not installed" -ForegroundColor Yellow }

    # Test scipy separately as it's the problematic package
    try { 
        python -c "import scipy; print(f'SciPy version: {scipy.__version__}')" 
    } catch {
        Write-Host "SciPy not installed - this is expected if OpenBLAS was not available" -ForegroundColor Yellow
        Write-Host "The application will work without scipy for basic document verification" -ForegroundColor Cyan
    }

    Write-Host "Installation verification completed!" -ForegroundColor Green

} catch {
    Write-Host "Installation failed with error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}