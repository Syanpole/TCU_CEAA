# Tesseract OCR Installation Guide for Windows

## Why You Need This
The AI name verification system requires OCR (Optical Character Recognition) to read student names from documents. Without it, the system will REJECT all submissions for security.

## Installation Steps

### Method 1: Download Installer (Recommended)

1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)

2. **Run Installer:**
   - Run the downloaded .exe file
   - Install to: `C:\Program Files\Tesseract-OCR`
   - ✅ Check "Add to PATH" during installation

3. **Verify Installation:**
   ```powershell
   tesseract --version
   ```
   Should show: `tesseract 5.3.3`

### Method 2: Using Chocolatey

```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Tesseract
choco install tesseract
```

### Method 3: Manual Setup

1. Download from: https://digi.bib.uni-mannheim.de/tesseract/
2. Extract to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced System Settings → Environment Variables
   - Edit PATH, add: `C:\Program Files\Tesseract-OCR`

## After Installation

### Test OCR is Working:

```powershell
cd D:\xp\htdocs\TCU_CEAA\backend
python test_grade_name_verification.py
```

**Expected output:**
```
Verification Result:
  Name Match: True (or False if name doesn't match)
  Confidence: 85.0% (NOT 40% anymore)
  Expected Name: sean paul feliciano
  Matched Name: sean paul feliciano
```

### Restart Backend:

The Django server should automatically reload, but if not:
```powershell
# Find and kill the Django process
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process

# Restart
cd D:\xp\htdocs\TCU_CEAA\backend
python manage.py runserver 8000
```

## Verification

Once installed, the system will:
- ✅ Read text from documents using OCR
- ✅ Extract student names from documents
- ✅ Compare with submitting student's name
- ✅ Approve if names match (85-95% confidence)
- ❌ Reject if names don't match (fraud detection)

## Current System Behavior (WITHOUT OCR)

Until you install Tesseract:
- ❌ **ALL document uploads → REJECTED**
- ❌ **ALL grade submissions → REJECTED**
- Error message: "🔒 SECURITY: OCR text extraction is not available..."

This is **BY DESIGN** for security - better to reject everything than approve fraud.

## Troubleshooting

### "tesseract: command not found"
- OCR not installed or not in PATH
- Reinstall and ensure "Add to PATH" is checked

### "TesseractNotFoundError"
- Python can't find tesseract.exe
- Check PATH includes: `C:\Program Files\Tesseract-OCR`

### Still showing 40% confidence
- Backend needs restart
- Run: `python test_grade_name_verification.py` to test directly

## Summary

| Status | Document Uploads | Grade Submissions | Security Level |
|--------|-----------------|-------------------|----------------|
| **Without OCR** | ❌ All Rejected | ❌ All Rejected | 🔒 Maximum (but unusable) |
| **With OCR** | ✅ Legitimate Approved | ✅ Legitimate Approved | 🔒 High (functional) |
| | ❌ Fraud Rejected | ❌ Fraud Rejected | |

**Install Tesseract OCR to make the system fully functional while maintaining high security.**
