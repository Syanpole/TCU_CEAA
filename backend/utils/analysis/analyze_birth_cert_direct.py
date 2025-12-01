import os
import django
import cv2
import numpy as np
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

print("=" * 80)
print("BIRTH CERTIFICATE - DIRECT OCR ANALYSIS")
print("=" * 80)

# Path to birth certificate
image_path = "media/documents/2025/11/BirthCertificate-PSA_OnuoIrB.jpg"

print(f"\n📄 Image: {image_path}")
print(f"📁 Exists: {os.path.exists(image_path)}")

if os.path.exists(image_path):
    # Get file info
    file_size = os.path.getsize(image_path)
    print(f"📊 File Size: {file_size / 1024:.2f} KB")
    
    # Load image with OpenCV
    print("\n" + "=" * 80)
    print("LOADING IMAGE")
    print("=" * 80)
    
    img = cv2.imread(image_path)
    if img is not None:
        height, width = img.shape[:2]
        print(f"✅ Image loaded successfully")
        print(f"📐 Dimensions: {width} x {height}")
        print(f"🎨 Channels: {img.shape[2] if len(img.shape) > 2 else 1}")
        
        # Try Tesseract OCR first
        print("\n" + "=" * 80)
        print("TESSERACT OCR EXTRACTION")
        print("=" * 80)
        
        try:
            import pytesseract
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Extract text
            text = pytesseract.image_to_string(denoised, config='--psm 6')
            
            print(f"✅ Tesseract extraction completed")
            print(f"📊 Characters extracted: {len(text)}")
            
            print("\n" + "=" * 80)
            print("EXTRACTED TEXT (TESSERACT)")
            print("=" * 80)
            print(text)
            
        except Exception as e:
            print(f"❌ Tesseract OCR failed: {str(e)}")
        
        # Try EasyOCR
        print("\n" + "=" * 80)
        print("EASYOCR EXTRACTION")
        print("=" * 80)
        
        try:
            import easyocr
            
            reader = easyocr.Reader(['en'])
            results = reader.readtext(image_path)
            
            print(f"✅ EasyOCR extraction completed")
            print(f"📊 Text blocks detected: {len(results)}")
            
            # Combine all text
            easy_text = '\n'.join([result[1] for result in results])
            
            print("\n" + "=" * 80)
            print("EXTRACTED TEXT (EASYOCR)")
            print("=" * 80)
            print(easy_text)
            
            print("\n" + "=" * 80)
            print("EASYOCR DETAILED RESULTS")
            print("=" * 80)
            for i, (bbox, text, confidence) in enumerate(results, 1):
                print(f"\n{i}. Text: {text}")
                print(f"   Confidence: {confidence*100:.1f}%")
                print(f"   Position: {bbox[0]}")
            
        except Exception as e:
            print(f"❌ EasyOCR failed: {str(e)}")
        
        # Try AWS Textract (if credentials available)
        print("\n" + "=" * 80)
        print("AWS TEXTRACT EXTRACTION")
        print("=" * 80)
        
        try:
            from myapp.advanced_ocr_service import get_advanced_ocr_service
            
            advanced_ocr = get_advanced_ocr_service()
            if advanced_ocr and advanced_ocr.is_enabled():
                # Read image as bytes
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                
                result = advanced_ocr.extract_text(image_bytes)
                
                if result.get('success'):
                    print(f"✅ AWS Textract extraction completed")
                    print(f"📊 Confidence: {result.get('confidence', 0)*100:.2f}%")
                    
                    print("\n" + "=" * 80)
                    print("EXTRACTED TEXT (AWS TEXTRACT)")
                    print("=" * 80)
                    print(result.get('text', 'No text'))
                else:
                    print(f"❌ AWS Textract failed: {result.get('error', 'Unknown error')}")
            else:
                print("⚠️ AWS Textract not available (credentials not configured)")
                
        except Exception as e:
            print(f"❌ AWS Textract error: {str(e)}")
    else:
        print("❌ Failed to load image with OpenCV")
else:
    print("❌ Image file not found!")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
