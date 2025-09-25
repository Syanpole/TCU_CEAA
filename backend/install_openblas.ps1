# Install OpenBLAS and system dependencies for scipy build (Windows PowerShell)
# This script should be run before installing Python dependencies

Write-Host "Installing OpenBLAS and system dependencies for Windows..." -ForegroundColor Green

# Check if running in CI environment
$isCI = $env:CI -eq "true" -or $env:GITHUB_ACTIONS -eq "true"

if ($isCI) {
    Write-Host "CI environment detected. Installing dependencies via package managers..." -ForegroundColor Yellow
    
    # For GitHub Actions Windows runners
    if ($env:GITHUB_ACTIONS -eq "true") {
        Write-Host "GitHub Actions detected. Using choco for dependencies..." -ForegroundColor Blue
        
        # Install chocolatey packages
        choco install cmake --yes
        choco install pkgconfiglite --yes
        
        # Install vcpkg for OpenBLAS (alternative approach)
        if (!(Test-Path "C:\vcpkg")) {
            git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
            C:\vcpkg\bootstrap-vcpkg.bat
        }
        
        # Install OpenBLAS via vcpkg
        C:\vcpkg\vcpkg.exe install openblas:x64-windows
        
        # Set environment variables
        $env:CMAKE_TOOLCHAIN_FILE = "C:\vcpkg\scripts\buildsystems\vcpkg.cmake"
        $env:VCPKG_TARGET_TRIPLET = "x64-windows"
        
        Write-Host "Environment variables set for vcpkg" -ForegroundColor Green
    }
} else {
    Write-Host "Local development environment detected." -ForegroundColor Yellow
    Write-Host "For Windows, it's recommended to use conda or pre-built wheels." -ForegroundColor Blue
    Write-Host "Run: conda install scipy or pip install --only-binary=all scipy" -ForegroundColor Cyan
}

# Alternative: Install via conda if available
if (Get-Command conda -ErrorAction SilentlyContinue) {
    Write-Host "Conda detected. Installing scipy via conda..." -ForegroundColor Green
    conda install -y scipy numpy
} else {
    Write-Host "Conda not found. Will attempt to use pre-built wheels." -ForegroundColor Yellow
}

Write-Host "OpenBLAS setup completed!" -ForegroundColor Green