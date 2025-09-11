"""
Base AI Document Verifier - Enhanced Document Type Detection
This module provides advanced AI capabilities for verifying document authenticity and type matching.
"""

import os
import re
import json
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import tempfile
from pathlib import Path
import logging

# Image processing and computer vision
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter, ImageStat
    import pytesseract
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

# Advanced text analysis
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import nltk
    from textblob import TextBlob
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# PDF processing
try:
    import PyPDF2
    import fitz  # PyMuPDF for better PDF handling
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class DocumentTypeDetector:
    """Advanced AI system for detecting document types and preventing fraudulent submissions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced document patterns with balanced validation (more lenient for legitimate documents)
        self.document_signatures = {
            'birth_certificate': {
                'required_keywords': {
                    'primary': ['birth', 'certificate', 'civil', 'registry', 'registrar'],
                    'supporting': ['born', 'child', 'parent', 'mother', 'father', 'date of birth', 'place of birth'],
                    'official': ['republic', 'philippines', 'civil registrar', 'psa', 'nso']
                },
                'forbidden_keywords': ['school', 'student', 'grade', 'transcript', 'diploma', 'enrollment'],
                'layout_features': {
                    'expected_structure': ['header', 'personal_info', 'parent_info', 'registry_info', 'seal'],
                    'text_density': 'medium',
                    'has_official_seal': True
                },
                'confidence_threshold': 0.30,  # Lowered from 0.75 to 0.30
                'strict_mode': False  # Changed to False for more lenient processing
            },
            'school_id': {
                'required_keywords': {
                    'primary': ['student', 'id', 'identification', 'school', 'university', 'college'],
                    'supporting': ['name', 'student number', 'photo', 'signature', 'valid until'],
                    'official': ['tcu', 'trinity college', 'university']
                },
                'forbidden_keywords': ['birth', 'civil', 'registry', 'marriage', 'death'],
                'layout_features': {
                    'expected_structure': ['photo', 'student_info', 'id_number', 'validity'],
                    'text_density': 'low',
                    'has_photo': True
                },
                'confidence_threshold': 0.25,  # Lowered from 0.70 to 0.25
                'strict_mode': False  # Changed to False
            },
            'report_card': {
                'required_keywords': {
                    'primary': ['grade', 'report', 'transcript', 'academic', 'semester'],
                    'supporting': ['subject', 'gwa', 'swa', 'units', 'credit', 'average', 'final grade'],
                    'official': ['registrar', 'school', 'university', 'college']
                },
                'forbidden_keywords': ['birth', 'civil', 'marriage', 'death', 'clearance'],
                'layout_features': {
                    'expected_structure': ['header', 'student_info', 'grades_table', 'summary'],
                    'text_density': 'high',
                    'has_table_structure': True
                },
                'confidence_threshold': 0.35,  # Lowered from 0.80 to 0.35
                'strict_mode': False  # Changed to False
            },
            'enrollment_certificate': {
                'required_keywords': {
                    'primary': ['enrollment', 'certificate', 'enrolled', 'student'],
                    'supporting': ['semester', 'academic year', 'units', 'status', 'enrolled in'],
                    'official': ['registrar', 'school', 'university', 'college']
                },
                'forbidden_keywords': ['birth', 'civil', 'marriage', 'death', 'grade'],
                'layout_features': {
                    'expected_structure': ['header', 'student_info', 'enrollment_details', 'official_signature'],
                    'text_density': 'medium',
                    'has_official_seal': True
                },
                'confidence_threshold': 0.30,  # Lowered from 0.75 to 0.30
                'strict_mode': False  # Changed to False
            },
            'barangay_clearance': {
                'required_keywords': {
                    'primary': ['barangay', 'clearance', 'certificate', 'clearance'],
                    'supporting': ['resident', 'good moral', 'character', 'issued to', 'purpose'],
                    'official': ['barangay', 'captain', 'chairman', 'official']
                },
                'forbidden_keywords': ['birth', 'school', 'student', 'grade', 'transcript'],
                'layout_features': {
                    'expected_structure': ['header', 'recipient_info', 'purpose', 'official_signature'],
                    'text_density': 'medium',
                    'has_official_seal': True
                },
                'confidence_threshold': 0.25,  # Lowered from 0.70 to 0.25
                'strict_mode': False  # Changed to False
            },
            'parents_id': {
                'required_keywords': {
                    'primary': ['identification', 'id', 'identity', 'card'],
                    'supporting': ['name', 'address', 'signature', 'photo', 'valid until'],
                    'official': ['government', 'issued', 'republic', 'philippines']
                },
                'forbidden_keywords': ['student', 'school', 'birth', 'grade', 'enrollment'],
                'layout_features': {
                    'expected_structure': ['photo', 'personal_info', 'id_number', 'validity'],
                    'text_density': 'low',
                    'has_photo': True
                },
                'confidence_threshold': 0.20,  # Lowered from 0.65 to 0.20
                'strict_mode': False  # Changed to False
            },
            'voter_certification': {
                'required_keywords': {
                    'primary': ['voter', 'voting', 'certification', 'certificate', 'registered'],
                    'supporting': ['comelec', 'election', 'precinct', 'registered voter'],
                    'official': ['commission', 'elections', 'comelec', 'government']
                },
                'forbidden_keywords': ['student', 'school', 'birth', 'grade', 'enrollment'],
                'layout_features': {
                    'expected_structure': ['header', 'voter_info', 'registration_details', 'official_seal'],
                    'text_density': 'medium',
                    'has_official_seal': True
                },
                'confidence_threshold': 0.30,  # Lowered from 0.75 to 0.30
                'strict_mode': False  # Changed to False
            }
        }
        
        # Image quality thresholds for different document types (more lenient)
        self.quality_thresholds = {
            'min_resolution': (400, 300),      # Lowered from (800, 600) to (400, 300)
            'min_file_size': 10 * 1024,        # Lowered from 50KB to 10KB
            'max_file_size': 15 * 1024 * 1024, # Increased from 10MB to 15MB
            'min_text_confidence': 30,          # Lowered from 60 to 30
            'blur_threshold': 50,               # Lowered from 100 to 50 (more lenient)
            'brightness_range': (20, 240),     # Expanded from (30, 225) to (20, 240)
        }

    def verify_document_type(self, document_submission, uploaded_file) -> Dict[str, Any]:
        """
        Comprehensive document type verification with fraud detection
        """
        verification_result = {
            'is_valid_document': False,
            'document_type_match': False,
            'confidence_score': 0.0,
            'fraud_indicators': [],
            'quality_issues': [],
            'verification_notes': [],
            'extracted_features': {},
            'similarity_scores': {},
            'recommendation': 'reject'
        }
        
        try:
            declared_type = document_submission.document_type
            
            # Step 1: Basic file validation
            file_validation = self._validate_file_properties(uploaded_file)
            verification_result.update(file_validation)
            
            if not file_validation['basic_validation_passed']:
                verification_result['recommendation'] = 'reject'
                return verification_result
            
            # Step 2: Extract text and analyze content
            content_analysis = self._analyze_document_content(uploaded_file)
            verification_result['extracted_features'] = content_analysis
            
            # Step 3: Verify document type against declared type
            type_verification = self._verify_against_declared_type(
                declared_type, content_analysis, uploaded_file
            )
            verification_result.update(type_verification)
            
            # Step 4: Fraud detection
            fraud_analysis = self._detect_fraud_indicators(
                declared_type, content_analysis, uploaded_file
            )
            verification_result.update(fraud_analysis)
            
            # Step 5: Quality assessment
            quality_analysis = self._assess_document_quality(uploaded_file)
            verification_result.update(quality_analysis)
            
            # Step 6: Final decision
            final_decision = self._make_final_decision(verification_result, declared_type)
            verification_result.update(final_decision)
            
        except Exception as e:
            self.logger.error(f"Document verification error: {str(e)}")
            verification_result['verification_notes'].append(f"Verification error: {str(e)}")
            verification_result['recommendation'] = 'manual_review'
        
        return verification_result

    def _validate_file_properties(self, uploaded_file) -> Dict[str, Any]:
        """Validate basic file properties"""
        validation = {
            'basic_validation_passed': False,
            'file_size_mb': 0.0,
            'file_format': 'unknown',
            'validation_notes': []
        }
        
        try:
            file_size = uploaded_file.size
            filename = uploaded_file.name.lower()
            
            validation['file_size_mb'] = round(file_size / (1024 * 1024), 2)
            
            # Check file size
            if file_size < self.quality_thresholds['min_file_size']:
                validation['validation_notes'].append(f"File too small ({validation['file_size_mb']} MB) - likely not a real document")
                return validation
            
            if file_size > self.quality_thresholds['max_file_size']:
                validation['validation_notes'].append(f"File too large ({validation['file_size_mb']} MB)")
                return validation
            
            # Check file format
            if filename.endswith('.pdf'):
                validation['file_format'] = 'pdf'
            elif filename.endswith(('.jpg', '.jpeg', '.png')):
                validation['file_format'] = 'image'
            else:
                validation['validation_notes'].append("Unsupported file format")
                return validation
            
            validation['basic_validation_passed'] = True
            validation['validation_notes'].append("Basic file validation passed")
            
        except Exception as e:
            validation['validation_notes'].append(f"File validation error: {str(e)}")
        
        return validation

    def _analyze_document_content(self, uploaded_file) -> Dict[str, Any]:
        """Extract and analyze document content"""
        content_analysis = {
            'extracted_text': '',
            'text_confidence': 0.0,
            'detected_languages': [],
            'text_structure': {},
            'visual_features': {},
            'layout_analysis': {}
        }
        
        try:
            # Extract text based on file type
            filename = uploaded_file.name.lower()
            
            if filename.endswith('.pdf'):
                content_analysis.update(self._analyze_pdf_content(uploaded_file))
            elif filename.endswith(('.jpg', '.jpeg', '.png')):
                content_analysis.update(self._analyze_image_content(uploaded_file))
            
            # Analyze extracted text
            if content_analysis['extracted_text']:
                text_analysis = self._analyze_text_structure(content_analysis['extracted_text'])
                content_analysis['text_structure'] = text_analysis
            
        except Exception as e:
            self.logger.error(f"Content analysis error: {str(e)}")
            content_analysis['extraction_error'] = str(e)
        
        return content_analysis

    def _analyze_image_content(self, uploaded_file) -> Dict[str, Any]:
        """Analyze image-based documents"""
        if not CV_AVAILABLE:
            return {'error': 'Computer vision libraries not available'}
        
        analysis = {
            'extracted_text': '',
            'text_confidence': 0.0,
            'visual_features': {},
            'layout_analysis': {}
        }
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Load and process image
            image = cv2.imread(temp_path)
            if image is None:
                raise ValueError("Could not load image file")
            
            # Get image properties
            height, width = image.shape[:2]
            analysis['visual_features'] = {
                'dimensions': (width, height),
                'aspect_ratio': width / height,
                'total_pixels': width * height
            }
            
            # Check minimum resolution
            if width < self.quality_thresholds['min_resolution'][0] or height < self.quality_thresholds['min_resolution'][1]:
                analysis['quality_issues'] = [f"Low resolution: {width}x{height}"]
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Extract text using OCR
            try:
                # Try with basic OCR first
                extracted_text = pytesseract.image_to_string(processed_image)
                analysis['extracted_text'] = extracted_text
                analysis['text_confidence'] = 75  # Default good confidence for basic OCR
                
                # If we got reasonable text, try to get detailed confidence scores
                if len(extracted_text.strip()) > 5:
                    try:
                        custom_config = r'--oem 3 --psm 6'
                        
                        # Get text with confidence scores
                        ocr_data = pytesseract.image_to_data(processed_image, config=custom_config, output_type=pytesseract.Output.DICT)
                        
                        # Extract text and calculate confidence
                        words = []
                        confidences = []
                        
                        for i in range(len(ocr_data['text'])):
                            word = ocr_data['text'][i].strip()
                            confidence = int(ocr_data['conf'][i])
                            
                            if word and confidence > 0:
                                words.append(word)
                                confidences.append(confidence)
                        
                        if words and confidences:
                            analysis['extracted_text'] = ' '.join(words)
                            analysis['text_confidence'] = np.mean(confidences)
                        
                        # Layout analysis
                        analysis['layout_analysis'] = self._analyze_document_layout(ocr_data)
                        
                    except Exception as detailed_ocr_error:
                        # Fallback to basic extraction already done above
                        analysis['detailed_ocr_error'] = str(detailed_ocr_error)
                        # Keep the basic extracted_text and confidence
                
            except Exception as ocr_error:
                analysis['ocr_error'] = str(ocr_error)
                # Even more basic fallback - assume there's some text content
                analysis['extracted_text'] = "Document content detected"
                analysis['text_confidence'] = 50  # Default moderate confidence
            
            # Visual feature analysis
            visual_analysis = self._analyze_visual_features(image)
            analysis['visual_features'].update(visual_analysis)
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis

    def _preprocess_image_for_ocr(self, image):
        """Preprocess image to improve OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Noise removal
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Improve contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast_enhanced = clahe.apply(denoised)
        
        # Gaussian blur to smooth
        blurred = cv2.GaussianBlur(contrast_enhanced, (1, 1), 0)
        
        # Thresholding to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def _analyze_visual_features(self, image) -> Dict[str, Any]:
        """Analyze visual features that indicate document authenticity"""
        features = {}
        
        try:
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Blur detection using Laplacian variance
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            features['blur_score'] = float(blur_score)
            features['is_blurry'] = blur_score < self.quality_thresholds['blur_threshold']
            
            # Brightness analysis
            brightness = np.mean(gray)
            features['brightness'] = float(brightness)
            features['brightness_acceptable'] = (
                self.quality_thresholds['brightness_range'][0] <= brightness <= 
                self.quality_thresholds['brightness_range'][1]
            )
            
            # Contrast analysis
            contrast = gray.std()
            features['contrast'] = float(contrast)
            
            # Edge detection for document structure
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            features['edge_density'] = float(edge_density)
            
            # Color analysis
            color_hist = cv2.calcHist([hsv], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
            features['color_complexity'] = float(np.count_nonzero(color_hist))
            
            # Texture analysis
            features['texture_complexity'] = self._calculate_texture_complexity(gray)
            
        except Exception as e:
            features['analysis_error'] = str(e)
        
        return features

    def _calculate_texture_complexity(self, gray_image) -> float:
        """Calculate texture complexity to distinguish documents from random images"""
        try:
            # Calculate local binary patterns or similar texture features
            # This is a simplified version - in production, use more sophisticated methods
            
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Calculate texture measure
            texture_score = np.std(magnitude)
            return float(texture_score)
            
        except Exception:
            return 0.0

    def _analyze_document_layout(self, ocr_data) -> Dict[str, Any]:
        """Analyze document layout structure from OCR data"""
        layout = {
            'text_blocks': 0,
            'line_count': 0,
            'word_count': 0,
            'has_structured_layout': False,
            'text_distribution': {}
        }
        
        try:
            # Count text elements
            valid_words = [word for word in ocr_data['text'] if word.strip()]
            layout['word_count'] = len(valid_words)
            
            # Analyze text distribution
            if 'top' in ocr_data and 'left' in ocr_data:
                tops = [int(top) for top, conf in zip(ocr_data['top'], ocr_data['conf']) if int(conf) > 30]
                lefts = [int(left) for left, conf in zip(ocr_data['left'], ocr_data['conf']) if int(conf) > 30]
                
                if tops and lefts:
                    layout['text_distribution'] = {
                        'vertical_spread': max(tops) - min(tops),
                        'horizontal_spread': max(lefts) - min(lefts),
                        'text_regions': len(set([(t//50, l//50) for t, l in zip(tops, lefts)]))
                    }
            
            # Determine if layout suggests a structured document
            layout['has_structured_layout'] = (
                layout['word_count'] > 10 and 
                layout['text_distribution'].get('text_regions', 0) > 3
            )
            
        except Exception as e:
            layout['error'] = str(e)
        
        return layout

    def _analyze_pdf_content(self, uploaded_file) -> Dict[str, Any]:
        """Analyze PDF documents"""
        if not PDF_AVAILABLE:
            return {'error': 'PDF processing libraries not available'}
        
        analysis = {
            'extracted_text': '',
            'page_count': 0,
            'has_images': False,
            'pdf_metadata': {}
        }
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Use PyMuPDF for better text extraction
            try:
                pdf_document = fitz.open(temp_path)
                
                analysis['page_count'] = pdf_document.page_count
                
                # Extract text from all pages
                text_content = []
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    text_content.append(page.get_text())
                    
                    # Check for images
                    if page.get_images():
                        analysis['has_images'] = True
                
                analysis['extracted_text'] = '\n'.join(text_content)
                
                # Get metadata
                analysis['pdf_metadata'] = {
                    'title': pdf_document.metadata.get('title', ''),
                    'author': pdf_document.metadata.get('author', ''),
                    'creator': pdf_document.metadata.get('creator', ''),
                    'producer': pdf_document.metadata.get('producer', '')
                }
                
                pdf_document.close()
                
            except Exception:
                # Fallback to PyPDF2
                with open(temp_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    analysis['page_count'] = len(pdf_reader.pages)
                    
                    text_content = []
                    for page in pdf_reader.pages:
                        text_content.append(page.extract_text())
                    
                    analysis['extracted_text'] = '\n'.join(text_content)
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis

    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the structure and content of extracted text"""
        structure = {
            'word_count': 0,
            'line_count': 0,
            'character_count': 0,
            'language_patterns': {},
            'formal_indicators': {},
            'date_patterns': [],
            'name_patterns': [],
            'official_indicators': []
        }
        
        if not text or len(text.strip()) < 10:
            return structure
        
        try:
            text_clean = text.strip()
            structure['character_count'] = len(text_clean)
            structure['word_count'] = len(text_clean.split())
            structure['line_count'] = len(text_clean.split('\n'))
            
            # Language analysis
            text_lower = text_clean.lower()
            
            # Look for formal language indicators
            formal_words = ['certificate', 'hereby', 'certify', 'issued', 'official', 'republic', 'government']
            formal_count = sum(1 for word in formal_words if word in text_lower)
            structure['formal_indicators']['formal_word_count'] = formal_count
            structure['formal_indicators']['formality_score'] = formal_count / len(formal_words)
            
            # Date pattern detection
            date_patterns = [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
                r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b',  # DD Month YYYY
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}\b'  # Month DD, YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                structure['date_patterns'].extend(matches)
            
            # Name pattern detection (simple)
            name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
            name_matches = re.findall(name_pattern, text)
            structure['name_patterns'] = name_matches[:5]  # Limit to first 5 names
            
            # Official document indicators
            official_phrases = [
                'republic of the philippines',
                'civil registrar',
                'this is to certify',
                'issued this',
                'official seal',
                'government id',
                'valid until'
            ]
            
            for phrase in official_phrases:
                if phrase in text_lower:
                    structure['official_indicators'].append(phrase)
            
        except Exception as e:
            structure['analysis_error'] = str(e)
        
        return structure

    def _verify_against_declared_type(self, declared_type: str, content_analysis: Dict, uploaded_file) -> Dict[str, Any]:
        """Verify if document content matches the declared document type"""
        verification = {
            'document_type_match': False,
            'confidence_score': 0.0,
            'keyword_analysis': {},
            'structure_match': False,
            'verification_notes': []
        }
        
        if declared_type not in self.document_signatures:
            verification['verification_notes'].append(f"Unknown document type: {declared_type}")
            return verification
        
        signature = self.document_signatures[declared_type]
        extracted_text = content_analysis.get('extracted_text', '').lower()
        
        if not extracted_text or len(extracted_text.strip()) < 20:
            verification['verification_notes'].append("Insufficient text extracted from document")
            verification['confidence_score'] = 0.0
            return verification
        
        # Keyword analysis
        keyword_scores = self._analyze_keywords(extracted_text, signature)
        verification['keyword_analysis'] = keyword_scores
        
        # Structure analysis
        structure_score = self._analyze_document_structure(content_analysis, signature)
        verification['structure_match'] = structure_score > 0.5
        
        # Calculate overall confidence
        confidence_factors = [
            keyword_scores.get('primary_score', 0) * 0.4,
            keyword_scores.get('supporting_score', 0) * 0.3,
            keyword_scores.get('official_score', 0) * 0.2,
            structure_score * 0.1
        ]
        
        # Penalize forbidden keywords
        forbidden_penalty = keyword_scores.get('forbidden_penalty', 0)
        
        base_confidence = sum(confidence_factors)
        final_confidence = max(0.0, base_confidence - forbidden_penalty)
        
        verification['confidence_score'] = final_confidence
        verification['document_type_match'] = final_confidence >= signature['confidence_threshold']
        
        # Generate verification notes
        if verification['document_type_match']:
            verification['verification_notes'].append(
                f"✅ Document verified as {declared_type} (confidence: {final_confidence:.1%})"
            )
        else:
            verification['verification_notes'].append(
                f"❌ Document does not match {declared_type} (confidence: {final_confidence:.1%})"
            )
            
            # Provide specific reasons
            if keyword_scores.get('primary_score', 0) < 0.3:
                verification['verification_notes'].append("- Missing primary keywords for this document type")
            if forbidden_penalty > 0:
                verification['verification_notes'].append("- Contains keywords from other document types")
            if not verification['structure_match']:
                verification['verification_notes'].append("- Document structure doesn't match expected layout")
        
        return verification

    def _analyze_keywords(self, text: str, signature: Dict) -> Dict[str, Any]:
        """Analyze keyword presence and calculate scores"""
        keyword_analysis = {
            'primary_score': 0.0,
            'supporting_score': 0.0,
            'official_score': 0.0,
            'forbidden_penalty': 0.0,
            'found_keywords': {
                'primary': [],
                'supporting': [],
                'official': [],
                'forbidden': []
            }
        }
        
        # Check primary keywords
        primary_keywords = signature['required_keywords']['primary']
        primary_found = [kw for kw in primary_keywords if kw in text]
        keyword_analysis['found_keywords']['primary'] = primary_found
        keyword_analysis['primary_score'] = len(primary_found) / len(primary_keywords)
        
        # Check supporting keywords
        supporting_keywords = signature['required_keywords']['supporting']
        supporting_found = [kw for kw in supporting_keywords if kw in text]
        keyword_analysis['found_keywords']['supporting'] = supporting_found
        keyword_analysis['supporting_score'] = len(supporting_found) / len(supporting_keywords)
        
        # Check official keywords
        official_keywords = signature['required_keywords']['official']
        official_found = [kw for kw in official_keywords if kw in text]
        keyword_analysis['found_keywords']['official'] = official_found
        keyword_analysis['official_score'] = len(official_found) / len(official_keywords)
        
        # Check forbidden keywords (penalty)
        forbidden_keywords = signature.get('forbidden_keywords', [])
        forbidden_found = [kw for kw in forbidden_keywords if kw in text]
        keyword_analysis['found_keywords']['forbidden'] = forbidden_found
        keyword_analysis['forbidden_penalty'] = len(forbidden_found) * 0.2  # 20% penalty per forbidden keyword
        
        return keyword_analysis

    def _analyze_document_structure(self, content_analysis: Dict, signature: Dict) -> float:
        """Analyze document structure and layout"""
        structure_score = 0.0
        
        try:
            layout_features = signature.get('layout_features', {})
            text_structure = content_analysis.get('text_structure', {})
            visual_features = content_analysis.get('visual_features', {})
            
            # Check text density
            expected_density = layout_features.get('text_density', 'medium')
            word_count = text_structure.get('word_count', 0)
            
            if expected_density == 'high' and word_count > 100:
                structure_score += 0.3
            elif expected_density == 'medium' and 30 <= word_count <= 150:
                structure_score += 0.3
            elif expected_density == 'low' and word_count < 50:
                structure_score += 0.3
            
            # Check for official indicators
            if layout_features.get('has_official_seal') and text_structure.get('official_indicators'):
                structure_score += 0.2
            
            # Check for photo presence (for ID documents)
            if layout_features.get('has_photo'):
                # This would require more sophisticated image analysis
                # For now, give partial credit if document seems to have image elements
                if visual_features.get('color_complexity', 0) > 1000:
                    structure_score += 0.2
            
            # Check for table structure (for grades)
            if layout_features.get('has_table_structure'):
                # Look for tabular patterns in text
                line_count = text_structure.get('line_count', 0)
                if line_count > 10:  # Tables usually have multiple lines
                    structure_score += 0.3
            
        except Exception as e:
            self.logger.error(f"Structure analysis error: {str(e)}")
        
        return min(1.0, structure_score)

    def _detect_fraud_indicators(self, declared_type: str, content_analysis: Dict, uploaded_file) -> Dict[str, Any]:
        """Detect potential fraud indicators in the document"""
        fraud_analysis = {
            'fraud_indicators': [],
            'fraud_risk_score': 0.0,
            'is_likely_fraud': False
        }
        
        try:
            extracted_text = content_analysis.get('extracted_text', '')
            visual_features = content_analysis.get('visual_features', {})
            
            # Check 1: Random image indicators
            if self._is_likely_random_image(visual_features, extracted_text):
                fraud_analysis['fraud_indicators'].append("Document appears to be a random image, not an official document")
                fraud_analysis['fraud_risk_score'] += 0.8
            
            # Check 2: Very low text content
            if len(extracted_text.strip()) < 20:
                fraud_analysis['fraud_indicators'].append("Insufficient text content for a valid document")
                fraud_analysis['fraud_risk_score'] += 0.6
            
            # Check 3: Wrong document type keywords
            if declared_type in self.document_signatures:
                forbidden_keywords = self.document_signatures[declared_type].get('forbidden_keywords', [])
                forbidden_found = [kw for kw in forbidden_keywords if kw in extracted_text.lower()]
                
                if forbidden_found:
                    fraud_analysis['fraud_indicators'].append(
                        f"Contains keywords from other document types: {', '.join(forbidden_found)}"
                    )
                    fraud_analysis['fraud_risk_score'] += len(forbidden_found) * 0.3
            
            # Check 4: Image quality issues that suggest screenshots or digital manipulation
            if visual_features:
                if visual_features.get('is_blurry', False):
                    fraud_analysis['fraud_indicators'].append("Image is significantly blurred")
                    fraud_analysis['fraud_risk_score'] += 0.3
                
                if not visual_features.get('brightness_acceptable', True):
                    fraud_analysis['fraud_indicators'].append("Poor image lighting/exposure")
                    fraud_analysis['fraud_risk_score'] += 0.2
                
                # Check for very low resolution
                dimensions = visual_features.get('dimensions', (0, 0))
                if dimensions[0] * dimensions[1] < 480000:  # Less than 800x600
                    fraud_analysis['fraud_indicators'].append("Image resolution too low for document verification")
                    fraud_analysis['fraud_risk_score'] += 0.4
            
            # Check 5: OCR confidence too low
            text_confidence = content_analysis.get('text_confidence', 0)
            if text_confidence < self.quality_thresholds['min_text_confidence']:
                fraud_analysis['fraud_indicators'].append(f"OCR confidence too low: {text_confidence}%")
                fraud_analysis['fraud_risk_score'] += 0.4
            
            # Determine if likely fraud
            fraud_analysis['is_likely_fraud'] = fraud_analysis['fraud_risk_score'] >= 0.7
            
        except Exception as e:
            fraud_analysis['fraud_indicators'].append(f"Fraud detection error: {str(e)}")
        
        return fraud_analysis

    def _is_likely_random_image(self, visual_features: Dict, extracted_text: str) -> bool:
        """Determine if the image is likely a random photo rather than a document"""
        indicators = 0
        
        # Very little text extracted
        if len(extracted_text.strip()) < 10:
            indicators += 1
        
        # High color complexity (documents are usually simpler)
        if visual_features.get('color_complexity', 0) > 5000:
            indicators += 1
        
        # High texture complexity (documents have more uniform text regions)
        if visual_features.get('texture_complexity', 0) > 50:
            indicators += 1
        
        # Low edge density (documents usually have clear text edges)
        if visual_features.get('edge_density', 1) < 0.05:
            indicators += 1
        
        # Unusual aspect ratio for documents
        aspect_ratio = visual_features.get('aspect_ratio', 1.0)
        if aspect_ratio < 0.7 or aspect_ratio > 2.0:  # Documents are usually between 0.7 and 2.0
            indicators += 1
        
        return indicators >= 3

    def _assess_document_quality(self, uploaded_file) -> Dict[str, Any]:
        """Assess overall document quality"""
        quality_analysis = {
            'quality_issues': [],
            'quality_score': 1.0,
            'is_acceptable_quality': True
        }
        
        try:
            filename = uploaded_file.name.lower()
            file_size = uploaded_file.size
            
            # File size issues
            if file_size < 100 * 1024:  # Less than 100KB
                quality_analysis['quality_issues'].append("File size very small - may be low quality")
                quality_analysis['quality_score'] -= 0.2
            elif file_size > 8 * 1024 * 1024:  # Greater than 8MB
                quality_analysis['quality_issues'].append("File size very large - may be unnecessarily high resolution")
                quality_analysis['quality_score'] -= 0.1
            
            # File format preferences
            if filename.endswith(('.jpg', '.jpeg')):
                quality_analysis['quality_score'] -= 0.1  # Slight preference for PNG/PDF
            elif filename.endswith('.png'):
                pass  # Good format
            elif filename.endswith('.pdf'):
                quality_analysis['quality_score'] += 0.1  # Slight bonus for PDF
            
            quality_analysis['is_acceptable_quality'] = quality_analysis['quality_score'] >= 0.5
            
        except Exception as e:
            quality_analysis['quality_issues'].append(f"Quality assessment error: {str(e)}")
        
        return quality_analysis

    def _make_final_decision(self, verification_result: Dict, declared_type: str) -> Dict[str, Any]:
        """Make final decision on document verification (more lenient approach)"""
        decision = {
            'recommendation': 'auto_approve',  # Default to approval unless clear fraud
            'final_confidence': 0.0,
            'decision_reasoning': []
        }
        
        try:
            confidence_score = verification_result.get('confidence_score', 0.0)
            fraud_risk = verification_result.get('fraud_risk_score', 0.0)
            is_acceptable_quality = verification_result.get('is_acceptable_quality', True)
            document_type_match = verification_result.get('document_type_match', False)
            
            # Calculate final confidence considering fraud risk
            final_confidence = max(0.0, confidence_score - (fraud_risk * 0.5))  # Reduce fraud penalty
            decision['final_confidence'] = final_confidence
            
            # More lenient decision logic - focus on preventing obvious fraud only
            if fraud_risk >= 0.8:  # Only reject very high fraud risk (was 0.7)
                decision['recommendation'] = 'reject'
                decision['decision_reasoning'].append("Very high fraud risk detected")
            elif fraud_risk >= 0.6 and confidence_score < 0.1:  # Both high fraud AND very low confidence
                decision['recommendation'] = 'reject'
                decision['decision_reasoning'].append("High fraud risk with very low confidence")
            elif not is_acceptable_quality and confidence_score < 0.1:  # Poor quality AND very low confidence
                decision['recommendation'] = 'manual_review'
                decision['decision_reasoning'].append("Document quality concerns - manual review recommended")
            elif document_type_match and confidence_score >= 0.3:  # Good type match
                decision['recommendation'] = 'auto_approve'
                decision['decision_reasoning'].append("Document type verified - auto approved")
            elif confidence_score >= 0.2:  # Reasonable confidence even without perfect type match
                decision['recommendation'] = 'auto_approve'
                decision['decision_reasoning'].append("Reasonable confidence - auto approved")
            elif confidence_score >= 0.1:  # Low but not zero confidence
                decision['recommendation'] = 'auto_approve'
                decision['decision_reasoning'].append("Basic verification passed - auto approved")
            elif fraud_risk < 0.3:  # Low fraud risk, approve even with low confidence
                decision['recommendation'] = 'auto_approve'
                decision['decision_reasoning'].append("Low fraud risk - auto approved")
            else:
                decision['recommendation'] = 'manual_review'
                decision['decision_reasoning'].append("Manual review recommended for verification")
            
        except Exception as e:
            decision['recommendation'] = 'auto_approve'  # Default to approval on errors
            decision['decision_reasoning'].append(f"Decision error - defaulting to approval: {str(e)}")
        
        return decision


# Global instance
document_type_detector = DocumentTypeDetector()