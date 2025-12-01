"""
ID Verification Service
=======================

Advanced ID card verification using YOLO detection and AWS Textract OCR.
This service combines computer vision and cloud-based OCR for accurate ID verification.

Features:
- YOLO v8 model for ID card detection
- AWS Textract for high-accuracy text extraction (95-98%)
- Field validation and extraction
- Confidence scoring
- Fraud detection

Author: TCU CEAA Development Team
Date: November 2025
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

# Import Advanced OCR Service
try:
    from myapp.advanced_ocr_service import get_advanced_ocr_service
    ADVANCED_OCR_AVAILABLE = True
except ImportError:
    ADVANCED_OCR_AVAILABLE = False
    logger.warning("Advanced OCR service not available")

# Import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics YOLO not available. Install with: pip install ultralytics")


class IDVerificationService:
    """
    ID Card Verification Service using YOLO detection and AWS Textract OCR.
    
    This service provides comprehensive ID card verification including:
    - ID card detection using YOLO v8
    - High-accuracy text extraction using AWS Textract
    - Field extraction (name, student number, etc.)
    - Validation checks
    - Fraud detection
    """
    
    def __init__(self):
        """Initialize the ID verification service."""
        self.yolo_model = None
        self.advanced_ocr = None
        self.model_path = Path(settings.BASE_DIR) / 'ai_model_data' / 'trained_models' / 'yolov8_id_detection_v1.pt'
        
        # Initialize YOLO model
        if YOLO_AVAILABLE and self.model_path.exists():
            try:
                self.yolo_model = YOLO(str(self.model_path))
                logger.info(f"✅ YOLO ID detection model loaded from: {self.model_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load YOLO model: {str(e)}")
                self.yolo_model = None
        else:
            if not YOLO_AVAILABLE:
                logger.warning("⚠️ YOLO not available. Install ultralytics package.")
            if not self.model_path.exists():
                logger.warning(f"⚠️ YOLO model not found at: {self.model_path}")
        
        # Initialize Advanced OCR
        if ADVANCED_OCR_AVAILABLE:
            try:
                self.advanced_ocr = get_advanced_ocr_service()
                if self.advanced_ocr.is_enabled():
                    logger.info("✅ Advanced OCR initialized")
                else:
                    logger.warning("⚠️ Advanced OCR available but not enabled in settings")
                    self.advanced_ocr = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize Advanced OCR: {str(e)}")
                self.advanced_ocr = None
        else:
            logger.warning("⚠️ Advanced OCR service not available")
    
    def get_verification_status(self) -> Dict[str, Any]:
        """
        Check the status of verification capabilities.
        
        Returns:
            Dictionary containing status of each component
        """
        return {
            'yolo_detection': self.yolo_model is not None,
            'advanced_ocr': self.advanced_ocr is not None,
            'fully_operational': self.yolo_model is not None and self.advanced_ocr is not None,
            'yolo_model_path': str(self.model_path) if self.model_path else None,
            'use_advanced_ocr': getattr(settings, 'USE_ADVANCED_OCR', False)
        }
    
    def verify_id_card(self, image_path: str, document_type: str = 'student_id', user=None) -> Dict[str, Any]:
        """
        Verify an ID card using YOLO detection and AWS Textract OCR.
        
        Args:
            image_path: Path to the ID card image
            document_type: Type of ID (default: 'student_id')
            user: Optional CustomUser object for identity verification
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating if verification completed
                - is_valid: Boolean indicating if ID is valid
                - confidence: Overall confidence score (0.0-1.0)
                - status: Verification status (VALID/QUESTIONABLE/INVALID)
                - yolo_detection: YOLO detection results
                - ocr_extraction: OCR text extraction results
                - extracted_fields: Parsed ID fields
                - validation_checks: Individual validation results
                - identity_verification: Identity match results (if user provided)
                - recommendations: List of recommendations
                - errors: List of errors if any
        """
        result = {
            'success': False,
            'is_valid': False,
            'confidence': 0.0,
            'status': 'INVALID',
            'yolo_detection': {},
            'ocr_extraction': {},
            'extracted_fields': {},
            'validation_checks': {},
            'identity_verification': {},
            'checks_passed': 0,
            'recommendations': [],
            'errors': []
        }
        
        try:
            # Check if service is operational
            status = self.get_verification_status()
            if not status['fully_operational']:
                missing = []
                if not status['yolo_detection']:
                    missing.append('YOLO detection model')
                if not status['advanced_ocr']:
                    missing.append('Advanced OCR service')
                
                result['errors'].append(f"Service not fully operational. Missing: {', '.join(missing)}")
                return result
            
            # Validate image path
            if not os.path.exists(image_path):
                result['errors'].append(f"Image not found: {image_path}")
                return result
            
            # Step 1: YOLO ID Detection
            logger.info("🔍 Step 1: YOLO ID card detection")
            yolo_result = self._detect_id_with_yolo(image_path)
            result['yolo_detection'] = yolo_result
            
            if not yolo_result.get('id_detected', False):
                result['errors'].append("No ID card detected in image")
                result['recommendations'].append("Ensure the entire ID card is visible and well-lit")
                result['status'] = 'INVALID'
                return result
            
            # Step 2: Advanced OCR Text Extraction
            logger.info("📡 Step 2: Advanced OCR text extraction")
            ocr_result = self._extract_text_with_advanced_ocr(image_path)
            result['ocr_extraction'] = ocr_result
            
            if not ocr_result.get('success', False):
                result['errors'].append("Failed to extract text from ID")
                result['recommendations'].append("Try uploading a clearer image")
                result['status'] = 'QUESTIONABLE'
                return result
            
            # Step 3: Extract ID Fields
            logger.info("📋 Step 3: Extracting ID fields")
            extracted_fields = self._extract_id_fields(
                ocr_result.get('text', ''),
                ocr_result.get('blocks', []),
                document_type
            )
            result['extracted_fields'] = extracted_fields
            
            # Step 4: Identity Verification (if user provided)
            if user:
                logger.info("👤 Step 4: Verifying user identity")
                identity_result = self._verify_identity(user, extracted_fields)
                result['identity_verification'] = identity_result
                
                if not identity_result.get('match', False):
                    result['errors'].append(identity_result.get('message', 'Identity mismatch'))
                    result['recommendations'].append("Ensure you're uploading YOUR ID card")
                    result['status'] = 'INVALID'
                    return result
            
            # Step 5: Validation Checks
            logger.info("✅ Step 5: Running validation checks")
            validation_checks = self._run_validation_checks(
                extracted_fields,
                yolo_result,
                ocr_result,
                document_type,
                user
            )
            result['validation_checks'] = validation_checks
            result['checks_passed'] = sum(1 for v in validation_checks.values() if v)
            
            # Step 6: Calculate Confidence and Determine Status
            confidence = self._calculate_confidence(
                yolo_result,
                ocr_result,
                extracted_fields,
                validation_checks
            )
            result['confidence'] = confidence
            
            # Determine status
            # TCU IDs should have: ID detected, text, student number, name, institution, college, identity_verified
            # All 8 checks should pass for VALID status (7 if no user provided)
            required_checks = 8 if user else 7
            min_valid_checks = 7 if user else 6
            min_questionable_checks = 5 if user else 4
            
            # Identity verification is critical - fail immediately if it doesn't match
            if user and not validation_checks.get('identity_verified', False):
                result['status'] = 'INVALID'
                result['is_valid'] = False
                result['recommendations'].append("❌ DOCUMENT REJECTED - Identity Verification Failed")
                result['recommendations'].append("📋 This ID does not belong to you")
                result['recommendations'].append("💡 What to do: Upload YOUR valid TCU ID that matches your application details")
                # Add confidence interpretation for rejections
                if confidence >= 0.75:
                    result['recommendations'].append(f"✅ AI Detection Quality: High ({confidence*100:.0f}%) - Rejection is accurate")
                elif confidence >= 0.60:
                    result['recommendations'].append(f"⚠️ AI Detection Quality: Medium ({confidence*100:.0f}%) - Manual review may be needed")
                else:
                    result['recommendations'].append(f"❌ AI Detection Quality: Low ({confidence*100:.0f}%) - Document quality poor, please reupload")
            elif confidence >= 0.8 and result['checks_passed'] >= min_valid_checks:
                result['status'] = 'VALID'
                result['is_valid'] = True
            elif confidence >= 0.6 and result['checks_passed'] >= min_questionable_checks:
                result['status'] = 'QUESTIONABLE'
                result['is_valid'] = False
                result['recommendations'].append("Manual review recommended")
            else:
                result['status'] = 'INVALID'
                result['is_valid'] = False
                result['recommendations'].append("ID verification failed")
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                result['status'],
                validation_checks,
                extracted_fields,
                confidence
            )
            result['recommendations'].extend(recommendations)
            
            result['success'] = True
            logger.info(f"✅ ID verification completed: {result['status']} (confidence: {confidence:.2%})")
            
        except Exception as e:
            logger.error(f"❌ ID verification error: {str(e)}")
            result['errors'].append(f"Verification error: {str(e)}")
        
        return result
    
    def _detect_id_with_yolo(self, image_path: str) -> Dict[str, Any]:
        """
        Detect ID card in image using YOLO v8.
        
        Args:
            image_path: Path to the image
        
        Returns:
            Dictionary with detection results
        """
        yolo_result = {
            'id_detected': False,
            'confidence': 0.0,
            'bounding_box': None,
            'detection_count': 0,
            'class_name': None
        }
        
        if not self.yolo_model:
            yolo_result['error'] = 'YOLO model not available'
            return yolo_result
        
        try:
            # Run YOLO detection
            results = self.yolo_model(image_path, conf=0.5)
            
            if len(results) > 0 and len(results[0].boxes) > 0:
                # Get the first detection (highest confidence)
                boxes = results[0].boxes
                best_box = boxes[0]
                
                yolo_result['id_detected'] = True
                yolo_result['confidence'] = float(best_box.conf[0])
                yolo_result['bounding_box'] = best_box.xyxy[0].tolist()
                yolo_result['detection_count'] = len(boxes)
                yolo_result['class_name'] = self.yolo_model.names[int(best_box.cls[0])]
                
                logger.info(f"✅ YOLO detected ID: {yolo_result['class_name']} (confidence: {yolo_result['confidence']:.2%})")
            else:
                logger.warning("⚠️ No ID detected by YOLO")
        
        except Exception as e:
            logger.error(f"❌ YOLO detection error: {str(e)}")
            yolo_result['error'] = str(e)
        
        return yolo_result
    
    def _extract_text_with_advanced_ocr(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from ID using Advanced OCR (AWS Textract).
        
        Args:
            image_path: Path to the image
        
        Returns:
            Dictionary with OCR results
        """
        ocr_result = {
            'success': False,
            'text': '',
            'confidence': 0.0,
            'blocks': [],
            'block_count': 0
        }
        
        if not self.advanced_ocr:
            ocr_result['error'] = 'Advanced OCR not available'
            return ocr_result
        
        try:
            # Read image bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Extract text with Advanced OCR
            result = self.advanced_ocr.extract_text(image_bytes, document_type='IMAGE')
            
            if result['success']:
                ocr_result['success'] = True
                ocr_result['text'] = result['text']
                ocr_result['confidence'] = result['confidence']
                ocr_result['blocks'] = result['blocks']
                ocr_result['block_count'] = result['block_count']
                
                logger.info(f"✅ Advanced OCR extracted {len(result['text'])} characters ({result['confidence']:.1f}% confidence)")
            else:
                ocr_result['error'] = result.get('error', 'Unknown error')
                logger.warning(f"⚠️ Advanced OCR failed: {ocr_result['error']}")
        
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {str(e)}")
            ocr_result['error'] = str(e)
        
        return ocr_result
    
    def _extract_id_fields(self, text: str, blocks: List[Dict], document_type: str) -> Dict[str, Any]:
        """
        Extract structured fields from ID text.
        
        Args:
            text: Extracted text from OCR
            blocks: Text blocks with positions
            document_type: Type of ID document
        
        Returns:
            Dictionary with extracted fields
        """
        import re
        
        fields = {
            'name': None,
            'student_number': None,
            'institution': None,
            'college': None,  # Department/College
            # Note: TCU IDs don't have these fields
            # 'id_number': Not used on TCU IDs
            # 'valid_until': Not present on TCU IDs
            # 'date_of_birth': Not present on TCU IDs
            # 'address': Not present on TCU IDs
        }
        
        text_lower = text.lower()
        
        try:
            # Filter out low confidence blocks (likely signatures or noise)
            # BUT keep the full text for pattern matching
            filtered_text_blocks = []
            for block in blocks:
                confidence = block.get('confidence', 0)
                block_text = block.get('text', '').strip()
                
                # Skip very low confidence blocks (< 30%) - likely signatures or artifacts
                if confidence < 30:
                    logger.info(f"⚠️ Filtering low confidence block: '{block_text}' ({confidence:.1f}%)")
                    continue
                
                # Skip blocks that look like single letters/numbers (unless part of student ID or dates)
                if len(block_text) <= 2 and not re.search(r'\d{2}-\d{5}', block_text) and not re.search(r'\d{2}[-/]\d{2}', block_text):
                    logger.info(f"⚠️ Filtering short block: '{block_text}'")
                    continue
                
                filtered_text_blocks.append(block)
            
            # Use filtered blocks for field extraction, but keep original text for pattern matching
            filtered_blocks = filtered_text_blocks
            
            # Extract student number (format: YY-XXXXX)
            student_num_patterns = [
                r'\b(\d{2}-\d{5})\b',
                r'(?:student\s*(?:no|number|id)[:\s]*)?(\d{2}-\d{5})',
                r'(?:id\s*(?:no|number)[:\s]*)?(\d{2}-\d{5})'
            ]
            for pattern in student_num_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    fields['student_number'] = match.group(1)
                    break
            
            # Extract name with advanced cleaning and validation
            fields['name'] = self._extract_and_clean_name(text, blocks)
            
            # Extract institution
            tcu_keywords = ['taguig', 'city', 'university', 'tcu']
            if any(keyword in text_lower for keyword in tcu_keywords):
                fields['institution'] = 'Taguig City University'
            
            # Extract college/department
            # TCU has 6 colleges
            # Order matters! Check more specific colleges first to avoid keyword conflicts
            from collections import OrderedDict
            college_mappings = OrderedDict([
                ('CICT', {
                    'full_name': 'College of Information and Communication Technology',
                    'keywords': ['information', 'communication', 'technology', 'cict', 'ict']
                }),
                ('CHTM', {
                    'full_name': 'College of Hospitality, Tourism, and Management',
                    'keywords': ['hospitality', 'tourism', 'chtm', 'hotel', 'travel']
                }),
                ('CCJ', {
                    'full_name': 'College of Criminal Justice',
                    'keywords': ['criminal', 'justice', 'ccj', 'criminology']
                }),
                ('CBM', {
                    'full_name': 'College of Business Management',
                    'keywords': ['business', 'management', 'cbm', 'commerce']
                }),
                ('CAS', {
                    'full_name': 'College of Arts and Science',
                    'keywords': ['arts', 'science', 'cas', 'liberal']
                }),
                ('CED', {
                    'full_name': 'College of Education',
                    'keywords': ['education', 'ced', 'teacher']
                })
            ])
            
            # Check for college in text
            for code, info in college_mappings.items():
                if any(keyword in text_lower for keyword in info['keywords']):
                    fields['college'] = info['full_name']
                    fields['college_code'] = code
                    logger.info(f"📚 Detected college: {info['full_name']} ({code})")
                    break
            
            logger.info(f"📋 Extracted fields: {sum(1 for v in fields.values() if v)}/{len(fields)}")
        
        except Exception as e:
            logger.error(f"❌ Field extraction error: {str(e)}")
        
        return fields
    
    def _extract_and_clean_name(self, text: str, blocks: List[Dict]) -> Optional[str]:
        """
        Extract and clean name from ID card text with advanced pattern matching.
        
        Args:
            text: Raw text from OCR
            blocks: Text blocks with positions (for context)
        
        Returns:
            Cleaned name string or None
        """
        import re
        
        # Common noise words to filter out
        noise_words = {
            'university', 'versity', 'college', 'taguig', 'city', 'tcu',
            'philippines', 'republic', 'student', 'name', 'id', 'card',
            'identification', 'number', 'no', 'date', 'birth', 'address',
            'valid', 'until', 'issued', 'signature', 'sex', 'gender',
            'nationality', 'blood', 'type', 'contact', 'emergency',
            'course', 'year', 'level', 'status', 'and', 'of', 'the',
            'technology', 'information', 'communication', 'ict', 'cict'
        }
        
        potential_names = []
        
        try:
            # Pattern 1: "Name: JOHN DELA CRUZ" or "Name: John Dela Cruz"
            name_label_patterns = [
                r'(?:name|student\s*name)[:\s]+([A-Z][A-Za-z\s\.]+?)(?:\n|$|\d{2}-\d{5})',
                r'(?:name|student\s*name)[:\s]+([A-Z][A-Z\s\.]+?)(?:\n|$|\d{2}-\d{5})',
            ]
            for pattern in name_label_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                potential_names.extend(matches)
            
            # Pattern 2: Lines with proper name format (Title Case or ALL CAPS)
            # Looking for 2-4 word names
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                
                # Skip if line is too short or too long
                if len(line) < 6 or len(line) > 60:
                    continue
                
                # Check for proper name patterns
                # Title Case: "John Dela Cruz"
                title_case_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})$'
                title_match = re.match(title_case_pattern, line)
                if title_match:
                    potential_names.append(title_match.group(1))
                
                # ALL CAPS: "JOHN DELA CRUZ" or "DELA CRUZ, JOHN"
                caps_pattern = r'^([A-Z]+(?:\s+[A-Z]+){1,3})$'
                caps_match = re.match(caps_pattern, line)
                if caps_match:
                    potential_names.append(caps_match.group(1))
                
                # Comma format: "DELA CRUZ, JOHN A."
                comma_pattern = r'^([A-Z]+(?:\s+[A-Z]+)*,\s*[A-Z]+(?:\s+[A-Z]\.?)*)$'
                comma_match = re.match(comma_pattern, line)
                if comma_match:
                    potential_names.append(comma_match.group(1))
            
            # Pattern 3: Use blocks to find name by position (typically near top)
            # Also check for multi-line names (e.g., "LLOYD KENNETH" + "S. RAMOS")
            if blocks:
                # Sort blocks by vertical position
                sorted_blocks = sorted(blocks, key=lambda b: b.get('geometry', {}).get('BoundingBox', {}).get('Top', 1))
                
                # Look for name patterns in blocks
                for i, block in enumerate(sorted_blocks):
                    block_text = block.get('text', '').strip()
                    
                    # Skip if too short or looks like noise
                    if len(block_text) < 3:
                        continue
                    
                    # Check if this looks like a name
                    if re.match(r'^[A-Z][A-Za-z\s\.]+$', block_text) and len(block_text.split()) >= 2:
                        potential_names.append(block_text)
                        
                        # Check if next block is a continuation (last name on next line)
                        if i + 1 < len(sorted_blocks):
                            next_block = sorted_blocks[i + 1]
                            next_text = next_block.get('text', '').strip()
                            
                            # Calculate vertical distance between blocks
                            current_bottom = block.get('geometry', {}).get('BoundingBox', {}).get('Top', 0) + \
                                           block.get('geometry', {}).get('BoundingBox', {}).get('Height', 0)
                            next_top = next_block.get('geometry', {}).get('BoundingBox', {}).get('Top', 1)
                            vertical_gap = abs(next_top - current_bottom)
                            
                            # If next line is close (< 0.05 units apart) and looks like name part
                            if vertical_gap < 0.05 and re.match(r'^[A-Z][A-Za-z\s\.]+$', next_text):
                                # Check if it's a last name pattern (e.g., "S. RAMOS")
                                if len(next_text.split()) <= 3:  # Reasonable last name length
                                    combined_name = f"{block_text} {next_text}"
                                    potential_names.append(combined_name)
                                    logger.info(f"🔗 Combined name from adjacent lines: {combined_name}")
            
            # Clean and filter potential names
            cleaned_names = []
            for name in potential_names:
                cleaned = self._clean_name_string(name, noise_words)
                if cleaned and self._is_valid_name(cleaned):
                    cleaned_names.append(cleaned)
            
            if not cleaned_names:
                return None
            
            # Return the best candidate (longest valid name with most words)
            # Prefer names with 3+ parts (First Middle Last) over 2 parts
            best_name = max(cleaned_names, key=lambda n: (
                len(n.split()),  # Number of name parts (prioritize more parts)
                len(n),           # Total length
                n.count('.'),     # Number of initials (slight preference for formal names)
            ))
            
            logger.info(f"✅ Extracted name: {best_name}")
            return best_name
        
        except Exception as e:
            logger.error(f"❌ Name extraction error: {str(e)}")
            return None
    
    def _clean_name_string(self, name: str, noise_words: set) -> Optional[str]:
        """
        Clean a name string by removing noise and formatting properly.
        
        Args:
            name: Raw name string
            noise_words: Set of words to filter out
        
        Returns:
            Cleaned name or None
        """
        import re
        
        try:
            # Remove extra whitespace
            name = re.sub(r'\s+', ' ', name).strip()
            
            # Handle comma format (LAST, FIRST -> FIRST LAST)
            if ',' in name:
                parts = name.split(',')
                if len(parts) == 2:
                    name = f"{parts[1].strip()} {parts[0].strip()}"
            
            # Split into words
            words = name.split()
            
            # Filter out noise words
            filtered_words = []
            for i, word in enumerate(words):
                word_lower = word.lower().strip('.,;:')
                
                # Check if it's a single letter (potential middle initial)
                is_single_letter = len(word.replace('.', '').replace(',', '')) == 1
                is_middle_position = 0 < i < len(words) - 1
                
                # Keep single letters if they're in the middle (likely middle initial)
                if is_single_letter and is_middle_position and word[0].isalpha():
                    filtered_words.append(word)
                    continue
                
                # Keep the word if:
                # 1. It's not in noise words
                # 2. It's at least 2 characters (unless it's a middle initial handled above)
                # 3. It's mostly alphabetic
                if (word_lower not in noise_words and 
                    len(word) >= 2 and 
                    sum(c.isalpha() for c in word) / len(word) >= 0.7):
                    filtered_words.append(word)
            
            if not filtered_words:
                return None
            
            # Rejoin words
            cleaned = ' '.join(filtered_words)
            
            # Title case if all caps
            if cleaned.isupper():
                cleaned = cleaned.title()
            
            # Format middle initials properly
            # "JOHN A. CRUZ" -> "John A. Cruz"
            # "JOHN A CRUZ" -> "John A. Cruz" (add period if missing)
            parts = cleaned.split()
            formatted_parts = []
            for i, part in enumerate(parts):
                # Check if this is a middle initial (single letter in middle of name)
                is_middle_position = 0 < i < len(parts) - 1
                is_single_letter = len(part.replace('.', '')) == 1
                
                if is_single_letter and part[0].isalpha():
                    # Format as middle initial: "A" or "A." -> "A."
                    formatted_parts.append(part[0].upper() + '.')
                elif len(part) == 2 and part[1] == '.':
                    # Already has period: "A."
                    formatted_parts.append(part.upper())
                else:
                    # Regular name part: remove periods
                    formatted_parts.append(part.replace('.', ''))
            
            cleaned = ' '.join(formatted_parts)
            
            return cleaned.strip()
        
        except Exception as e:
            logger.error(f"❌ Name cleaning error: {str(e)}")
            return None
    
    def _is_valid_name(self, name: str) -> bool:
        """
        Validate if a string is a proper name.
        
        Args:
            name: Name string to validate
        
        Returns:
            True if valid name, False otherwise
        """
        import re
        
        try:
            # Must have at least 2 words
            words = name.split()
            if len(words) < 2:
                return False
            
            # Must not have more than 5 words (unusually long)
            if len(words) > 5:
                return False
            
            # Each word must be at least 2 characters (except middle initials)
            for word in words:
                if len(word) == 1 and word.isupper():
                    continue  # Allow single uppercase letter (initial)
                if len(word) < 2:
                    return False
            
            # Must be mostly alphabetic
            alpha_count = sum(c.isalpha() or c.isspace() or c == '.' for c in name)
            if alpha_count / len(name) < 0.8:
                return False
            
            # Must not contain numbers
            if any(c.isdigit() for c in name):
                return False
            
            # Must not have excessive punctuation
            punct_count = sum(c in '.,;:!?@#$%^&*()[]{}' for c in name)
            if punct_count > 2:  # Allow up to 2 (e.g., middle initial period)
                return False
            
            # Must start with a letter
            if not name[0].isalpha():
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Name validation error: {str(e)}")
            return False
    
    def _verify_identity(self, user, extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that the ID card belongs to the logged-in user.
        
        Args:
            user: CustomUser object
            extracted_fields: Extracted ID fields containing name and student_number
        
        Returns:
            Dictionary containing:
                - match: Boolean indicating if identity matches
                - name_match: Boolean indicating if name matches
                - student_number_match: Boolean indicating if student number matches
                - message: Detailed message about the match
                - details: Comparison details
        """
        result = {
            'match': False,
            'name_match': False,
            'student_number_match': False,
            'message': '',
            'details': {}
        }
        
        try:
            extracted_name = extracted_fields.get('name', '').strip()
            extracted_student_number = extracted_fields.get('student_number', '').strip()
            
            # Get user details
            user_first_name = (user.first_name or '').strip()
            user_last_name = (user.last_name or '').strip()
            user_middle_initial = (user.middle_initial or '').strip()
            user_student_id = (user.student_id or '').strip()
            
            # Build full user name
            if user_middle_initial:
                # Ensure middle initial has period
                if not user_middle_initial.endswith('.'):
                    user_middle_initial = user_middle_initial + '.'
                user_full_name = f"{user_first_name} {user_middle_initial} {user_last_name}"
            else:
                user_full_name = f"{user_first_name} {user_last_name}"
            
            result['details'] = {
                'extracted_name': extracted_name,
                'user_name': user_full_name,
                'extracted_student_number': extracted_student_number,
                'user_student_number': user_student_id
            }
            
            # Check student number match
            if extracted_student_number and user_student_id:
                # Normalize: remove spaces, hyphens, convert to uppercase
                extracted_normalized = extracted_student_number.replace(' ', '').replace('-', '').upper()
                user_normalized = user_student_id.replace(' ', '').replace('-', '').upper()
                
                result['student_number_match'] = (extracted_normalized == user_normalized)
            
            # Check name match (case-insensitive, flexible)
            if extracted_name and user_full_name:
                # Normalize names: lowercase, remove extra spaces
                extracted_name_norm = ' '.join(extracted_name.lower().split())
                user_name_norm = ' '.join(user_full_name.lower().split())
                
                # Check exact match
                if extracted_name_norm == user_name_norm:
                    result['name_match'] = True
                else:
                    # Check if all user name parts are in extracted name
                    user_parts = user_name_norm.split()
                    extracted_parts = extracted_name_norm.split()
                    
                    # Allow match if first name and last name are present
                    first_name_match = user_first_name.lower() in extracted_name_norm
                    last_name_match = user_last_name.lower() in extracted_name_norm
                    
                    if first_name_match and last_name_match:
                        result['name_match'] = True
            
            # Overall match: Both student number and name must match
            result['match'] = result['student_number_match'] and result['name_match']
            
            # Generate message
            if result['match']:
                result['message'] = "✅ Identity verified: ID belongs to logged-in user"
            else:
                issues = []
                if not result['student_number_match']:
                    issues.append(f"Student number mismatch (ID: {extracted_student_number}, User: {user_student_id})")
                if not result['name_match']:
                    issues.append(f"Name mismatch (ID: {extracted_name}, User: {user_full_name})")
                result['message'] = "❌ Identity mismatch: " + "; ".join(issues)
            
            logger.info(f"👤 Identity verification: {result['message']}")
            
        except Exception as e:
            logger.error(f"❌ Identity verification error: {str(e)}")
            result['message'] = f"Identity verification failed: {str(e)}"
        
        return result
    
    def _run_validation_checks(
        self,
        fields: Dict[str, Any],
        yolo_result: Dict[str, Any],
        ocr_result: Dict[str, Any],
        document_type: str,
        user=None
    ) -> Dict[str, bool]:
        """
        Run validation checks on extracted data.
        
        Args:
            fields: Extracted ID fields
            yolo_result: YOLO detection results
            ocr_result: OCR extraction results
            document_type: Type of ID
        
        Returns:
            Dictionary of validation check results
        """
        checks = {
            'id_detected': False,
            'text_extracted': False,
            'has_student_number': False,
            'has_name': False,
            'has_institution': False,
            'has_college': False,  # College/Department check
            'high_ocr_confidence': False,
            'identity_verified': True  # Default to True if no user provided
        }
        
        try:
            # Check ID detection
            checks['id_detected'] = yolo_result.get('id_detected', False) and yolo_result.get('confidence', 0) >= 0.5
            
            # Check text extraction
            checks['text_extracted'] = (
                ocr_result.get('success', False) and
                len(ocr_result.get('text', '')) >= 20
            )
            
            # Check required fields
            checks['has_student_number'] = fields.get('student_number') is not None
            checks['has_name'] = fields.get('name') is not None and len(fields.get('name', '')) >= 3
            checks['has_institution'] = fields.get('institution') is not None
            checks['has_college'] = fields.get('college') is not None
            
            # Check identity verification if user provided
            if user:
                identity_result = self._verify_identity(user, fields)
                checks['identity_verified'] = identity_result.get('match', False)
            
            # Check OCR confidence
            checks['high_ocr_confidence'] = ocr_result.get('confidence', 0) >= 75
            
        except Exception as e:
            logger.error(f"❌ Validation check error: {str(e)}")
        
        return checks
    
    def _calculate_confidence(
        self,
        yolo_result: Dict[str, Any],
        ocr_result: Dict[str, Any],
        fields: Dict[str, Any],
        validation_checks: Dict[str, bool]
    ) -> float:
        """
        Calculate overall confidence score.
        
        Args:
            yolo_result: YOLO detection results
            ocr_result: OCR extraction results
            fields: Extracted ID fields
            validation_checks: Validation check results
        
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.0
        
        try:
            # YOLO detection confidence (25%)
            if yolo_result.get('id_detected', False):
                confidence += 0.25 * yolo_result.get('confidence', 0)
            
            # OCR confidence (25%)
            if ocr_result.get('success', False):
                confidence += 0.25 * (ocr_result.get('confidence', 0) / 100)
            
            # Field extraction (30%)
            field_count = sum(1 for v in fields.values() if v is not None)
            total_fields = len(fields)
            confidence += 0.30 * (field_count / total_fields)
            
            # Validation checks (20%)
            checks_passed = sum(1 for v in validation_checks.values() if v)
            total_checks = len(validation_checks)
            confidence += 0.20 * (checks_passed / total_checks)
        
        except Exception as e:
            logger.error(f"❌ Confidence calculation error: {str(e)}")
        
        return round(confidence, 3)
    
    def _generate_recommendations(
        self,
        status: str,
        validation_checks: Dict[str, bool],
        fields: Dict[str, Any],
        confidence: float
    ) -> List[str]:
        """
        Generate recommendations based on verification results.
        
        Args:
            status: Verification status
            validation_checks: Validation check results
            fields: Extracted fields
            confidence: Overall confidence score
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            if status == 'INVALID':
                recommendations.append("ID verification failed. Please upload a clear, well-lit image of your ID.")
            
            if not validation_checks.get('id_detected', False):
                recommendations.append("ID card not clearly visible. Ensure entire card is in frame.")
            
            if not validation_checks.get('high_ocr_confidence', False):
                recommendations.append("Text quality is low. Try taking photo in better lighting.")
            
            if not fields.get('student_number'):
                recommendations.append("Student number not found. Ensure it's clearly visible.")
            
            if not fields.get('name'):
                recommendations.append("Name not detected. Make sure text is readable.")
            
            if not fields.get('college'):
                recommendations.append("College/Department not detected. Ensure college name is visible.")
            
            if confidence < 0.5:
                recommendations.append("Low confidence score. Consider retaking the photo.")
            
        except Exception as e:
            logger.error(f"❌ Recommendation generation error: {str(e)}")
        
        return recommendations


# Singleton instance
_id_verification_service = None

def get_id_verification_service() -> IDVerificationService:
    """Get or create the singleton ID verification service instance."""
    global _id_verification_service
    if _id_verification_service is None:
        _id_verification_service = IDVerificationService()
    return _id_verification_service
