"""
COE Verification Service
========================

Certificate of Enrollment (COE) verification using YOLO v8 object detection.
This service detects and verifies key elements in COE documents.

Features:
- YOLO v8 model for COE element detection
- Detection of logos, watermarks, stamps
- Validation of required document elements
- Confidence scoring
- Document authenticity verification

Detected Classes:
- CITY OF TAGUIG LOGO
- ENROLLED status text
- Free Tuition indicator
- Taguig City University Logo
- Validated stamp
- WATERMARK
- IloveTaguig Logo

Author: TCU CEAA Development Team
Date: November 11, 2025
"""

import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from django.conf import settings
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Import OCR components
try:
    import pytesseract
    from ocr_text_interpreter import OCRTextInterpreter
    from myapp.advanced_ocr_service import get_advanced_ocr_service
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR components not available. Install with: pip install pytesseract")

# Import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics YOLO not available. Install with: pip install ultralytics")


class COEVerificationService:
    """
    Certificate of Enrollment Verification Service using YOLO v8.
    
    This service provides comprehensive COE document verification including:
    - Detection of official logos and stamps
    - Verification of enrollment status text
    - Authentication through watermarks
    - Validation of required document elements
    """
    
    # Class names mapping (from training data)
    CLASS_NAMES = {
        0: 'CITY OF TAGUIG LOGO',
        1: 'ENROLLED',
        2: 'Free Tuition',
        3: 'Taguig City University Logo',
        4: 'Validated',
        5: 'WATERMARK',
        6: 'IloveTaguig Logo'
    }
    
    # Required elements for valid COE
    REQUIRED_ELEMENTS = {
        'city_logo': 0,          # CITY OF TAGUIG LOGO
        'enrolled_text': 1,      # ENROLLED
        'university_logo': 3,    # Taguig City University Logo
    }
    
    # Optional but important elements
    OPTIONAL_ELEMENTS = {
        'free_tuition': 2,       # Free Tuition
        'validated': 4,          # Validated
        'watermark': 5,          # WATERMARK
        'ilovetaguig_logo': 6    # IloveTaguig Logo
    }
    
    def __init__(self):
        """Initialize the COE verification service."""
        self.yolo_model = None
        self.model_path = Path(settings.BASE_DIR) / 'ai_model_data' / 'trained_models' / 'yolov8_certificate_of_enrollment_detector.pt'
        self.ocr_interpreter = None
        
        # Initialize YOLO model
        if YOLO_AVAILABLE and self.model_path.exists():
            try:
                self.yolo_model = YOLO(str(self.model_path))
                logger.info(f"✅ COE YOLO detection model loaded from: {self.model_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load COE YOLO model: {str(e)}")
                self.yolo_model = None
        else:
            if not YOLO_AVAILABLE:
                logger.warning("⚠️ YOLO not available. Install ultralytics package.")
            if not self.model_path.exists():
                logger.warning(f"⚠️ COE YOLO model not found at: {self.model_path}")
        
        # Initialize OCR interpreter
        if OCR_AVAILABLE:
            try:
                self.ocr_interpreter = OCRTextInterpreter()
                logger.info("✅ OCR Text Interpreter initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OCR interpreter: {str(e)}")
                self.ocr_interpreter = None
        else:
            logger.warning("⚠️ OCR not available. Install pytesseract package.")
        
        # Initialize Advanced OCR (AWS Textract)
        self.advanced_ocr = None
        try:
            self.advanced_ocr = get_advanced_ocr_service()
            if self.advanced_ocr.is_enabled():
                logger.info("✅ Advanced OCR (AWS Textract) initialized")
            else:
                logger.info("ℹ️ Advanced OCR (AWS Textract) not configured, using Tesseract fallback")
        except Exception as e:
            logger.warning(f"⚠️ Advanced OCR initialization failed: {str(e)}")
    
    def get_verification_status(self) -> Dict[str, Any]:
        """
        Check the status of COE verification capabilities.
        
        Returns:
            Dictionary containing status of each component
        """
        advanced_ocr_enabled = self.advanced_ocr and self.advanced_ocr.is_enabled()
        
        return {
            'coe_detection': self.yolo_model is not None,
            'ocr_available': self.ocr_interpreter is not None,
            'advanced_ocr_enabled': advanced_ocr_enabled,
            'ocr_method': 'AWS Textract' if advanced_ocr_enabled else 'Tesseract (Fallback)',
            'model_path': str(self.model_path) if self.model_path else None,
            'fully_operational': self.yolo_model is not None and self.ocr_interpreter is not None
        }
    
    def extract_subject_list(self, image_path: str) -> Dict[str, Any]:
        """
        Extract list of subjects from COE document.
        
        Args:
            image_path: Path to the COE document image
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if extraction completed
                - subjects: List of dictionaries with 'subject_code' and 'subject_name'
                - subject_count: Total number of subjects found
                - confidence: Overall extraction confidence (0.0-1.0)
                - errors: List of errors if any
        """
        result = {
            'success': False,
            'subjects': [],
            'subject_count': 0,
            'confidence': 0.0,
            'errors': []
        }
        
        try:
            if not OCR_AVAILABLE or not self.ocr_interpreter:
                result['errors'].append("OCR service not available")
                return result
            
            if not os.path.exists(image_path):
                result['errors'].append(f"Image not found: {image_path}")
                return result
            
            # Read and preprocess image
            logger.info("🔍 Extracting subject list from COE...")
            image = cv2.imread(image_path)
            
            if image is None:
                result['errors'].append("Failed to read image")
                return result
            
            # Use advanced OCR extraction
            ocr_data = self._advanced_ocr_extraction(image)
            
            if not ocr_data['success']:
                result['errors'].extend(ocr_data.get('errors', []))
                return result
            
            # Extract subjects using pattern matching
            subjects = self._extract_subjects_from_text(ocr_data['text'])
            
            result['success'] = len(subjects) > 0
            result['subjects'] = subjects
            result['subject_count'] = len(subjects)
            result['confidence'] = ocr_data['confidence']
            
            if len(subjects) == 0:
                result['errors'].append("No subjects found in COE document")
                logger.warning("⚠️ No subjects extracted from COE")
            else:
                logger.info(f"✅ Extracted {len(subjects)} subjects from COE")
            
        except Exception as e:
            logger.error(f"❌ Subject extraction error: {str(e)}")
            result['errors'].append(f"Subject extraction error: {str(e)}")
        
        return result
    
    def _extract_subjects_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract subject codes and names from OCR text.
        
        Args:
            text: Raw OCR text from COE document
        
        Returns:
            List of dictionaries with 'subject_code' and 'subject_name'
        """
        import re
        subjects = []
        
        try:
            # Split text into lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # TCU Format: 4-digit code + Subject code on one line, name typically on next line
            # Example:  
            #   1127 IT 102
            #   Social Media And Presentation
            
            # First pass: Find all course codes with their line numbers
            course_code_lines = []
            for i, line in enumerate(lines):
                match = re.search(r'^\d{4}\s+([A-Z]{2,6})\s+(\d{1,3}[A-Z]?)(?:\s|$)', line)
                if match:
                    code_letters = match.group(1).strip()
                    code_numbers = match.group(2).strip()
                    subject_code = f"{code_letters} {code_numbers}"
                    course_code_lines.append((i, subject_code))
                    logger.debug(f"Found course code at line {i}: {subject_code}")
            
            # Second pass: Find subject names for each course code
            for i, subject_code in course_code_lines:
                subject_name = None
                
                # Strategy 1: Check next line for subject name (most common case)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    
                    # Valid subject name: starts with capital, has letters, not metadata
                    if (re.match(r'^[A-Z][a-zA-Z\s/\-\(\)&,]+', next_line) and 
                        not re.match(r'^(BSCS|UNITS|CODE|SUBJECT|ENROLLED|VALIDATED|BY:|DATE:|Total)', next_line) and
                        not re.search(r'^\d+\.\d+\s', next_line) and  # Not starting with units like "3.0"
                        not re.search(r'^\d+-\d+\s+(am|pm)', next_line) and  # Not a schedule
                        len(next_line.strip()) >= 3):
                        
                        subject_name = next_line.strip()
                        logger.debug(f"Found name for {subject_code} on next line: {subject_name}")
                
                # Strategy 2: Look backward for orphaned subject names (for ELEC 4A case)
                if not subject_name and i >= 2:
                    for lookback in range(2, min(6, i + 1)):
                        prev_line = lines[i - lookback]
                        
                        # Check if this looks like a subject name
                        if (re.match(r'^[A-Z][a-zA-Z\s/\-\(\)&,]{10,}', prev_line) and  # At least 10 chars
                            not re.match(r'^(BSCS|UNITS|CODE|SUBJECT|ENROLLED|VALIDATED|BY:|DATE:|Total|Taguig|Republic|CERTIFICATE|Student|Course|Department|Enrollment)', prev_line) and
                            not re.search(r'\d{4}\s+[A-Z]{2,6}\s+\d', prev_line) and  # Doesn't contain course code
                            not re.search(r'^\d+\.\d+\s', prev_line) and  # Not units
                            not re.search(r'\d+-\d+\s+(am|pm)', prev_line)):  # Not schedule
                            
                            # Check if this name hasn't been used
                            name_candidate = prev_line.strip()
                            already_used = any(s['subject_name'] == name_candidate for s in subjects)
                            
                            if not already_used:
                                subject_name = name_candidate
                                logger.debug(f"Found name for {subject_code} by lookback ({lookback} lines): {subject_name}")
                                break
                
                # Clean and add subject if name was found
                if subject_name:
                    # Remove trailing units/credits
                    subject_name = re.sub(r'\s+\d+\.\d+\s+units?\s*$', '', subject_name, flags=re.IGNORECASE)
                    subject_name = re.sub(r'\s+\d+\s+units?\s*$', '', subject_name, flags=re.IGNORECASE)
                    
                    if len(subject_name) >= 3:
                        subjects.append({
                            'subject_code': subject_code,
                            'subject_name': subject_name
                        })
                        logger.info(f"✓ Extracted: {subject_code} - {subject_name}")
                else:
                    logger.warning(f"⚠️ No name found for {subject_code}")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_subjects = []
            for subject in subjects:
                # Normalize for comparison
                key = (subject['subject_code'].upper().replace(' ', ''), 
                       subject['subject_name'].lower())
                if key not in seen:
                    seen.add(key)
                    unique_subjects.append(subject)
            
            logger.info(f"📚 Extracted {len(unique_subjects)} unique subjects from COE")
            for i, subject in enumerate(unique_subjects, 1):
                logger.info(f"   {i}. {subject['subject_code']} - {subject['subject_name']}")
            
        except Exception as e:
            logger.error(f"❌ Subject parsing error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return unique_subjects
    
    def extract_coe_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract and interpret text from COE document using OCR.
        
        Args:
            image_path: Path to the COE document image
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if extraction completed
                - raw_text: Raw OCR extracted text
                - ocr_confidence: OCR confidence score
                - interpreted_fields: Dictionary of interpreted fields
                - student_name: Extracted student name
                - student_id: Extracted student ID
                - program: Extracted program/course
                - year_level: Extracted year level
                - semester: Extracted semester info
                - enrollment_date: Extracted enrollment date
                - subjects: List of subjects (added)
                - subject_count: Number of subjects (added)
                - errors: List of errors if any
        """
        result = {
            'success': False,
            'raw_text': '',
            'ocr_confidence': 0.0,
            'interpreted_fields': {},
            'student_name': None,
            'student_id': None,
            'program': None,
            'year_level': None,
            'semester': None,
            'enrollment_date': None,
            'subjects': [],
            'subject_count': 0,
            'errors': []
        }
        
        try:
            if not OCR_AVAILABLE or not self.ocr_interpreter:
                result['errors'].append("OCR service not available")
                return result
            
            if not os.path.exists(image_path):
                result['errors'].append(f"Image not found: {image_path}")
                return result
            
            # Read and preprocess image
            logger.info("🔍 Extracting text from COE document...")
            image = cv2.imread(image_path)
            
            if image is None:
                result['errors'].append("Failed to read image")
                return result
            
            # Use advanced OCR extraction
            ocr_data = self._advanced_ocr_extraction(image)
            
            if not ocr_data['success']:
                result['errors'].extend(ocr_data.get('errors', []))
                return result
            
            result['raw_text'] = ocr_data['text']
            result['ocr_confidence'] = ocr_data['confidence']
            
            # Extract subjects from the text
            logger.info("📚 Extracting subjects from COE text...")
            subjects = self._extract_subjects_from_text(ocr_data['text'])
            result['subjects'] = subjects
            result['subject_count'] = len(subjects)
            
            # Apply intelligent interpretation
            logger.info("🧠 Applying intelligent text interpretation...")
            interpreted = self.ocr_interpreter.interpret_document_text(ocr_data['text'])
            
            if interpreted is None:
                interpreted = {}
            
            result['interpreted_fields'] = interpreted
            
            # Extract specific fields with safe navigation
            result['student_name'] = interpreted.get('student_name', {}).get('interpreted_value') if isinstance(interpreted.get('student_name'), dict) else None
            result['student_id'] = interpreted.get('student_id', {}).get('interpreted_value') if isinstance(interpreted.get('student_id'), dict) else None
            result['program'] = interpreted.get('program', {}).get('interpreted_value') if isinstance(interpreted.get('program'), dict) else None
            result['year_level'] = interpreted.get('year_level', {}).get('interpreted_value') if isinstance(interpreted.get('year_level'), dict) else None
            result['semester'] = interpreted.get('semester', {}).get('interpreted_value') if isinstance(interpreted.get('semester'), dict) else None
            result['enrollment_date'] = interpreted.get('enrollment_date', {}).get('interpreted_value') if isinstance(interpreted.get('enrollment_date'), dict) else None
            
            result['success'] = True
            
            # Count successfully interpreted fields
            fields_extracted = sum(1 for field in [
                result['student_name'], result['student_id'], result['program'],
                result['year_level'], result['semester'], result['enrollment_date']
            ] if field is not None)
            
            logger.info(f"✅ OCR extraction completed. Extracted {fields_extracted}/6 fields + {len(subjects)} subjects")
            
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {str(e)}")
            result['errors'].append(f"OCR extraction error: {str(e)}")
        
        return result
    
    def _advanced_ocr_extraction(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Perform advanced OCR extraction with AWS Textract (primary) or Tesseract (fallback).
        
        Args:
            image: OpenCV image (numpy array)
        
        Returns:
            Dictionary with extracted text and confidence
        """
        result = {
            'success': False,
            'text': '',
            'confidence': 0.0,
            'method': None,
            'errors': []
        }
        
        try:
            # Try AWS Textract first (if available)
            if self.advanced_ocr and self.advanced_ocr.is_enabled():
                logger.info("🔍 Using AWS Textract for OCR extraction...")
                try:
                    # Convert image to bytes
                    success, buffer = cv2.imencode('.jpg', image)
                    if success:
                        image_bytes = buffer.tobytes()
                        
                        # Extract text using AWS Textract
                        textract_result = self.advanced_ocr.extract_text(image_bytes)
                        
                        if textract_result['success']:
                            result['success'] = True
                            result['text'] = textract_result['text']
                            result['confidence'] = textract_result['confidence'] / 100.0  # Convert to 0-1 scale
                            result['method'] = 'aws_textract'
                            logger.info(f"✅ AWS Textract OCR: {result['confidence']:.2%} confidence")
                            return result
                        else:
                            logger.warning(f"⚠️ AWS Textract failed: {textract_result.get('error', 'Unknown error')}")
                            result['errors'].append(f"AWS Textract: {textract_result.get('error', 'Failed')}")
                except Exception as e:
                    logger.warning(f"⚠️ AWS Textract error: {str(e)}")
                    result['errors'].append(f"AWS Textract error: {str(e)}")
            
            # Fallback to Tesseract with multiple preprocessing methods
            logger.info("🔍 Falling back to Tesseract OCR with multiple preprocessing methods...")
            methods = {
                'adaptive_threshold': self._preprocess_adaptive,
                'grayscale': self._preprocess_grayscale,
                'otsu_threshold': self._preprocess_otsu
            }
            
            best_result = None
            best_confidence = 0
            
            # Try all preprocessing methods and pick the best
            for method_name, preprocess_func in methods.items():
                try:
                    processed = preprocess_func(image)
                    
                    # Run Tesseract with custom config
                    custom_config = r'--oem 3 --psm 6'
                    ocr_data = pytesseract.image_to_data(
                        processed,
                        output_type=pytesseract.Output.DICT,
                        config=custom_config
                    )
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Extract text
                    text = pytesseract.image_to_string(processed, config=custom_config)
                    
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_result = {
                            'text': text,
                            'confidence': avg_confidence / 100.0,  # Convert to 0-1 scale
                            'method': f'tesseract_{method_name}'
                        }
                
                except Exception as e:
                    logger.warning(f"⚠️ Tesseract method {method_name} failed: {str(e)}")
                    continue
            
            if best_result:
                result['success'] = True
                result['text'] = best_result['text']
                result['confidence'] = best_result['confidence']
                result['method'] = best_result['method']
                logger.info(f"📊 Best Tesseract method: {result['method']} (confidence: {result['confidence']:.2%})")
            else:
                result['errors'].append("All OCR methods (AWS Textract + Tesseract) failed")
        
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {str(e)}")
            result['errors'].append(f"OCR error: {str(e)}")
        
        return result
    
    def _preprocess_adaptive(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image using adaptive thresholding."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        # Adaptive threshold
        processed = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return processed
    
    def _preprocess_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image using grayscale conversion and enhancement."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return enhanced
    
    def _preprocess_otsu(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image using Otsu's thresholding."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        # Otsu's threshold
        _, processed = cv2.threshold(
            denoised, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return processed
    
    def verify_coe_document(
        self, 
        image_path: str, 
        confidence_threshold: float = 0.5,
        include_ocr: bool = True
    ) -> Dict[str, Any]:
        """
        Verify a Certificate of Enrollment document.
        
        Args:
            image_path: Path to the COE document image
            confidence_threshold: Minimum confidence for detections (default: 0.5)
            include_ocr: Whether to include OCR text extraction (default: True)
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if verification completed
                - is_valid: Boolean indicating if COE is valid
                - confidence: Overall confidence score (0.0-1.0)
                - status: Verification status (VALID/QUESTIONABLE/INVALID)
                - detections: List of detected elements
                - detected_elements: Dictionary of element presence
                - validation_checks: Individual validation results
                - ocr_data: OCR extraction results (if include_ocr=True)
                - extracted_info: Interpreted COE information
                - recommendations: List of recommendations
                - errors: List of errors if any
        """
        result = {
            'success': False,
            'is_valid': False,
            'confidence': 0.0,
            'status': 'INVALID',
            'detections': [],
            'detected_elements': {},
            'validation_checks': {},
            'ocr_data': None,
            'extracted_info': {},
            'recommendations': [],
            'errors': []
        }
        
        try:
            # Check if service is operational
            status = self.get_verification_status()
            if not status['fully_operational']:
                result['errors'].append("COE verification service not operational. Model not loaded.")
                return result
            
            # Validate image path
            if not os.path.exists(image_path):
                result['errors'].append(f"Image not found: {image_path}")
                return result
            
            # Run YOLO detection
            logger.info("🔍 Running YOLO COE detection...")
            detections = self._detect_coe_elements(image_path, confidence_threshold)
            result['detections'] = detections
            
            if len(detections) == 0:
                result['errors'].append("No COE elements detected in image")
                result['status'] = 'INVALID'
                result['recommendations'].append("Ensure the document is clear and well-lit")
                return result
            
            # Analyze detected elements
            logger.info("📋 Analyzing detected elements...")
            detected_elements = self._analyze_detections(detections)
            result['detected_elements'] = detected_elements
            
            # Run validation checks
            logger.info("✅ Running validation checks...")
            validation_checks = self._run_validation_checks(detected_elements)
            result['validation_checks'] = validation_checks
            
            # Extract text using OCR (if requested)
            ocr_confidence = 0.0
            if include_ocr and OCR_AVAILABLE and self.ocr_interpreter:
                logger.info("📝 Extracting text information...")
                ocr_result = self.extract_coe_text(image_path)
                result['ocr_data'] = ocr_result
                
                if ocr_result['success']:
                    ocr_confidence = ocr_result['ocr_confidence']
                    
                    # Store extracted information in a cleaner format
                    result['extracted_info'] = {
                        'student_name': ocr_result.get('student_name'),
                        'student_id': ocr_result.get('student_id'),
                        'program': ocr_result.get('program'),
                        'year_level': ocr_result.get('year_level'),
                        'semester': ocr_result.get('semester'),
                        'enrollment_date': ocr_result.get('enrollment_date'),
                        'subjects': ocr_result.get('subjects', []),
                        'subject_count': ocr_result.get('subject_count', 0)
                    }
                    
                    logger.info(f"✅ OCR extraction successful (confidence: {ocr_confidence:.2%}), found {ocr_result.get('subject_count', 0)} subjects")
                else:
                    logger.warning("⚠️ OCR extraction failed or incomplete")
            
            # Calculate confidence (now includes OCR if available)
            confidence = self._calculate_confidence(
                detected_elements, 
                validation_checks, 
                detections,
                ocr_confidence
            )
            result['confidence'] = confidence
            
            # Determine status
            checks_passed = sum(1 for v in validation_checks.values() if v)
            total_checks = len(validation_checks)
            
            if checks_passed >= 3 and confidence >= 0.8:
                result['status'] = 'VALID'
                result['is_valid'] = True
            elif checks_passed >= 2 and confidence >= 0.6:
                result['status'] = 'QUESTIONABLE'
                result['is_valid'] = False
                result['recommendations'].append("Manual review recommended")
            else:
                result['status'] = 'INVALID'
                result['is_valid'] = False
                result['recommendations'].append("Document may not be a valid COE")
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                result['status'],
                validation_checks,
                detected_elements,
                confidence
            )
            result['recommendations'].extend(recommendations)
            
            result['success'] = True
            logger.info(f"✅ COE verification completed: {result['status']} (confidence: {confidence:.2%})")
            
        except Exception as e:
            logger.error(f"❌ COE verification error: {str(e)}")
            result['errors'].append(f"Verification error: {str(e)}")
        
        return result
    
    def _detect_coe_elements(
        self, 
        image_path: str, 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Detect COE elements using YOLO model.
        
        Args:
            image_path: Path to the image
            confidence_threshold: Minimum confidence for detections
        
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        if not self.yolo_model:
            return detections
        
        try:
            # Run YOLO detection
            results = self.yolo_model(image_path, conf=confidence_threshold, verbose=False)
            
            if len(results) > 0 and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()
                    
                    detection = {
                        'class_id': class_id,
                        'class_name': self.CLASS_NAMES.get(class_id, f'Unknown ({class_id})'),
                        'confidence': confidence,
                        'bbox': {
                            'x1': bbox[0],
                            'y1': bbox[1],
                            'x2': bbox[2],
                            'y2': bbox[3]
                        }
                    }
                    detections.append(detection)
                    
                logger.info(f"✅ Detected {len(detections)} COE elements")
            else:
                logger.warning("⚠️ No COE elements detected")
        
        except Exception as e:
            logger.error(f"❌ YOLO detection error: {str(e)}")
        
        return detections
    
    def _analyze_detections(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze detections to determine which elements are present.
        
        Args:
            detections: List of detection dictionaries
        
        Returns:
            Dictionary of element presence and details
        """
        detected_elements = {
            'city_logo': {'present': False, 'count': 0, 'confidence': 0.0},
            'enrolled_text': {'present': False, 'count': 0, 'confidence': 0.0},
            'free_tuition': {'present': False, 'count': 0, 'confidence': 0.0},
            'university_logo': {'present': False, 'count': 0, 'confidence': 0.0},
            'validated': {'present': False, 'count': 0, 'confidence': 0.0},
            'watermark': {'present': False, 'count': 0, 'confidence': 0.0},
            'ilovetaguig_logo': {'present': False, 'count': 0, 'confidence': 0.0}
        }
        
        # Count detections by class
        class_detections = {}
        for detection in detections:
            class_id = detection['class_id']
            confidence = detection['confidence']
            
            if class_id not in class_detections:
                class_detections[class_id] = {
                    'count': 0,
                    'max_confidence': 0.0
                }
            
            class_detections[class_id]['count'] += 1
            class_detections[class_id]['max_confidence'] = max(
                class_detections[class_id]['max_confidence'],
                confidence
            )
        
        # Map to element names
        element_map = {
            0: 'city_logo',
            1: 'enrolled_text',
            2: 'free_tuition',
            3: 'university_logo',
            4: 'validated',
            5: 'watermark',
            6: 'ilovetaguig_logo'
        }
        
        for class_id, data in class_detections.items():
            element_key = element_map.get(class_id)
            if element_key:
                detected_elements[element_key]['present'] = True
                detected_elements[element_key]['count'] = data['count']
                detected_elements[element_key]['confidence'] = data['max_confidence']
        
        return detected_elements
    
    def _run_validation_checks(self, detected_elements: Dict[str, Any]) -> Dict[str, bool]:
        """
        Run validation checks on detected elements.
        
        Args:
            detected_elements: Dictionary of element presence
        
        Returns:
            Dictionary of validation check results
        """
        checks = {
            'has_city_logo': False,
            'has_enrolled_text': False,
            'has_university_logo': False,
            'has_required_elements': False,
            'has_security_features': False
        }
        
        # Check required elements
        checks['has_city_logo'] = detected_elements['city_logo']['present']
        checks['has_enrolled_text'] = detected_elements['enrolled_text']['present']
        checks['has_university_logo'] = detected_elements['university_logo']['present']
        
        # All required elements present
        checks['has_required_elements'] = (
            checks['has_city_logo'] and
            checks['has_enrolled_text'] and
            checks['has_university_logo']
        )
        
        # Check for security features (watermark or validated stamp)
        checks['has_security_features'] = (
            detected_elements['watermark']['present'] or
            detected_elements['validated']['present']
        )
        
        return checks
    
    def _calculate_confidence(
        self,
        detected_elements: Dict[str, Any],
        validation_checks: Dict[str, bool],
        detections: List[Dict[str, Any]],
        ocr_confidence: float = 0.0
    ) -> float:
        """
        Calculate overall confidence score.
        
        Args:
            detected_elements: Dictionary of element presence
            validation_checks: Validation check results
            detections: List of detections
            ocr_confidence: OCR extraction confidence (0.0-1.0)
        
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.0
        
        try:
            if ocr_confidence > 0:
                # With OCR: YOLO (60%) + OCR (40%)
                # YOLO component
                if detections:
                    avg_detection_confidence = sum(d['confidence'] for d in detections) / len(detections)
                    yolo_score = 0.0
                    
                    # Detection confidence (40%)
                    yolo_score += 0.40 * avg_detection_confidence
                    
                    # Required elements (30%)
                    required_score = sum([
                        detected_elements['city_logo']['confidence'],
                        detected_elements['enrolled_text']['confidence'],
                        detected_elements['university_logo']['confidence']
                    ]) / 3 if any([
                        detected_elements['city_logo']['present'],
                        detected_elements['enrolled_text']['present'],
                        detected_elements['university_logo']['present']
                    ]) else 0
                    yolo_score += 0.30 * required_score
                    
                    # Optional elements (15%)
                    optional_elements = ['free_tuition', 'validated', 'watermark', 'ilovetaguig_logo']
                    optional_present = sum(1 for e in optional_elements if detected_elements[e]['present'])
                    yolo_score += 0.15 * (optional_present / len(optional_elements))
                    
                    # Validation checks (15%)
                    checks_passed = sum(1 for v in validation_checks.values() if v)
                    total_checks = len(validation_checks)
                    yolo_score += 0.15 * (checks_passed / total_checks)
                    
                    # Combine: 60% YOLO + 40% OCR
                    confidence = 0.60 * yolo_score + 0.40 * ocr_confidence
            else:
                # Without OCR: YOLO only (100%)
                # Base confidence from detection confidences
                if detections:
                    avg_detection_confidence = sum(d['confidence'] for d in detections) / len(detections)
                    confidence += 0.40 * avg_detection_confidence
                
                # Required elements (30%)
                required_score = sum([
                    detected_elements['city_logo']['confidence'],
                    detected_elements['enrolled_text']['confidence'],
                    detected_elements['university_logo']['confidence']
                ]) / 3 if any([
                    detected_elements['city_logo']['present'],
                    detected_elements['enrolled_text']['present'],
                    detected_elements['university_logo']['present']
                ]) else 0
                confidence += 0.30 * required_score
                
                # Optional elements (15%)
                optional_elements = ['free_tuition', 'validated', 'watermark', 'ilovetaguig_logo']
                optional_present = sum(1 for e in optional_elements if detected_elements[e]['present'])
                confidence += 0.15 * (optional_present / len(optional_elements))
                
                # Validation checks (15%)
                checks_passed = sum(1 for v in validation_checks.values() if v)
                total_checks = len(validation_checks)
                confidence += 0.15 * (checks_passed / total_checks)
        
        except Exception as e:
            logger.error(f"❌ Confidence calculation error: {str(e)}")
        
        return round(confidence, 3)
    
    def _generate_recommendations(
        self,
        status: str,
        validation_checks: Dict[str, bool],
        detected_elements: Dict[str, Any],
        confidence: float
    ) -> List[str]:
        """
        Generate recommendations based on verification results.
        
        Args:
            status: Verification status
            validation_checks: Validation check results
            detected_elements: Dictionary of element presence
            confidence: Overall confidence score
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            if status == 'INVALID':
                recommendations.append("Document does not appear to be a valid COE")
            
            if not validation_checks.get('has_city_logo', False):
                recommendations.append("City of Taguig logo not detected")
            
            if not validation_checks.get('has_enrolled_text', False):
                recommendations.append("'ENROLLED' status text not found")
            
            if not validation_checks.get('has_university_logo', False):
                recommendations.append("TCU logo not detected")
            
            if not validation_checks.get('has_security_features', False):
                recommendations.append("No security features detected (watermark/validated stamp)")
            
            if confidence < 0.5:
                recommendations.append("Low confidence - ensure document is clear and complete")
            
            if not detected_elements['free_tuition']['present']:
                recommendations.append("Free tuition indicator not found (may not be applicable)")
        
        except Exception as e:
            logger.error(f"❌ Recommendation generation error: {str(e)}")
        
        return recommendations


# Singleton instance
_coe_verification_service = None

def get_coe_verification_service() -> COEVerificationService:
    """Get or create the singleton COE verification service instance."""
    global _coe_verification_service
    if _coe_verification_service is None:
        _coe_verification_service = COEVerificationService()
    return _coe_verification_service
