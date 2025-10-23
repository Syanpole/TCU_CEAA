"""
Advanced AI Algorithms for TCU-CEAA Document Verification System
Implements 6 Core AI Algorithms + Advanced Cosine Similarity Integration

✅ Core Algorithms:
1. Document Validator - OCR with Pytesseract + pattern matching
2. Cross-Document Matcher - Fuzzy string matching with Levenshtein/Jaro-Winkler
3. Grade Verifier - GWA calculation + suspicious pattern detection
4. Face Verifier - OpenCV face detection with graceful fallbacks
5. Fraud Detector - Metadata analysis + tampering detection
6. AI Verification Manager - Orchestrates all algorithms with weighted scoring

✅ Advanced Features:
- TF-IDF Vectorization using scikit-learn
- Vector Space Analysis for intelligent text comparison
- Model Data Comparison service
- Multi-field Similarity Scoring
"""

import re
import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal
import tempfile

# Core dependencies
import numpy as np
from collections import Counter

# OCR and Image Processing
try:
    import cv2
    import pytesseract
    from PIL import Image, ImageEnhance, ImageStat
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

# PDF Processing
try:
    import PyPDF2
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Machine Learning for Text Analysis
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Fuzzy String Matching
try:
    import Levenshtein
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# ALGORITHM 1: Document Validator - OCR with Pytesseract + Pattern Matching
# ============================================================================

class DocumentValidator:
    """
    Advanced OCR-based document validation with pattern matching
    Uses Pytesseract for text extraction and regex patterns for validation
    """
    
    def __init__(self):
        self.document_patterns = {
            'birth_certificate': {
                'required_patterns': [
                    r'(?i)(birth\s*certificate|certificate\s*of\s*birth)',
                    r'(?i)(civil\s*registr|registry)',
                    r'\d{2}[/-]\d{2}[/-]\d{4}',  # Date pattern
                ],
                'keywords': ['birth', 'certificate', 'registry', 'civil', 'mother', 'father', 'child'],
                'min_confidence': 0.6
            },
            'school_id': {
                'required_patterns': [
                    r'(?i)(student|school)\s*(id|identification)',
                    r'(?i)\d{2}-\d{5}',  # Student ID pattern
                ],
                'keywords': ['student', 'university', 'college', 'id', 'identification'],
                'min_confidence': 0.5
            },
            'report_card': {
                'required_patterns': [
                    r'(?i)(grade|report|transcript)',
                    r'(?i)(gwa|average|semestral)',
                    r'\d{1,2}\.\d{2}',  # Grade pattern
                ],
                'keywords': ['grade', 'subject', 'semester', 'academic', 'year', 'gwa', 'swa'],
                'min_confidence': 0.7
            }
        }
    
    def validate_document(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """
        Validate document using OCR and pattern matching
        Returns validation results with confidence score
        """
        result = {
            'is_valid': False,
            'confidence_score': 0.0,
            'extracted_text': '',
            'patterns_found': [],
            'keywords_found': [],
            'ocr_confidence': 0.0,
            'validation_details': {}
        }
        
        try:
            # Extract text using OCR
            extracted_text, ocr_confidence = self._extract_text_ocr(file_path)
            result['extracted_text'] = extracted_text
            result['ocr_confidence'] = ocr_confidence
            
            if not extracted_text or len(extracted_text.strip()) < 20:
                result['validation_details']['error'] = 'Insufficient text extracted'
                return result
            
            # Pattern matching validation
            if document_type in self.document_patterns:
                pattern_data = self.document_patterns[document_type]
                
                # Check required patterns
                patterns_found = []
                for pattern in pattern_data['required_patterns']:
                    matches = re.findall(pattern, extracted_text)
                    if matches:
                        patterns_found.append(pattern)
                
                pattern_score = len(patterns_found) / len(pattern_data['required_patterns'])
                result['patterns_found'] = patterns_found
                
                # Check keywords
                keywords_found = []
                text_lower = extracted_text.lower()
                for keyword in pattern_data['keywords']:
                    if keyword in text_lower:
                        keywords_found.append(keyword)
                
                keyword_score = len(keywords_found) / len(pattern_data['keywords'])
                result['keywords_found'] = keywords_found
                
                # Calculate final confidence
                confidence = (pattern_score * 0.5 + keyword_score * 0.3 + ocr_confidence * 0.2)
                result['confidence_score'] = confidence
                result['is_valid'] = confidence >= pattern_data['min_confidence']
                
                result['validation_details'] = {
                    'pattern_score': pattern_score,
                    'keyword_score': keyword_score,
                    'patterns_matched': len(patterns_found),
                    'keywords_matched': len(keywords_found)
                }
            
        except Exception as e:
            logger.error(f"Document validation error: {e}")
            result['validation_details']['error'] = str(e)
        
        return result
    
    def _extract_text_ocr(self, file_path: str) -> Tuple[str, float]:
        """Extract text using Pytesseract OCR with confidence scoring"""
        if not CV_AVAILABLE:
            return "", 0.0
        
        try:
            # Load and preprocess image
            if file_path.lower().endswith('.pdf'):
                # Convert PDF to image first
                image = self._pdf_to_image(file_path)
            else:
                image = cv2.imread(file_path)
            
            if image is None:
                return "", 0.0
            
            # Preprocess for better OCR
            processed = self._preprocess_for_ocr(image)
            
            # Extract text with confidence
            custom_config = r'--oem 3 --psm 6'
            ocr_data = pytesseract.image_to_data(
                processed, 
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
            
            extracted_text = ' '.join(text_parts)
            avg_confidence = np.mean(confidences) / 100.0 if confidences else 0.0
            
            return extracted_text, avg_confidence
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return "", 0.0
    
    def _preprocess_for_ocr(self, image):
        """Preprocess image for optimal OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _pdf_to_image(self, pdf_path: str):
        """Convert first page of PDF to image"""
        try:
            if not PDF_AVAILABLE:
                return None
            
            doc = fitz.open(pdf_path)
            page = doc[0]
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            
            # Convert to OpenCV format
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            doc.close()
            return image
        except Exception:
            return None


# ============================================================================
# ALGORITHM 2: Cross-Document Matcher - Fuzzy String Matching
# ============================================================================

class CrossDocumentMatcher:
    """
    Fuzzy string matching using Levenshtein distance and Jaro-Winkler similarity
    Matches information across multiple documents for consistency verification
    """
    
    def __init__(self):
        self.similarity_thresholds = {
            'name': 0.85,
            'address': 0.75,
            'date': 0.90,
            'id_number': 0.95
        }
    
    def match_documents(self, doc1_data: Dict, doc2_data: Dict) -> Dict[str, Any]:
        """
        Match data between two documents using fuzzy matching
        Returns similarity scores for each field
        """
        result = {
            'overall_match': False,
            'overall_similarity': 0.0,
            'field_matches': {},
            'discrepancies': []
        }
        
        total_similarity = 0.0
        fields_compared = 0
        
        # Compare each common field
        common_fields = set(doc1_data.keys()) & set(doc2_data.keys())
        
        for field in common_fields:
            value1 = str(doc1_data[field]).strip()
            value2 = str(doc2_data[field]).strip()
            
            if not value1 or not value2:
                continue
            
            # Calculate similarity
            levenshtein_sim = self._levenshtein_similarity(value1, value2)
            jaro_sim = self._jaro_winkler_similarity(value1, value2)
            
            # Weighted average
            similarity = (levenshtein_sim * 0.6 + jaro_sim * 0.4)
            
            result['field_matches'][field] = {
                'similarity': similarity,
                'levenshtein': levenshtein_sim,
                'jaro_winkler': jaro_sim,
                'value1': value1,
                'value2': value2,
                'matches': similarity >= self.similarity_thresholds.get(field, 0.8)
            }
            
            total_similarity += similarity
            fields_compared += 1
            
            # Track discrepancies
            threshold = self.similarity_thresholds.get(field, 0.8)
            if similarity < threshold:
                result['discrepancies'].append({
                    'field': field,
                    'similarity': similarity,
                    'value1': value1,
                    'value2': value2
                })
        
        # Calculate overall similarity
        if fields_compared > 0:
            result['overall_similarity'] = total_similarity / fields_compared
            result['overall_match'] = result['overall_similarity'] >= 0.80
        
        return result
    
    def _levenshtein_similarity(self, str1: str, str2: str) -> float:
        """Calculate Levenshtein similarity (normalized distance)"""
        if LEVENSHTEIN_AVAILABLE:
            distance = Levenshtein.distance(str1.lower(), str2.lower())
            max_len = max(len(str1), len(str2))
            return 1.0 - (distance / max_len) if max_len > 0 else 1.0
        else:
            # Fallback: simple implementation
            return self._simple_similarity(str1, str2)
    
    def _jaro_winkler_similarity(self, str1: str, str2: str) -> float:
        """Calculate Jaro-Winkler similarity"""
        if LEVENSHTEIN_AVAILABLE:
            return Levenshtein.jaro_winkler(str1.lower(), str2.lower())
        else:
            # Fallback to Levenshtein
            return self._levenshtein_similarity(str1, str2)
    
    def _simple_similarity(self, str1: str, str2: str) -> float:
        """Simple character-based similarity (fallback)"""
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        if str1_lower == str2_lower:
            return 1.0
        
        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(str1_lower, str2_lower))
        max_len = max(len(str1), len(str2))
        
        return matches / max_len if max_len > 0 else 0.0


# ============================================================================
# ALGORITHM 3: Grade Verifier - GWA Calculation + Suspicious Pattern Detection
# ============================================================================

class GradeVerifier:
    """
    Intelligent grade verification with GWA calculation and fraud detection
    Detects suspicious patterns in grade submissions
    """
    
    def __init__(self):
        self.suspicious_patterns = {
            'perfect_grades': {
                'description': 'Too many perfect scores',
                'threshold': 0.5,  # More than 50% perfect grades
                'severity': 'medium'
            },
            'uniform_grades': {
                'description': 'Grades too uniform (low variance)',
                'threshold': 2.0,  # Variance less than 2.0
                'severity': 'high'
            },
            'impossible_gwa': {
                'description': 'GWA impossible given individual grades',
                'threshold': 2.0,  # Difference more than 2 points
                'severity': 'critical'
            },
            'rounded_numbers': {
                'description': 'All grades are rounded numbers',
                'threshold': 0.8,  # More than 80% rounded
                'severity': 'low'
            }
        }
    
    def verify_grades(self, grade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify grades and detect suspicious patterns
        """
        result = {
            'is_valid': True,
            'calculated_gwa': 0.0,
            'submitted_gwa': 0.0,
            'gwa_matches': False,
            'suspicious_patterns': [],
            'fraud_probability': 0.0,
            'grade_analysis': {}
        }
        
        try:
            # Extract grade information
            grades = grade_data.get('grades', [])
            units = grade_data.get('units', [])
            submitted_gwa = float(grade_data.get('gwa', 0))
            
            if not grades or not units:
                result['is_valid'] = False
                return result
            
            # Calculate GWA
            calculated_gwa = self._calculate_gwa(grades, units)
            result['calculated_gwa'] = calculated_gwa
            result['submitted_gwa'] = submitted_gwa
            result['gwa_matches'] = abs(calculated_gwa - submitted_gwa) <= 0.5
            
            # Analyze grade distribution
            grade_analysis = self._analyze_grade_distribution(grades)
            result['grade_analysis'] = grade_analysis
            
            # Detect suspicious patterns
            suspicious = self._detect_suspicious_patterns(grades, calculated_gwa, submitted_gwa)
            result['suspicious_patterns'] = suspicious
            
            # Calculate fraud probability
            fraud_prob = self._calculate_fraud_probability(suspicious, grade_analysis)
            result['fraud_probability'] = fraud_prob
            
            result['is_valid'] = fraud_prob < 0.6 and result['gwa_matches']
            
        except Exception as e:
            logger.error(f"Grade verification error: {e}")
            result['is_valid'] = False
        
        return result
    
    def _calculate_gwa(self, grades: List[float], units: List[int]) -> float:
        """Calculate General Weighted Average"""
        if len(grades) != len(units):
            return 0.0
        
        total_grade_units = sum(g * u for g, u in zip(grades, units))
        total_units = sum(units)
        
        return round(total_grade_units / total_units, 2) if total_units > 0 else 0.0
    
    def _analyze_grade_distribution(self, grades: List[float]) -> Dict[str, Any]:
        """Analyze statistical properties of grades"""
        if not grades:
            return {}
        
        grades_array = np.array(grades)
        
        return {
            'mean': float(np.mean(grades_array)),
            'median': float(np.median(grades_array)),
            'std_dev': float(np.std(grades_array)),
            'variance': float(np.var(grades_array)),
            'min': float(np.min(grades_array)),
            'max': float(np.max(grades_array)),
            'range': float(np.max(grades_array) - np.min(grades_array))
        }
    
    def _detect_suspicious_patterns(self, grades: List[float], calculated_gwa: float, 
                                   submitted_gwa: float) -> List[Dict[str, Any]]:
        """Detect suspicious patterns in grades"""
        suspicious = []
        
        # Pattern 1: Perfect grades
        perfect_count = sum(1 for g in grades if g >= 99.0)
        perfect_ratio = perfect_count / len(grades)
        if perfect_ratio > self.suspicious_patterns['perfect_grades']['threshold']:
            suspicious.append({
                'pattern': 'perfect_grades',
                'description': self.suspicious_patterns['perfect_grades']['description'],
                'severity': self.suspicious_patterns['perfect_grades']['severity'],
                'details': f'{perfect_ratio:.1%} of grades are perfect'
            })
        
        # Pattern 2: Uniform grades (low variance)
        variance = np.var(grades)
        if variance < self.suspicious_patterns['uniform_grades']['threshold']:
            suspicious.append({
                'pattern': 'uniform_grades',
                'description': self.suspicious_patterns['uniform_grades']['description'],
                'severity': self.suspicious_patterns['uniform_grades']['severity'],
                'details': f'Grade variance is only {variance:.2f}'
            })
        
        # Pattern 3: Impossible GWA
        gwa_diff = abs(calculated_gwa - submitted_gwa)
        if gwa_diff > self.suspicious_patterns['impossible_gwa']['threshold']:
            suspicious.append({
                'pattern': 'impossible_gwa',
                'description': self.suspicious_patterns['impossible_gwa']['description'],
                'severity': self.suspicious_patterns['impossible_gwa']['severity'],
                'details': f'GWA differs by {gwa_diff:.2f} points'
            })
        
        # Pattern 4: All rounded numbers
        rounded_count = sum(1 for g in grades if g == round(g))
        rounded_ratio = rounded_count / len(grades)
        if rounded_ratio > self.suspicious_patterns['rounded_numbers']['threshold']:
            suspicious.append({
                'pattern': 'rounded_numbers',
                'description': self.suspicious_patterns['rounded_numbers']['description'],
                'severity': self.suspicious_patterns['rounded_numbers']['severity'],
                'details': f'{rounded_ratio:.1%} of grades are rounded'
            })
        
        return suspicious
    
    def _calculate_fraud_probability(self, suspicious_patterns: List[Dict], 
                                    grade_analysis: Dict) -> float:
        """Calculate overall fraud probability"""
        severity_weights = {
            'critical': 0.4,
            'high': 0.3,
            'medium': 0.2,
            'low': 0.1
        }
        
        fraud_score = 0.0
        for pattern in suspicious_patterns:
            severity = pattern['severity']
            fraud_score += severity_weights.get(severity, 0.1)
        
        return min(1.0, fraud_score)


# ============================================================================
# ALGORITHM 4: Face Verifier - OpenCV Face Detection
# ============================================================================

class FaceVerifier:
    """
    Face detection and verification using OpenCV
    With graceful fallbacks for missing dependencies
    """
    
    def __init__(self):
        self.face_cascade = None
        if CV_AVAILABLE:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception as e:
                logger.warning(f"Face cascade loading failed: {e}")
    
    def verify_face(self, image_path: str) -> Dict[str, Any]:
        """
        Detect and verify face in document image
        """
        result = {
            'has_face': False,
            'face_count': 0,
            'faces_detected': [],
            'confidence': 0.0,
            'quality_score': 0.0
        }
        
        if not CV_AVAILABLE or self.face_cascade is None:
            result['error'] = 'Face detection not available'
            return result
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                result['error'] = 'Could not load image'
                return result
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            result['face_count'] = len(faces)
            result['has_face'] = len(faces) > 0
            
            # Analyze detected faces
            for (x, y, w, h) in faces:
                face_data = {
                    'position': {'x': int(x), 'y': int(y)},
                    'size': {'width': int(w), 'height': int(h)},
                    'area': int(w * h)
                }
                
                # Extract face region for quality analysis
                face_region = gray[y:y+h, x:x+w]
                quality = self._assess_face_quality(face_region)
                face_data['quality'] = quality
                
                result['faces_detected'].append(face_data)
            
            # Calculate overall confidence
            if result['has_face']:
                avg_quality = np.mean([f['quality'] for f in result['faces_detected']])
                result['quality_score'] = avg_quality
                result['confidence'] = min(1.0, avg_quality * 1.2)
            
        except Exception as e:
            logger.error(f"Face verification error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _assess_face_quality(self, face_region) -> float:
        """Assess quality of detected face"""
        try:
            # Check brightness
            brightness = np.mean(face_region)
            brightness_score = 1.0 if 60 <= brightness <= 200 else 0.5
            
            # Check contrast
            contrast = np.std(face_region)
            contrast_score = 1.0 if contrast > 30 else 0.5
            
            # Check sharpness (using Laplacian variance)
            laplacian_var = cv2.Laplacian(face_region, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 500.0)
            
            # Weighted average
            quality = (brightness_score * 0.3 + contrast_score * 0.3 + sharpness_score * 0.4)
            return quality
            
        except Exception:
            return 0.5


# ============================================================================
# ALGORITHM 5: Fraud Detector - Metadata Analysis + Tampering Detection
# ============================================================================

class FraudDetector:
    """
    Advanced fraud detection using metadata analysis and tampering detection
    """
    
    def __init__(self):
        self.fraud_indicators = {
            'metadata_missing': 0.3,
            'recent_modification': 0.4,
            'suspicious_software': 0.5,
            'image_manipulation': 0.6,
            'inconsistent_metadata': 0.7
        }
    
    def detect_fraud(self, file_path: str) -> Dict[str, Any]:
        """
        Comprehensive fraud detection analysis
        """
        result = {
            'is_likely_fraud': False,
            'fraud_probability': 0.0,
            'fraud_indicators': [],
            'metadata_analysis': {},
            'tampering_analysis': {}
        }
        
        try:
            # Analyze file metadata
            metadata_analysis = self._analyze_metadata(file_path)
            result['metadata_analysis'] = metadata_analysis
            
            # Detect image tampering
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                tampering_analysis = self._detect_image_tampering(file_path)
                result['tampering_analysis'] = tampering_analysis
            
            # Calculate fraud probability
            fraud_score = 0.0
            indicators = []
            
            # Check metadata indicators
            if metadata_analysis.get('metadata_missing'):
                indicators.append('Missing or incomplete metadata')
                fraud_score += self.fraud_indicators['metadata_missing']
            
            if metadata_analysis.get('recent_modification'):
                indicators.append('Recently modified file')
                fraud_score += self.fraud_indicators['recent_modification']
            
            if metadata_analysis.get('suspicious_software'):
                indicators.append('Created with image editing software')
                fraud_score += self.fraud_indicators['suspicious_software']
            
            # Check tampering indicators
            if result['tampering_analysis'].get('likely_tampered'):
                indicators.append('Evidence of image manipulation')
                fraud_score += self.fraud_indicators['image_manipulation']
            
            result['fraud_indicators'] = indicators
            result['fraud_probability'] = min(1.0, fraud_score)
            result['is_likely_fraud'] = fraud_score >= 0.6
            
        except Exception as e:
            logger.error(f"Fraud detection error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _analyze_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyze file metadata for suspicious patterns"""
        metadata = {
            'metadata_missing': False,
            'recent_modification': False,
            'suspicious_software': False,
            'file_details': {}
        }
        
        try:
            # Get basic file stats
            stats = os.stat(file_path)
            creation_time = datetime.fromtimestamp(stats.st_ctime)
            modified_time = datetime.fromtimestamp(stats.st_mtime)
            
            metadata['file_details'] = {
                'size': stats.st_size,
                'created': creation_time.isoformat(),
                'modified': modified_time.isoformat()
            }
            
            # Check if recently modified
            time_diff = (datetime.now() - modified_time).total_seconds()
            metadata['recent_modification'] = time_diff < 3600  # Modified in last hour
            
            # Try to extract EXIF data for images
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                from PIL import Image
                from PIL.ExifTags import TAGS
                
                img = Image.open(file_path)
                exif_data = img._getexif()
                
                if exif_data:
                    exif_info = {}
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        exif_info[tag_name] = str(value)
                    
                    metadata['file_details']['exif'] = exif_info
                    
                    # Check for editing software
                    software = exif_info.get('Software', '').lower()
                    suspicious_software = ['photoshop', 'gimp', 'paint.net', 'editor']
                    metadata['suspicious_software'] = any(s in software for s in suspicious_software)
                else:
                    metadata['metadata_missing'] = True
            
        except Exception as e:
            logger.warning(f"Metadata analysis error: {e}")
            metadata['metadata_missing'] = True
        
        return metadata
    
    def _detect_image_tampering(self, image_path: str) -> Dict[str, Any]:
        """Detect image tampering using error level analysis"""
        tampering = {
            'likely_tampered': False,
            'tampering_score': 0.0,
            'analysis_details': {}
        }
        
        if not CV_AVAILABLE:
            return tampering
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return tampering
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect edges (tampered areas often have different edge characteristics)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Analyze noise patterns
            noise = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Check for copy-paste patterns (simplified)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_uniformity = np.std(hist)
            
            tampering['analysis_details'] = {
                'edge_density': float(edge_density),
                'noise_level': float(noise),
                'histogram_uniformity': float(hist_uniformity)
            }
            
            # Calculate tampering score
            score = 0.0
            if edge_density > 0.3:  # Unusually high edges
                score += 0.3
            if noise < 50:  # Unusually smooth (over-processed)
                score += 0.3
            if hist_uniformity < 100:  # Uniform histogram (suspicious)
                score += 0.4
            
            tampering['tampering_score'] = score
            tampering['likely_tampered'] = score >= 0.5
            
        except Exception as e:
            logger.error(f"Tampering detection error: {e}")
        
        return tampering


# ============================================================================
# ALGORITHM 6: AI Verification Manager - Orchestrates All Algorithms
# ============================================================================

class AIVerificationManager:
    """
    Master orchestrator that combines all AI algorithms with weighted scoring
    """
    
    def __init__(self):
        self.document_validator = DocumentValidator()
        self.cross_matcher = CrossDocumentMatcher()
        self.grade_verifier = GradeVerifier()
        self.face_verifier = FaceVerifier()
        self.fraud_detector = FraudDetector()
        
        # Algorithm weights
        self.weights = {
            'document_validation': 0.25,
            'cross_matching': 0.20,
            'grade_verification': 0.20,
            'face_verification': 0.15,
            'fraud_detection': 0.20
        }
    
    def comprehensive_verification(self, file_path: str, document_type: str, 
                                  user_data: Dict = None, grade_data: Dict = None) -> Dict[str, Any]:
        """
        Run all verification algorithms and produce weighted final score
        """
        result = {
            'overall_confidence': 0.0,
            'is_verified': False,
            'recommendation': 'manual_review',
            'algorithm_results': {},
            'weighted_scores': {}
        }
        
        try:
            total_score = 0.0
            
            # 1. Document Validation
            doc_validation = self.document_validator.validate_document(file_path, document_type)
            result['algorithm_results']['document_validation'] = doc_validation
            validation_score = doc_validation.get('confidence_score', 0.0)
            result['weighted_scores']['document_validation'] = validation_score * self.weights['document_validation']
            total_score += result['weighted_scores']['document_validation']
            
            # 2. Cross-Document Matching (if user data available)
            if user_data and doc_validation.get('extracted_text'):
                # Extract data from document
                extracted_data = self._extract_structured_data(doc_validation['extracted_text'])
                cross_match = self.cross_matcher.match_documents(user_data, extracted_data)
                result['algorithm_results']['cross_matching'] = cross_match
                match_score = cross_match.get('overall_similarity', 0.0)
                result['weighted_scores']['cross_matching'] = match_score * self.weights['cross_matching']
                total_score += result['weighted_scores']['cross_matching']
            
            # 3. Grade Verification (if grade data available)
            if grade_data:
                grade_verification = self.grade_verifier.verify_grades(grade_data)
                result['algorithm_results']['grade_verification'] = grade_verification
                grade_score = 1.0 - grade_verification.get('fraud_probability', 1.0)
                result['weighted_scores']['grade_verification'] = grade_score * self.weights['grade_verification']
                total_score += result['weighted_scores']['grade_verification']
            
            # 4. Face Verification (for ID documents)
            if document_type in ['school_id', 'parents_id']:
                face_verification = self.face_verifier.verify_face(file_path)
                result['algorithm_results']['face_verification'] = face_verification
                face_score = face_verification.get('confidence', 0.0)
                result['weighted_scores']['face_verification'] = face_score * self.weights['face_verification']
                total_score += result['weighted_scores']['face_verification']
            
            # 5. Fraud Detection
            fraud_detection = self.fraud_detector.detect_fraud(file_path)
            result['algorithm_results']['fraud_detection'] = fraud_detection
            fraud_score = 1.0 - fraud_detection.get('fraud_probability', 1.0)
            result['weighted_scores']['fraud_detection'] = fraud_score * self.weights['fraud_detection']
            total_score += result['weighted_scores']['fraud_detection']
            
            # Calculate final confidence
            result['overall_confidence'] = total_score
            
            # Make recommendation
            if fraud_detection.get('is_likely_fraud'):
                result['recommendation'] = 'reject'
                result['is_verified'] = False
            elif total_score >= 0.80:
                result['recommendation'] = 'auto_approve'
                result['is_verified'] = True
            elif total_score >= 0.60:
                result['recommendation'] = 'manual_review'
                result['is_verified'] = False
            else:
                result['recommendation'] = 'reject'
                result['is_verified'] = False
            
        except Exception as e:
            logger.error(f"Comprehensive verification error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from text for cross-matching"""
        data = {}
        
        # Extract name
        name_pattern = r'name[:\s]*([a-zA-Z\s,\.]+)'
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            data['name'] = name_match.group(1).strip()
        
        # Extract date
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        date_match = re.search(date_pattern, text)
        if date_match:
            data['date'] = date_match.group(1)
        
        # Extract ID number
        id_pattern = r'\b(\d{2}-\d{5})\b'
        id_match = re.search(id_pattern, text)
        if id_match:
            data['id_number'] = id_match.group(1)
        
        return data


# ============================================================================
# ADVANCED FEATURE: TF-IDF Cosine Similarity Analyzer
# ============================================================================

class CosineSimilarityAnalyzer:
    """
    Advanced text comparison using TF-IDF vectorization and cosine similarity
    For intelligent document content comparison
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        ) if ML_AVAILABLE else None
    
    def compare_documents(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Compare two documents using TF-IDF and cosine similarity
        """
        result = {
            'similarity_score': 0.0,
            'is_similar': False,
            'vector_analysis': {}
        }
        
        if not ML_AVAILABLE or not self.vectorizer:
            result['error'] = 'ML libraries not available'
            return result
        
        try:
            # Create TF-IDF vectors
            documents = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            result['similarity_score'] = float(similarity)
            result['is_similar'] = similarity >= 0.7
            
            # Vector analysis
            feature_names = self.vectorizer.get_feature_names_out()
            doc1_vector = tfidf_matrix[0].toarray()[0]
            doc2_vector = tfidf_matrix[1].toarray()[0]
            
            # Top features for each document
            top_indices_1 = doc1_vector.argsort()[-10:][::-1]
            top_indices_2 = doc2_vector.argsort()[-10:][::-1]
            
            result['vector_analysis'] = {
                'top_features_doc1': [feature_names[i] for i in top_indices_1 if doc1_vector[i] > 0],
                'top_features_doc2': [feature_names[i] for i in top_indices_2 if doc2_vector[i] > 0],
                'vector_size': len(feature_names)
            }
            
        except Exception as e:
            logger.error(f"Cosine similarity error: {e}")
            result['error'] = str(e)
        
        return result
    
    def compare_multi_field(self, user_profile: Dict, document_data: Dict) -> Dict[str, Any]:
        """
        Multi-field similarity scoring for comprehensive comparison
        """
        result = {
            'overall_similarity': 0.0,
            'field_similarities': {},
            'matching_fields': [],
            'discrepancies': []
        }
        
        try:
            total_similarity = 0.0
            fields_compared = 0
            
            # Compare each field
            for field in ['name', 'address', 'guardian', 'full_text']:
                if field in user_profile and field in document_data:
                    text1 = str(user_profile[field])
                    text2 = str(document_data[field])
                    
                    if text1 and text2:
                        comparison = self.compare_documents(text1, text2)
                        similarity = comparison.get('similarity_score', 0.0)
                        
                        result['field_similarities'][field] = similarity
                        total_similarity += similarity
                        fields_compared += 1
                        
                        if similarity >= 0.7:
                            result['matching_fields'].append(field)
                        else:
                            result['discrepancies'].append({
                                'field': field,
                                'similarity': similarity,
                                'user_value': text1[:50],
                                'document_value': text2[:50]
                            })
            
            # Calculate overall similarity
            if fields_compared > 0:
                result['overall_similarity'] = total_similarity / fields_compared
            
        except Exception as e:
            logger.error(f"Multi-field comparison error: {e}")
            result['error'] = str(e)
        
        return result


# Import the AI Generated Detector
from .ai_generated_detector import AIGeneratedDetector

# Export main classes
__all__ = [
    'DocumentValidator',
    'CrossDocumentMatcher',
    'GradeVerifier',
    'FaceVerifier',
    'FraudDetector',
    'AIVerificationManager',
    'CosineSimilarityAnalyzer',
    'AIGeneratedDetector'
]
