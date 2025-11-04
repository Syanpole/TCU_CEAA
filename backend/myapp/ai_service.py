"""
AI Service for TCU-CEAA Document and Grade Analysis
This module provides advanced AI capabilities for analyzing student documents and grades.
Now includes Autonomous AI (EasyOCR) for grade sheet name verification!
Enhanced with Advanced OCR for superior accuracy!
"""

import os
import re
import json
import base64
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Import Advanced OCR Service
try:
    from myapp.advanced_ocr_service import get_advanced_ocr_service
    ADVANCED_OCR_AVAILABLE = True
except ImportError:
    ADVANCED_OCR_AVAILABLE = False
    logger.warning("Advanced OCR service not available")

def check_optional_imports(imports):
    try:
        for imp in imports:
            exec(f"import {imp}", globals())
        return True
    except ImportError:
        return False

# Conditional imports for optional dependencies
try:
    import PyPDF2
    PDF_PYPDF2_AVAILABLE = True
except ImportError:
    PDF_PYPDF2_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# PDF and image processing
PDF_AVAILABLE = check_optional_imports([
    "PyPDF2",
    "PIL.Image",
    "PIL.ImageEnhance",
    "PIL.ImageFilter",
    "cv2",
    "numpy"
])

# OCR capabilities 
OCR_AVAILABLE = check_optional_imports([
    "pytesseract"
])

# Machine learning for text classification
ML_AVAILABLE = check_optional_imports([
    "sklearn.feature_extraction.text",
    "sklearn.metrics.pairwise",
    "nltk"
])


class AIDocumentAnalyzer:
    """Advanced AI-powered document analysis system"""
    
    def __init__(self):
        self.document_patterns = {
            'birth_certificate': {
                'keywords': ['birth', 'certificate', 'civil', 'registry', 'born', 'child', 'parent', 'mother', 'father'],
                'required_fields': ['name', 'date', 'place', 'registry'],
                'confidence_threshold': 0.7
            },
            'school_id': {
                'keywords': ['student', 'id', 'school', 'university', 'college', 'identification', 'tcu', 'student number'],
                'required_fields': ['name', 'student_number', 'school'],
                'confidence_threshold': 0.6
            },
            'report_card': {
                'keywords': ['grade', 'report', 'card', 'transcript', 'academic', 'semester', 'subject', 'gwa', 'average'],
                'required_fields': ['grades', 'semester', 'year', 'student'],
                'confidence_threshold': 0.8
            },
            'enrollment_certificate': {
                'keywords': ['enrollment', 'certificate', 'enrolled', 'student', 'semester', 'academic', 'year', 'units'],
                'required_fields': ['student', 'semester', 'year', 'status'],
                'confidence_threshold': 0.7
            },
            'barangay_clearance': {
                'keywords': ['barangay', 'clearance', 'certificate', 'good', 'moral', 'character', 'resident'],
                'required_fields': ['name', 'barangay', 'date'],
                'confidence_threshold': 0.6
            }
        }
        
        # Grade patterns for OCR extraction
        self.grade_patterns = {
            'gwa_pattern': r'(?:gwa|general.*average|overall.*average)[\s:]*(\d{1,2}\.?\d{0,2})',
            'swa_pattern': r'(?:swa|semestral.*average|semester.*average)[\s:]*(\d{1,2}\.?\d{0,2})',
            'grade_pattern': r'(\d{1,2}\.?\d{0,2})',
            'unit_pattern': r'(?:unit|units|credit)[\s:]*(\d{1,2})',
            'subject_pattern': r'([A-Z]{2,4}\s*\d{3,4})',
        }

    def analyze_document(self, document_submission) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of uploaded document
        """
        analysis_result = {
            'confidence_score': 0.0,
            'document_type_match': False,
            'extracted_text': '',
            'key_information': {},
            'quality_assessment': {},
            'recommendations': [],
            'auto_approve': False,
            'analysis_notes': []
        }
        
        try:
            # Basic file analysis
            file_analysis = self._analyze_file_properties(document_submission)
            analysis_result.update(file_analysis)
            
            # Extract text from document
            extracted_text = self._extract_text_from_file(document_submission.document_file)
            analysis_result['extracted_text'] = extracted_text
            
            # Document type validation
            type_analysis = self._validate_document_type(
                document_submission.document_type, 
                extracted_text, 
                document_submission.document_file.name
            )
            analysis_result.update(type_analysis)
            
            # Quality assessment
            quality_assessment = self._assess_document_quality(document_submission.document_file)
            analysis_result['quality_assessment'] = quality_assessment
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis_result)
            analysis_result['recommendations'] = recommendations
            
            # Determine auto-approval eligibility
            analysis_result['auto_approve'] = self._should_auto_approve(analysis_result)
            
        except Exception as e:
            analysis_result['analysis_notes'].append(f"⚠️ Analysis error: {str(e)}")
            analysis_result['confidence_score'] = 0.0
        
        return analysis_result

    def _analyze_file_properties(self, document_submission) -> Dict[str, Any]:
        """Analyze basic file properties"""
        file_obj = document_submission.document_file
        filename = file_obj.name.lower()
        file_size = file_obj.size
        
        analysis = {
            'file_format': 'unknown',
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'filename_analysis': {},
            'analysis_notes': []
        }
        
        # Determine file format
        if filename.endswith('.pdf'):
            analysis['file_format'] = 'pdf'
            analysis['analysis_notes'].append("✅ PDF format - excellent for document preservation")
        elif filename.endswith(('.jpg', '.jpeg', '.png')):
            analysis['file_format'] = 'image'
            analysis['analysis_notes'].append("✅ Image format - ensure high resolution and clarity")
        elif filename.endswith(('.doc', '.docx')):
            analysis['file_format'] = 'document'
            analysis['analysis_notes'].append("⚠️ Word document - PDF preferred for official documents")
        
        # File size analysis
        if file_size < 50 * 1024:  # Less than 50KB
            analysis['analysis_notes'].append("⚠️ File very small - may be incomplete or low quality")
        elif file_size > 10 * 1024 * 1024:  # Greater than 10MB
            analysis['analysis_notes'].append("⚠️ Large file size - consider compression")
        else:
            analysis['analysis_notes'].append("✅ File size appropriate")
        
        # Filename analysis
        doc_type = document_submission.document_type
        if doc_type in self.document_patterns:
            keywords = self.document_patterns[doc_type]['keywords']
            matches = sum(1 for keyword in keywords if keyword in filename)
            match_ratio = matches / len(keywords)
            
            analysis['filename_analysis'] = {
                'keyword_matches': matches,
                'match_ratio': match_ratio,
                'matches_type': match_ratio > 0.2
            }
            
            if match_ratio > 0.3:
                analysis['analysis_notes'].append("✅ Filename clearly indicates document type")
            elif match_ratio > 0.1:
                analysis['analysis_notes'].append("⚠️ Filename partially matches document type")
            else:
                analysis['analysis_notes'].append("⚠️ Filename doesn't clearly indicate document type")
        
        return analysis

    def _extract_text_from_file(self, file_obj) -> str:
        """
        Extract text from various file formats
        Priority: Advanced OCR → Local OCR → Basic extraction
        """
        filename = file_obj.name.lower()
        extracted_text = ""
        ocr_method = "unknown"
        
        try:
            # Try Advanced OCR first (if enabled) - HIGHEST ACCURACY
            if ADVANCED_OCR_AVAILABLE and (filename.endswith(('.jpg', '.jpeg', '.png', '.pdf'))):
                try:
                    advanced_ocr = get_advanced_ocr_service()
                    if advanced_ocr.is_enabled():
                        logger.info("📡 Using Advanced OCR (95-98% accuracy)")
                        
                        # Read file bytes
                        file_obj.seek(0)
                        file_bytes = file_obj.read()
                        file_obj.seek(0)  # Reset file pointer
                        
                        # Extract text with Advanced OCR
                        result = advanced_ocr.extract_text(file_bytes)
                        
                        if result['success']:
                            extracted_text = result['text']
                            confidence = result['confidence']
                            ocr_method = "advanced_ocr"
                            logger.info(f"✅ Advanced OCR extracted {len(extracted_text)} chars (confidence: {confidence:.1f}%)")
                            return extracted_text
                        else:
                            logger.warning(f"Advanced OCR failed: {result.get('error')}, falling back to local OCR")
                except Exception as e:
                    logger.warning(f"Advanced OCR error: {str(e)}, falling back to local OCR")
            
            # Fallback to local OCR methods (original code)
            if filename.endswith('.pdf') and PDF_PYPDF2_AVAILABLE:
                logger.info("📄 Using local PDF text extraction")
                extracted_text = self._extract_text_from_pdf(file_obj)
                ocr_method = "local_pdf"
            elif filename.endswith(('.jpg', '.jpeg', '.png')) and (CV2_AVAILABLE and PYTESSERACT_AVAILABLE):
                logger.info("🔍 Using local OCR (Tesseract, ~85% accuracy)")
                extracted_text = self._extract_text_from_image(file_obj)
                ocr_method = "local_tesseract"
            elif filename.endswith(('.doc', '.docx')):
                # For demonstration - in production, use python-docx
                extracted_text = "Document text extraction not implemented for Word files"
                ocr_method = "unsupported"
                
            if extracted_text:
                logger.info(f"✅ Text extraction completed using {ocr_method}")
        except Exception as e:
            extracted_text = f"Text extraction failed: {str(e)}"
            logger.error(f"Text extraction error: {str(e)}")
        
        return extracted_text

    def _extract_text_from_pdf(self, file_obj) -> str:
        """Extract text from PDF files"""
        if not PDF_PYPDF2_AVAILABLE:
            return "PDF processing not available"
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                for chunk in file_obj.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Extract text
            text = ""
            with open(temp_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # Clean up
            os.unlink(temp_path)
            return text.strip()
            
        except Exception as e:
            return f"PDF text extraction failed: {str(e)}"

    def _extract_text_from_image(self, file_obj) -> str:
        """Extract text from image files using OCR"""
        if not (CV2_AVAILABLE and PYTESSERACT_AVAILABLE):
            return "OCR processing not available"
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file_obj.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Process image for better OCR
            image = cv2.imread(temp_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance image quality
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Extract text
            text = pytesseract.image_to_string(gray, config='--psm 6')
            
            # Clean up
            os.unlink(temp_path)
            return text.strip()
            
        except Exception as e:
            return f"OCR text extraction failed: {str(e)}"

    def _validate_document_type(self, declared_type: str, extracted_text: str, filename: str) -> Dict[str, Any]:
        """Validate if document matches declared type"""
        validation_result = {
            'document_type_match': False,
            'confidence_score': 0.0,
            'key_information': {},
            'analysis_notes': []
        }
        
        if declared_type not in self.document_patterns:
            validation_result['analysis_notes'].append("⚠️ Unknown document type")
            return validation_result
        
        pattern_data = self.document_patterns[declared_type]
        keywords = pattern_data['keywords']
        text_lower = extracted_text.lower()
        filename_lower = filename.lower()
        
        # Calculate keyword matches in text
        text_matches = sum(1 for keyword in keywords if keyword in text_lower)
        filename_matches = sum(1 for keyword in keywords if keyword in filename_lower)
        
        # Calculate confidence score
        total_possible_matches = len(keywords) * 2  # Text + filename
        total_matches = text_matches + filename_matches
        confidence = total_matches / total_possible_matches
        
        validation_result['confidence_score'] = confidence
        validation_result['document_type_match'] = confidence >= pattern_data['confidence_threshold']
        
        # Extract key information based on document type
        key_info = self._extract_key_information(declared_type, extracted_text)
        validation_result['key_information'] = key_info
        
        # Generate analysis notes
        if validation_result['document_type_match']:
            validation_result['analysis_notes'].append(
                f"✅ Document matches declared type (confidence: {confidence:.1%})"
            )
        else:
            validation_result['analysis_notes'].append(
                f"⚠️ Document may not match declared type (confidence: {confidence:.1%})"
            )
        
        validation_result['analysis_notes'].append(
            f"📊 Found {text_matches} relevant keywords in document text"
        )
        
        return validation_result

    def _extract_key_information(self, doc_type: str, text: str) -> Dict[str, Any]:
        """Extract key information from document text"""
        key_info = {}
        text_lower = text.lower()
        
        # Common patterns
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        name_pattern = r'name[:\s]*([a-zA-Z\s,]+)'
        
        if doc_type == 'birth_certificate':
            # Extract birth certificate specific information
            key_info.update({
                'dates_found': re.findall(date_pattern, text),
                'names_found': re.findall(name_pattern, text_lower),
                'has_registry_info': 'registry' in text_lower or 'civil' in text_lower,
                'has_parent_info': 'mother' in text_lower or 'father' in text_lower
            })
        
        elif doc_type == 'school_id':
            # Extract student ID specific information
            student_id_pattern = r'(?:student.*id|id.*number)[:\s]*([a-zA-Z0-9-]+)'
            key_info.update({
                'student_ids_found': re.findall(student_id_pattern, text_lower),
                'has_school_name': any(school in text_lower for school in ['tcu', 'university', 'college']),
                'has_photo_reference': 'photo' in text_lower or 'picture' in text_lower
            })
        
        elif doc_type == 'report_card':
            # Extract grade information
            key_info.update(self._extract_grade_information(text))
        
        return key_info

    def _extract_grade_information(self, text: str) -> Dict[str, Any]:
        """Extract grade-specific information from text"""
        grade_info = {
            'gwa_found': [],
            'swa_found': [],
            'subjects_found': [],
            'units_found': [],
            'semester_info': []
        }
        
        text_lower = text.lower()
        
        # Extract GWA
        gwa_matches = re.findall(self.grade_patterns['gwa_pattern'], text_lower)
        grade_info['gwa_found'] = [float(g) for g in gwa_matches if g.replace('.', '').isdigit()]
        
        # Extract SWA
        swa_matches = re.findall(self.grade_patterns['swa_pattern'], text_lower)
        grade_info['swa_found'] = [float(g) for g in swa_matches if g.replace('.', '').isdigit()]
        
        # Extract subjects
        subject_matches = re.findall(self.grade_patterns['subject_pattern'], text)
        grade_info['subjects_found'] = subject_matches
        
        # Extract units
        unit_matches = re.findall(self.grade_patterns['unit_pattern'], text_lower)
        grade_info['units_found'] = [int(u) for u in unit_matches if u.isdigit()]
        
        # Look for semester information
        semester_keywords = ['1st semester', '2nd semester', 'first semester', 'second semester', 'summer']
        grade_info['semester_info'] = [kw for kw in semester_keywords if kw in text_lower]
        
        return grade_info

    def _assess_document_quality(self, file_obj) -> Dict[str, Any]:
        """Assess the quality of the uploaded document"""
        quality_assessment = {
            'overall_quality': 'unknown',
            'quality_score': 0.0,
            'issues': [],
            'strengths': []
        }
        
        try:
            filename = file_obj.name.lower()
            file_size = file_obj.size
            
            # File size assessment
            if file_size < 50 * 1024:
                quality_assessment['issues'].append("Very small file size - may be incomplete")
            elif file_size > 50 * 1024 and file_size < 500 * 1024:
                quality_assessment['strengths'].append("Appropriate file size")
            elif file_size > 10 * 1024 * 1024:
                quality_assessment['issues'].append("Large file size - may affect processing")
            
            # Format assessment
            if filename.endswith('.pdf'):
                quality_assessment['strengths'].append("PDF format - good for preservation")
                quality_assessment['quality_score'] += 0.3
            elif filename.endswith(('.jpg', '.jpeg', '.png')):
                quality_assessment['strengths'].append("Image format - good for scanned documents")
                quality_assessment['quality_score'] += 0.2
            
            # Calculate overall quality
            total_issues = len(quality_assessment['issues'])
            total_strengths = len(quality_assessment['strengths'])
            
            if total_issues == 0 and total_strengths > 0:
                quality_assessment['overall_quality'] = 'excellent'
                quality_assessment['quality_score'] += 0.5
            elif total_issues <= 1 and total_strengths >= 1:
                quality_assessment['overall_quality'] = 'good'
                quality_assessment['quality_score'] += 0.3
            elif total_issues <= 2:
                quality_assessment['overall_quality'] = 'fair'
                quality_assessment['quality_score'] += 0.1
            else:
                quality_assessment['overall_quality'] = 'poor'
            
            # Ensure score is between 0 and 1
            quality_assessment['quality_score'] = min(1.0, max(0.0, quality_assessment['quality_score']))
            
        except Exception as e:
            quality_assessment['issues'].append(f"Quality assessment error: {str(e)}")
        
        return quality_assessment

    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Based on confidence score
        if analysis_result.get('confidence_score', 0) < 0.5:
            recommendations.append("Consider re-uploading with a clearer filename that matches the document type")
        
        # Based on quality assessment
        quality = analysis_result.get('quality_assessment', {})
        if quality.get('overall_quality') == 'poor':
            recommendations.append("Document quality is poor - consider re-scanning or taking a clearer photo")
        
        # Based on file size
        file_size_mb = analysis_result.get('file_size_mb', 0)
        if file_size_mb > 5:
            recommendations.append("Large file size - consider compressing the document")
        elif file_size_mb < 0.1:
            recommendations.append("File size is very small - ensure the document is complete")
        
        # Based on format
        if analysis_result.get('file_format') != 'pdf':
            recommendations.append("For official documents, PDF format is preferred over images")
        
        return recommendations

    def _should_auto_approve(self, analysis_result: Dict[str, Any]) -> bool:
        """Determine if document should be auto-approved - Enhanced for autonomous processing"""
        confidence = analysis_result.get('confidence_score', 0)
        quality_score = analysis_result.get('quality_assessment', {}).get('quality_score', 0)
        type_match = analysis_result.get('document_type_match', False)
        
        # Stricter auto-approve criteria for autonomous processing
        # Auto-approve only if confidence >= 70%, quality_score >= 0.6, and no issues
        basic_approval = (
            confidence >= 0.7 and
            quality_score >= 0.6 and
            len(analysis_result.get('quality_assessment', {}).get('issues', [])) == 0
        )
        
        # Higher approval for perfect matches (raise thresholds slightly)
        high_confidence_approval = (
            confidence >= 0.8 and
            quality_score >= 0.7 and
            type_match
        )
        
        # Even if type doesn't perfectly match, approve only if other criteria are very strong
        flexible_approval = (
            confidence >= 0.75 and
            quality_score >= 0.65 and
            len(analysis_result.get('quality_assessment', {}).get('issues', [])) == 0
        )
        
        return basic_approval or high_confidence_approval or flexible_approval


class AIGradeAnalyzer:
    """Advanced AI system for grade analysis and allowance calculation"""
    
    def __init__(self):
        self.allowance_rules = {
            'basic_allowance': {
                'amount': 5000,
                'min_gwa': 80.0,
                'min_units': 15,
                'allow_failing': False,
                'allow_incomplete': False,
                'allow_dropped': False
            },
            'merit_incentive': {
                'amount': 5000,
                'min_swa': 87.0,  # GWA 1.75 or better (≥87%)
                'min_units': 15,
                'allow_failing': False,
                'allow_incomplete': False,
                'allow_dropped': False
            }
        }

    def analyze_grades(self, grade_submission) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of grade submission
        NOW INCLUDES: Student name verification on grade sheet (fraud prevention)
        """
        analysis_result = {
            'basic_allowance_analysis': {},
            'merit_incentive_analysis': {},
            'grade_validation': {},
            'extracted_grades': {},
            'name_verification': {},
            'recommendations': [],
            'total_allowance': 0,
            'analysis_notes': [],
            'confidence_score': 0.0
        }
        
        try:
            # Validate input grades
            validation_result = self._validate_grade_inputs(grade_submission)
            analysis_result['grade_validation'] = validation_result
            
            # 🔒 CRITICAL: Verify student name on grade sheet (fraud prevention)
            if grade_submission.grade_sheet:
                name_verification = self._verify_grade_sheet_ownership(grade_submission)
                analysis_result['name_verification'] = name_verification
                
                # If name doesn't match, REJECT immediately
                if not name_verification.get('name_match', False):
                    analysis_result['grade_validation']['issues'].append('🚨 FRAUD ALERT: Student name on grade sheet does not match your account')
                    analysis_result['confidence_score'] = 0.0
                    analysis_result['analysis_notes'].append(
                        f"⛔ SECURITY REJECTION: {name_verification.get('mismatch_reason', 'Name verification failed')}"
                    )
                    return analysis_result
            
            # Analyze grade sheet file if provided
            if grade_submission.grade_sheet:
                extracted_grades = self._analyze_grade_sheet(grade_submission.grade_sheet)
                analysis_result['extracted_grades'] = extracted_grades
                
                # Cross-validate with submitted values
                cross_validation = self._cross_validate_grades(grade_submission, extracted_grades)
                analysis_result['grade_validation'].update(cross_validation)
            
            # Analyze basic allowance eligibility
            basic_analysis = self._analyze_basic_allowance_eligibility(grade_submission)
            analysis_result['basic_allowance_analysis'] = basic_analysis
            
            # Analyze merit incentive eligibility
            merit_analysis = self._analyze_merit_incentive_eligibility(grade_submission)
            analysis_result['merit_incentive_analysis'] = merit_analysis
            
            # Calculate total allowance
            total_allowance = 0
            if basic_analysis.get('eligible', False):
                total_allowance += self.allowance_rules['basic_allowance']['amount']
            if merit_analysis.get('eligible', False):
                total_allowance += self.allowance_rules['merit_incentive']['amount']
            
            analysis_result['total_allowance'] = total_allowance
            
            # Generate comprehensive analysis notes
            analysis_notes = self._generate_analysis_notes(grade_submission, analysis_result)
            analysis_result['analysis_notes'] = analysis_notes
            
            # Generate recommendations
            recommendations = self._generate_grade_recommendations(analysis_result)
            analysis_result['recommendations'] = recommendations
            
            # Calculate overall confidence
            confidence = self._calculate_analysis_confidence(analysis_result)
            analysis_result['confidence_score'] = confidence
            
        except Exception as e:
            analysis_result['analysis_notes'].append(f"⚠️ Analysis error: {str(e)}")
            analysis_result['confidence_score'] = 0.0
        
        return analysis_result

    def _validate_grade_inputs(self, grade_submission) -> Dict[str, Any]:
        """Validate the submitted grade information"""
        validation = {
            'gwa_valid': True,
            'swa_valid': True,
            'units_valid': True,
            'semester_valid': True,
            'issues': [],
            'warnings': []
        }
        
        # Validate GWA
        gwa = float(grade_submission.general_weighted_average)
        if gwa < 65 or gwa > 100:
            validation['gwa_valid'] = False
            validation['issues'].append(f"GWA {gwa}% is outside valid range (65-100%)")
        elif gwa < 75:
            validation['warnings'].append(f"GWA {gwa}% is quite low - may affect allowance eligibility")
        
        # Validate SWA
        swa = float(grade_submission.semestral_weighted_average)
        if swa < 65 or swa > 100:
            validation['swa_valid'] = False
            validation['issues'].append(f"SWA {swa}% is outside valid range (65-100%)")
        elif swa < 75:
            validation['warnings'].append(f"SWA {swa}% is quite low - may affect allowance eligibility")
        
        # Validate units
        units = grade_submission.total_units
        if units < 1 or units > 30:
            validation['units_valid'] = False
            validation['issues'].append(f"Total units {units} is outside valid range (1-30)")
        elif units < 12:
            validation['warnings'].append(f"Only {units} units - may not qualify for full allowance")
        
        # Cross-validate GWA and SWA
        if abs(gwa - swa) > 20:
            validation['warnings'].append(f"Large difference between GWA ({gwa}%) and SWA ({swa}%) - please verify")
        
        # Check academic year format
        academic_year = grade_submission.academic_year
        if not re.match(r'^\d{4}-\d{4}$', academic_year):
            validation['warnings'].append(f"Academic year format should be YYYY-YYYY (e.g., 2024-2025)")
        
        return validation

    def _analyze_grade_sheet(self, grade_sheet_file) -> Dict[str, Any]:
        """
        Analyze the uploaded grade sheet for additional validation
        Uses Advanced OCR for best accuracy, falls back to local OCR
        """
        extracted_data = {
            'text_extracted': '',
            'grades_found': [],
            'gwa_found': [],
            'swa_found': [],
            'subjects_found': [],
            'units_found': [],
            'analysis_confidence': 0.0,
            'ocr_method': 'unknown'
        }
        
        try:
            # Try Advanced OCR first (if enabled) - BEST ACCURACY
            if ADVANCED_OCR_AVAILABLE:
                try:
                    advanced_ocr = get_advanced_ocr_service()
                    if advanced_ocr.is_enabled():
                        logger.info("📡 Using Advanced OCR for grade sheet analysis")
                        
                        # Read file bytes
                        grade_sheet_file.seek(0)
                        file_bytes = grade_sheet_file.read()
                        grade_sheet_file.seek(0)  # Reset
                        
                        # Extract with Advanced OCR
                        result = advanced_ocr.process_grade_document(file_bytes)
                        
                        if result['overall_success']:
                            # Get text extraction
                            text_result = result['text_extraction']
                            extracted_text = text_result.get('text', '')
                            extracted_data['text_extracted'] = extracted_text
                            extracted_data['ocr_method'] = 'advanced_ocr'
                            
                            logger.info(f"✅ Advanced OCR extracted {len(extracted_text)} chars ({text_result.get('confidence', 0):.1f}% confidence)")
                            
                            # Extract grade information
                            if extracted_text and len(extracted_text.strip()) > 10:
                                doc_analyzer = AIDocumentAnalyzer()
                                grade_info = doc_analyzer._extract_grade_information(extracted_text)
                                extracted_data.update(grade_info)
                                
                                # Use Advanced OCR confidence
                                extracted_data['analysis_confidence'] = text_result.get('confidence', 0) / 100
                                
                                return extracted_data
                except Exception as e:
                    logger.warning(f"Advanced OCR failed for grade sheet: {str(e)}, falling back to local OCR")
            
            # Fallback to local OCR (original code)
            logger.info("🔍 Using local OCR for grade sheet analysis")
            doc_analyzer = AIDocumentAnalyzer()
            extracted_text = doc_analyzer._extract_text_from_file(grade_sheet_file)
            extracted_data['text_extracted'] = extracted_text
            extracted_data['ocr_method'] = 'local_ocr'
            
            if extracted_text and len(extracted_text.strip()) > 10:
                # Extract grade information
                grade_info = doc_analyzer._extract_grade_information(extracted_text)
                extracted_data.update(grade_info)
                
                # Calculate confidence based on extracted information
                confidence_factors = []
                
                # Text extraction success
                if extracted_text and len(extracted_text.strip()) > 10:
                    confidence_factors.append(0.3)
                
                # Grade information found
                if grade_info.get('gwa_found'):
                    confidence_factors.append(0.25)
                if grade_info.get('swa_found'):
                    confidence_factors.append(0.25)
                if grade_info.get('subjects_found'):
                    confidence_factors.append(0.15)
                if grade_info.get('units_found'):
                    confidence_factors.append(0.15)
                
                # Semester information
                if grade_info.get('semester_info'):
                    confidence_factors.append(0.1)
                
                # Even if some information is missing, give partial confidence
                extracted_data['analysis_confidence'] = min(1.0, sum(confidence_factors))
            
        except Exception as e:
            extracted_data['text_extracted'] = f"Error extracting text: {str(e)}"
            logger.error(f"Grade sheet analysis error: {str(e)}")
        
        return extracted_data
    
    def _verify_grade_sheet_ownership(self, grade_submission) -> Dict[str, Any]:
        """
        🔒 CRITICAL SECURITY: Verify student name on grade sheet matches submitting student
        Prevents students from submitting other people's grades
        
        NOW USES: Autonomous AI (EasyOCR) - no Tesseract needed!
        """
        result = {
            'name_match': False,
            'confidence': 0.0,
            'mismatch_reason': '',
            'expected_name': '',
            'found_names': [],
            'matched_name': '',
            'verification_method': 'none'
        }
        
        try:
            from PIL import Image
            import re
            
            # Get student information
            student = grade_submission.student
            first_name = student.first_name.lower().strip() if student.first_name else ''
            last_name = student.last_name.lower().strip() if student.last_name else ''
            full_name = f"{first_name} {last_name}".strip()
            reverse_name = f"{last_name} {first_name}".strip()
            username = student.username.lower().strip() if student.username else ''
            
            result['expected_name'] = full_name
            
            # If no name set, REJECT for security (can't verify without name)
            if not first_name or not last_name:
                result['name_match'] = False
                result['confidence'] = 0.0
                result['mismatch_reason'] = '⚠️ Your profile name is incomplete. Please update your First Name and Last Name in your profile settings before submitting grades. This is required for document verification.'
                return result
            
            # Get grade sheet file
            grade_sheet_file = grade_submission.grade_sheet
            
            # Get file path
            if hasattr(grade_sheet_file, 'path'):
                file_path = grade_sheet_file.path
            else:
                # File might be uploaded but not saved yet
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                for chunk in grade_sheet_file.chunks():
                    temp_file.write(chunk)
                temp_file.close()
                file_path = temp_file.name
            
            # 🤖 OCR VERIFICATION - Try Advanced OCR first, then local methods
            extracted_text = None
            ocr_method = None
            
            # Priority 1: Advanced OCR (95-98% accuracy)
            if ADVANCED_OCR_AVAILABLE:
                try:
                    advanced_ocr = get_advanced_ocr_service()
                    if advanced_ocr.is_enabled():
                        logger.info("📡 Using Advanced OCR for name verification")
                        
                        # Read file bytes
                        with open(file_path, 'rb') as f:
                            file_bytes = f.read()
                        
                        # Extract text with Advanced OCR
                        ocr_result = advanced_ocr.extract_text(file_bytes)
                        
                        if ocr_result['success']:
                            extracted_text = ocr_result['text'].lower()
                            ocr_method = 'advanced_ocr'
                            result['verification_method'] = 'advanced_ocr'
                            
                            logger.info(f"✅ Advanced OCR extracted {len(extracted_text)} characters (confidence: {ocr_result.get('confidence', 0):.1f}%)")
                        else:
                            logger.warning(f"Advanced OCR failed: {ocr_result.get('error')}, falling back to local OCR")
                except Exception as e:
                    logger.warning(f"Advanced OCR error: {str(e)}, falling back to local OCR")
            
            # Priority 2: Autonomous AI (EasyOCR) - Local fallback
            if extracted_text is None:
                try:
                    import easyocr
                    import numpy as np
                    
                    logger.info("🤖 Using Autonomous AI (EasyOCR) for name verification")
                    
                    # Load image
                    img = Image.open(file_path)
                    
                    # Resize if needed
                    max_size = 2000
                    if img.width > max_size or img.height > max_size:
                        ratio = min(max_size / img.width, max_size / img.height)
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to numpy array
                    img_array = np.array(img)
                    
                    # Initialize EasyOCR
                    reader = easyocr.Reader(['en'], gpu=False)
                    
                    # Extract text
                    results = reader.readtext(img_array)
                    extracted_text = ' '.join([text for (bbox, text, conf) in results]).lower()
                    
                    ocr_method = 'autonomous_ai_easyocr'
                    result['verification_method'] = 'autonomous_ai'
                    
                    img.close()
                    
                    logger.info(f"✅ Autonomous AI (EasyOCR) extracted {len(extracted_text)} characters from grade sheet")
                    
                except Exception as easyocr_error:
                    logger.warning(f"EasyOCR failed: {str(easyocr_error)}, trying Tesseract fallback...")
                    
                    # Priority 3: Tesseract OCR - Final fallback
                    try:
                        import pytesseract
                        
                        logger.info("📄 Using Tesseract OCR for name verification")
                        
                        # Configure Tesseract path
                        tesseract_paths = [
                            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                            r'C:\Users\Public\tesseract\tesseract.exe'
                        ]
                        
                        for path in tesseract_paths:
                            if os.path.exists(path):
                                pytesseract.pytesseract.tesseract_cmd = path
                                logger.info(f"📄 Using Tesseract at: {path}")
                                break
                        
                        img = Image.open(file_path)
                        
                        # Resize if needed
                        max_size = 2000
                        if img.width > max_size or img.height > max_size:
                            ratio = min(max_size / img.width, max_size / img.height)
                            new_size = (int(img.width * ratio), int(img.height * ratio))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        extracted_text = pytesseract.image_to_string(img).lower()
                        ocr_method = 'tesseract_ocr'
                        result['verification_method'] = 'tesseract_fallback'
                        
                        img.close()
                        
                        logger.info(f"✅ Tesseract OCR extracted {len(extracted_text)} characters from grade sheet")
                        
                    except Exception as tesseract_error:
                        # ALL OCR METHODS FAILED - CRITICAL SECURITY ISSUE
                        
                        # ⚠️ WITHOUT OCR, WE CANNOT VERIFY NAMES - MUST REJECT FOR SECURITY
                        result['name_match'] = False
                        result['confidence'] = 0.0
                        result['mismatch_reason'] = f'🔒 SECURITY REJECTION: Cannot verify student name on grade sheet. All OCR methods failed (Advanced OCR, EasyOCR, and Tesseract). This is required to prevent fraud. Please ensure your grade sheet image is clear and readable.'
                        result['verification_method'] = 'failed_all_ocr_methods'
                        return result
            
            # Validate extracted text
            if not extracted_text or len(extracted_text.strip()) < 20:
                result['name_match'] = False
                result['confidence'] = 0.0
                result['mismatch_reason'] = f'🔒 SECURITY REJECTION: Insufficient text extracted from grade sheet (only {len(extracted_text if extracted_text else 0)} characters). Cannot verify student name. Please upload a clearer, higher quality image of your grade sheet.'
                return result
                
            # Clean text
            text_cleaned = re.sub(r'[^a-z\s]', ' ', extracted_text.lower())
            text_cleaned = re.sub(r'\s+', ' ', text_cleaned).strip()
            
            # Look for name matches
            name_found = False
            confidence = 0.0
            matched_format = ''
            
            # Check various name formats
            if full_name in text_cleaned:
                name_found = True
                confidence = 0.95
                matched_format = full_name
            elif reverse_name in text_cleaned:
                name_found = True
                confidence = 0.90
                matched_format = reverse_name
            elif first_name in text_cleaned and last_name in text_cleaned:
                name_found = True
                confidence = 0.85
                matched_format = f"{first_name} and {last_name}"
            elif len(username) > 4 and username in text_cleaned:
                name_found = True
                confidence = 0.75
                matched_format = username
            
            # Find potential other names (fraud detection)
            potential_names = re.findall(r'\b[a-z]{3,}\s+[a-z]{3,}\b', text_cleaned)
            result['found_names'] = list(set(potential_names))[:5]
            
            if name_found:
                result['name_match'] = True
                result['confidence'] = confidence
                result['matched_name'] = matched_format
            else:
                # 🚨 NAME NOT FOUND - FRAUD DETECTED - REJECT IMMEDIATELY
                result['name_match'] = False
                result['confidence'] = 0.0
                result['mismatch_reason'] = f"🚨 SECURITY REJECTION: Your name '{full_name.title()}' was not found on this grade sheet. You can only submit YOUR OWN grades. Submitting someone else's grades is considered academic fraud."
                
                if result['found_names']:
                    other_names = ', '.join([n.title() for n in result['found_names'][:3]])
                    result['mismatch_reason'] += f" This grade sheet appears to belong to: {other_names}."
            
        except Exception as e:
            # 🔒 CRITICAL: Any error during verification = REJECT for security
            # We cannot take risks with name verification - if unsure, REJECT
            result['name_match'] = False
            result['confidence'] = 0.0
            result['mismatch_reason'] = f'🔒 SECURITY REJECTION: Grade sheet verification failed due to technical error. Cannot verify if this is your grade sheet. Please try uploading a clearer image or contact support. Error: {str(e)}'
        
        return result

    def _cross_validate_grades(self, grade_submission, extracted_grades: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-validate submitted grades with extracted grades"""
        cross_validation = {
            'gwa_matches': False,
            'swa_matches': False,
            'discrepancies': [],
            'confidence_boost': 0.0
        }
        
        submitted_gwa = float(grade_submission.general_weighted_average)
        submitted_swa = float(grade_submission.semestral_weighted_average)
        
        # Check GWA matches
        extracted_gwa = extracted_grades.get('gwa_found', [])
        if extracted_gwa:
            closest_gwa = min(extracted_gwa, key=lambda x: abs(x - submitted_gwa))
            if abs(closest_gwa - submitted_gwa) <= 1.0:  # Within 1 point
                cross_validation['gwa_matches'] = True
                cross_validation['confidence_boost'] += 0.3
            else:
                cross_validation['discrepancies'].append(
                    f"Submitted GWA ({submitted_gwa}%) doesn't match extracted GWA ({closest_gwa}%)"
                )
        
        # Check SWA matches
        extracted_swa = extracted_grades.get('swa_found', [])
        if extracted_swa:
            closest_swa = min(extracted_swa, key=lambda x: abs(x - submitted_swa))
            if abs(closest_swa - submitted_swa) <= 1.0:  # Within 1 point
                cross_validation['swa_matches'] = True
                cross_validation['confidence_boost'] += 0.3
            else:
                cross_validation['discrepancies'].append(
                    f"Submitted SWA ({submitted_swa}%) doesn't match extracted SWA ({closest_swa}%)"
                )
        
        return cross_validation

    def _analyze_basic_allowance_eligibility(self, grade_submission) -> Dict[str, Any]:
        """Analyze eligibility for basic educational allowance"""
        rules = self.allowance_rules['basic_allowance']
        
        analysis = {
            'eligible': False,
            'requirements_met': {},
            'reasons_denied': [],
            'amount': rules['amount']
        }
        
        gwa = float(grade_submission.general_weighted_average)
        units = grade_submission.total_units
        
        # Check GWA requirement
        gwa_meets = gwa >= rules['min_gwa']
        analysis['requirements_met']['gwa'] = gwa_meets
        if not gwa_meets:
            analysis['reasons_denied'].append(f"GWA {gwa}% < {rules['min_gwa']}%")
        
        # Check units requirement
        units_meets = units >= rules['min_units']
        analysis['requirements_met']['units'] = units_meets
        if not units_meets:
            analysis['reasons_denied'].append(f"Units {units} < {rules['min_units']}")
        
        # Check failing grades
        no_failing = not grade_submission.has_failing_grades or rules['allow_failing']
        analysis['requirements_met']['no_failing'] = no_failing
        if not no_failing:
            analysis['reasons_denied'].append("Has failing grades")
        
        # Check incomplete grades
        no_incomplete = not grade_submission.has_incomplete_grades or rules['allow_incomplete']
        analysis['requirements_met']['no_incomplete'] = no_incomplete
        if not no_incomplete:
            analysis['reasons_denied'].append("Has incomplete grades")
        
        # Check dropped subjects
        no_dropped = not grade_submission.has_dropped_subjects or rules['allow_dropped']
        analysis['requirements_met']['no_dropped'] = no_dropped
        if not no_dropped:
            analysis['reasons_denied'].append("Has dropped subjects")
        
        # Determine eligibility
        analysis['eligible'] = all([
            gwa_meets, units_meets, no_failing, no_incomplete, no_dropped
        ])
        
        return analysis

    def _analyze_merit_incentive_eligibility(self, grade_submission) -> Dict[str, Any]:
        """Analyze eligibility for merit incentive"""
        rules = self.allowance_rules['merit_incentive']
        
        analysis = {
            'eligible': False,
            'requirements_met': {},
            'reasons_denied': [],
            'amount': rules['amount']
        }
        
        swa = float(grade_submission.semestral_weighted_average)
        units = grade_submission.total_units
        
        # Check SWA requirement
        swa_meets = swa >= rules['min_swa']
        analysis['requirements_met']['swa'] = swa_meets
        if not swa_meets:
            analysis['reasons_denied'].append(f"SWA {swa}% < {rules['min_swa']}%")
        
        # Check units requirement
        units_meets = units >= rules['min_units']
        analysis['requirements_met']['units'] = units_meets
        if not units_meets:
            analysis['reasons_denied'].append(f"Units {units} < {rules['min_units']}")
        
        # Check failing grades
        no_failing = not grade_submission.has_failing_grades or rules['allow_failing']
        analysis['requirements_met']['no_failing'] = no_failing
        if not no_failing:
            analysis['reasons_denied'].append("Has failing grades")
        
        # Check incomplete grades
        no_incomplete = not grade_submission.has_incomplete_grades or rules['allow_incomplete']
        analysis['requirements_met']['no_incomplete'] = no_incomplete
        if not no_incomplete:
            analysis['reasons_denied'].append("Has incomplete grades")
        
        # Check dropped subjects
        no_dropped = not grade_submission.has_dropped_subjects or rules['allow_dropped']
        analysis['requirements_met']['no_dropped'] = no_dropped
        if not no_dropped:
            analysis['reasons_denied'].append("Has dropped subjects")
        
        # Determine eligibility
        analysis['eligible'] = all([
            swa_meets, units_meets, no_failing, no_incomplete, no_dropped
        ])
        
        return analysis

    def _generate_analysis_notes(self, grade_submission, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate comprehensive analysis notes"""
        notes = []
        
        # Basic analysis header
        notes.append("🤖 AI-Powered Grade Analysis Results")
        notes.append("=" * 40)
        
        # Basic allowance analysis
        basic_analysis = analysis_result['basic_allowance_analysis']
        if basic_analysis.get('eligible'):
            notes.append("✅ Qualifies for Basic Educational Assistance (₱5,000)")
        else:
            reasons = basic_analysis.get('reasons_denied', [])
            notes.append(f"❌ Does not qualify for Basic Allowance: {', '.join(reasons)}")
        
        # Merit incentive analysis
        merit_analysis = analysis_result['merit_incentive_analysis']
        if merit_analysis.get('eligible'):
            notes.append("✅ Qualifies for Merit Incentive (₱5,000)")
        else:
            reasons = merit_analysis.get('reasons_denied', [])
            notes.append(f"❌ Does not qualify for Merit Incentive: {', '.join(reasons)}")
        
        # Total allowance
        total = analysis_result.get('total_allowance', 0)
        notes.append(f"💰 Total Allowance Qualified: ₱{total:,}")
        
        # Grade validation insights
        validation = analysis_result.get('grade_validation', {})
        if validation.get('warnings'):
            notes.append("\n⚠️ Grade Validation Warnings:")
            for warning in validation['warnings']:
                notes.append(f"  • {warning}")
        
        # Cross-validation results
        if 'discrepancies' in validation and validation['discrepancies']:
            notes.append("\n🔍 Grade Sheet Cross-Validation:")
            for discrepancy in validation['discrepancies']:
                notes.append(f"  • {discrepancy}")
        
        # Analysis confidence
        confidence = analysis_result.get('confidence_score', 0)
        notes.append(f"\n📊 Analysis Confidence: {confidence:.1%}")
        
        # Additional insights
        extracted_grades = analysis_result.get('extracted_grades', {})
        if extracted_grades.get('subjects_found'):
            subject_count = len(extracted_grades['subjects_found'])
            notes.append(f"📚 Detected {subject_count} subjects in grade sheet")
        
        return notes

    def _generate_grade_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on grade analysis"""
        recommendations = []
        
        basic_analysis = analysis_result.get('basic_allowance_analysis', {})
        merit_analysis = analysis_result.get('merit_incentive_analysis', {})
        validation = analysis_result.get('grade_validation', {})
        
        # Recommendations for basic allowance
        if not basic_analysis.get('eligible'):
            reasons = basic_analysis.get('reasons_denied', [])
            for reason in reasons:
                if 'GWA' in reason:
                    recommendations.append("Focus on improving overall academic performance to reach 80% GWA")
                elif 'Units' in reason:
                    recommendations.append("Consider enrolling in additional units next semester")
                elif 'failing' in reason.lower():
                    recommendations.append("Retake failed subjects to improve eligibility")
        
        # Recommendations for merit incentive
        if not merit_analysis.get('eligible') and basic_analysis.get('eligible'):
            reasons = merit_analysis.get('reasons_denied', [])
            for reason in reasons:
                if 'SWA' in reason:
                    recommendations.append("Aim for 87% SWA (GWA 1.75 or better) to qualify for merit incentive")
        
        # Validation-based recommendations
        if validation.get('issues'):
            recommendations.append("Please verify and correct the reported grade information")
        
        # Confidence-based recommendations
        confidence = analysis_result.get('confidence_score', 0)
        if confidence < 0.7:
            recommendations.append("Consider uploading a clearer grade sheet for better analysis")
        
        return recommendations

    def _calculate_analysis_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall confidence in the analysis"""
        confidence_factors = []
        
        # Validation confidence
        validation = analysis_result.get('grade_validation', {})
        if not validation.get('issues'):
            confidence_factors.append(0.3)
        if not validation.get('warnings'):
            confidence_factors.append(0.2)
        
        # Cross-validation confidence
        if validation.get('confidence_boost', 0) > 0:
            confidence_factors.append(validation['confidence_boost'])
        
        # Grade sheet analysis confidence
        extracted_grades = analysis_result.get('extracted_grades', {})
        if extracted_grades.get('analysis_confidence', 0) > 0:
            confidence_factors.append(extracted_grades['analysis_confidence'])
        
        # Base confidence for having complete data
        if analysis_result.get('basic_allowance_analysis') and analysis_result.get('merit_incentive_analysis'):
            confidence_factors.append(0.2)
        
        return min(1.0, sum(confidence_factors))


# Service instances
document_analyzer = AIDocumentAnalyzer()
grade_analyzer = AIGradeAnalyzer()
