# 🤖 Installing OCR Libraries for AI Document Processing

## Why You Need This

Your AI document verification system requires OCR (Optical Character Recognition) libraries to:
- ✅ Extract text from document images
- ✅ Verify document types automatically
- ✅ Detect student names in documents
- ✅ Analyze document quality
- ✅ Detect fraud and fake documents
- ✅ Provide AI confidence scores

Without these libraries, documents will stay in "Processing" status with 0% confidence.

## Required Libraries

### 1. **EasyOCR** (Primary - Best Quality)
- Deep learning-based OCR
- Supports 80+ languages
- High accuracy for printed text
- **Size**: ~500MB (includes AI models)

### 2. **Pytesseract** (Backup - Faster)
- Traditional OCR engine
- Faster processing
- Good for simple documents
- **Size**: ~50MB

### 3. **OpenCV (cv2)** (Required)
- Image processing and computer vision
- Face detection
- Image quality analysis
- **Size**: ~100MB

## Installation Methods

### Option 1: Quick Install (Recommended)

Run this command in your backend directory:

```powershell
cd C:\xampp\htdocs\TCU_CEAA\backend
& C:\xampp\htdocs\TCU_CEAA\.venv\Scripts\Activate.ps1
pip install easyocr pytesseract opencv-python pillow
```

### Option 2: Install Tesseract OCR Engine

EasyOCR works standalone, but for Pytesseract you need the Tesseract engine:

1. **Download Tesseract for Windows**:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.exe`
   - Install to: `C:\Program Files\Tesseract-OCR`

2. **Add to System PATH**:
   ```powershell
   $env:PATH += ";C:\Program Files\Tesseract-OCR"
   ```

3. **Configure Pytesseract** (backend will auto-detect)

### Option 3: Lightweight Installation (Only OpenCV)

If disk space is limited, install only OpenCV for basic image processing:

```powershell
pip install opencv-python pillow
```

**Note**: This won't provide OCR, so AI confidence scores will be lower.

## Verification

After installation, check what's available:

```powershell
cd C:\xampp\htdocs\TCU_CEAA\backend
& C:\xampp\htdocs\TCU_CEAA\.venv\Scripts\Activate.ps1
python -c "from ai_verification.vision_ai import default_vision_ai; print('Available engines:', default_vision_ai.get_available_engines()); print('Is available:', default_vision_ai.is_available())"
```

**Expected Output**:
```
Available engines: ['EasyOCR', 'Pytesseract', 'OpenCV']
Is available: True
```

## First-Time Setup (EasyOCR Model Download)

When you first use EasyOCR, it will download AI models (~400MB):

```python
import easyocr
reader = easyocr.Reader(['en'])  # Downloads English model
```

This happens automatically on first document upload. Progress is shown in logs.

## Testing After Installation

1. **Restart Django server**:
   ```powershell
   cd C:\xampp\htdocs\TCU_CEAA\backend
   python manage.py runserver
   ```

2. **Upload a test document** via the frontend

3. **Check server logs** for:
   ```
   ✅ EasyOCR initialized successfully
   ✅ Pytesseract available
   ✅ OpenCV available
   🎉 Dual OCR Setup: EasyOCR (primary) + Tesseract (fallback)
   ```

4. **Verify AI processing**:
   - Document status should change from "Processing" to "Approved/Rejected"
   - AI confidence score should show (e.g., "88%")
   - Processing should complete in 5-15 seconds

## Performance Expectations

| Library | Processing Time | Accuracy | Disk Space |
|---------|----------------|----------|------------|
| EasyOCR | 5-10 seconds | ⭐⭐⭐⭐⭐ | 500MB |
| Pytesseract | 2-5 seconds | ⭐⭐⭐⭐ | 50MB |
| OpenCV only | 1 second | ⭐⭐ | 100MB |

## Troubleshooting

### Issue: "EasyOCR not available"
**Solution**: 
```powershell
pip install easyocr torch torchvision
```

### Issue: "Pytesseract not found"
**Solution**: Install Tesseract OCR engine (see Option 2 above)

### Issue: "Out of memory"
**Solution**: EasyOCR uses GPU if available. For CPU-only:
```powershell
pip install easyocr --no-deps
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: Documents still show 0%
**Solution**: 
1. Check server logs for errors
2. Verify libraries are installed: `pip list | findstr "easyocr|pytesseract|opencv"`
3. Restart Django server
4. Clear browser cache and re-upload

## System Requirements

### Minimum:
- **RAM**: 4GB (8GB recommended for EasyOCR)
- **Disk**: 1GB free space
- **CPU**: Any modern CPU

### Recommended:
- **RAM**: 8GB+
- **Disk**: 2GB free space
- **GPU**: NVIDIA GPU with CUDA (optional, 10x faster)

## Alternative: Use Mock AI (Testing Only)

If you can't install OCR libraries, you can enable mock AI for testing:

1. Edit `backend/settings.py`:
```python
# AI Configuration
USE_MOCK_AI = True  # Change to True for testing without OCR
```

2. Mock AI will generate random confidence scores (60-95%) for testing the UI

**⚠️ Warning**: Mock AI doesn't actually verify documents - use only for UI testing!

## Next Steps

After installing OCR libraries:

1. ✅ Restart Django server
2. ✅ Upload a test document
3. ✅ Watch server logs for AI processing
4. ✅ Check AI confidence scores in frontend
5. ✅ View AI Analysis Report in "View Details" modal

## Need Help?

- Check server logs: `backend/logs/` directory
- View AI dashboard: Admin → AI System Performance
- Test individual algorithms: Admin → Run AI Tests

---

**Status**: Ready to install! 🚀
**Estimated Time**: 5-10 minutes
**Difficulty**: Easy (just run pip install commands)
