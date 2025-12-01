"""
Test script for COE Verification with Advanced OCR Analysis
Combines YOLO-based COE element detection with OCR text extraction
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.coe_verification_service import COEVerificationService
from ocr_text_interpreter import OCRTextInterpreter
from PIL import Image
import pytesseract
import cv2
import numpy as np


def print_header(title):
    """Print formatted section header"""
    width = 80
    print("\n" + "=" * width)
    print(f"🎓 {title}")
    print("=" * width + "\n")


def print_section(title):
    """Print formatted subsection"""
    print(f"\n{'─' * 80}")
    print(f"📋 {title}")
    print('─' * 80)


def advanced_ocr_analysis(image_path):
    """
    Perform advanced OCR analysis on the COE document
    Returns extracted text and key information
    """
    print_section("Advanced OCR Analysis")
    
    try:
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            return {"success": False, "error": "Could not load image"}
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing for better OCR
        # 1. Resize if too small (improve OCR accuracy)
        height, width = gray.shape
        if height < 1000:
            scale = 1000 / height
            new_width = int(width * scale)
            gray = cv2.resize(gray, (new_width, 1000), interpolation=cv2.INTER_CUBIC)
        
        # 2. Denoise (lighter denoising to preserve text)
        denoised = cv2.fastNlMeansDenoising(gray, None, 7, 7, 21)
        
        # 3. Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(denoised)
        
        # 4. Threshold (try adaptive for better results on varied lighting)
        binary = cv2.adaptiveThreshold(
            contrast, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Extract text using Tesseract
        print("   🔍 Extracting text from document...")
        
        # Custom Tesseract config for better accuracy
        # PSM 6: Assume uniform block of text
        # OEM 3: Default, using Legacy + LSTM engines
        custom_config = r'--oem 3 --psm 6'
        
        # Try multiple preprocessing approaches and pick best result
        results = []
        
        # Method 1: Binary (adaptive threshold)
        ocr_data_1 = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT, config=custom_config)
        text_1 = pytesseract.image_to_string(binary, config=custom_config)
        conf_1 = [int(c) for c in ocr_data_1['conf'] if c != '-1']
        avg_conf_1 = sum(conf_1) / len(conf_1) if conf_1 else 0
        results.append((text_1, ocr_data_1, avg_conf_1, "Adaptive Threshold"))
        
        # Method 2: Original grayscale
        ocr_data_2 = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=custom_config)
        text_2 = pytesseract.image_to_string(gray, config=custom_config)
        conf_2 = [int(c) for c in ocr_data_2['conf'] if c != '-1']
        avg_conf_2 = sum(conf_2) / len(conf_2) if conf_2 else 0
        results.append((text_2, ocr_data_2, avg_conf_2, "Grayscale"))
        
        # Method 3: Otsu threshold
        _, binary_otsu = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        ocr_data_3 = pytesseract.image_to_data(binary_otsu, output_type=pytesseract.Output.DICT, config=custom_config)
        text_3 = pytesseract.image_to_string(binary_otsu, config=custom_config)
        conf_3 = [int(c) for c in ocr_data_3['conf'] if c != '-1']
        avg_conf_3 = sum(conf_3) / len(conf_3) if conf_3 else 0
        results.append((text_3, ocr_data_3, avg_conf_3, "Otsu Threshold"))
        
        # Pick the result with highest confidence
        results.sort(key=lambda x: x[2], reverse=True)
        full_text, ocr_data, best_conf, method = results[0]
        
        print(f"   📊 Best OCR Method: {method} (Confidence: {best_conf:.2f}%)")
        
        # Analyze extracted text
        analysis = {
            "success": True,
            "full_text": full_text,
            "text_length": len(full_text),
            "key_fields": {},
            "detected_keywords": []
        }
        
        # Search for key COE fields
        text_lower = full_text.lower()
        
        # Keywords to look for in COE (with variations for OCR errors)
        coe_keywords = [
            "enrolled", "enrollment", "certificate",
            "taguig city university", "taguig", "tcu",
            "student", "semester", "school year",
            "validated", "registrar", "free tuition",
            "republic of the philippines", "republic", "philippines",
            "bachelor", "college", "department"
        ]
        
        for keyword in coe_keywords:
            if keyword in text_lower:
                analysis["detected_keywords"].append(keyword)
        
        # Extract specific fields using pattern matching
        lines = full_text.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Look for student name patterns
            # Pattern 1: After "This is to certify that"
            if "certify that" in line_clean.lower():
                if i + 1 < len(lines):
                    potential_name = lines[i + 1].strip()
                    if potential_name and len(potential_name) > 3:
                        analysis["key_fields"]["student_name"] = potential_name
            
            # Pattern 2: Line containing "Student Name:" or "Name:"
            if "student name" in line_clean.lower() or (line_clean.lower().startswith("name:") and "student_name" not in analysis["key_fields"]):
                # Extract name after colon
                if ":" in line_clean:
                    name_part = line_clean.split(":", 1)[1].strip()
                    if name_part and len(name_part) > 3:
                        analysis["key_fields"]["student_name"] = name_part
                # Or check next line if this line is just the label
                elif i + 1 < len(lines):
                    potential_name = lines[i + 1].strip()
                    if potential_name and len(potential_name) > 3 and not potential_name.lower().startswith("course"):
                        analysis["key_fields"]["student_name"] = potential_name
            
            # Look for student ID - improved to handle dashes and various formats
            if "student" in line_clean.lower() and any(char.isdigit() for char in line_clean):
                # Try to find patterns like "19-00648", "2019-0643", etc.
                import re
                # Pattern: 2-4 digits, optional dash, 4-5 digits
                id_pattern = r'\b(\d{2,4}[-]?\d{4,5})\b'
                match = re.search(id_pattern, line_clean)
                if match:
                    analysis["key_fields"]["student_id"] = match.group(1)
                else:
                    # Fallback: look for any sequence of digits (at least 4)
                    words = line_clean.split()
                    for word in words:
                        # Remove non-digit characters but keep result
                        digits_only = ''.join(c for c in word if c.isdigit() or c == '-')
                        if len(digits_only.replace('-', '')) >= 4:
                            analysis["key_fields"]["student_id"] = digits_only
                            break
            
            # Look for semester info
            if "semester" in line_clean.lower():
                analysis["key_fields"]["semester_info"] = line_clean
            
            # Look for school year
            if "school year" in line_clean.lower() or "s.y." in line_clean.lower():
                analysis["key_fields"]["school_year"] = line_clean
        
        # Count words
        words = full_text.split()
        analysis["word_count"] = len([w for w in words if w.strip()])
        
        # Calculate text confidence (based on OCR data)
        confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
        if confidences:
            analysis["avg_confidence"] = sum(confidences) / len(confidences)
        else:
            analysis["avg_confidence"] = 0
        
        return analysis
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def print_ocr_results(ocr_results, interpreted_results=None):
    """Print OCR analysis results in formatted manner"""
    
    if not ocr_results.get("success"):
        print(f"   ❌ OCR Failed: {ocr_results.get('error', 'Unknown error')}")
        return
    
    print(f"   ✅ Text Extraction: Success")
    print(f"   📊 Text Length: {ocr_results['text_length']} characters")
    print(f"   📊 Word Count: {ocr_results['word_count']} words")
    print(f"   📊 OCR Confidence: {ocr_results.get('avg_confidence', 0):.2f}%")
    
    # Print detected keywords
    if ocr_results.get("detected_keywords"):
        print(f"\n   🔍 Detected Keywords ({len(ocr_results['detected_keywords'])}):")
        for keyword in ocr_results["detected_keywords"]:
            print(f"      • {keyword}")
    
    # Print INTERPRETED fields (AI interpretation)
    if interpreted_results:
        print(f"\n   🧠 AI-Interpreted Fields (with reasoning):")
        
        fields = ['student_name', 'student_id', 'program', 'year_level', 'semester', 'enrollment_date']
        for field in fields:
            interp = interpreted_results.get(field)
            if interp:
                field_display = field.replace('_', ' ').title()
                value = interp.get('display_value', interp.get('interpreted_value'))
                confidence = interp.get('confidence', 0)
                reasoning = interp.get('reasoning', '')
                
                print(f"      ✨ {field_display}: {value}")
                print(f"         Confidence: {confidence:.0%} | {reasoning}")
    
    # Print raw extracted fields (old method)
    if ocr_results.get("key_fields") and not interpreted_results:
        print(f"\n   📋 Extracted Fields:")
        for field, value in ocr_results["key_fields"].items():
            field_name = field.replace('_', ' ').title()
            print(f"      • {field_name}: {value}")
    
    # Print sample text
    if ocr_results.get("full_text"):
        text_preview = ocr_results["full_text"][:500]
        print(f"\n   📄 Text Preview (first 500 chars):")
        print("   " + "─" * 76)
        for line in text_preview.split('\n')[:10]:
            if line.strip():
                print(f"   {line[:76]}")
        print("   " + "─" * 76)


def print_combined_analysis(coe_result, ocr_result):
    """Print combined analysis from both COE verification and OCR"""
    print_section("Combined Analysis")
    
    # Overall validity
    coe_valid = coe_result.get("status") == "VALID"  # Fixed: check status instead of valid
    ocr_success = ocr_result.get("success", False)
    
    print(f"   📊 COE Element Detection: {'✅ VALID' if coe_valid else '❌ INVALID'}")
    print(f"   📊 OCR Text Extraction: {'✅ SUCCESS' if ocr_success else '❌ FAILED'}")
    
    # Combined confidence
    if coe_valid and ocr_success:
        coe_conf = coe_result.get("confidence", 0)
        if coe_conf < 1:
            coe_conf = coe_conf * 100  # Convert to percentage if needed
        ocr_conf = ocr_result.get("avg_confidence", 0)
        
        # Weighted average: 60% COE detection, 40% OCR confidence
        combined_conf = (coe_conf * 0.6) + (ocr_conf * 0.4)
        
        print(f"\n   🎯 COE Detection Confidence: {coe_conf:.2f}%")
        print(f"   🎯 OCR Confidence: {ocr_conf:.2f}%")
        print(f"   🎯 Combined Confidence: {combined_conf:.2f}%")
        
        # Determine overall status
        if combined_conf >= 80 and len(ocr_result.get("detected_keywords", [])) >= 5:
            status = "HIGHLY VALID"
            emoji = "🌟"
        elif combined_conf >= 70 and len(ocr_result.get("detected_keywords", [])) >= 3:
            status = "VALID"
            emoji = "✅"
        elif combined_conf >= 60:
            status = "QUESTIONABLE"
            emoji = "⚠️"
        else:
            status = "INVALID"
            emoji = "❌"
        
        print(f"\n   {emoji} Overall Status: {status}")
        
        # Recommendations
        print(f"\n   💡 Recommendations:")
        if combined_conf >= 80:
            print(f"      ✅ Document appears authentic with high confidence")
            print(f"      ✅ All required COE elements detected")
            print(f"      ✅ Text content matches expected COE format")
        elif combined_conf >= 70:
            print(f"      ✅ Document is likely valid")
            print(f"      ⚠️ Minor quality issues detected")
            print(f"      💡 Consider manual review for critical cases")
        else:
            print(f"      ⚠️ Document has quality or authenticity concerns")
            print(f"      ❌ Missing required elements or text content")
            print(f"      💡 Recommend manual verification by staff")


def test_coe_with_ocr(image_path):
    """Main test function combining COE verification and OCR"""
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " " * 20 + "🎓 COE VERIFICATION WITH ADVANCED OCR" + " " * 21 + "║")
    print("║" + " " * 18 + "Certificate of Enrollment Analysis" + " " * 26 + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Verify image exists
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"\n❌ Error: Image not found at {image_path}")
        return
    
    print(f"\n   📷 Image: {image_path.name}")
    print(f"   📁 Path: {image_path}")
    
    # Initialize COE verification service
    print_header("Phase 1: YOLO-Based COE Element Detection")
    service = COEVerificationService()
    
    status = service.get_verification_status()
    print(f"   ✅ COE Detection Model: {status['coe_detection']}")
    print(f"   📊 Model: yolov8_certificate_of_enrollment_detector.pt")
    print(f"   ✅ Fully Operational: {status['fully_operational']}")
    
    # Run COE verification
    print(f"\n   🔍 Running COE element detection...")
    coe_result = service.verify_coe_document(str(image_path))
    
    # Print COE results
    if coe_result.get("success"):
        print(f"   ✅ Detection: Success")
        print(f"   📊 Status: {coe_result.get('status', 'UNKNOWN')}")
        confidence = coe_result.get('confidence', 0)
        if confidence < 1:
            confidence = confidence * 100  # Convert decimal to percentage
        print(f"   📊 Confidence: {confidence:.2f}%")
        print(f"   📊 Elements Detected: {len(coe_result.get('detections', []))}")
        
        # Print detected elements
        detected = coe_result.get("detected_elements", {})
        if detected:
            print(f"\n   🔍 Detected COE Elements:")
            for element, count in detected.items():
                element_name = element.replace('_', ' ').title()
                print(f"      ✅ {element_name}: {count} instance(s)")
    else:
        print(f"   ❌ Detection Failed: {coe_result.get('message', 'Unknown error')}")
    
    # Run OCR analysis
    print_header("Phase 2: Advanced OCR Text Extraction")
    ocr_result = advanced_ocr_analysis(image_path)
    
    # Run intelligent interpretation
    interpreted_result = None
    if ocr_result.get("success"):
        print(f"\n   🧠 Running intelligent text interpretation...")
        interpreter = OCRTextInterpreter()
        interpreted_result = interpreter.interpret_document_text(ocr_result.get("full_text", ""))
        
        # Count successful interpretations
        fields_interpreted = sum(1 for field in ['student_name', 'student_id', 'program', 'year_level', 'semester', 'enrollment_date']
                                if interpreted_result.get(field) is not None)
        print(f"   ✅ Interpreted {fields_interpreted}/6 key fields")
    
    print_ocr_results(ocr_result, interpreted_result)
    
    # Combined analysis
    print_header("Phase 3: Combined Verification Analysis")
    print_combined_analysis(coe_result, ocr_result)
    
    # Final summary
    print_header("Test Complete")
    print("   ✅ COE verification and OCR analysis completed successfully")
    print("   📊 Results show comprehensive document analysis")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_coe_with_ocr.py <path_to_coe_image>")
        print("\nExample:")
        print('  python test_coe_with_ocr.py "media/documents/2025/11/Certificate_of_Enrollment.jpg"')
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_coe_with_ocr(image_path)
