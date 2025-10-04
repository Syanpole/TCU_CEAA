# AI Algorithms Installation Script
# Installs all required dependencies for the 6 core algorithms + advanced features

Write-Host "🤖 TCU-CEAA AI Algorithms Installation" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated!" -ForegroundColor Yellow
    Write-Host "   Please activate your virtual environment first:" -ForegroundColor Yellow
    Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        exit
    }
}

Write-Host ""
Write-Host "📦 Installing AI Algorithm Dependencies..." -ForegroundColor Green
Write-Host ""

# Change to backend directory
Set-Location backend

# Core dependencies
Write-Host "Installing core dependencies..." -ForegroundColor Yellow
pip install --upgrade pip setuptools wheel

# Algorithm 1: Document Validator
Write-Host ""
Write-Host "1️⃣  Installing Document Validator dependencies (Pytesseract)..." -ForegroundColor Cyan
pip install pytesseract==0.3.13

# Algorithm 2: Cross-Document Matcher
Write-Host ""
Write-Host "2️⃣  Installing Cross-Document Matcher dependencies (Levenshtein)..." -ForegroundColor Cyan
pip install python-Levenshtein==0.25.1

# Algorithm 3: Grade Verifier
Write-Host ""
Write-Host "3️⃣  Installing Grade Verifier dependencies (NumPy, SciPy)..." -ForegroundColor Cyan
pip install numpy==1.26.4
pip install scipy==1.13.1

# Algorithm 4: Face Verifier
Write-Host ""
Write-Host "4️⃣  Installing Face Verifier dependencies (OpenCV)..." -ForegroundColor Cyan
pip install opencv-python==4.10.0.84

# Algorithm 5: Fraud Detector
Write-Host ""
Write-Host "5️⃣  Installing Fraud Detector dependencies (PDF processing)..." -ForegroundColor Cyan
pip install PyPDF2==3.0.1
pip install PyMuPDF==1.24.10

# Algorithm 6 uses all above libraries
Write-Host ""
Write-Host "6️⃣  AI Verification Manager uses all above libraries ✅" -ForegroundColor Cyan

# Advanced Features: TF-IDF & Cosine Similarity
Write-Host ""
Write-Host "🚀 Installing Advanced Features (TF-IDF, Cosine Similarity)..." -ForegroundColor Cyan
pip install scikit-learn==1.5.2
pip install nltk==3.9.1
pip install textblob==0.18.0

# Supporting libraries
Write-Host ""
Write-Host "📚 Installing supporting libraries..." -ForegroundColor Cyan
pip install python-docx==1.1.2
pip install pdfplumber==0.11.0
pip install matplotlib==3.8.4

# Verify installation
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""

Write-Host "📋 Verifying installation..." -ForegroundColor Yellow
Write-Host ""

# Check each package
$packages = @(
    "pytesseract",
    "Levenshtein",
    "numpy",
    "scipy",
    "cv2",
    "PyPDF2",
    "fitz",
    "sklearn",
    "nltk",
    "textblob"
)

foreach ($package in $packages) {
    $result = python -c "import $package; print('✅ $package installed')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result -ForegroundColor Green
    } else {
        Write-Host "❌ $package not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🎉 AI Algorithms Ready!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the algorithms:" -ForegroundColor White
Write-Host "   python test_ai_algorithms.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run Django server:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Check the documentation:" -ForegroundColor White
Write-Host "   ../AI_ALGORITHMS_IMPLEMENTATION.md" -ForegroundColor Gray
Write-Host ""

# Return to root directory
Set-Location ..
