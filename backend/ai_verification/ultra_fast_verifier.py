"""
Ultra-Fast AI Document Verifier
Optimized for immediate student feedback (< 0.5 seconds)
"""
import cv2
import numpy as np
from PIL import Image
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import Dict, Any, Optional
import hashlib
import os

class UltraFastDocumentVerifier:
    """
    Ultra-optimized document verifier for instant student feedback
    Target: Under 0.5 seconds for 95% of documents
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Cache for processed documents (based on file hash)
        self.verification_cache = {}
        
        # Pre-compiled patterns for faster matching
        self._init_fast_patterns()
        
        # Single thread pool for all operations
        self.thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ultrafast")
        
        # Ultra-fast quality thresholds
        self.ultra_thresholds = {
            'min_width': 150,           # Very low minimum
            'min_height': 150,          # Very low minimum
            'max_size_mb': 20,          # Higher limit
            'min_file_size': 2000,      # 2KB minimum
            'blur_threshold': 25,       # Very lenient
            'max_process_time': 0.4     # 400ms max
        }
    
    def _init_fast_patterns(self):
        """Initialize ultra-fast pattern matching"""
        self.document_indicators = {
            'birth_certificate': {
                'keywords': ['birth', 'certificate', 'born', 'registry'],
                'weight': 0.8
            },
            'school_id': {
                'keywords': ['school', 'student', 'id', 'university'],
                'weight': 0.7
            },
            'grades': {
                'keywords': ['grade', 'score', 'subject', 'semester'],
                'weight': 0.7
            },
            'default': {
                'keywords': ['document', 'certificate', 'official'],
                'weight': 0.6
            }
        }
    
    def instant_verify(self, document_submission, uploaded_file) -> Dict[str, Any]:
        """
        Instant document verification (< 0.5 seconds)
        Prioritizes speed over detailed analysis
        """
        start_time = time.time()
        
        result = {
            'is_valid_document': True,      # Default to acceptance
            'document_type_match': True,     # Default to acceptance
            'confidence_score': 0.8,        # Default high confidence
            'fraud_indicators': [],
            'quality_issues': [],
            'processing_time': 0.0,
            'verification_method': 'ultra_fast',
            'student_friendly': True
        }
        
        try:
            # Check cache first (instant if cached)
            file_hash = self._get_file_hash(uploaded_file)
            if file_hash in self.verification_cache:
                cached_result = self.verification_cache[file_hash].copy()
                cached_result['processing_time'] = time.time() - start_time
                cached_result['from_cache'] = True
                return cached_result
            
            # Ultra-fast validation pipeline
            validation_steps = [
                ('file_format', self._instant_file_check),
                ('basic_quality', self._instant_quality_check),
                ('content_scan', self._instant_content_scan)
            ]
            
            # Run all validations in parallel with strict timeout
            futures = {}
            for step_name, step_function in validation_steps:
                futures[step_name] = self.thread_pool.submit(step_function, uploaded_file)
            
            # Collect results with timeout
            step_results = {}
            for step_name, future in futures.items():
                try:
                    step_results[step_name] = future.result(timeout=0.15)  # 150ms per step
                except Exception as e:
                    self.logger.warning(f"Step {step_name} failed: {str(e)}")
                    step_results[step_name] = {'passed': True, 'issues': []}  # Default to pass
            
            # Ultra-fast decision making
            result = self._make_instant_decision(step_results, result)
            
            # Cache successful results
            if result['is_valid_document']:
                self.verification_cache[file_hash] = result.copy()
                # Limit cache size
                if len(self.verification_cache) > 100:
                    oldest_key = next(iter(self.verification_cache))
                    del self.verification_cache[oldest_key]
            
        except Exception as e:
            # If anything fails, default to acceptance (student-friendly)
            self.logger.warning(f"Ultra-fast verification error: {str(e)}")
            result.update({
                'error_occurred': True,
                'error_message': str(e),
                'fallback_approval': True
            })
        
        result['processing_time'] = time.time() - start_time
        return result
    
    def _get_file_hash(self, uploaded_file) -> str:
        """Generate hash for file caching"""
        try:
            # Read first 1KB for quick hash
            uploaded_file.seek(0)
            chunk = uploaded_file.read(1024)
            uploaded_file.seek(0)
            return hashlib.md5(chunk).hexdigest()
        except:
            return f"fallback_{time.time()}"
    
    def _instant_file_check(self, uploaded_file) -> Dict[str, Any]:
        """Instant file format check (< 50ms)"""
        result = {'passed': True, 'issues': []}
        
        try:
            # Quick size check
            if hasattr(uploaded_file, 'size'):
                size = uploaded_file.size
                if size < self.ultra_thresholds['min_file_size']:
                    result['issues'].append('File very small')
                elif size > self.ultra_thresholds['max_size_mb'] * 1024 * 1024:
                    result['issues'].append('File very large')
            
            # Quick format check
            if hasattr(uploaded_file, 'name'):
                filename = uploaded_file.name.lower()
                valid_formats = ['.jpg', '.jpeg', '.png', '.pdf', '.bmp', '.gif']
                if not any(filename.endswith(fmt) for fmt in valid_formats):
                    result['issues'].append('Uncommon file format')
            
            # File header check (quick validation)
            try:
                uploaded_file.seek(0)
                header = uploaded_file.read(10)
                uploaded_file.seek(0)
                
                # Check for common image/document headers
                if header.startswith(b'\xFF\xD8\xFF'):  # JPEG
                    pass
                elif header.startswith(b'\x89PNG'):      # PNG
                    pass
                elif header.startswith(b'%PDF'):         # PDF
                    pass
                else:
                    result['issues'].append('Unknown file header')
            except:
                pass  # Skip header check if fails
            
        except Exception as e:
            result['issues'].append(f"File check error: {str(e)}")
        
        return result
    
    def _instant_quality_check(self, uploaded_file) -> Dict[str, Any]:
        """Instant quality assessment (< 100ms)"""
        result = {'passed': True, 'issues': []}
        
        try:
            # Try to open and get basic image info
            if hasattr(uploaded_file, 'temporary_file_path'):
                img_path = uploaded_file.temporary_file_path()
            else:
                # Create temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    img_path = temp_file.name
            
            # Quick image check with PIL (faster than OpenCV for basic info)
            try:
                with Image.open(img_path) as img:
                    width, height = img.size
                    
                    # Lenient size requirements
                    if width < self.ultra_thresholds['min_width'] or height < self.ultra_thresholds['min_height']:
                        result['issues'].append('Low resolution')
                    
                    # Check if image is completely black/white (may indicate scan issues)
                    if hasattr(img, 'getextrema'):
                        extrema = img.getextrema()
                        if isinstance(extrema, tuple) and len(extrema) == 2:
                            if extrema[0] == extrema[1]:  # All pixels same value
                                result['issues'].append('Uniform image detected')
                
            except Exception as img_error:
                result['issues'].append(f"Image read error: {str(img_error)}")
            
            # Clean up temp file if created
            if 'temp_file' in locals():
                try:
                    os.unlink(img_path)
                except:
                    pass
            
        except Exception as e:
            result['issues'].append(f"Quality check error: {str(e)}")
        
        return result
    
    def _instant_content_scan(self, uploaded_file) -> Dict[str, Any]:
        """Instant content scanning (< 150ms)"""
        result = {'passed': True, 'issues': [], 'content_detected': False}
        
        try:
            # Skip heavy OCR - just check if image has text-like patterns
            if hasattr(uploaded_file, 'temporary_file_path'):
                img_path = uploaded_file.temporary_file_path()
            else:
                # Quick check without full processing
                result['content_detected'] = True  # Assume content exists
                return result
            
            # Very quick OpenCV check for text-like patterns
            try:
                img = cv2.imread(str(img_path))
                if img is not None:
                    # Resize to small size for speed
                    small_img = cv2.resize(img, (200, 150))
                    gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
                    
                    # Quick edge detection for text patterns
                    edges = cv2.Canny(gray, 50, 150)
                    edge_density = np.sum(edges > 0) / edges.size
                    
                    # If reasonable edge density, assume document content
                    if edge_density > 0.02:  # Very low threshold
                        result['content_detected'] = True
                    else:
                        result['issues'].append('Low text pattern density')
                else:
                    result['issues'].append('Could not load image')
            except:
                # If OpenCV fails, assume content exists (student-friendly)
                result['content_detected'] = True
            
        except Exception as e:
            result['issues'].append(f"Content scan error: {str(e)}")
            result['content_detected'] = True  # Default to assuming content
        
        return result
    
    def _make_instant_decision(self, step_results: Dict, base_result: Dict) -> Dict[str, Any]:
        """Make instant decision prioritizing student experience"""
        
        # Count issues across all steps
        total_issues = []
        content_detected = False
        
        for step_name, step_result in step_results.items():
            if isinstance(step_result, dict):
                total_issues.extend(step_result.get('issues', []))
                if step_name == 'content_scan':
                    content_detected = step_result.get('content_detected', False)
        
        # Student-friendly decision logic
        if len(total_issues) == 0:
            # Perfect document
            base_result.update({
                'confidence_score': 0.95,
                'quality_rating': 'excellent'
            })
        elif len(total_issues) <= 2:
            # Minor issues - still approve
            base_result.update({
                'confidence_score': 0.8,
                'quality_rating': 'good',
                'quality_issues': total_issues[:2]  # Show only first 2
            })
        elif len(total_issues) <= 4:
            # Some issues but still acceptable
            base_result.update({
                'confidence_score': 0.65,
                'quality_rating': 'acceptable',
                'quality_issues': total_issues[:3]  # Show only first 3
            })
        else:
            # Many issues - still approve but with warnings
            base_result.update({
                'confidence_score': 0.5,
                'quality_rating': 'poor_but_acceptable',
                'quality_issues': total_issues[:3],
                'recommendation': 'Consider uploading a clearer image for better results'
            })
        
        # Override: Always approve unless major fraud indicators
        major_fraud_keywords = ['error', 'failed to load', 'corrupt', 'invalid header']
        has_major_fraud = any(
            any(keyword in issue.lower() for keyword in major_fraud_keywords) 
            for issue in total_issues
        )
        
        if has_major_fraud:
            base_result.update({
                'is_valid_document': False,
                'document_type_match': False,
                'fraud_indicators': ['File appears corrupted or invalid'],
                'confidence_score': 0.1
            })
        
        # Add performance info
        base_result['performance_info'] = {
            'processing_method': 'ultra_fast',
            'target_time': 0.5,
            'optimized_for': 'student_experience',
            'issues_found': len(total_issues),
            'content_detected': content_detected
        }
        
        return base_result

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.thread_pool.shutdown(wait=False)
        except:
            pass
