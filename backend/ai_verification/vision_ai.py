"""
🎯 ADVANCED VISION AI SYSTEM
Like ChatGPT Vision - Understands document structure, layout, and context
Inspired by GPT-4V capabilities for document analysis
"""

import cv2
import numpy as np
from PIL import Image
import logging
import re
from typing import Dict, List, Tuple, Any
import json

logger = logging.getLogger(__name__)

class VisionAI:
    """
    Advanced Computer Vision AI for document analysis
    Mimics ChatGPT's vision capabilities for document understanding
    """
    
    def __init__(self):
        self.document_templates = self._load_document_templates()
        
    def _load_document_templates(self) -> Dict:
        """Load document templates and patterns"""
        return {
            'birth_certificate': {
                'required_sections': [
                    'certificate of live birth',
                    'republic of the philippines',
                    'civil registrar',
                    'name',
                    'date of birth',
                    'place of birth'
                ],
                'header_patterns': [
                    'certificate of live birth',
                    'office of the civil registrar',
                    'republic of the philippines'
                ],
                'field_patterns': {
                    'name': r'(?:name|child.*name)[:\s]*([A-Z\s,]+)',
                    'birth_date': r'(?:date.*birth|birth.*date)[:\s]*([0-9/\-\s]+)',
                    'registry_no': r'(?:registry.*no|reg.*no)[:\s]*([0-9\-]+)',
                    'place_birth': r'(?:place.*birth)[:\s]*([A-Z\s,]+)'
                },
                'validation_keywords': [
                    'civil', 'registrar', 'birth', 'certificate', 
                    'philippines', 'republic', 'live', 'registry'
                ]
            },
            'school_id': {
                'required_sections': [
                    'student',
                    'university',
                    'college',
                    'student no'
                ],
                'header_patterns': [
                    'taguig city university',
                    'college of',
                    'student no'
                ],
                'field_patterns': {
                    'student_name': r'([A-Z\s\.]+)(?:\s*$|\s*\n)',
                    'student_no': r'(?:student.*no|no)[:\s]*([0-9\-]+)',
                    'university': r'(taguig.*university|.*college.*)'
                },
                'validation_keywords': [
                    'student', 'university', 'college', 'taguig', 'tcu'
                ]
            }
        }
    
    def analyze_document_structure(self, img_array: np.ndarray) -> Dict[str, Any]:
        """
        🔍 Analyze document structure like ChatGPT Vision
        Understands layout, sections, headers, and content areas
        """
        analysis = {
            'document_type': 'unknown',
            'confidence': 0.0,
            'sections': [],
            'headers': [],
            'text_regions': [],
            'quality_assessment': {},
            'layout_structure': {}
        }
        
        try:
            # 1. Image quality assessment
            quality = self._assess_image_quality(img_array)
            analysis['quality_assessment'] = quality
            
            # 2. Document layout detection
            layout = self._detect_document_layout(img_array)
            analysis['layout_structure'] = layout
            
            # 3. Text region detection
            text_regions = self._detect_text_regions(img_array)
            analysis['text_regions'] = text_regions
            
            # 4. Header detection
            headers = self._detect_headers(img_array)
            analysis['headers'] = headers
            
            # 5. Document type classification
            doc_type, confidence = self._classify_document_type(headers, text_regions)
            analysis['document_type'] = doc_type
            analysis['confidence'] = confidence
            
            logger.info(f"🎯 Vision AI Analysis: {doc_type} (confidence: {confidence:.1%})")
            
        except Exception as e:
            logger.error(f"Vision AI analysis error: {str(e)}")
            
        return analysis
    
    def _assess_image_quality(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Assess image quality like human vision"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Blur detection (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness analysis
        brightness = np.mean(gray)
        
        # Contrast analysis
        contrast = np.std(gray)
        
        # Noise detection
        noise_level = np.std(cv2.medianBlur(gray, 5) - gray)
        
        return {
            'blur_score': float(blur_score),
            'brightness': float(brightness),
            'contrast': float(contrast),
            'noise_level': float(noise_level),
            'is_acceptable': blur_score > 100 and 50 < brightness < 200 and contrast > 30
        }
    
    def _detect_document_layout(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Detect document structure and layout"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Edge detection for structure
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours (boxes, sections)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        return {
            'has_form_structure': len(contours) > 10,
            'horizontal_lines': np.count_nonzero(horizontal_lines) > 1000,
            'vertical_lines': np.count_nonzero(vertical_lines) > 1000,
            'section_count': len(contours),
            'layout_type': 'form' if len(contours) > 15 else 'document'
        }
    
    def _detect_text_regions(self, img_array: np.ndarray) -> List[Dict]:
        """Detect text regions in the document"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # MSER (Maximally Stable Extremal Regions) for text detection
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        text_regions = []
        for region in regions:
            if len(region) > 10:  # Filter small regions
                x, y, w, h = cv2.boundingRect(region)
                text_regions.append({
                    'bbox': (x, y, w, h),
                    'area': w * h,
                    'aspect_ratio': w / h if h > 0 else 0
                })
        
        # Sort by vertical position (top to bottom)
        text_regions.sort(key=lambda r: r['bbox'][1])
        
        return text_regions[:20]  # Top 20 text regions
    
    def _detect_headers(self, img_array: np.ndarray) -> List[str]:
        """Detect header text using size and position"""
        # This would use OCR on the top portion of the document
        height, width = img_array.shape[:2]
        
        # Focus on top 25% for headers
        header_region = img_array[:int(height * 0.25), :]
        
        # Use EasyOCR for header detection
        try:
            import easyocr
            reader = easyocr.Reader(['en'])
            results = reader.readtext(header_region)
            
            headers = []
            for (bbox, text, conf) in results:
                if conf > 0.5 and len(text) > 3:
                    headers.append(text.lower().strip())
            
            return headers
            
        except Exception as e:
            logger.error(f"Header detection error: {str(e)}")
            return []
    
    def _classify_document_type(self, headers: List[str], text_regions: List[Dict]) -> Tuple[str, float]:
        """Classify document type based on visual analysis"""
        header_text = ' '.join(headers)
        
        best_match = 'unknown'
        best_confidence = 0.0
        
        for doc_type, template in self.document_templates.items():
            confidence = 0.0
            
            # Check header patterns
            for pattern in template['header_patterns']:
                if pattern in header_text:
                    confidence += 0.3
            
            # Check validation keywords
            keyword_count = 0
            for keyword in template['validation_keywords']:
                if keyword in header_text:
                    keyword_count += 1
            
            keyword_confidence = keyword_count / len(template['validation_keywords'])
            confidence += keyword_confidence * 0.7
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = doc_type
        
        return best_match, best_confidence
    
    def extract_structured_data(self, img_array: np.ndarray, document_type: str) -> Dict[str, Any]:
        """
        🎯 Extract structured data like ChatGPT Vision
        Understands context and relationships between text elements
        """
        if document_type not in self.document_templates:
            return {}
        
        template = self.document_templates[document_type]
        extracted_data = {}
        
        try:
            # Use EasyOCR for full text extraction
            import easyocr
            reader = easyocr.Reader(['en'])
            results = reader.readtext(img_array)
            
            # Combine all text
            full_text = ' '.join([text for (bbox, text, conf) in results if conf > 0.3])
            
            # Extract specific fields using patterns
            for field_name, pattern in template['field_patterns'].items():
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    extracted_data[field_name] = matches[0].strip()
            
            # Post-process and validate extracted data
            extracted_data = self._post_process_extracted_data(extracted_data, document_type)
            
        except Exception as e:
            logger.error(f"Structured data extraction error: {str(e)}")
        
        return extracted_data
    
    def _post_process_extracted_data(self, data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Clean and validate extracted data"""
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Clean up text
                cleaned_value = re.sub(r'[^\w\s\-/.,]', '', value)
                cleaned_value = ' '.join(cleaned_value.split())  # Normalize whitespace
                
                # Validate based on field type
                if 'name' in key and len(cleaned_value) > 2:
                    cleaned_data[key] = cleaned_value.title()
                elif 'date' in key and len(cleaned_value) > 4:
                    cleaned_data[key] = cleaned_value
                elif 'no' in key and cleaned_value.replace('-', '').replace(' ', '').isdigit():
                    cleaned_data[key] = cleaned_value
                elif len(cleaned_value) > 1:
                    cleaned_data[key] = cleaned_value
        
        return cleaned_data

# Global instance
vision_ai = VisionAI()