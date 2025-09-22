#!/bin/bash
# Install OpenBLAS and system dependencies for scipy build
# This script should be run before installing Python dependencies

set -e

echo "Installing OpenBLAS and system dependencies..."

# Detect OS and install accordingly
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    echo "Detected Ubuntu/Debian system"
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
        libssl-dev
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    echo "Detected CentOS/RHEL system"
    sudo yum update -y
    sudo yum install -y \
        openblas-devel \
        lapack-devel \
        blas-devel \
        gcc-gfortran \
        gcc-c++ \
        make \
        pkgconfig \
        cmake \
        python3-devel \
        libffi-devel \
        openssl-devel
elif command -v brew &> /dev/null; then
    # macOS
    echo "Detected macOS system"
    brew install openblas lapack cmake pkg-config gfortran
else
    echo "Unsupported operating system"
    exit 1
fi

echo "OpenBLAS and system dependencies installed successfully!"

# Set environment variables for OpenBLAS discovery
export PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
export LD_LIBRARY_PATH="/usr/lib:/usr/local/lib:$LD_LIBRARY_PATH"

echo "Environment variables set:"
echo "PKG_CONFIG_PATH=$PKG_CONFIG_PATH"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"