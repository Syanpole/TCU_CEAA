"""
Birth Certificate Verification Service
Uses Advanced OCR (AWS Textract primary, Tesseract fallback) for PSA/NSO birth certificate verification.
"""

import os
import re
import cv2
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Service singleton
_birth_cert_service_instance = None


def get_birth_certificate_verification_service():
    """Get or create the birth certificate verification service singleton."""
    global _birth_cert_service_instance
    if _birth_cert_service_instance is None:
        _birth_cert_service_instance = BirthCertificateVerificationService()
    return _birth_cert_service_instance


class BirthCertificateVerificationService:
    """
    Birth Certificate Verification Service using Advanced OCR.
    Detects and validates Philippine PSA/NSO birth certificates.
    """
    
    def __init__(self):
        """Initialize the birth certificate verification service."""
        self.advanced_ocr = None
        self.ocr_interpreter = None
        
        # Initialize Advanced OCR Service (AWS Textract)
        try:
            from myapp.advanced_ocr_service import get_advanced_ocr_service
            self.advanced_ocr = get_advanced_ocr_service()
            logger.info("✅ Advanced OCR service initialized for birth certificate verification")
        except Exception as e:
            logger.warning(f"⚠️ Advanced OCR service not available: {str(e)}")
        
        # Initialize Tesseract as fallback
        try:
            import pytesseract
            self.ocr_interpreter = pytesseract
            logger.info("✅ Tesseract OCR initialized as fallback")
        except ImportError:
            logger.warning("⚠️ Tesseract OCR not available")
        
        # Expected keywords for birth certificate validation
        self.birth_cert_keywords = [
            'BIRTH', 'CERTIFICATE', 'LIVE BIRTH',
            'REPUBLIC', 'PHILIPPINES',
            'PSA', 'NSO', 'NATIONAL STATISTICS',
            'CIVIL REGISTRAR', 'OFFICE OF THE CIVIL REGISTRAR'
        ]
        
        logger.info("🎯 Birth Certificate Verification Service initialized")
    
    def get_verification_status(self) -> Dict[str, Any]:
        """
        Check the status of birth certificate verification capabilities.
        
        Returns:
            Dictionary containing status of each component
        """
        advanced_ocr_enabled = self.advanced_ocr and self.advanced_ocr.is_enabled()
        
        return {
            'birth_certificate_verification': True,
            'ocr_available': self.ocr_interpreter is not None,
            'advanced_ocr_enabled': advanced_ocr_enabled,
            'ocr_method': 'Advanced OCR' if advanced_ocr_enabled else 'Standard OCR (Fallback)',
            'fully_operational': advanced_ocr_enabled or self.ocr_interpreter is not None
        }
    
    def verify_birth_certificate_document(
        self, 
        image_path: str,
        user_application_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verify a birth certificate document using advanced OCR and compare with user's application data.
        
        Args:
            image_path: Path to the birth certificate document image
            user_application_data: Optional dictionary containing user's full application data for comparison
                Expected fields: first_name, middle_name, last_name, date_of_birth, sex, place_of_birth,
                                father_name, mother_name
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if verification completed
                - is_valid: Boolean indicating if birth certificate is valid
                - confidence: Overall confidence score (0.0-1.0)
                - status: Verification status (VALID/QUESTIONABLE/INVALID)
                - extracted_fields: Dictionary of extracted birth certificate fields
                - ocr_text: Raw OCR extracted text
                - document_type_match: Boolean indicating if it's a birth certificate
                - field_matches: Dictionary showing which fields match user's application data
                - recommendations: List of recommendations
                - errors: List of errors if any
        """
        result = {
            'success': False,
            'is_valid': False,
            'confidence': 0.0,
            'status': 'INVALID',
            'extracted_fields': {},
            'ocr_text': '',
            'document_type_match': False,
            'field_matches': {},
            'recommendations': [],
            'errors': []
        }
        
        try:
            # Validate image path
            if not os.path.exists(image_path):
                result['errors'].append(f"Image not found: {image_path}")
                return result
            
            # Extract text using advanced OCR
            logger.info("🔍 Running advanced OCR on birth certificate...")
            ocr_result = self._advanced_ocr_extraction(image_path)
            
            if not ocr_result.get('success'):
                result['errors'].append("OCR extraction failed")
                return result
            
            # Store raw OCR text
            result['ocr_text'] = ocr_result.get('raw_text', '')
            ocr_confidence = ocr_result.get('ocr_confidence', 0.0)
            
            # Validate document type
            is_birth_cert = self._validate_document_type(result['ocr_text'])
            result['document_type_match'] = is_birth_cert
            
            if not is_birth_cert:
                result['errors'].append("Document does not appear to be a birth certificate")
                result['recommendations'].append("⚠️ Please upload a valid PSA/NSO birth certificate")
                return result
            
            # Extract birth certificate fields
            logger.info("📋 Extracting birth certificate fields...")
            extracted_fields = self._extract_birth_certificate_fields(result['ocr_text'])
            result['extracted_fields'] = extracted_fields
            
            # Compare with user application data if provided
            if user_application_data:
                logger.info("🔍 Comparing extracted data with user's application...")
                field_matches = self._compare_with_application(extracted_fields, user_application_data)
                result['field_matches'] = field_matches
                
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
                    
                    # Add detailed field matches section
                    result['recommendations'].append("\n📊 Field Matches:")
                    for field_name, field_data in field_matches.items():
                        match_icon = "✓" if field_data.get('match') else "✗"
                        score = field_data.get('score', 0) * 100
                        extracted_val = field_data.get('extracted', 'N/A')
                        app_val = field_data.get('application', 'N/A')
                        reason = field_data.get('reason', '')
                        
                        # Format field name nicely
                        display_name = field_name.replace('_', ' ').title()
                        
                        match_line = f"  {match_icon} {display_name}: {score:.0f}% - Extracted: '{extracted_val}' | Application: '{app_val}'"
                        if reason:
                            match_line += f" ({reason})"
                        
                        result['recommendations'].append(match_line)
            
            # Calculate confidence (with field matching if available)
            confidence = self._calculate_confidence(
                is_birth_cert,
                extracted_fields,
                ocr_confidence,
                field_matches=result.get('field_matches')
            )
            result['confidence'] = confidence
            
            # Check critical field matches - Use intelligent matching with parent verification
            critical_fields_match = True
            mismatch_reasons = []
            partial_match_warning = False
            parent_match_count = 0
            
            if field_matches:
                # Name matching - allow partial matches if parents match
                if 'child_name' in field_matches:
                    name_score = field_matches['child_name'].get('score', 0)
                    name_match = field_matches['child_name'].get('match', False)
                    
                    # Check if it's a partial name match (e.g., missing last name)
                    if not name_match and name_score >= 0.70:
                        # Partial match - check parent names for verification
                        partial_match_warning = True
                        if 'father_name' in field_matches and field_matches['father_name'].get('match', False):
                            parent_match_count += 1
                        if 'mother_name' in field_matches and field_matches['mother_name'].get('match', False):
                            parent_match_count += 1
                        
                        # If at least one parent matches, accept the document
                        if parent_match_count >= 1:
                            mismatch_reasons.append(f"✓ Partial name match ({name_score*100:.0f}%) verified by parent information")
                        else:
                            critical_fields_match = False
                            mismatch_reasons.append(f"❌ Name mismatch: Document '{field_matches['child_name'].get('extracted', 'N/A')}' vs Application '{field_matches['child_name'].get('application', 'N/A')}'")
                    elif not name_match and name_score < 0.70:
                        critical_fields_match = False
                        mismatch_reasons.append(f"❌ Name mismatch: Document '{field_matches['child_name'].get('extracted', 'N/A')}' vs Application '{field_matches['child_name'].get('application', 'N/A')}'")
                
                # Date of birth is CRITICAL - must match
                if 'date_of_birth' in field_matches and not field_matches['date_of_birth'].get('match', False):
                    dob_score = field_matches['date_of_birth'].get('score', 0)
                    # Allow slight DOB variations if parents match
                    if dob_score >= 0.85 and parent_match_count >= 1:
                        mismatch_reasons.append(f"✓ Date of birth close match ({dob_score*100:.0f}%) verified by parent information")
                    else:
                        critical_fields_match = False
                        mismatch_reasons.append(f"❌ Date of birth mismatch: Document '{field_matches['date_of_birth'].get('extracted', 'N/A')}' vs Application '{field_matches['date_of_birth'].get('application', 'N/A')}'")
            
            # Determine validity - APPROVE if critical fields match OR parent verification successful
            if not critical_fields_match:
                result['is_valid'] = False
                result['status'] = 'INVALID'
                # Lower confidence when critical fields don't match
                # High OCR quality but wrong person's document = low overall confidence
                result['confidence'] = min(confidence * 0.3, 0.5)  # Max 50% confidence for mismatched documents
                result['recommendations'].append("❌ DOCUMENT REJECTED - Identity Verification Failed")
                result['recommendations'].append("📋 The information on this birth certificate does not match your application.")
                result['recommendations'].append("🔍 Please ensure you uploaded YOUR OWN birth certificate, not someone else's.")
                result['recommendations'].extend(mismatch_reasons)
                result['recommendations'].append("💡 What to do: Upload a clear photo of YOUR PSA/NSO birth certificate that matches your application details.")
                # Add confidence interpretation for rejections
                if confidence >= 0.75:
                    result['recommendations'].append(f"✅ AI Detection Quality: High ({confidence*100:.0f}%) - Rejection is accurate")
                elif confidence >= 0.60:
                    result['recommendations'].append(f"⚠️ AI Detection Quality: Medium ({confidence*100:.0f}%) - Manual review may be needed")
                else:
                    result['recommendations'].append(f"❌ AI Detection Quality: Low ({confidence*100:.0f}%) - Document quality poor, please reupload")
            elif partial_match_warning and parent_match_count >= 1:
                # Partial name match but verified by parent info - APPROVE
                result['is_valid'] = True
                result['status'] = 'VALID'
                result['recommendations'].append("✅ Birth certificate approved - Identity verified by parent information")
                result['recommendations'].extend(mismatch_reasons)  # Show partial match details
                if parent_match_count == 2:
                    result['recommendations'].append("✅ Both father and mother names match - Strong verification")
                elif 'father_name' in field_matches and field_matches['father_name'].get('match', False):
                    result['recommendations'].append("✅ Father's name verified - Identity confirmed")
                elif 'mother_name' in field_matches and field_matches['mother_name'].get('match', False):
                    result['recommendations'].append("✅ Mother's name verified - Identity confirmed")
            elif confidence >= 0.85:
                result['is_valid'] = True
                result['status'] = 'VALID'
                result['recommendations'].append("✅ Birth certificate appears valid with high confidence")
            elif confidence >= 0.70:
                result['is_valid'] = True
                result['status'] = 'QUESTIONABLE'
                result['recommendations'].append("⚠️ Birth certificate may be valid but has some quality issues")
            else:
                result['is_valid'] = False
                result['status'] = 'INVALID'
                result['recommendations'].append("❌ Birth certificate quality is too low or information is incomplete")
            
            # Add field-specific recommendations
            if not extracted_fields.get('child_name'):
                result['recommendations'].append("⚠️ Could not extract child's name clearly")
            if not extracted_fields.get('date_of_birth'):
                result['recommendations'].append("⚠️ Could not extract date of birth clearly")
            if not extracted_fields.get('place_of_birth'):
                result['recommendations'].append("⚠️ Could not extract place of birth clearly")
            
            result['success'] = True
            logger.info(f"✅ Birth certificate verification completed: {result['status']} ({confidence*100:.1f}%)")
            
        except Exception as e:
            error_msg = f"Birth certificate verification error: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _advanced_ocr_extraction(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text using advanced OCR (AWS Textract primary, Tesseract fallback).
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Dictionary with OCR results
        """
        result = {
            'success': False,
            'raw_text': '',
            'ocr_confidence': 0.0,
            'ocr_method': 'none'
        }
        
        try:
            # Try advanced OCR first (most accurate)
            if self.advanced_ocr and self.advanced_ocr.is_enabled():
                logger.info("🔍 Using advanced OCR for text extraction...")
                
                # Read image as bytes
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                
                textract_result = self.advanced_ocr.extract_text(image_bytes)
                
                if textract_result.get('success'):
                    result['raw_text'] = textract_result.get('text', '')
                    result['ocr_confidence'] = textract_result.get('confidence', 0.0)
                    result['ocr_method'] = 'Advanced OCR'
                    result['success'] = True
                    logger.info(f"✅ Advanced OCR extraction successful ({result['ocr_confidence']*100:.1f}% confidence)")
                    return result
            
            # Fallback to Tesseract
            if self.ocr_interpreter:
                logger.info("🔍 Using standard OCR as fallback...")
                
                # Load and preprocess image
                img = cv2.imread(image_path)
                if img is None:
                    raise ValueError("Failed to load image")
                
                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Denoise
                denoised = cv2.fastNlMeansDenoising(gray)
                
                # Apply adaptive thresholding for better text extraction
                binary = cv2.adaptiveThreshold(
                    denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 11, 2
                )
                
                # Extract text
                text = self.ocr_interpreter.image_to_string(binary, config='--psm 6')
                
                result['raw_text'] = text
                result['ocr_confidence'] = 0.85  # Estimated confidence for standard OCR
                result['ocr_method'] = 'Standard OCR'
                result['success'] = True
                logger.info("✅ Standard OCR extraction completed")
                return result
            
            raise Exception("No OCR method available")
            
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {str(e)}")
            result['success'] = False
        
        return result
    
    def _validate_document_type(self, text: str) -> bool:
        """
        Validate if the document is a birth certificate based on keywords.
        
        Args:
            text: Extracted text from OCR
        
        Returns:
            Boolean indicating if it's a birth certificate
        """
        text_upper = text.upper()
        
        # Count matching keywords
        matches = sum(1 for keyword in self.birth_cert_keywords if keyword in text_upper)
        
        # Need at least 4 keyword matches to be confident it's a birth certificate
        is_birth_cert = matches >= 4
        
        logger.info(f"📋 Birth certificate keyword matches: {matches}/{len(self.birth_cert_keywords)}")
        
        return is_birth_cert
    
    def _extract_birth_certificate_fields(self, text: str) -> Dict[str, Any]:
        """
        Extract structured fields from birth certificate text.
        
        Args:
            text: Raw OCR text
        
        Returns:
            Dictionary of extracted fields
        """
        fields = {}
        text_upper = text.upper()
        
        # Extract Child's Name - Updated to handle multi-line format
        child_name_patterns = [
            # Pattern 1: Multi-line format (most PSA birth certificates)
            # Format: 1. NAME\n(First)\n(Middle)\n(LAST)name\nFirst Name\nMiddle Name
            r"1\.\s*NAME[^\n]*\n[^\n]*\n[^\n]*\n\s*(.+?)\s*\n\s*([A-Z\s]+?)\s*\n\s*([A-Z]+)",
            # Pattern 2: Original patterns (backward compatibility)
            r"(?:CHILD'S NAME|NAME OF CHILD|1\.\s*NAME)[:\s]*(?:\(FIRST\)|FIRST)?[:\s]*([A-Z][A-Z\s]+?)(?:\(MIDDLE\)|MIDDLE)",
            r"NAME[:\s]*(?:\(LAST\))?[:\s]*([A-Z]+)[:\s]*(?:\(FIRST\))?[:\s]*([A-Z\s]+?)(?:\(MIDDLE\)|MIDDLE)",
        ]
        
        for pattern in child_name_patterns:
            match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
            if match:
                # Try to extract full name from multiple groups
                name_parts = [g.strip() for g in match.groups() if g and g.strip()]
                
                if len(name_parts) == 3:
                    # Clean the last name from label artifacts (e.g., "(LABILICIANO")
                    last_name = name_parts[0]
                    
                    # Remove opening parenthesis if present
                    if last_name.startswith('('):
                        last_name = last_name[1:]
                    
                    # Remove common label remnants from "(LAST)"
                    if last_name.startswith('LAST'):
                        last_name = last_name[4:]
                    elif last_name.startswith('LA') and len(last_name) > 4:
                        last_name = last_name[2:]
                    
                    # Rearrange from Last, First, Middle to First Middle Last
                    full_name = f"{name_parts[1]} {name_parts[2]} {last_name}"
                    fields['child_name'] = full_name.strip()
                    break
                elif len(name_parts) > 0:
                    # Fallback: join all parts
                    full_name = ' '.join(name_parts)
                    if len(full_name) > 3:
                        fields['child_name'] = full_name.strip()
                        break
        
        # Extract Date of Birth - Updated to handle multi-line format
        dob_patterns = [
            # Pattern 1: Multi-line format - day and month on separate lines after "3. DATE OF BIRTH"
            r"3\.\s*DATE OF BIRTH\s*\n\s*(\d{1,2})\s*\n\s*(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)",
            # Pattern 2: Compact format on one or two lines
            r"(?:DATE OF BIRTH|BIRTH DATE|3\.\s*DATE OF BIRTH)[:\s]*(\d{1,2}[-/\s]+(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[-/\s]+\d{4})",
            # Pattern 3: Day, month, year with optional labels
            r"(?:DATE OF BIRTH)[:\s]*(?:\(DAY\))?[:\s]*(\d{1,2})[:\s]*(?:\(MONTH\))?[:\s]*([A-Z]+)[:\s]*(?:\(YEAR\))?[:\s]*(\d{4})",
        ]
        
        year_found = None
        # Try to find year from registry number (often matches birth year)
        year_match = re.search(r"REGISTRY[\s#NO\.:]*([\d\-]+)", text_upper)
        if year_match:
            registry = year_match.group(1)
            year_part = re.match(r"(\d{4})", registry)
            if year_part:
                year_found = year_part.group(1)
        
        for pattern in dob_patterns:
            match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    # Day, month, year in separate groups
                    fields['date_of_birth'] = f"{groups[0]} {groups[1]} {groups[2]}"
                    break
                elif len(groups) == 2 and year_found:
                    # Day and month found, use year from registry
                    fields['date_of_birth'] = f"{groups[0]} {groups[1]} {year_found}"
                    break
                else:
                    fields['date_of_birth'] = groups[0].strip()
                    break
        
        # Extract Sex - Updated to handle checkbox format ("1 Male" or "2 Female")
        sex_patterns = [
            r"2\.\s*SEX.*?1\s*MALE",  # Matches "1 Male" checkbox pattern
            r"2\.\s*SEX.*?2\s*FEMALE",  # Matches "2 Female" checkbox pattern
            r"(?:2\.\s*)?SEX[:\s]*(MALE|FEMALE)",  # Original pattern
        ]
        
        for pattern in sex_patterns:
            sex_match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
            if sex_match:
                if "MALE" in sex_match.group(0):
                    fields['sex'] = 'MALE'
                elif "FEMALE" in sex_match.group(0):
                    fields['sex'] = 'FEMALE'
                break
        
        # Extract Place of Birth
        place_patterns = [
            r"(?:PLACE OF BIRTH|4\.\s*PLACE OF BIRTH)[:\s]*(?:HOUSE NO|STREET|BARANGAY)?[:\s]*([A-Z][A-Z\s,\.\-]+?)(?:\(CITY/MUNICIPALITY\)|CITY|MUNICIPALITY|\n|5\.)",
            r"(?:HOSPITAL|CLINIC|INSTITUTION)[:\s]*([A-Z][A-Z\s,\.\-]+?)(?:CITY|MANILA|\n)",
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, text_upper)
            if match:
                place = match.group(1).strip()
                if len(place) > 5:
                    fields['place_of_birth'] = place
                    break
        
        # Extract Mother's Maiden Name
        mother_patterns = [
            r"(?:MOTHER'S MAIDEN NAME|MAIDEN NAME|6\.\s*MAIDEN NAME)[:\s]*(?:\(FIRST\))?[:\s]*([A-Z][A-Z\s,\.]+?)(?:\n|7\.|CITIZENSHIP)",
            r"MAIDEN[:\s]*NAME[:\s]*(?:\(LAST\))?[:\s]*([A-Z]+)[:\s]*(?:\(FIRST\))?[:\s]*([A-Z\s]+?)(?:\(MIDDLE\)|MIDDLE)",
        ]
        
        for pattern in mother_patterns:
            match = re.search(pattern, text_upper)
            if match:
                mother_parts = [g.strip() for g in match.groups() if g]
                mother_name = ' '.join(mother_parts)
                if len(mother_name) > 5:
                    fields['mother_name'] = mother_name.strip()
                    break
        
        # Extract Father's Name - Enhanced patterns for better extraction
        father_patterns = [
            # Pattern 1: Multi-line format similar to child name
            r"13\.\s*NAME[^\n]*\n[^\n]*\n[^\n]*\n\s*(.+?)\s*\n\s*([A-Z\s]+?)\s*\n\s*([A-Z]+)",
            # Pattern 2: Father's name with field labels
            r"(?:FATHER'S NAME|13\.\s*NAME)[:\s]*(?:\(FIRST\))?[:\s]*([A-Z][A-Z\s,\.]+?)(?:\n|14\.|CITIZENSHIP)",
            # Pattern 3: Format with LAST/FIRST/MIDDLE labels
            r"(?:13\.\s*NAME|FATHER)[:\s]*(?:\(LAST\))?[:\s]*([A-Z]+)[:\s]*(?:\(FIRST\))?[:\s]*([A-Z\s]+?)(?:\(MIDDLE\)|MIDDLE|14\.)",
            # Pattern 4: Simple FATHER line
            r"F\s*A\s*T\s*H\s*E\s*R[:\s]*\n\s*13\.\s*NAME[:\s]*([A-Z\s]+)",
        ]
        
        for pattern in father_patterns:
            match = re.search(pattern, text_upper, re.MULTILINE | re.DOTALL)
            if match:
                father_parts = [g.strip() for g in match.groups() if g and g.strip()]
                father_name = ' '.join(father_parts)
                # Clean up common OCR artifacts
                father_name = re.sub(r'\(.*?\)', '', father_name).strip()
                if len(father_name) > 5:
                    fields['father_name'] = father_name.strip()
                    break
        
        # Extract Registry Number
        registry_patterns = [
            r"REGISTRY[\s#NO\.:]*([\d\-]+)",
            r"REG[:\s#NO\.]*([\d\-]+)",
        ]
        
        for pattern in registry_patterns:
            match = re.search(pattern, text_upper)
            if match:
                fields['registry_number'] = match.group(1).strip()
                break
        
        # Extract Birth Weight
        weight_match = re.search(r"WEIGHT\s*(?:AT\s*)?BIRTH[:\s]*(\d+)\s*(?:GRAMS|G)?", text_upper)
        if weight_match:
            fields['birth_weight'] = weight_match.group(1).strip()
        
        # Extract Document Number (BREN or Document ID)
        doc_patterns = [
            r"([\d]{5,}-[A-Z0-9]{2,}-[A-Z0-9]+-[\d]+-[A-Z]+[\d]+)",
            r"BREN[:\s]*([\w\d]+)",
            r"(DE[\d]{20,})",
        ]
        
        for pattern in doc_patterns:
            match = re.search(pattern, text_upper)
            if match:
                fields['document_number'] = match.group(1).strip()
                break
        
        logger.info(f"📋 Extracted {len(fields)} fields from birth certificate")
        
        return fields
    
    def _compare_with_application(
        self,
        extracted_fields: Dict[str, Any],
        user_application_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare extracted birth certificate fields with user's application data.
        
        Args:
            extracted_fields: Fields extracted from birth certificate
            user_application_data: User's full application data
        
        Returns:
            Dictionary with field-by-field comparison results
        """
        from difflib import SequenceMatcher
        
        def fuzzy_match(str1: str, str2: str, threshold: float = 0.80) -> Tuple[bool, float]:
            """Compare two strings with fuzzy matching using fuzzywuzzy for better results"""
            if not str1 or not str2:
                return False, 0.0
            
            str1_clean = str1.upper().strip()
            str2_clean = str2.upper().strip()
            
            # Exact match
            if str1_clean == str2_clean:
                return True, 1.0
            
            # Try fuzzywuzzy for better partial matching
            try:
                from fuzzywuzzy import fuzz
                # Use token_sort_ratio for better name matching (handles word order)
                ratio = fuzz.token_sort_ratio(str1_clean, str2_clean) / 100.0
                logger.info(f"🔍 Fuzzy match (fuzzywuzzy): '{str1_clean}' vs '{str2_clean}' = {ratio*100:.1f}%")
            except ImportError:
                # Fallback to difflib if fuzzywuzzy not available
                ratio = SequenceMatcher(None, str1_clean, str2_clean).ratio()
                logger.info(f"🔍 Fuzzy match (difflib): '{str1_clean}' vs '{str2_clean}' = {ratio*100:.1f}%")
            
            return ratio >= threshold, ratio
        
        def compare_date(date1: str, date2: Any) -> Tuple[bool, float]:
            """Compare dates (extracted vs application) with enhanced fuzzy matching"""
            if not date1 or not date2:
                return False, 0.0
            
            try:
                from datetime import datetime
                import re
                
                # Convert date2 to string if it's a date object
                if hasattr(date2, 'strftime'):
                    date2_str = date2.strftime('%d %B %Y')
                else:
                    date2_str = str(date2)
                
                # Normalize date strings
                date1_clean = date1.upper().strip().replace(',', '')
                date2_clean = date2_str.upper().strip().replace(',', '')
                
                logger.info(f"🗓️ Comparing dates: '{date1_clean}' vs '{date2_clean}'")
                
                # Try exact match
                if date1_clean == date2_clean:
                    logger.info("✅ Exact date match")
                    return True, 1.0
                
                # Try parsing both dates to compare actual date values
                date_formats = [
                    '%d %B %Y', '%d %b %Y', '%B %d %Y', '%b %d %Y',
                    '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y',
                    '%Y/%m/%d', '%d %B%Y', '%d%B %Y'
                ]
                
                parsed_date1 = None
                parsed_date2 = None
                
                for fmt in date_formats:
                    try:
                        if not parsed_date1:
                            parsed_date1 = datetime.strptime(date1_clean, fmt)
                    except:
                        pass
                    try:
                        if not parsed_date2:
                            parsed_date2 = datetime.strptime(date2_clean, fmt)
                    except:
                        pass
                    if parsed_date1 and parsed_date2:
                        break
                
                # If both dates parsed successfully, compare them
                if parsed_date1 and parsed_date2:
                    if parsed_date1 == parsed_date2:
                        logger.info(f"✅ Parsed date match: {parsed_date1.strftime('%Y-%m-%d')}")
                        return True, 1.0
                    else:
                        logger.info(f"❌ Parsed dates differ: {parsed_date1.strftime('%Y-%m-%d')} vs {parsed_date2.strftime('%Y-%m-%d')}")
                        # Still apply fuzzy matching in case format differences
                
                # Extract day, month, year components for flexible matching
                def extract_date_components(date_str):
                    # Try to extract day, month, year
                    day_match = re.search(r'\b(\d{1,2})\b', date_str)
                    year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
                    
                    months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
                             'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER',
                             'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    
                    month = None
                    for m in months:
                        if m in date_str:
                            month = m
                            break
                    
                    return {
                        'day': day_match.group(1) if day_match else None,
                        'month': month,
                        'year': year_match.group(0) if year_match else None
                    }
                
                comp1 = extract_date_components(date1_clean)
                comp2 = extract_date_components(date2_clean)
                
                # Check if core components match
                components_match = (
                    comp1['day'] == comp2['day'] and
                    comp1['year'] == comp2['year'] and
                    (comp1['month'] == comp2['month'] or 
                     (comp1['month'] and comp2['month'] and comp1['month'][:3] == comp2['month'][:3]))
                )
                
                if components_match and comp1['day'] and comp1['year']:
                    logger.info(f"✅ Date components match: {comp1['day']}/{comp1['month']}/{comp1['year']}")
                    return True, 0.95
                
                # ALWAYS apply fuzzy matching for birth certificates
                ratio = SequenceMatcher(None, date1_clean, date2_clean).ratio()
                logger.info(f"📊 Fuzzy date similarity: {ratio:.2%}")
                
                # Lower threshold for date matching (70%)
                match = ratio >= 0.70
                if match:
                    logger.info(f"✅ Date fuzzy match passed (threshold: 70%)")
                else:
                    logger.info(f"⚠️ Date fuzzy match below threshold: {ratio:.2%} < 70%")
                
                return match, ratio
                
            except Exception as e:
                logger.warning(f"Date comparison error: {str(e)}")
                return False, 0.0
        
        matches = {}
        
        # Compare child's name
        if extracted_fields.get('child_name') and user_application_data.get('first_name'):
            app_full_name = f"{user_application_data.get('first_name', '')} {user_application_data.get('middle_name', '')} {user_application_data.get('last_name', '')}".strip()
            match, score = fuzzy_match(extracted_fields['child_name'], app_full_name, threshold=0.75)
            matches['child_name'] = {
                'match': match,
                'score': score,
                'extracted': extracted_fields['child_name'],
                'application': app_full_name
            }
        
        # Compare date of birth
        if extracted_fields.get('date_of_birth') and user_application_data.get('date_of_birth'):
            match, score = compare_date(extracted_fields['date_of_birth'], user_application_data['date_of_birth'])
            
            # Determine reason for match/mismatch
            if match:
                if score == 1.0:
                    reason = "Exact date match"
                elif score >= 0.95:
                    reason = "Date components (day/month/year) match"
                else:
                    reason = f"Fuzzy date match ({score:.1%} similarity)"
            else:
                reason = f"Date mismatch (only {score:.1%} similarity, threshold: 70%)"
            
            matches['date_of_birth'] = {
                'match': match,
                'score': score,
                'extracted': extracted_fields['date_of_birth'],
                'application': str(user_application_data['date_of_birth']),
                'reason': reason
            }
        
        # Compare sex
        if extracted_fields.get('sex') and user_application_data.get('sex'):
            match, score = fuzzy_match(extracted_fields['sex'], user_application_data['sex'], threshold=0.90)
            matches['sex'] = {
                'match': match,
                'score': score,
                'extracted': extracted_fields['sex'],
                'application': user_application_data['sex']
            }
        
        # Compare place of birth - Enhanced to handle city/municipality matching
        if extracted_fields.get('place_of_birth') and user_application_data.get('place_of_birth'):
            extracted_place = extracted_fields['place_of_birth'].upper().strip()
            app_place = user_application_data['place_of_birth'].upper().strip()
            
            # First try exact fuzzy match
            match, score = fuzzy_match(extracted_place, app_place, threshold=0.70)
            
            # If direct match fails, check if extracted place is contained in application place
            # (e.g., "MANILA" is in "Philippine General Hospital, Manila")
            if not match and extracted_place in app_place:
                match = True
                score = 0.85  # High confidence since it's a substring match
                logger.info(f"Place match found: '{extracted_place}' is within '{app_place}'")
            
            # Also check reverse: if application place is in extracted place
            # (e.g., "MANILA" in "MANILA CITY")
            elif not match and app_place in extracted_place:
                match = True
                score = 0.85
                logger.info(f"Place match found: '{app_place}' is within '{extracted_place}'")
            
            matches['place_of_birth'] = {
                'match': match,
                'score': score,
                'extracted': extracted_fields['place_of_birth'],
                'application': user_application_data['place_of_birth']
            }
        
        # Compare mother's name
        if extracted_fields.get('mother_name') and user_application_data.get('mother_name'):
            match, score = fuzzy_match(extracted_fields['mother_name'], user_application_data['mother_name'], threshold=0.75)
            matches['mother_name'] = {
                'match': match,
                'score': score,
                'extracted': extracted_fields['mother_name'],
                'application': user_application_data['mother_name']
            }
        
        # Compare father's name
        if extracted_fields.get('father_name') and user_application_data.get('father_name'):
            match, score = fuzzy_match(extracted_fields['father_name'], user_application_data['father_name'], threshold=0.75)
            matches['father_name'] = {
                'match': match,
                'score': score,
                'extracted': extracted_fields['father_name'],
                'application': user_application_data['father_name']
            }
        
        logger.info(f"✅ Compared {len(matches)} fields with user application")
        
        return matches
    
    def _calculate_confidence(
        self,
        is_birth_cert: bool,
        extracted_fields: Dict[str, Any],
        ocr_confidence: float,
        field_matches: Dict[str, Any] = None
    ) -> float:
        """
        Calculate overall confidence score for birth certificate verification.
        
        Args:
            is_birth_cert: Whether document type validation passed
            extracted_fields: Dictionary of extracted fields
            ocr_confidence: OCR confidence score (0.0-1.0)
            field_matches: Dictionary of field match results (optional)
        
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.0
        
        try:
            if field_matches:
                # WITH FIELD MATCHING (ownership validation)
                # Base confidence from OCR (25%)
                confidence += 0.25 * ocr_confidence
                
                # Document type validation (15%)
                if is_birth_cert:
                    confidence += 0.15
                
                # Critical fields present (20%)
                critical_fields = ['child_name', 'date_of_birth', 'place_of_birth']
                critical_present = sum(1 for field in critical_fields if extracted_fields.get(field))
                confidence += 0.20 * (critical_present / len(critical_fields))
                
                # FIELD MATCHING SCORE (40%) - Most important for ownership verification
                if field_matches:
                    match_scores = [match.get('score', 0.0) for match in field_matches.values() if isinstance(match, dict)]
                    if match_scores:
                        avg_match_score = sum(match_scores) / len(match_scores)
                        confidence += 0.40 * avg_match_score
                        logger.info(f"🎯 Field matching average score: {avg_match_score:.2%} -> contributes {0.40 * avg_match_score:.2%} to confidence")
            else:
                # WITHOUT FIELD MATCHING (fallback mode)
                # Base confidence from OCR (40%)
                confidence += 0.40 * ocr_confidence
                
                # Document type validation (20%)
                if is_birth_cert:
                    confidence += 0.20
                
                # Critical fields present (40%)
                critical_fields = ['child_name', 'date_of_birth', 'place_of_birth']
                critical_present = sum(1 for field in critical_fields if extracted_fields.get(field))
                confidence += 0.40 * (critical_present / len(critical_fields))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
        
        return min(confidence, 1.0)


# Module-level initialization
logger.info("🎯 Birth Certificate Verification Service module loaded")
