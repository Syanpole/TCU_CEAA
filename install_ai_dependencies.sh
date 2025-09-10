#!/bin/bash

# AI Dependencies Installation Script for TCU-CEAA
echo "Installing AI dependencies for TCU-CEAA backend..."

# Navigate to backend directory
cd backend

# Install Python dependencies
echo "Installing Python packages..."
pip install PyPDF2==3.0.1
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pytesseract==0.3.10
pip install scikit-learn==1.3.0
pip install nltk==3.8.1
pip install python-docx==0.8.11

# Note: Tesseract OCR engine needs to be installed separately
echo ""
echo "⚠️  IMPORTANT INSTALLATION NOTES:"
echo ""
echo "1. Tesseract OCR Engine:"
echo "   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
echo "   - macOS: brew install tesseract"
echo "   - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
echo ""
echo "2. Make sure Tesseract is added to your system PATH"
echo ""
echo "3. For better accuracy, install additional language packs:"
echo "   - English: already included"
echo "   - For other languages, download from Tesseract GitHub"
echo ""

# Run Django migrations
echo "Running Django migrations for AI fields..."
python manage.py migrate

echo ""
echo "✅ AI dependencies installation completed!"
echo ""
echo "🤖 Your TCU-CEAA system now includes:"
echo "   • Advanced document analysis with OCR"
echo "   • Intelligent grade validation and cross-checking"
echo "   • Automated allowance eligibility calculation"
echo "   • Quality assessment and recommendation system"
echo "   • Confidence scoring for all AI operations"
echo ""
echo "🚀 Start your server with: python manage.py runserver"
echo ""
