# TCU-CEAA Installation Guide

## Quick Start (Windows)

### Option 1: Automated Installation (Recommended)

```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run automated installation script
.\install_dependencies.ps1
```

The script will:
1. ✅ Upgrade pip, setuptools, and wheel
2. ✅ Install NumPy and SciPy using prebuilt wheels (fast)
3. ✅ Install all remaining dependencies
4. ✅ Verify critical AI packages

### Option 2: Manual Installation

```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip tools
python -m pip install --upgrade pip setuptools wheel

# Install NumPy and SciPy first (prebuilt wheels only, avoids compilation)
python -m pip install --only-binary=:all: numpy==1.26.4 scipy==1.14.1

# Install remaining dependencies
pip install -r requirements.txt

# Verify installation
python -c "import django, numpy, scipy, cv2, pytesseract, sklearn; print('✅ All packages installed')"
```

---

## Troubleshooting

### Problem: SciPy installation fails with "ERROR: Dependency 'OpenBLAS' not found"

**Cause**: Pip is trying to build SciPy from source because no prebuilt wheel is available for your Python version/platform.

**Solutions** (in order of preference):

#### Solution 1: Use Prebuilt Wheels (Fastest)
```powershell
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install with --only-binary flag
python -m pip install --only-binary=:all: numpy scipy

# If that fails, try installing specific versions with wheels
python -m pip install numpy==1.26.4 scipy==1.14.1
```

#### Solution 2: Use Compatible Python Version
SciPy provides prebuilt wheels for:
- ✅ Python 3.9, 3.10, 3.11, 3.12 (recommended)
- ⚠️ Python 3.13 (limited wheel support as of Oct 2025)

**Check your Python version:**
```powershell
python --version
```

**If using Python 3.13+, consider downgrading to Python 3.11 or 3.12:**
```powershell
# Download Python 3.12 from python.org
# Recreate virtual environment
python3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\install_dependencies.ps1
```

#### Solution 3: Use Conda (Alternative Package Manager)
Conda provides prebuilt NumPy/SciPy with optimized BLAS libraries:

```powershell
# Install Miniconda from https://docs.conda.io/en/latest/miniconda.html
# Create environment
conda create -n tcu-ceaa python=3.12 -y
conda activate tcu-ceaa

# Install scientific packages from conda-forge
conda install -c conda-forge numpy=1.26 scipy=1.14 pillow pytesseract python-dotenv -y

# Install remaining packages via pip
pip install -r requirements.txt
```

#### Solution 4: Build from Source (Linux/CI Only)
**Only if above solutions fail and you're on Linux/CI:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential gfortran pkg-config cmake \
  libopenblas-dev liblapack-dev libblas-dev

# Then install normally
pip install -r requirements.txt
```

---

## CI/CD Setup (GitHub Actions)

For GitHub Actions or other CI platforms, use this workflow:

```yaml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']  # Use versions with wheel support

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip packages
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies (with binary wheels)
      run: |
        cd backend
        python -m pip install --upgrade pip setuptools wheel
        # Install NumPy/SciPy first with binary-only flag
        pip install --only-binary=:all: numpy==1.26.4 scipy==1.14.1
        # Install remaining dependencies
        pip install -r requirements.txt
    
    - name: Run migrations
      run: |
        cd backend
        python manage.py migrate
    
    - name: Run tests
      run: |
        cd backend
        python manage.py test
```

**Alternative CI approach (if wheels unavailable):**
```yaml
    - name: Install system dependencies (if building from source)
      run: |
        sudo apt-get update
        sudo apt-get install -y libopenblas-dev gfortran
    
    - name: Install Python dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt
```

---

## Python Version Compatibility

| Python Version | NumPy 1.26.4 | SciPy 1.14.1 | Recommendation |
|----------------|--------------|--------------|----------------|
| 3.9            | ✅ Wheels     | ✅ Wheels     | ⚠️ EOL Oct 2025 |
| 3.10           | ✅ Wheels     | ✅ Wheels     | ✅ Good         |
| 3.11           | ✅ Wheels     | ✅ Wheels     | ✅ Recommended  |
| 3.12           | ✅ Wheels     | ✅ Wheels     | ✅ Recommended  |
| 3.13           | ✅ Wheels     | ⚠️ Limited    | ⚠️ Use 3.12    |

---

## Environment Setup

### Windows (PowerShell)
```powershell
# Clone repository
git clone https://github.com/Syanpole/TCU_CEAA.git
cd TCU_CEAA

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
cd backend
.\install_dependencies.ps1

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Linux/macOS (Bash)
```bash
# Clone repository
git clone https://github.com/Syanpole/TCU_CEAA.git
cd TCU_CEAA

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install backend dependencies
cd backend
pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: numpy==1.26.4 scipy==1.14.1
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

---

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'numpy'`
**Solution**: Ensure virtual environment is activated and dependencies are installed:
```powershell
.\.venv\Scripts\Activate.ps1
.\install_dependencies.ps1
```

### Issue: `ImportError: DLL load failed while importing cv2`
**Solution**: Reinstall opencv-python:
```powershell
pip uninstall opencv-python -y
pip install opencv-python==4.10.0.84
```

### Issue: Tesseract not found
**Solution**: Install Tesseract OCR:
```powershell
# Windows: Download installer from
# https://github.com/UB-Mannheim/tesseract/wiki
# Default path: C:\Program Files\Tesseract-OCR\tesseract.exe

# Or use Chocolatey
choco install tesseract
```

### Issue: Very slow pip install
**Solution**: Use `--only-binary` flag or switch to conda (faster prebuilt packages).

---

## Production Deployment

For production environments (Heroku, AWS, etc.):

1. **Use Python 3.11 or 3.12** for best wheel support
2. **Pin all dependencies** (already done in requirements.txt)
3. **Use --only-binary flag** in Dockerfile or buildpacks:
   ```dockerfile
   RUN pip install --only-binary=:all: numpy scipy
   RUN pip install -r requirements.txt
   ```
4. **Consider using conda** for complex numerical packages

---

## Need Help?

- **Documentation**: Check `AI_ALGORITHMS_EXPLANATION.md` for technical details
- **Issues**: Open a GitHub issue with your Python version and error message
- **Quick test**: Run `python -c "import numpy, scipy; print('✅ OK')"` to verify installation

---

## Summary

**Best practices:**
1. ✅ Use Python 3.11 or 3.12
2. ✅ Always upgrade pip before installing
3. ✅ Install NumPy/SciPy first with `--only-binary` flag
4. ✅ Use the provided `install_dependencies.ps1` script
5. ✅ Use conda for complex environments (optional but recommended)

**Quick commands:**
```powershell
# Windows
cd backend
.\.venv\Scripts\Activate.ps1
.\install_dependencies.ps1

# Linux/macOS
cd backend
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: numpy scipy
pip install -r requirements.txt
```
