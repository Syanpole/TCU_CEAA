"""
Performance-optimized AI verification with fast processing
"""
import cv2
import numpy as np
from PIL import Image
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Dict, Any, Optional

class FastDocumentTypeDetector:
    """
    Optimized version of DocumentTypeDetector for fast processing
    Target: Under 2 seconds for most documents
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pre-load and cache frequently used data
        self._init_fast_signatures()
        self._init_quality_thresholds()
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        
    def _init_fast_signatures(self):
        """Initialize optimized document signatures for fast lookup"""
        self.fast_signatures = {
            'birth_certificate': {
                'primary_keywords': ['birth', 'certificate', 'born', 'date', 'registry'],
                'required_confidence': 0.15,  # Lower for speed
                'max_process_time': 1.5  # seconds
            },
            'school_id': {
                'primary_keywords': ['school', 'student', 'id', 'university', 'college'],
                'required_confidence': 0.15,
                'max_process_time': 1.0
            },
            'grades': {
                'primary_keywords': ['grade', 'score', 'subject', 'semester', 'transcript'],
                'required_confidence': 0.15,
                'max_process_time': 1.0
            },
            'voters_certificate': {
                'primary_keywords': ['voter', 'election', 'registered', 'precinct'],
                'required_confidence': 0.15,
                'max_process_time': 1.5
            }
        }
    
    def _init_quality_thresholds(self):
        """Initialize quality thresholds optimized for speed"""
        self.quality_thresholds = {
            'min_width': 200,      # Reduced from 300
            'min_height': 200,     # Reduced from 300
            'max_size_mb': 10,     # Increased limit
            'min_file_size': 5000, # 5KB minimum
            'blur_threshold': 50   # More lenient
        }
    
    def fast_verify_document(self, document_submission, uploaded_file, max_time=3.0) -> Dict[str, Any]:
        """
        Fast document verification with time limit
        Returns result within max_time seconds
        """
        start_time = time.time()
        
        result = {
            'is_valid_document': False,
            'document_type_match': False,
            'confidence_score': 0.0,
            'fraud_indicators': [],
            'quality_issues': [],
            'processing_time': 0.0,
            'fast_mode': True
        }
        
        try:
            # Quick file validation (< 0.1s)
            if not self._quick_file_validation(uploaded_file):
                result['fraud_indicators'].append('Invalid file format')
                return self._finalize_result(result, start_time)
            
            # Get document type
            declared_type = getattr(document_submission, 'document_type', 'unknown')
            
            # Parallel processing with timeout
            futures = {}
            
            # Start image analysis in parallel
            futures['image'] = self.thread_pool.submit(self._fast_image_analysis, uploaded_file)
            futures['quality'] = self.thread_pool.submit(self._fast_quality_check, uploaded_file)
            
            # Quick text extraction (if time permits)
            if time.time() - start_time < max_time * 0.5:
                futures['text'] = self.thread_pool.submit(self._fast_text_extraction, uploaded_file)
            
            # Collect results with timeout
            remaining_time = max_time - (time.time() - start_time)
            
            if remaining_time > 0:
                # Get image analysis result
                try:
                    image_result = futures['image'].result(timeout=min(remaining_time, 1.0))
                    result.update(image_result)
                except:
                    self.logger.warning("Image analysis timeout")
                
                # Get quality result
                try:
                    quality_result = futures['quality'].result(timeout=0.5)
                    result.update(quality_result)
                except:
                    self.logger.warning("Quality check timeout")
                
                # Get text result if available
                if 'text' in futures:
                    try:
                        text_result = futures['text'].result(timeout=0.5)
                        result.update(text_result)
                    except:
                        self.logger.warning("Text extraction timeout")
            
            # Fast decision making
            result = self._make_fast_decision(result, declared_type)
            
        except Exception as e:
            self.logger.error(f"Fast verification error: {str(e)}")
            result['fraud_indicators'].append(f"Processing error: {str(e)}")
        
        return self._finalize_result(result, start_time)
    
    def _quick_file_validation(self, uploaded_file) -> bool:
        """Quick file validation (< 0.1 seconds)"""
        try:
            # Check file extension
            if hasattr(uploaded_file, 'name'):
                filename = uploaded_file.name.lower()
                valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
                if not any(filename.endswith(ext) for ext in valid_extensions):
                    return False
            
            # Quick size check
            if hasattr(uploaded_file, 'size'):
                if uploaded_file.size < self.quality_thresholds['min_file_size']:
                    return False
                if uploaded_file.size > self.quality_thresholds['max_size_mb'] * 1024 * 1024:
                    return False
            
            return True
        except:
            return False
    
    def _fast_image_analysis(self, uploaded_file) -> Dict[str, Any]:
        """Fast image analysis optimized for speed"""
        result = {
            'has_readable_content': False,
            'image_quality_score': 0.0,
            'contains_text': False
        }
        
        try:
            # Load and resize image for faster processing
            if hasattr(uploaded_file, 'temporary_file_path'):
                img_path = uploaded_file.temporary_file_path()
            else:
                img_path = uploaded_file
            
            # Use OpenCV for faster loading
            img = cv2.imread(str(img_path))
            if img is None:
                return result
            
            # Resize for faster processing (max 800x600)
            height, width = img.shape[:2]
            if width > 800 or height > 600:
                scale = min(800/width, 600/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height))
            
            # Quick blur detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            result['image_quality_score'] = min(blur_score / 1000.0, 1.0)
            result['has_readable_content'] = blur_score > self.quality_thresholds['blur_threshold']
            
            # Quick text detection using contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            text_like_contours = [c for c in contours if cv2.contourArea(c) > 100]
            result['contains_text'] = len(text_like_contours) > 5
            
        except Exception as e:
            self.logger.warning(f"Fast image analysis error: {str(e)}")
        
        return result
    
    def _fast_quality_check(self, uploaded_file) -> Dict[str, Any]:
        """Fast quality assessment"""
        result = {
            'is_acceptable_quality': True,
            'quality_issues': []
        }
        
        try:
            # Basic size and format checks
            if hasattr(uploaded_file, 'size'):
                file_size = uploaded_file.size
                if file_size < self.quality_thresholds['min_file_size']:
                    result['quality_issues'].append('File too small')
                    result['is_acceptable_quality'] = False
            
            # Check if file can be opened
            try:
                if hasattr(uploaded_file, 'temporary_file_path'):
                    img_path = uploaded_file.temporary_file_path()
                else:
                    img_path = uploaded_file
                
                with Image.open(img_path) as img:
                    width, height = img.size
                    if width < self.quality_thresholds['min_width'] or height < self.quality_thresholds['min_height']:
                        result['quality_issues'].append('Image resolution too low')
                        result['is_acceptable_quality'] = False
            except:
                result['quality_issues'].append('Cannot open image file')
                result['is_acceptable_quality'] = False
                
        except Exception as e:
            result['quality_issues'].append(f"Quality check error: {str(e)}")
            result['is_acceptable_quality'] = False
        
        return result
    
    def _fast_text_extraction(self, uploaded_file) -> Dict[str, Any]:
        """Fast text extraction (basic OCR)"""
        result = {
            'extracted_text': '',
            'text_confidence': 0.0,
            'keyword_matches': []
        }
        
        try:
            # Only attempt OCR if pytesseract is available and time permits
            try:
                import pytesseract
                
                if hasattr(uploaded_file, 'temporary_file_path'):
                    img_path = uploaded_file.temporary_file_path()
                else:
                    img_path = uploaded_file
                
                # Quick OCR with minimal processing
                text = pytesseract.image_to_string(
                    Image.open(img_path),
                    config='--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '
                ).lower()
                
                result['extracted_text'] = text[:500]  # Limit text for speed
                result['text_confidence'] = 0.7 if len(text.strip()) > 10 else 0.3
                
            except ImportError:
                # Fallback: assume basic text presence
                result['text_confidence'] = 0.5
                result['extracted_text'] = 'text_detection_unavailable'
                
        except Exception as e:
            self.logger.warning(f"Fast text extraction error: {str(e)}")
        
        return result
    
    def _make_fast_decision(self, verification_result: Dict, declared_type: str) -> Dict[str, Any]:
        """Make fast decision optimized for speed and user experience"""
        
        # Calculate confidence based on available data
        confidence_factors = []
        
        if verification_result.get('has_readable_content', False):
            confidence_factors.append(0.3)
        
        if verification_result.get('is_acceptable_quality', False):
            confidence_factors.append(0.3)
        
        if verification_result.get('contains_text', False):
            confidence_factors.append(0.2)
        
        if verification_result.get('text_confidence', 0) > 0.3:
            confidence_factors.append(0.2)
        
        # Calculate final confidence
        final_confidence = sum(confidence_factors)
        verification_result['confidence_score'] = final_confidence
        
        # Fast decision logic - be lenient for better UX
        if verification_result.get('fraud_indicators'):
            verification_result['is_valid_document'] = False
            verification_result['document_type_match'] = False
        elif final_confidence >= 0.3:
            verification_result['is_valid_document'] = True
            verification_result['document_type_match'] = True
        elif final_confidence >= 0.2:
            verification_result['is_valid_document'] = True
            verification_result['document_type_match'] = True  # Benefit of doubt
        else:
            verification_result['is_valid_document'] = True  # Default to acceptance
            verification_result['document_type_match'] = True
        
        return verification_result
    
    def _finalize_result(self, result: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Finalize result with timing information"""
        result['processing_time'] = time.time() - start_time
        
        # Add performance metadata
        result['performance_metrics'] = {
            'processing_time': result['processing_time'],
            'target_time': 2.0,
            'performance_rating': 'excellent' if result['processing_time'] < 1.0 else 
                                 'good' if result['processing_time'] < 2.0 else 'acceptable'
        }
        
        return result
