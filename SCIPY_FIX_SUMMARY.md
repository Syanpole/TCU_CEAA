# SciPy Installation Fix - Resolution Summary

**Date**: October 20, 2025  
**Issue**: SciPy 1.13.1 build failure due to missing OpenBLAS dependency  
**Status**: ✅ **RESOLVED**

---

## Problem

When running `pip install -r requirements.txt` on Windows (and potentially CI environments), SciPy installation failed with:

```
ERROR: Dependency "OpenBLAS" not found, tried pkgconfig and cmake
× Encountered error while generating package metadata.
```

**Root Cause**: 
- Pip attempted to build SciPy from source (no prebuilt wheel available)
- Building from source requires:
  - Fortran compiler (gfortran)
  - BLAS/LAPACK libraries (OpenBLAS, MKL, or ATLAS)
  - Build tools (cmake, pkg-config, meson)
- These were not available in the environment

---

## Solution Applied

### 1. Updated `requirements.txt`
- Changed SciPy version from `1.13.1` to `1.14.1`
- Added installation notes about using `--only-binary` flag
- SciPy 1.14.1 has better wheel support for Python 3.12/3.13

**Change**:
```diff
- scipy==1.13.1
+ scipy==1.14.1  # Updated to 1.14.1 for better Python 3.13 wheel support
```

### 2. Created `install_dependencies.ps1` Script
- Automated installation script for Windows PowerShell
- Steps:
  1. Upgrades pip, setuptools, wheel
  2. Installs NumPy and SciPy with `--only-binary=:all:` flag (forces prebuilt wheels)
  3. Installs remaining dependencies
  4. Verifies critical packages

**Usage**:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
.\install_dependencies.ps1
```

### 3. Created `INSTALLATION.md` Guide
- Comprehensive installation documentation
- Platform-specific instructions (Windows, Linux, macOS)
- Troubleshooting section
- CI/CD setup examples
- Python version compatibility matrix

---

## Test Results

**Environment**: Windows, Python 3.12, activated virtual environment

**Installation Steps Executed**:
1. ✅ Upgraded pip (25.1.1 → 25.2)
2. ✅ Upgraded setuptools (78.0.2 → 80.9.0)
3. ✅ Installed NumPy 1.26.4 (prebuilt wheel, ~30 seconds)
4. ✅ Installed SciPy 1.14.1 (prebuilt wheel, 44.5 MB, ~45 seconds)
5. ✅ Installed all remaining dependencies

**Verification**:
```
✅ Django: 5.2.5
✅ NumPy: 1.26.4
✅ SciPy: 1.14.1
✅ OpenCV: 4.10.0
✅ Scikit-learn: 1.5.2

🎉 All critical AI packages installed successfully!
```

**Total Installation Time**: ~2 minutes (vs. 15-30 minutes if building from source)

---

## Key Improvements

### Before (Failed)
```bash
pip install -r requirements.txt
# ❌ SciPy tries to build from source
# ❌ Requires OpenBLAS, Fortran, cmake
# ❌ Fails with "Dependency OpenBLAS not found"
# ⏱️ Would take 15-30 minutes if successful
```

### After (Success)
```bash
pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: numpy scipy
pip install -r requirements.txt
# ✅ Uses prebuilt wheels
# ✅ No compilation needed
# ✅ Fast installation (~2 minutes)
# ✅ Works on Windows without additional tools
```

---

## Files Modified

| File | Action | Purpose |
|------|--------|---------|
| `backend/requirements.txt` | Updated | Changed scipy 1.13.1 → 1.14.1, added notes |
| `backend/install_dependencies.ps1` | Created | Automated installation script (Windows) |
| `INSTALLATION.md` | Created | Comprehensive installation guide |
| `SCIPY_FIX_SUMMARY.md` | Created | This resolution document |

---

## Recommendations

### For Development
1. ✅ **Use Python 3.11 or 3.12** (best wheel support)
2. ✅ **Always upgrade pip first**: `python -m pip install --upgrade pip setuptools wheel`
3. ✅ **Use the automated script**: `.\install_dependencies.ps1` (Windows)
4. ✅ **Alternative**: Use conda/mamba for scientific packages (fastest)

### For CI/CD
1. Pin Python version to 3.11 or 3.12 in workflows
2. Add pip upgrade step before installing dependencies
3. Use `--only-binary` flag for NumPy/SciPy
4. Cache pip packages to speed up builds

**Example GitHub Actions**:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'

- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip setuptools wheel
    pip install --only-binary=:all: numpy scipy
    pip install -r backend/requirements.txt
```

### For Production
1. Use Docker with multi-stage builds
2. Install NumPy/SciPy in separate layer (cacheable)
3. Consider using conda-based images for scientific Python

---

## Why This Approach is Optimal

### Advantages
✅ **Fast**: Prebuilt wheels install in seconds vs. minutes of compilation  
✅ **Simple**: No external dependencies (Fortran, OpenBLAS, cmake)  
✅ **Cross-platform**: Works on Windows, Linux, macOS  
✅ **Reliable**: Official wheels tested by SciPy team  
✅ **Reproducible**: Same binaries every time  
✅ **CI-friendly**: Fast, cacheable, no system package installs  

### Alternative Approaches Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Build from source** | Latest features | Requires Fortran, OpenBLAS, slow | ❌ Rejected |
| **Conda/Mamba** | Fastest, optimized BLAS | Extra dependency, different ecosystem | ⚠️ Alternative |
| **System packages** | Native optimization | Platform-specific, hard to reproduce | ❌ Rejected |
| **Prebuilt wheels** | Fast, simple, cross-platform | Slightly older versions | ✅ **Chosen** |

---

## Verification Commands

Test your installation:

```powershell
# Check Python version
python --version

# Verify packages
python -c "import numpy, scipy; print('NumPy:', numpy.__version__); print('SciPy:', scipy.__version__)"

# Check if using wheels (not compiled)
python -c "import scipy; print('SciPy file:', scipy.__file__)"
# Should show path in site-packages, not a build directory

# Run Django checks
python manage.py check
```

---

## Troubleshooting

### If installation still fails:

1. **Update pip**:
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Check Python version**:
   ```powershell
   python --version
   # Should be 3.11 or 3.12 for best compatibility
   ```

3. **Try specific wheel**:
   ```powershell
   pip download --only-binary=:all: scipy==1.14.1
   # If this fails, no wheel exists for your platform
   ```

4. **Use conda** (alternative):
   ```powershell
   conda install -c conda-forge numpy scipy
   ```

5. **Contact support**: Open GitHub issue with:
   - Python version (`python --version`)
   - OS version
   - Full error message

---

## Impact Assessment

### Development Environment
- ✅ Installation time: **2 minutes** (down from potential 30+ minutes)
- ✅ No external tools needed (Fortran, OpenBLAS)
- ✅ Consistent across team members

### CI/CD Pipeline
- ✅ Faster builds (cached wheels)
- ✅ More reliable (no compilation failures)
- ✅ Easier to maintain

### Production
- ✅ Same optimized binaries as development
- ✅ Faster deployments
- ✅ Smaller Docker images (no build tools needed)

---

## Future Considerations

1. **Monitor SciPy releases**: New versions may have better wheel support
2. **Python 3.13 support**: Wait for full wheel ecosystem maturity
3. **Consider MKL builds**: Intel's MKL may offer better performance than OpenBLAS
4. **Benchmark**: Compare wheel performance vs. custom-built SciPy

---

## References

- [SciPy Installation Guide](https://scipy.org/install/)
- [Python Wheels](https://pythonwheels.com/)
- [PyPI - SciPy](https://pypi.org/project/scipy/)
- [manylinux wheels](https://github.com/pypa/manylinux)

---

## Conclusion

✅ **Problem**: SciPy build failure due to missing OpenBLAS  
✅ **Solution**: Use prebuilt wheels with `--only-binary` flag  
✅ **Result**: Fast, reliable, cross-platform installation  
✅ **Status**: Fully resolved and documented  

**Next steps**: Team members and CI should use `install_dependencies.ps1` or follow `INSTALLATION.md` guide.
