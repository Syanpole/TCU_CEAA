"""
AI Service for TCU-CEAA Document and Grade Analysis
This module provides advanced AI capabilities for analyzing student documents and grades.
"""

import os
import re
import json
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal
import tempfile
from pathlib import Path

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
        """Extract text from various file formats"""
        filename = file_obj.name.lower()
        extracted_text = ""
        
        try:
            if filename.endswith('.pdf') and PDF_PYPDF2_AVAILABLE:
                extracted_text = self._extract_text_from_pdf(file_obj)
            elif filename.endswith(('.jpg', '.jpeg', '.png')) and (CV2_AVAILABLE and PYTESSERACT_AVAILABLE):
                extracted_text = self._extract_text_from_image(file_obj)
            elif filename.endswith(('.doc', '.docx')):
                # For demonstration - in production, use python-docx
                extracted_text = "Document text extraction not implemented for Word files"
        except Exception as e:
            extracted_text = f"Text extraction failed: {str(e)}"
        
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
        """
        analysis_result = {
            'basic_allowance_analysis': {},
            'merit_incentive_analysis': {},
            'grade_validation': {},
            'extracted_grades': {},
            'recommendations': [],
            'total_allowance': 0,
            'analysis_notes': [],
            'confidence_score': 0.0
        }
        
        try:
            # Validate input grades
            validation_result = self._validate_grade_inputs(grade_submission)
            analysis_result['grade_validation'] = validation_result
            
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
        """Analyze the uploaded grade sheet for additional validation"""
        extracted_data = {
            'text_extracted': '',
            'grades_found': [],
            'gwa_found': [],
            'swa_found': [],
            'subjects_found': [],
            'units_found': [],
            'analysis_confidence': 0.0
        }
        
        try:
            # Create AI document analyzer instance
            doc_analyzer = AIDocumentAnalyzer()
            
            # Extract text from the file
            extracted_text = doc_analyzer._extract_text_from_file(grade_sheet_file)
            extracted_data['text_extracted'] = extracted_text
            
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
        
        return extracted_data

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
