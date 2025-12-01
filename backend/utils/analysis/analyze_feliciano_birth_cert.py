import os
import django
import cv2
import numpy as np
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

print("=" * 80)
print("FELICIANO BIRTH CERTIFICATE - ADVANCED OCR ANALYSIS")
print("=" * 80)

# Path to birth certificate
image_path = "media/documents/2025/11/FELICIANO- BIRTH CERTIFICATE.jpg"

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
        
        # Try AWS Textract first (most accurate)
        print("\n" + "=" * 80)
        print("AWS TEXTRACT EXTRACTION (PRIMARY)")
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
                    
                    extracted_text = result.get('text', 'No text')
                    
                    print("\n" + "=" * 80)
                    print("EXTRACTED TEXT (AWS TEXTRACT)")
                    print("=" * 80)
                    print(extracted_text)
                    
                    # Analyze the text
                    print("\n" + "=" * 80)
                    print("TEXT ANALYSIS")
                    print("=" * 80)
                    
                    lines = extracted_text.split('\n')
                    print(f"Total Lines: {len(lines)}")
                    print(f"Total Characters: {len(extracted_text)}")
                    
                    # Try to identify key sections
                    print("\n📋 Detected Keywords:")
                    keywords = [
                        'BIRTH', 'CERTIFICATE', 'REPUBLIC', 'PHILIPPINES', 
                        'PSA', 'NATIONAL', 'STATISTICS', 'OFFICE',
                        'NAME', 'SEX', 'DATE', 'PLACE', 'MOTHER', 'FATHER',
                        'REGISTRY', 'CIVIL', 'REGISTRAR', 'FELICIANO'
                    ]
                    
                    for keyword in keywords:
                        if keyword in extracted_text.upper():
                            print(f"   ✅ Found: {keyword}")
                    
                    # Extract birth certificate fields
                    print("\n" + "=" * 80)
                    print("EXTRACTING BIRTH CERTIFICATE FIELDS")
                    print("=" * 80)
                    
                    import re
                    
                    fields = {}
                    text_upper = extracted_text.upper()
                    
                    # Child's name - look for patterns
                    name_patterns = [
                        r"NAME[:\s]*([A-Z][A-Z\s,\.]+?)(?:\n|SEX|DATE|MALE|FEMALE)",
                        r"(?:CHILD'S NAME|NAME OF CHILD)[:\s]*([A-Z][A-Z\s,\.]+?)(?:\n|SEX)",
                    ]
                    
                    for pattern in name_patterns:
                        match = re.search(pattern, text_upper)
                        if match:
                            name = match.group(1).strip()
                            if len(name) > 3 and 'FELICIANO' in name:
                                fields['child_name'] = name
                                break
                    
                    # Look for FELICIANO specifically
                    if 'FELICIANO' in text_upper:
                        # Try to extract full name context around FELICIANO
                        feliciano_context = re.search(r'([A-Z\s,\.]{3,}FELICIANO[A-Z\s,\.]{3,})', text_upper)
                        if feliciano_context:
                            fields['name_context'] = feliciano_context.group(1).strip()
                    
                    # Date of birth
                    dob_patterns = [
                        r"(?:DATE OF BIRTH|BIRTH DATE)[:\s]*(\d{1,2}[-/\s]\w+[-/\s]\d{2,4})",
                        r"(?:DATE OF BIRTH|BIRTH DATE)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
                        r"(\d{1,2}\s+(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{4})",
                    ]
                    
                    for pattern in dob_patterns:
                        match = re.search(pattern, text_upper)
                        if match:
                            fields['date_of_birth'] = match.group(1).strip()
                            break
                    
                    # Sex
                    sex_match = re.search(r"SEX[:\s]*(MALE|FEMALE)", text_upper)
                    if sex_match:
                        fields['sex'] = sex_match.group(1).strip()
                    
                    # Place of birth
                    place_patterns = [
                        r"PLACE OF BIRTH[:\s]*([A-Z][A-Z\s,\.\-]+?)(?:\n|MOTHER|FATHER|TYPE)",
                        r"(?:HOSPITAL|CLINIC|INSTITUTION)[:\s]*([A-Z][A-Z\s,\.\-]+?)(?:CITY|MUNICIPALITY)",
                    ]
                    
                    for pattern in place_patterns:
                        match = re.search(pattern, text_upper)
                        if match:
                            place = match.group(1).strip()
                            if len(place) > 3:
                                fields['place_of_birth'] = place
                                break
                    
                    # Mother's name
                    mother_patterns = [
                        r"(?:MOTHER'S NAME|MOTHER NAME|MAIDEN NAME)[:\s]*([A-Z][A-Z\s,\.]+?)(?:\n|FATHER|CITIZENSHIP)",
                    ]
                    
                    for pattern in mother_patterns:
                        match = re.search(pattern, text_upper)
                        if match:
                            mother = match.group(1).strip()
                            if len(mother) > 5:
                                fields['mother_name'] = mother
                                break
                    
                    # Father's name
                    father_patterns = [
                        r"(?:FATHER'S NAME|FATHER NAME)[:\s]*([A-Z][A-Z\s,\.]+?)(?:\n|CITIZENSHIP|OCCUPATION)",
                    ]
                    
                    for pattern in father_patterns:
                        match = re.search(pattern, text_upper)
                        if match:
                            father = match.group(1).strip()
                            if len(father) > 5:
                                fields['father_name'] = father
                                break
                    
                    # Registry number
                    registry_patterns = [
                        r"REGISTRY[\s#NO\.:]*([\d\-]+)",
                        r"REG[:\s#NO\.]*([\d\-]+)",
                    ]
                    
                    for pattern in registry_patterns:
                        match = re.search(pattern, text_upper)
                        if match:
                            fields['registry_number'] = match.group(1).strip()
                            break
                    
                    print("\n🔍 Extracted Fields:")
                    if fields:
                        for field, value in fields.items():
                            print(f"   • {field.replace('_', ' ').title()}: {value}")
                    else:
                        print("   ⚠️ No fields could be extracted automatically")
                    
                    # Show first 500 chars for manual inspection
                    print("\n" + "=" * 80)
                    print("FIRST 500 CHARACTERS (FOR MANUAL REVIEW)")
                    print("=" * 80)
                    print(extracted_text[:500])
                    
                else:
                    print(f"❌ AWS Textract failed: {result.get('error', 'Unknown error')}")
            else:
                print("⚠️ AWS Textract not available")
                
        except Exception as e:
            print(f"❌ AWS Textract error: {str(e)}")
        
        # Try EasyOCR as backup
        print("\n" + "=" * 80)
        print("EASYOCR EXTRACTION (BACKUP)")
        print("=" * 80)
        
        try:
            import easyocr
            
            reader = easyocr.Reader(['en'])
            results = reader.readtext(image_path)
            
            print(f"✅ EasyOCR extraction completed")
            print(f"📊 Text blocks detected: {len(results)}")
            
            # Show high-confidence results
            print("\n📋 High-Confidence Detections (>70%):")
            high_conf = [r for r in results if r[2] > 0.7]
            for i, (bbox, text, confidence) in enumerate(high_conf[:20], 1):
                print(f"{i}. {text} ({confidence*100:.1f}%)")
            
            # Combine all text
            easy_text = '\n'.join([result[1] for result in results])
            
            print("\n" + "=" * 80)
            print("COMBINED EASYOCR TEXT (FIRST 500 CHARS)")
            print("=" * 80)
            print(easy_text[:500])
            
        except Exception as e:
            print(f"❌ EasyOCR failed: {str(e)}")
    else:
        print("❌ Failed to load image with OpenCV")
else:
    print("❌ Image file not found!")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
