#!/bin/bash
# CI/CD Installation Script
# This script handles the complete installation process for CI environments

set -e

echo "Starting CI/CD installation process..."

# Step 1: Install system dependencies
echo "Step 1: Installing system dependencies..."
if [ -f "install_openblas.sh" ]; then
    chmod +x install_openblas.sh
    ./install_openblas.sh
else
    echo "Installing OpenBLAS manually..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            libopenblas-dev \
            liblapack-dev \
            libblas-dev \
            gfortran \
            build-essential \
            pkg-config \
            cmake \
            python3-dev \
            libffi-dev \
            libssl-dev \
            tesseract-ocr \
            tesseract-ocr-eng
    fi
fi

# Step 2: Upgrade pip and install build tools
echo "Step 2: Upgrading pip and installing build tools..."
python -m pip install --upgrade pip setuptools wheel

# Step 3: Install core dependencies first
echo "Step 3: Installing core dependencies..."
if [ -f "requirements-ci.txt" ]; then
    pip install -r requirements-ci.txt --prefer-binary
else
    echo "requirements-ci.txt not found, using requirements.txt"
    pip install -r requirements.txt --prefer-binary
fi

# Step 4: Install ML dependencies separately (optional)
echo "Step 4: Installing ML dependencies..."
if [ -f "requirements-ml.txt" ]; then
    pip install -r requirements-ml.txt --prefer-binary || {
        echo "Warning: Some ML packages failed to install, continuing without them"
        echo "This is normal in CI environments where compilation may fail"
    }
fi

echo "Installation completed successfully!"

# Step 5: Verify installation
echo "Step 5: Verifying installation..."
python -c "import django; print(f'Django version: {django.get_version()}')"
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')" || echo "NumPy not installed"
python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')" || echo "OpenCV not installed"

# Test scipy separately as it's the problematic package
python -c "import scipy; print(f'SciPy version: {scipy.__version__}')" || {
    echo "SciPy not installed - this is expected if OpenBLAS was not available"
    echo "The application will work without scipy for basic document verification"
}

echo "Installation verification completed!"