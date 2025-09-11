#!/bin/bash
# Quick fix for CI dependency installation issues
# This script installs dependencies in a way that avoids compilation problems

echo "🚀 TCU CEAA - Quick CI Dependencies Fix"
echo "========================================"

# Navigate to backend directory
cd backend || { echo "❌ Backend directory not found"; exit 1; }

echo "📦 Installing basic dependencies..."
pip install --upgrade pip wheel setuptools

echo "📦 Installing core Django packages..."
pip install Django==5.2.5
pip install djangorestframework==3.15.2
pip install django-cors-headers==4.4.0
pip install "psycopg[binary]==3.2.3"
pip install Pillow==10.4.0

echo "📦 Installing document processing..."
pip install PyPDF2==3.0.1
pip install python-docx==1.1.2
pip install pdfplumber==0.9.0

echo "📦 Installing AI/ML packages (stable versions)..."
pip install numpy==1.26.4
pip install --only-binary=all opencv-python-headless==4.8.1.78 || pip install opencv-python-headless
pip install --only-binary=all scikit-learn==1.3.2 || pip install scikit-learn
pip install pytesseract==0.3.13
pip install nltk==3.9.1
pip install textblob==0.18.0

echo "📦 Attempting to install optional packages..."
pip install --only-binary=all matplotlib || echo "⚠️ matplotlib installation failed (optional)"
pip install --only-binary=all scipy || echo "⚠️ scipy installation failed (optional)"

echo "✅ Installation complete!"
echo "🔍 Checking installed packages..."
pip list | grep -E "(Django|numpy|opencv|scikit|nltk|PyPDF2)"

echo ""
echo "🎉 Ready to go! Run 'python manage.py runserver' to start the development server."
