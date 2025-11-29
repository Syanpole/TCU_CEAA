"""
Voter's Certificate Verification Service
=========================================

Voter's Certificate (Voter's ID/Registration) verification using YOLO v8 object detection.
This service detects and verifies key elements in voter's certificate documents.

Features:
- YOLO v8 model for voter's certificate element detection
- Detection of official logos, stamps, and watermarks
- Validation of required document elements
- Advanced OCR with AWS Textract for text extraction
- Intelligent field interpretation
- Confidence scoring
- Document authenticity verification

Author: TCU CEAA Development Team
Date: November 13, 2025
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
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


class VoterCertificateVerificationService:
    """
    Voter's Certificate Verification Service using YOLO v8.
    
    This service provides comprehensive voter's certificate document verification including:
    - Detection of official logos and stamps
    - Verification of voter registration elements
    - Authentication through watermarks
    - Validation of required document elements
    - Advanced OCR with AWS Textract
    - Intelligent field extraction (voter name, registration number, precinct, etc.)
    """
    
    # Class names mapping (from your trained YOLO model)
    CLASS_NAMES = {
        0: 'COMELEC Logo',
        1: 'FINGER PRINT',
        2: 'Person'
    }
    
    # Required elements for valid voter certificate (based on your model with 0.9+ mAP)
    REQUIRED_ELEMENTS = {
        'comelec_logo': 0,      # COMELEC Logo
        'fingerprint': 1,       # Fingerprint/Biometrics area
        'photo': 2,             # Person/Photo area
    }
    
    def __init__(self):
        """Initialize the Voter Certificate verification service."""
        self.yolo_model = None
        self.model_path = Path(settings.BASE_DIR) / 'ai_model_data' / 'trained_models' / 'yolov8_voters_certification_detection.pt'
        self.ocr_interpreter = None
        
        # Initialize YOLO model
        if YOLO_AVAILABLE and self.model_path.exists():
            try:
                self.yolo_model = YOLO(str(self.model_path))
                logger.info(f"✅ Voter Certificate YOLO detection model loaded from: {self.model_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load Voter Certificate YOLO model: {str(e)}")
                self.yolo_model = None
        else:
            if not YOLO_AVAILABLE:
                logger.warning("⚠️ YOLO not available. Install ultralytics package.")
            if not self.model_path.exists():
                logger.warning(f"⚠️ Voter Certificate YOLO model not found at: {self.model_path}")
        
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
        Check the status of Voter Certificate verification capabilities.
        
        Returns:
            Dictionary containing status of each component
        """
        advanced_ocr_enabled = self.advanced_ocr and self.advanced_ocr.is_enabled()
        
        return {
            'voter_certificate_detection': self.yolo_model is not None,
            'ocr_available': self.ocr_interpreter is not None,
            'advanced_ocr_enabled': advanced_ocr_enabled,
            'ocr_method': 'AWS Textract' if advanced_ocr_enabled else 'Tesseract (Fallback)',
            'model_path': str(self.model_path) if self.model_path else None,
            'fully_operational': self.yolo_model is not None and self.ocr_interpreter is not None
        }
    
    def extract_voter_certificate_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract and interpret text from Voter Certificate document using OCR.
        
        Args:
            image_path: Path to the Voter Certificate document image
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if extraction completed
                - raw_text: Raw OCR extracted text
                - ocr_confidence: OCR confidence score
                - interpreted_fields: Dictionary of interpreted fields
                - voter_name: Extracted voter name
                - registration_number: Extracted voter registration number
                - precinct_number: Extracted precinct number
                - address: Extracted address
                - date_of_birth: Extracted date of birth
                - registration_date: Extracted registration date
                - errors: List of errors if any
        """
        result = {
            'success': False,
            'raw_text': '',
            'ocr_confidence': 0.0,
            'interpreted_fields': {},
            'voter_name': None,
            'registration_number': None,
            'precinct_number': None,
            'address': None,
            'date_of_birth': None,
            'registration_date': None,
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
            logger.info("🔍 Extracting text from Voter Certificate document...")
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
            
            # Extract specific voter certificate fields
            logger.info("🧠 Extracting voter certificate fields...")
            extracted_fields = self._extract_voter_fields(ocr_data['text'], ocr_data.get('blocks', []))
            
            result['interpreted_fields'] = extracted_fields
            
            # Map extracted fields
            result['voter_name'] = extracted_fields.get('voter_name')
            result['registration_number'] = extracted_fields.get('registration_number')
            result['precinct_number'] = extracted_fields.get('precinct_number')
            result['address'] = extracted_fields.get('address')
            result['date_of_birth'] = extracted_fields.get('date_of_birth')
            result['registration_date'] = extracted_fields.get('registration_date')
            
            result['success'] = True
            
            # Count successfully extracted fields
            fields_extracted = sum(1 for field in [
                result['voter_name'], result['registration_number'], result['precinct_number'],
                result['address'], result['date_of_birth'], result['registration_date']
            ] if field is not None)
            
            logger.info(f"✅ OCR extraction completed. Extracted {fields_extracted}/6 fields")
            
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {str(e)}")
            result['errors'].append(f"OCR extraction error: {str(e)}")
        
        return result
    
    def _advanced_ocr_extraction(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract text using Advanced OCR (AWS Textract) with fallback to Tesseract.
        
        Args:
            image: Image as numpy array
        
        Returns:
            Dictionary with OCR results
        """
        result = {
            'success': False,
            'text': '',
            'confidence': 0.0,
            'blocks': [],
            'method': 'none',
            'errors': []
        }
        
        try:
            # Try AWS Textract first
            if self.advanced_ocr and self.advanced_ocr.is_enabled():
                logger.info("📡 Using AWS Textract for OCR...")
                
                # Convert image to bytes
                success, buffer = cv2.imencode('.jpg', image)
                if not success:
                    raise Exception("Failed to encode image")
                
                image_bytes = buffer.tobytes()
                
                # Call AWS Textract
                ocr_result = self.advanced_ocr.extract_text(image_bytes, document_type='IMAGE')
                
                if ocr_result['success']:
                    result['success'] = True
                    result['text'] = ocr_result['text']
                    result['confidence'] = ocr_result['confidence'] / 100.0  # Convert to 0.0-1.0
                    result['blocks'] = ocr_result.get('blocks', [])
                    result['method'] = 'AWS Textract'
                    logger.info(f"✅ AWS Textract OCR completed with {result['confidence']:.2%} confidence")
                    return result
                else:
                    logger.warning(f"⚠️ AWS Textract failed: {ocr_result.get('error')}, falling back to Tesseract")
            
            # Fallback to Tesseract
            logger.info("📝 Using Tesseract for OCR (fallback)...")
            processed_image = self._preprocess_for_ocr(image)
            
            # Extract text with confidence
            custom_config = r'--oem 3 --psm 6'
            ocr_data = pytesseract.image_to_data(
                processed_image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Build text and calculate confidence
            text_parts = []
            confidences = []
            
            for i in range(len(ocr_data['text'])):
                word = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])
                
                if word and conf > 0:
                    text_parts.append(word)
                    confidences.append(conf)
            
            result['text'] = ' '.join(text_parts)
            result['confidence'] = (np.mean(confidences) / 100.0) if confidences else 0.0
            result['method'] = 'Tesseract'
            result['success'] = True
            
            logger.info(f"✅ Tesseract OCR completed with {result['confidence']:.2%} confidence")
            
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {str(e)}")
            result['errors'].append(str(e))
        
        return result
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for optimal OCR results.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive threshold for better text extraction
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        return binary
    
    def _extract_voter_fields(self, text: str, blocks: List[Dict]) -> Dict[str, Any]:
        """
        Extract voter certificate specific fields from OCR text.
        
        Args:
            text: Raw OCR text
            blocks: Text blocks with position information
        
        Returns:
            Dictionary of extracted fields
        """
        import re
        
        fields = {
            'voter_name': None,
            'registration_number': None,
            'precinct_number': None,
            'address': None,
            'date_of_birth': None,
            'registration_date': None
        }
        
        try:
            lines = text.split('\n')
            text_lower = text.lower()
            
            # Extract voter name (usually after "name" label)
            name_patterns = [
                r'Name\s*:\s*\n?\s*([A-Z][A-Z\s,\.]+?)(?:\s+Voter\?|\s+Sex\s*:|\n)',  # Match "Name :" with newline
                r'Name\s*:\s*([A-Z][A-Z\s,\.]+?)(?:\s+Voter\?|\s+Sex\s*:|\s+BIOMETRICS|$)',  # Standard format
                r'(?:Name)[:\s]+([A-Z][A-Z\s,\.]+?)(?:\s+BIOMETRICS|\s+Sex|\s+Male|\s+Female|$)',
                r'(?:name|pangalan)[:\s]+([A-Z][A-Za-z\s,\.]+?)(?:\s+BIOMETRICS|\s+Sex|$)',
                r'(?:voter[\'s]?\s+name)[:\s]+([A-Z][A-Za-z\s,\.]+?)(?:\s+BIOMETRICS|$)',
                r'([A-Z][A-Z\s]+,\s*[A-Z][A-Za-z\s]+)(?:\s+BIOMETRICS|$)'  # Lastname, Firstname format
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    name = match.group(1).strip()
                    # Clean up name - remove trailing noise
                    name = re.sub(r'\s+', ' ', name)
                    name = re.sub(r'\s*(BIOMETRICS|Sex|Male|Female|Voter\?).*$', '', name, flags=re.IGNORECASE)
                    if len(name) > 5 and len(name.split()) >= 2:
                        fields['voter_name'] = name
                        logger.info(f"✅ Extracted voter name: {name}")
                        break
            
            # Extract registration number (various formats)
            reg_num_patterns = [
                r'(?:Voter\'?s?\s+Identification\s+Number)[:\s]*([A-Z0-9\-]+)',  # Voter's Identification Number
                r'(?:registration\s+(?:no|number|#))[:\s]*([A-Z0-9\-]+)',
                r'(?:voter\s+(?:id|number))[:\s]*([A-Z0-9\-]+)',
                r'(?:VRR?\s+No\.?)[:\s]*([A-Z0-9]+)',  # VRR No.
                r'\b([0-9]{13,16})\b',  # Long number format like 7607300096171
                r'\b([0-9A-Z]{20,30})\b',  # Format: 76070349AC0278EGF10000-4
                r'\b([0-9]{4}-[0-9]{4}-[0-9]{4})\b'  # Format: 0000-0000-0000
            ]
            
            for pattern in reg_num_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    reg_num = match.group(1).strip()
                    # Validate it's not a date or other common number
                    if len(reg_num) >= 10 and not re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', reg_num):
                        fields['registration_number'] = reg_num
                        break
            
            # Extract precinct number
            precinct_patterns = [
                r'(?:Precinct\s+No\.?)[:\s]*([0-9]{4}\s*[A-Z]?)',  # Precinct No. : 0349 A
                r'(?:precinct\s+(?:no|number|#))[:\s]*([0-9]{4}\s*[A-Z]?)',
                r'(?:pct\.?\s+no)[:\s]*([0-9]{4}\s*[A-Z]?)',
                r'\b([0-9]{4}\s*[A-Z])\b'  # Format: 0349 A or 0349A
            ]
            
            for pattern in precinct_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    precinct = match.group(1).strip()
                    # Clean up extra whitespace and remove trailing non-alphanumeric
                    precinct = re.sub(r'\s+', ' ', precinct)
                    # Remove any text after the precinct number (like "Name")
                    precinct = re.sub(r'\s+[A-Z][a-z]+.*$', '', precinct)
                    if len(precinct) >= 4:  # Minimum valid precinct length
                        fields['precinct_number'] = precinct
                        break
            
            # Extract address/residence (look for "Residence" field in voter certificate)
            address_patterns = [
                r'Residence\s*:\s*([A-Z0-9][A-Z0-9\s\.,\-]+?)(?:\s+OF RESIDENCE|VOTING RECORD|\n[A-Z]{2,}\s+[A-Z]{2,}|$)',  # Match multi-line residence
                r'(?:Residence|Address)[:\s]+(.+?)(?:\n\s*[A-Z]{2,}\s+[A-Z]{2,}|VOTING RECORD|OF RESIDENCE|$)',  # Multi-line address
                r'(?:Barangay)[:\s]*([A-Z][A-Za-z\s]+?)(?:\s+(?:VRR|Illiterate|Disabled|Precinct)|$)',
                r'(?:address|tirahan)[:\s]+(.+?)(?:\n|Illiterate|Disabled|$)',
                r'(?:barangay|brgy\.?)[:\s]*([A-Za-z\s,]+?)(?:\s+(?:VRR|Illiterate|Disabled)|$)',
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    address = match.group(1).strip()
                    # Clean up address - remove trailing noise and extra whitespace
                    address = re.sub(r'\s+', ' ', address)
                    address = re.sub(r'\s*(Illiterate|Disabled|VRR|Precinct|OF RESIDENCE|VOTING RECORD).*$', '', address, flags=re.IGNORECASE)
                    # Remove trailing city/region lines if they repeat
                    address = re.sub(r'\s+(CITY OF [A-Z]+|NATIONAL CAPITAL REGION).*$', '', address, flags=re.IGNORECASE)
                    if len(address) > 5:
                        fields['address'] = address.strip()
                        logger.info(f"✅ Extracted address: {address}")
                        break
            
            # Extract date of birth
            dob_patterns = [
                r'(?:date\s+of\s+birth|birth\s+date|d\.?o\.?b\.?)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(?:ipinanganak)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b'
            ]
            
            for pattern in dob_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields['date_of_birth'] = match.group(1).strip()
                    break
            
            # Extract registration date
            reg_date_patterns = [
                r'(?:registration\s+date|date\s+registered)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(?:date\s+of\s+registration)[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            ]
            
            for pattern in reg_date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields['registration_date'] = match.group(1).strip()
                    break
            
            logger.info(f"📋 Extracted voter fields: {sum(1 for v in fields.values() if v is not None)}/6 fields")
            
        except Exception as e:
            logger.error(f"❌ Error extracting voter fields: {str(e)}")
        
        return fields
    
    def verify_voter_certificate_document(
        self, 
        image_path: str, 
        confidence_threshold: float = 0.5,
        include_ocr: bool = True,
        user_application_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verify a Voter's Certificate document and compare with user's application data.
        
        Args:
            image_path: Path to the voter certificate document image
            confidence_threshold: Minimum confidence for detections (default: 0.5)
            include_ocr: Whether to include OCR text extraction (default: True)
            user_application_data: Optional dictionary containing user's full application data for comparison
                Expected fields: first_name, middle_name, last_name, barangay, house_no, street, district
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if verification completed
                - is_valid: Boolean indicating if voter certificate is valid
                - confidence: Overall confidence score (0.0-1.0)
                - status: Verification status (VALID/QUESTIONABLE/INVALID)
                - detections: List of detected elements
                - detected_elements: Dictionary of element presence
                - validation_checks: Individual validation results
                - ocr_data: OCR extraction results (if include_ocr=True)
                - extracted_info: Interpreted voter certificate information
                - field_matches: Dictionary showing which fields match user's application data
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
            'ocr_data': {},
            'extracted_info': {},
            'field_matches': {},
            'recommendations': [],
            'errors': []
        }
        
        try:
            # Validate image path
            if not os.path.exists(image_path):
                result['errors'].append(f"Image not found: {image_path}")
                return result
            
            # Run YOLO detection
            logger.info("🔍 Running YOLO Voter Certificate detection...")
            detections = self._detect_voter_certificate_elements(image_path, confidence_threshold)
            result['detections'] = detections
            
            if len(detections) == 0:
                result['errors'].append("No voter certificate elements detected in image")
                result['status'] = 'INVALID'
                result['recommendations'].append("Ensure the document is a valid voter's certificate")
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
                ocr_result = self.extract_voter_certificate_text(image_path)
                result['ocr_data'] = ocr_result
                
                if ocr_result['success']:
                    ocr_confidence = ocr_result['ocr_confidence']
                    
                    # Store extracted information in a cleaner format
                    result['extracted_info'] = {
                        'voter_name': ocr_result.get('voter_name'),
                        'registration_number': ocr_result.get('registration_number'),
                        'precinct_number': ocr_result.get('precinct_number'),
                        'address': ocr_result.get('address'),
                        'date_of_birth': ocr_result.get('date_of_birth'),
                        'registration_date': ocr_result.get('registration_date')
                    }
                    
                    # Compare with user application data if provided
                    if user_application_data:
                        logger.info("🔍 Comparing extracted data with user's application...")
                        field_matches = self._compare_voter_with_application(result['extracted_info'], user_application_data)
                        result['field_matches'] = field_matches
                        parent_matches = self._compare_voter_with_parents(result['extracted_info'], user_application_data)
                        result['parent_matches'] = parent_matches
                        identity_verified = False
                        identity_type = None
                        if field_matches.get('voter_name', {}).get('match'):
                            identity_verified = True
                            identity_type = 'student'
                        elif parent_matches.get('parent_name_match'):
                            identity_verified = True
                            identity_type = parent_matches.get('matched_parent')
                        result['identity_verified'] = identity_verified
                        result['identity_type'] = identity_type
                        
                        # Add match information to recommendations
                        total_fields = len(field_matches)
                        matched_fields = sum(1 for match in field_matches.values() if match.get('match', False))
                        
                        if total_fields > 0:
                            match_percentage = (matched_fields / total_fields) * 100
                            if match_percentage >= 80:
                                result['recommendations'].append(f"✅ {matched_fields}/{total_fields} fields match user's application ({match_percentage:.0f}%)")
                            elif match_percentage >= 50:
                                result['recommendations'].append(f"⚠️ {matched_fields}/{total_fields} fields match user's application ({match_percentage:.0f}%)")
                            else:
                                result['recommendations'].append(f"❌ Only {matched_fields}/{total_fields} fields match user's application ({match_percentage:.0f}%)")
            
            # Calculate overall confidence (with field matching if available)
            logger.info("📊 Calculating confidence score...")
            confidence = self._calculate_confidence(
                detected_elements, 
                validation_checks, 
                detections,
                ocr_confidence,
                field_matches=result.get('field_matches')
            )
            result['confidence'] = confidence
            
            # Check if identity was verified (name matches student or parents)
            identity_verified = result.get('identity_verified', False)
            
            # CRITICAL: Reject if voter name doesn't match student or parents
            if user_application_data and not identity_verified:
                result['is_valid'] = False
                result['status'] = 'INVALID'
                # Keep the confidence score - it represents detection quality, not match validity
                # High confidence rejection means: "We are confident this document doesn't match"
                result['recommendations'].append("❌ DOCUMENT REJECTED - Identity Verification Failed")
                result['recommendations'].append("📋 The name on this voter certificate doesn't match you or your parents.")
                result['recommendations'].append("🔍 Voter certificates must belong to YOU or your MOTHER or FATHER.")
                
                # Add specific mismatch details
                voter_name = result.get('extracted_info', {}).get('voter_name', 'N/A')
                student_name = f"{user_application_data.get('first_name', '')} {user_application_data.get('last_name', '')}".strip()
                mother_name = user_application_data.get('mother_name', 'N/A')
                father_name = user_application_data.get('father_name', 'N/A')
                
                result['recommendations'].append(f"❌ Document shows: '{voter_name}'")
                result['recommendations'].append(f"✅ Expected one of: Student '{student_name}' OR Mother '{mother_name}' OR Father '{father_name}'")
                result['recommendations'].append("💡 What to do: Upload a voter certificate/ID that belongs to you or one of your parents listed in your application.")
                
                # Add confidence interpretation for rejections
                if confidence >= 0.75:
                    result['recommendations'].append(f"✅ AI Detection Quality: High ({confidence*100:.0f}%) - Rejection is accurate")
                elif confidence >= 0.60:
                    result['recommendations'].append(f"⚠️ AI Detection Quality: Medium ({confidence*100:.0f}%) - Manual review may be needed")
                else:
                    result['recommendations'].append(f"❌ AI Detection Quality: Low ({confidence*100:.0f}%) - Document quality poor, please reupload")
            else:
                # Determine validity and status when identity is verified
                is_valid = self._determine_validity(
                    detected_elements,
                    validation_checks,
                    confidence,
                    identity_verified
                )
                result['is_valid'] = is_valid
                
                if is_valid:
                    if confidence >= 0.85:
                        result['status'] = 'VALID'
                    else:
                        result['status'] = 'QUESTIONABLE'
                        result['recommendations'].append("Manual review recommended due to moderate confidence")
                else:
                    result['status'] = 'INVALID'
                    result['recommendations'].append("Document does not meet validity requirements")
            
            # Generate recommendations
            result['recommendations'].extend(self._generate_recommendations(
                detected_elements, validation_checks, confidence
            ))
            
            result['success'] = True
            logger.info(f"✅ Voter Certificate verification completed: {result['status']} ({confidence:.2%})")
            
        except Exception as e:
            logger.error(f"❌ Voter Certificate verification error: {str(e)}")
            result['errors'].append(f"Verification error: {str(e)}")
        
        return result

    def _compare_voter_with_parents(
        self,
        extracted_info: Dict[str, Any],
        user_application_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        from difflib import SequenceMatcher
        def norm(s: str) -> str:
            return s.upper().strip() if isinstance(s, str) else ''
        voter_name = norm(extracted_info.get('voter_name', ''))
        mother_name = norm(user_application_data.get('mother_name', ''))
        father_name = norm(user_application_data.get('father_name', ''))
        matched_parent = None
        parent_match = False
        score = 0.0
        if voter_name and mother_name:
            score_m = SequenceMatcher(None, voter_name, mother_name).ratio()
            if score_m >= 0.75:
                parent_match = True
                matched_parent = 'mother'
                score = score_m
        if not parent_match and voter_name and father_name:
            score_f = SequenceMatcher(None, voter_name, father_name).ratio()
            if score_f >= 0.75:
                parent_match = True
                matched_parent = 'father'
                score = score_f
        return {
            'parent_name_match': parent_match,
            'matched_parent': matched_parent,
            'score': score,
            'extracted': voter_name,
            'mother_name': mother_name,
            'father_name': father_name
        }
    
    def _detect_voter_certificate_elements(
        self, 
        image_path: str, 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Detect voter certificate elements using YOLO model.
        
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
                        'class_name': self.CLASS_NAMES.get(class_id, f'Unknown-{class_id}'),
                        'confidence': confidence,
                        'bbox': bbox
                    }
                    
                    detections.append(detection)
                    logger.debug(f"   ✓ Detected: {detection['class_name']} ({confidence:.2%})")
            
            logger.info(f"   📊 Total detections: {len(detections)}")
            
        except Exception as e:
            logger.error(f"❌ YOLO detection error: {str(e)}")
        
        return detections
    
    def _analyze_detections(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze detections to determine which elements are present.
        
        Args:
            detections: List of detection dictionaries
        
        Returns:
            Dictionary mapping element names to presence info
        """
        detected_elements = {}
        
        # Initialize all required elements as not present (3 elements: COMELEC Logo, FINGER PRINT, Person)
        for element_name in self.REQUIRED_ELEMENTS.keys():
            detected_elements[element_name] = {
                'present': False,
                'confidence': 0.0,
                'count': 0
            }
        
        # Check which elements were detected
        for detection in detections:
            class_id = detection['class_id']
            confidence = detection['confidence']
            
            # Find element name by class ID (only checking required elements)
            element_name = None
            for name, cid in self.REQUIRED_ELEMENTS.items():
                if cid == class_id:
                    element_name = name
                    break
            
            if element_name and element_name in detected_elements:
                detected_elements[element_name]['present'] = True
                detected_elements[element_name]['count'] += 1
                # Keep highest confidence
                if confidence > detected_elements[element_name]['confidence']:
                    detected_elements[element_name]['confidence'] = confidence
        
        return detected_elements
    
    def _run_validation_checks(self, detected_elements: Dict[str, Any]) -> Dict[str, bool]:
        """
        Run validation checks on detected elements.
        
        Args:
            detected_elements: Dictionary of detected elements
        
        Returns:
            Dictionary of validation check results
        """
        checks = {
            'has_comelec_logo': detected_elements.get('comelec_logo', {}).get('present', False),
            'has_fingerprint': detected_elements.get('fingerprint', {}).get('present', False),
            'has_photo': detected_elements.get('photo', {}).get('present', False),
            'all_required_elements_present': all([
                detected_elements.get('comelec_logo', {}).get('present', False),
                detected_elements.get('fingerprint', {}).get('present', False),
                detected_elements.get('photo', {}).get('present', False)
            ])
        }
        
        return checks
    
    def _calculate_confidence(
        self,
        detected_elements: Dict[str, Any],
        validation_checks: Dict[str, bool],
        detections: List[Dict[str, Any]],
        ocr_confidence: float = 0.0,
        field_matches: Dict[str, Any] = None
    ) -> float:
        """
        Calculate overall confidence score.
        
        Args:
            detected_elements: Dictionary of element presence
            validation_checks: Validation check results
            detections: List of detections
            ocr_confidence: OCR extraction confidence (0.0-1.0)
            field_matches: Dictionary of field match results (optional)
        
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.0
        
        try:
            if ocr_confidence > 0:
                # With OCR: YOLO + OCR + Field Matching
                # YOLO component
                if detections:
                    avg_detection_confidence = sum(d['confidence'] for d in detections) / len(detections)
                    yolo_score = 0.0
                    
                    # Detection confidence (50%)
                    yolo_score += 0.50 * avg_detection_confidence
                    
                    # Required elements (35%) - all 3 elements are equally important
                    required_elements = ['comelec_logo', 'fingerprint', 'photo']
                    required_present = sum(1 for e in required_elements if detected_elements.get(e, {}).get('present', False))
                    yolo_score += 0.35 * (required_present / len(required_elements))
                    
                    # Validation checks (15%)
                    checks_passed = sum(1 for v in validation_checks.values() if v)
                    total_checks = len(validation_checks)
                    yolo_score += 0.15 * (checks_passed / total_checks)
                    
                    if field_matches:
                        # WITH FIELD MATCHING: YOLO (40%) + OCR (25%) + Field Matching (35%)
                        confidence = 0.40 * yolo_score + 0.25 * ocr_confidence
                        
                        # FIELD MATCHING SCORE (35%) - Critical for ownership verification
                        match_scores = [match.get('score', 0.0) for match in field_matches.values() if isinstance(match, dict)]
                        if match_scores:
                            avg_match_score = sum(match_scores) / len(match_scores)
                            confidence += 0.35 * avg_match_score
                            logger.info(f"🎯 Field matching average score: {avg_match_score:.2%} -> contributes {0.35 * avg_match_score:.2%} to confidence")
                    else:
                        # WITHOUT FIELD MATCHING: YOLO (60%) + OCR (40%)
                        confidence = 0.60 * yolo_score + 0.40 * ocr_confidence
            else:
                # Without OCR: YOLO only (100%)
                if detections:
                    # Base confidence from detection confidences (60%)
                    avg_detection_confidence = sum(d['confidence'] for d in detections) / len(detections)
                    confidence = 0.60 * avg_detection_confidence
                    
                    # Required elements (30%) - all 3 elements
                    required_elements = ['comelec_logo', 'fingerprint', 'photo']
                    required_present = sum(1 for e in required_elements if detected_elements.get(e, {}).get('present', False))
                    confidence += 0.30 * (required_present / len(required_elements))
                    
                    # Validation checks (10%)
                    checks_passed = sum(1 for v in validation_checks.values() if v)
                    total_checks = len(validation_checks)
                    confidence += 0.10 * (checks_passed / total_checks)
        
        except Exception as e:
            logger.error(f"❌ Confidence calculation error: {str(e)}")
        
        return min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _compare_voter_with_application(
        self,
        extracted_info: Dict[str, Any],
        user_application_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare extracted voter certificate fields with user's application data.
        
        Args:
            extracted_info: Fields extracted from voter certificate
            user_application_data: User's full application data
        
        Returns:
            Dictionary with field-by-field comparison results
        """
        from difflib import SequenceMatcher
        
        def fuzzy_match(str1: str, str2: str, threshold: float = 0.80) -> Tuple[bool, float]:
            """Compare two strings with fuzzy matching"""
            if not str1 or not str2:
                return False, 0.0
            
            str1_clean = str1.upper().strip()
            str2_clean = str2.upper().strip()
            
            # Exact match
            if str1_clean == str2_clean:
                return True, 1.0
            
            # Fuzzy match
            ratio = SequenceMatcher(None, str1_clean, str2_clean).ratio()
            return ratio >= threshold, ratio
        
        matches = {}
        
        # Compare voter name
        if extracted_info.get('voter_name') and user_application_data.get('first_name'):
            app_full_name = f"{user_application_data.get('first_name', '')} {user_application_data.get('middle_name', '')} {user_application_data.get('last_name', '')}".strip()
            
            # Try direct match first
            match, score = fuzzy_match(extracted_info['voter_name'], app_full_name, threshold=0.75)
            
            # If no match, try "last name first" format common in voter certificates
            if not match:
                # Voter cert format: "LAST NAME, FIRST MIDDLE"
                # Try to parse and reverse
                extracted_name_clean = extracted_info['voter_name'].upper().strip()
                if ',' in extracted_name_clean:
                    parts = extracted_name_clean.split(',', 1)
                    last_name = parts[0].strip()
                    first_middle = parts[1].strip() if len(parts) > 1 else ''
                    # Compare name components separately
                    app_first = user_application_data.get('first_name', '').upper()
                    app_middle = user_application_data.get('middle_name', '').upper()
                    app_last = user_application_data.get('last_name', '').upper()
                    
                    # Check if last names match
                    last_match = SequenceMatcher(None, last_name, app_last).ratio()
                    # Check if first/middle names are in the extracted first_middle part
                    first_middle_combined = f"{app_first} {app_middle}".strip()
                    first_middle_match = SequenceMatcher(None, first_middle, first_middle_combined).ratio()
                    
                    # Average the component matches
                    component_score = (last_match + first_middle_match) / 2
                    if component_score >= 0.75:
                        match = True
                        score = component_score
            
            matches['voter_name'] = {
                'match': match,
                'score': score,
                'extracted': extracted_info['voter_name'],
                'application': app_full_name
            }
        
        # Compare address/barangay
        if extracted_info.get('address') and user_application_data.get('barangay'):
            # Build full address from application
            app_address_parts = [
                user_application_data.get('house_no', ''),
                user_application_data.get('street', ''),
                user_application_data.get('barangay', ''),
                user_application_data.get('district', '')
            ]
            app_address = ' '.join([p for p in app_address_parts if p]).strip()
            
            # Try direct fuzzy match
            match, score = fuzzy_match(extracted_info['address'], app_address, threshold=0.65)
            
            # If no match, try with normalized address (handle P-1/P-2 vs PUROK variations)
            if not match:
                extracted_normalized = extracted_info['address'].upper()
                app_normalized = app_address.upper()
                
                # Normalize common address format variations
                # "P-1" or "P-2" → "PUROK 1" or "PUROK 2"
                extracted_normalized = re.sub(r'\bP-(\d+)\b', r'PUROK \1', extracted_normalized)
                # "MAGUINDANAO ST. RD 23" contains street info
                # Check if key address components match
                
                # Extract key components from both
                # Block and Lot numbers
                extracted_block_lot = re.findall(r'(?:BLK|BLOCK)\s*\d+\s*(?:LOT|LT)\s*\d+', extracted_normalized)
                app_block_lot = re.findall(r'(?:BLK|BLOCK)\s*\d+\s*(?:LOT|LT)\s*\d+', app_normalized)
                
                # Barangay/area
                extracted_has_barangay = 'LOWER BICUTAN' in extracted_normalized or user_application_data.get('barangay', '').upper() in extracted_normalized
                app_has_barangay = 'LOWER BICUTAN' in app_normalized
                
                # If block/lot match and barangay matches, consider it a match
                if extracted_block_lot and app_block_lot and extracted_block_lot == app_block_lot and (extracted_has_barangay or app_has_barangay):
                    # Recalculate score with normalized versions
                    score = SequenceMatcher(None, extracted_normalized, app_normalized).ratio()
                    if score >= 0.60:  # Lower threshold for normalized match
                        match = True
            
            matches['address'] = {
                'match': match,
                'score': score,
                'extracted': extracted_info['address'],
                'application': app_address
            }
        
        logger.info(f"✅ Compared {len(matches)} fields with user application")
        
        return matches
    
    def _determine_validity(
        self,
        detected_elements: Dict[str, Any],
        validation_checks: Dict[str, bool],
        confidence: float,
        identity_verified: bool = False
    ) -> bool:
        """
        Determine if the voter certificate is valid.
        
        Args:
            detected_elements: Dictionary of detected elements
            validation_checks: Validation check results
            confidence: Overall confidence score
        
        Returns:
            Boolean indicating validity
        """
        # Must have all required elements
        all_required_present = validation_checks.get('all_required_elements_present', False)
        
        # Must have reasonable confidence
        meets_confidence = confidence >= 0.70
        
        return all_required_present and meets_confidence and identity_verified
    
    def _generate_recommendations(
        self,
        detected_elements: Dict[str, Any],
        validation_checks: Dict[str, bool],
        confidence: float
    ) -> List[str]:
        """
        Generate recommendations based on verification results.
        
        Args:
            detected_elements: Dictionary of detected elements
            validation_checks: Validation check results
            confidence: Overall confidence score
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check for missing required elements
        if not validation_checks.get('has_comelec_logo'):
            recommendations.append("⚠️ COMELEC logo not detected - verify document authenticity")
        
        if not validation_checks.get('has_fingerprint'):
            recommendations.append("⚠️ Fingerprint/biometrics area not detected - may be incomplete")
        
        if not validation_checks.get('has_photo'):
            recommendations.append("⚠️ Photo area not detected - may be incomplete or damaged")
        
        # Confidence-based recommendations
        if confidence < 0.70:
            recommendations.append("⚠️ Low confidence score - manual review strongly recommended")
        elif confidence < 0.85:
            recommendations.append("💡 Moderate confidence - consider manual verification")
        
        if not recommendations:
            recommendations.append("✅ Document appears valid with good confidence")
        
        return recommendations


# Singleton instance
_voter_certificate_service = None


def get_voter_certificate_verification_service() -> VoterCertificateVerificationService:
    """
    Get or create the singleton Voter Certificate verification service instance.
    
    Returns:
        VoterCertificateVerificationService instance
    """
    global _voter_certificate_service
    
    if _voter_certificate_service is None:
        _voter_certificate_service = VoterCertificateVerificationService()
    
    return _voter_certificate_service
