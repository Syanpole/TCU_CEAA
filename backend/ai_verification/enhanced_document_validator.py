"""
Enhanced AI Document Validator with Strict Type Checking
This module implements advanced ML-based document classification to prevent type mismatches
Author: TCU-CEAA AI Enhancement Team
Date: October 2025
"""

import os
import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import tempfile
from pathlib import Path

# Image processing
try:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

# Machine learning
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.naive_bayes import MultinomialNB
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class EnhancedDocumentValidator:
    """
    Advanced AI Document Validator with Strict Type Checking
    Prevents wrong document type submissions (e.g., school ID instead of transcript)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # STRICT document type signatures with mutual exclusivity
        self.document_signatures = {
            'transcript_of_records': {
                'aliases': ['tor', 'transcript', 'academic transcript', 'grades transcript'],
                'required_keywords': {
                    # MUST have these keywords
                    'critical': ['transcript', 'records', 'grades', 'academic', 'registrar'],
                    # Should have most of these
                    'primary': ['semester', 'course', 'subject', 'units', 'credit', 'gwa', 'grade', 'final grade'],
                    # Supporting keywords
                    'supporting': ['university', 'college', 'student', 'earned', 'completed']
                },
                # MUST NOT have these keywords - indicates wrong document type
                'forbidden_keywords': {
                    'school_id': ['student id', 'identification card', 'id number', 'valid until', 'photo'],
                    'birth_certificate': ['birth certificate', 'civil registry', 'born', 'parent'],
                    'clearance': ['clearance', 'barangay', 'good moral'],
                    'enrollment': ['newly enrolled', 'enrollment certificate', 'currently enrolled']
                },
                'document_structure': {
                    'has_table': True,        # Must have table/grid structure
                    'min_lines': 15,          # Transcripts have many lines
                    'min_words': 100,         # Substantial text content
                    'has_grades': True,       # Must contain grade values
                    'text_density': 'high'    # Dense with information
                },
                'confidence_threshold': 0.75,  # HIGH threshold for strict validation
                'strict_mode': True            # Enable strict type checking
            },
            
            'school_id': {
                'aliases': ['student id', 'id card', 'student identification'],
                'required_keywords': {
                    'critical': ['student', 'id', 'identification'],
                    'primary': ['name', 'student number', 'course', 'year'],
                    'supporting': ['university', 'college', 'tcu', 'valid']
                },
                'forbidden_keywords': {
                    'transcript': ['transcript', 'records', 'grades', 'semester', 'gwa', 'registrar'],
                    'birth_certificate': ['birth certificate', 'civil registry', 'born', 'parent'],
                    'clearance': ['clearance', 'barangay'],
                    'report_card': ['grade sheet', 'report card', 'academic record']
                },
                'document_structure': {
                    'has_table': False,       # IDs don't have tables
                    'min_lines': 5,           # Minimal text
                    'min_words': 10,          # Brief information
                    'has_photo': True,        # Usually has photo
                    'text_density': 'low'     # Sparse information
                },
                'confidence_threshold': 0.70,
                'strict_mode': True
            },
            
            'report_card': {
                'aliases': ['grade sheet', 'grade report', 'semester grades'],
                'required_keywords': {
                    'critical': ['grade', 'report', 'semester'],
                    'primary': ['subject', 'units', 'final grade', 'average', 'gwa', 'swa'],
                    'supporting': ['student', 'academic', 'year', 'period']
                },
                'forbidden_keywords': {
                    'transcript': ['transcript of records', 'official transcript'],
                    'school_id': ['student id', 'identification card', 'valid until'],
                    'birth_certificate': ['birth certificate', 'civil registry'],
                    'clearance': ['clearance', 'barangay']
                },
                'document_structure': {
                    'has_table': True,
                    'min_lines': 10,
                    'min_words': 50,
                    'has_grades': True,
                    'text_density': 'high'
                },
                'confidence_threshold': 0.75,
                'strict_mode': True
            },
            
            'birth_certificate': {
                'aliases': ['psa birth certificate', 'birth cert', 'certificate of live birth'],
                'required_keywords': {
                    'critical': ['birth', 'certificate', 'civil', 'registry'],
                    'primary': ['child', 'parent', 'mother', 'father', 'born', 'date of birth'],
                    'supporting': ['republic', 'philippines', 'registrar', 'psa', 'nso']
                },
                'forbidden_keywords': {
                    'school_docs': ['student', 'school', 'grade', 'transcript', 'semester', 'id card'],
                    'clearance': ['clearance', 'barangay'],
                    'other_certs': ['marriage', 'death', 'enrollment']
                },
                'document_structure': {
                    'has_table': False,
                    'min_lines': 10,
                    'min_words': 50,
                    'has_official_seal': True,
                    'text_density': 'medium'
                },
                'confidence_threshold': 0.80,
                'strict_mode': True
            },
            
            'enrollment_certificate': {
                'aliases': ['certificate of enrollment', 'enrollment cert'],
                'required_keywords': {
                    'critical': ['enrollment', 'enrolled', 'certificate'],
                    'primary': ['student', 'semester', 'academic year', 'course', 'status'],
                    'supporting': ['university', 'registrar', 'issued']
                },
                'forbidden_keywords': {
                    'grades': ['transcript', 'grades', 'gwa', 'grade sheet'],
                    'school_id': ['student id', 'identification card'],
                    'birth_certificate': ['birth certificate', 'civil registry'],
                    'clearance': ['clearance', 'barangay']
                },
                'document_structure': {
                    'has_table': False,
                    'min_lines': 8,
                    'min_words': 40,
                    'has_official_seal': True,
                    'text_density': 'medium'
                },
                'confidence_threshold': 0.75,
                'strict_mode': True
            },
            
            'barangay_clearance': {
                'aliases': ['brgy clearance', 'barangay certificate'],
                'required_keywords': {
                    'critical': ['barangay', 'clearance'],
                    'primary': ['resident', 'good moral', 'character', 'purpose'],
                    'supporting': ['captain', 'chairman', 'issued', 'certificate']
                },
                'forbidden_keywords': {
                    'school_docs': ['student', 'school', 'grade', 'transcript', 'enrollment', 'id card'],
                    'birth_certificate': ['birth certificate', 'civil registry'],
                    'voter': ['voter', 'comelec']
                },
                'document_structure': {
                    'has_table': False,
                    'min_lines': 8,
                    'min_words': 30,
                    'has_official_seal': True,
                    'text_density': 'low'
                },
                'confidence_threshold': 0.70,
                'strict_mode': True
            }
        }
        
        # Machine learning model for document classification
        self.vectorizer = None
        self.classifier = None
        self._initialize_ml_model()
    
    def _initialize_ml_model(self):
        """Initialize the ML-based document classifier"""
        if not ML_AVAILABLE:
            self.logger.warning("ML libraries not available - using rule-based classification only")
            return
        
        try:
            # Create training data from document signatures
            training_texts = []
            training_labels = []
            
            for doc_type, signature in self.document_signatures.items():
                # Generate training samples from keywords
                critical_keywords = signature['required_keywords'].get('critical', [])
                primary_keywords = signature['required_keywords'].get('primary', [])
                
                # Create positive samples
                for _ in range(10):  # 10 variations per document type
                    sample_text = ' '.join(
                        critical_keywords * 3 +  # Critical keywords appear more
                        primary_keywords * 2
                    )
                    training_texts.append(sample_text.lower())
                    training_labels.append(doc_type)
                
                # Create negative samples with forbidden keywords
                for forbidden_category, forbidden_words in signature.get('forbidden_keywords', {}).items():
                    sample_text = ' '.join(forbidden_words * 2)
                    training_texts.append(sample_text.lower())
                    # Label as "not_" + doc_type
                    training_labels.append(f'not_{doc_type}')
            
            # Train the classifier
            self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 3))
            X = self.vectorizer.fit_transform(training_texts)
            
            self.classifier = MultinomialNB()
            self.classifier.fit(X, training_labels)
            
            self.logger.info("✅ ML document classifier initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML classifier: {str(e)}")
            self.vectorizer = None
            self.classifier = None
    
    def validate_document_type(self, document_submission, uploaded_file) -> Dict[str, Any]:
        """
        Comprehensive document type validation with strict checking
        Returns detailed validation results
        """
        validation_result = {
            'is_correct_type': False,
            'confidence_score': 0.0,
            'declared_type': document_submission.document_type,
            'detected_types': [],
            'type_mismatch': False,
            'fraud_risk': 0.0,
            'validation_errors': [],
            'validation_warnings': [],
            'extracted_text': '',
            'recommendation': 'reject'
        }
        
        try:
            declared_type = document_submission.document_type
            
            # Step 1: Extract text from document
            extracted_text = self._extract_document_text(uploaded_file)
            validation_result['extracted_text'] = extracted_text
            
            if not extracted_text or len(extracted_text.strip()) < 20:
                validation_result['validation_errors'].append(
                    "❌ CRITICAL: Insufficient text content - document may be blank or unreadable"
                )
                validation_result['fraud_risk'] = 0.9
                return validation_result
            
            # Step 2: Detect document type using multiple methods
            rule_based_detection = self._rule_based_type_detection(extracted_text, declared_type)
            validation_result.update(rule_based_detection)
            
            # Step 3: ML-based classification (if available)
            if self.classifier is not None:
                ml_detection = self._ml_based_type_detection(extracted_text, declared_type)
                # Combine rule-based and ML results
                validation_result = self._combine_detection_results(
                    validation_result, ml_detection, declared_type
                )
            
            # Step 4: Check for forbidden keywords (type mismatch detection)
            forbidden_check = self._check_forbidden_keywords(extracted_text, declared_type)
            validation_result.update(forbidden_check)
            
            # Step 5: Validate document structure
            structure_validation = self._validate_document_structure(extracted_text, uploaded_file, declared_type)
            validation_result.update(structure_validation)
            
            # Step 6: Calculate final confidence and make decision
            final_decision = self._make_validation_decision(validation_result, declared_type)
            validation_result.update(final_decision)
            
        except Exception as e:
            self.logger.error(f"Document validation error: {str(e)}")
            validation_result['validation_errors'].append(f"Validation system error: {str(e)}")
            validation_result['recommendation'] = 'manual_review'
        
        return validation_result
    
    def _extract_document_text(self, uploaded_file) -> str:
        """Extract text from uploaded file"""
        filename = uploaded_file.name.lower()
        extracted_text = ""
        
        try:
            if filename.endswith(('.jpg', '.jpeg', '.png')) and CV_AVAILABLE:
                extracted_text = self._extract_text_from_image(uploaded_file)
            elif filename.endswith('.pdf'):
                extracted_text = self._extract_text_from_pdf(uploaded_file)
            else:
                extracted_text = ""
        except Exception as e:
            self.logger.error(f"Text extraction error: {str(e)}")
        
        return extracted_text
    
    def _extract_text_from_image(self, uploaded_file) -> str:
        """Extract text from image using OCR"""
        if not CV_AVAILABLE:
            return ""
        
        try:
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Load and preprocess image
            image = cv2.imread(temp_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance for better OCR
            denoised = cv2.fastNlMeansDenoising(gray)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # OCR extraction
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(enhanced, config=custom_config)
            
            # Clean up
            os.unlink(temp_path)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Image text extraction failed: {str(e)}")
            return ""
    
    def _extract_text_from_pdf(self, uploaded_file) -> str:
        """Extract text from PDF"""
        try:
            # Try multiple PDF libraries
            try:
                import PyPDF2
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                text = ""
                with open(temp_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                
                os.unlink(temp_path)
                return text.strip()
                
            except ImportError:
                return ""
                
        except Exception as e:
            self.logger.error(f"PDF text extraction failed: {str(e)}")
            return ""
    
    def _rule_based_type_detection(self, extracted_text: str, declared_type: str) -> Dict[str, Any]:
        """Rule-based document type detection"""
        text_lower = extracted_text.lower()
        
        detection_result = {
            'detected_types': [],
            'type_scores': {},
            'is_correct_type': False,
            'confidence_score': 0.0
        }
        
        # Check against all document types
        for doc_type, signature in self.document_signatures.items():
            score = self._calculate_type_match_score(text_lower, signature)
            detection_result['type_scores'][doc_type] = score
            
            if score >= signature['confidence_threshold']:
                detection_result['detected_types'].append(doc_type)
        
        # Check if declared type matches
        if declared_type in detection_result['type_scores']:
            detection_result['confidence_score'] = detection_result['type_scores'][declared_type]
            detection_result['is_correct_type'] = (
                declared_type in detection_result['detected_types']
            )
        
        return detection_result
    
    def _calculate_type_match_score(self, text: str, signature: Dict) -> float:
        """Calculate how well text matches a document type signature"""
        score = 0.0
        weights = {'critical': 0.5, 'primary': 0.3, 'supporting': 0.2}
        
        for keyword_type, keywords in signature['required_keywords'].items():
            if keyword_type not in weights:
                continue
            
            matches = sum(1 for keyword in keywords if keyword in text)
            match_ratio = matches / len(keywords) if keywords else 0
            score += match_ratio * weights[keyword_type]
        
        return score
    
    def _ml_based_type_detection(self, extracted_text: str, declared_type: str) -> Dict[str, Any]:
        """ML-based document type classification"""
        ml_result = {
            'ml_predicted_type': None,
            'ml_confidence': 0.0,
            'ml_probabilities': {}
        }
        
        if self.classifier is None or self.vectorizer is None:
            return ml_result
        
        try:
            # Transform text
            X = self.vectorizer.transform([extracted_text.lower()])
            
            # Predict
            predicted_label = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]
            
            # Get class labels
            classes = self.classifier.classes_
            
            # Build probability dictionary
            for cls, prob in zip(classes, probabilities):
                if not cls.startswith('not_'):  # Only include positive predictions
                    ml_result['ml_probabilities'][cls] = float(prob)
            
            # Get top prediction (excluding negative classes)
            positive_probs = {k: v for k, v in ml_result['ml_probabilities'].items()}
            if positive_probs:
                ml_result['ml_predicted_type'] = max(positive_probs, key=positive_probs.get)
                ml_result['ml_confidence'] = positive_probs[ml_result['ml_predicted_type']]
            
        except Exception as e:
            self.logger.error(f"ML classification error: {str(e)}")
        
        return ml_result
    
    def _combine_detection_results(self, rule_result: Dict, ml_result: Dict, declared_type: str) -> Dict:
        """Combine rule-based and ML detection results"""
        combined = rule_result.copy()
        
        # Add ML predictions to detected types if confident
        if ml_result.get('ml_predicted_type') and ml_result.get('ml_confidence', 0) > 0.6:
            if ml_result['ml_predicted_type'] not in combined['detected_types']:
                combined['detected_types'].append(ml_result['ml_predicted_type'])
        
        # Adjust confidence score using ML
        if ml_result.get('ml_probabilities'):
            ml_score = ml_result['ml_probabilities'].get(declared_type, 0.0)
            # Weight: 70% rule-based, 30% ML
            combined['confidence_score'] = (
                combined['confidence_score'] * 0.7 +
                ml_score * 0.3
            )
        
        combined['ml_result'] = ml_result
        return combined
    
    def _check_forbidden_keywords(self, extracted_text: str, declared_type: str) -> Dict[str, Any]:
        """Check for forbidden keywords that indicate wrong document type"""
        forbidden_check = {
            'type_mismatch': False,
            'forbidden_matches': [],
            'mismatch_indicators': []
        }
        
        if declared_type not in self.document_signatures:
            return forbidden_check
        
        text_lower = extracted_text.lower()
        signature = self.document_signatures[declared_type]
        forbidden_keywords = signature.get('forbidden_keywords', {})
        
        # Check each category of forbidden keywords
        for wrong_type, keywords in forbidden_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                forbidden_check['forbidden_matches'].extend(matches)
                forbidden_check['mismatch_indicators'].append({
                    'suggested_type': wrong_type,
                    'found_keywords': matches
                })
        
        # Determine if there's a strong type mismatch
        if len(forbidden_check['forbidden_matches']) >= 2:  # 2+ forbidden keywords = mismatch
            forbidden_check['type_mismatch'] = True
        
        return forbidden_check
    
    def _validate_document_structure(self, extracted_text: str, uploaded_file, declared_type: str) -> Dict[str, Any]:
        """Validate document structure matches expected type"""
        structure_validation = {
            'structure_match': False,
            'structure_issues': []
        }
        
        if declared_type not in self.document_signatures:
            return structure_validation
        
        signature = self.document_signatures[declared_type]
        expected_structure = signature.get('document_structure', {})
        
        text_lines = extracted_text.split('\n')
        text_words = extracted_text.split()
        
        issues = []
        score = 0.0
        max_score = 0.0
        
        # Check minimum lines
        if 'min_lines' in expected_structure:
            max_score += 1
            min_lines = expected_structure['min_lines']
            if len(text_lines) >= min_lines:
                score += 1
            else:
                issues.append(f"Too few lines: {len(text_lines)} < {min_lines} expected")
        
        # Check minimum words
        if 'min_words' in expected_structure:
            max_score += 1
            min_words = expected_structure['min_words']
            if len(text_words) >= min_words:
                score += 1
            else:
                issues.append(f"Too few words: {len(text_words)} < {min_words} expected")
        
        # Check for grades (if required)
        if expected_structure.get('has_grades'):
            max_score += 1
            # Look for grade patterns (numbers 1.0-5.0 or 65-100)
            grade_pattern = r'\b(?:[1-5]\.\d{1,2}|[6-9]\d|100)\b'
            if re.search(grade_pattern, extracted_text):
                score += 1
            else:
                issues.append("No grade values detected")
        
        # Check for table structure (if required)
        if expected_structure.get('has_table'):
            max_score += 1
            # Simple heuristic: tables have consistent spacing/alignment
            # Look for repeated patterns of spaces or tabs
            if self._detect_table_structure(extracted_text):
                score += 1
            else:
                issues.append("No table structure detected")
        
        # Calculate structure match
        if max_score > 0:
            structure_match_ratio = score / max_score
            structure_validation['structure_match'] = structure_match_ratio >= 0.6
        
        structure_validation['structure_issues'] = issues
        return structure_validation
    
    def _detect_table_structure(self, text: str) -> bool:
        """Detect if text contains table-like structure"""
        lines = text.split('\n')
        
        # Check for consistent spacing patterns (indicates columns)
        space_patterns = []
        for line in lines:
            if len(line.strip()) > 10:  # Ignore short lines
                # Count consecutive spaces
                spaces = re.findall(r'\s{2,}', line)
                space_patterns.append(len(spaces))
        
        # If many lines have similar spacing patterns, likely a table
        if len(space_patterns) > 5:
            avg_spaces = sum(space_patterns) / len(space_patterns)
            if avg_spaces >= 2:  # At least 2 column separators on average
                return True
        
        return False
    
    def _make_validation_decision(self, validation_result: Dict, declared_type: str) -> Dict[str, Any]:
        """Make final validation decision"""
        decision = {
            'recommendation': 'reject',
            'validation_errors': validation_result.get('validation_errors', []),
            'validation_warnings': validation_result.get('validation_warnings', []),
            'fraud_risk': 0.0
        }
        
        confidence = validation_result.get('confidence_score', 0.0)
        is_correct_type = validation_result.get('is_correct_type', False)
        type_mismatch = validation_result.get('type_mismatch', False)
        detected_types = validation_result.get('detected_types', [])
        structure_match = validation_result.get('structure_match', False)
        
        # CRITICAL ERROR: Type mismatch detected
        if type_mismatch:
            mismatch_indicators = validation_result.get('mismatch_indicators', [])
            decision['validation_errors'].append(
                f"❌ CRITICAL ERROR: Document type mismatch detected!"
            )
            for indicator in mismatch_indicators:
                suggested = indicator['suggested_type']
                keywords = indicator['found_keywords']
                decision['validation_errors'].append(
                    f"   • Document appears to be a {suggested}: found keywords {keywords}"
                )
            decision['validation_errors'].append(
                f"   • Expected: {declared_type}"
            )
            decision['fraud_risk'] = 0.95
            decision['recommendation'] = 'reject'
            return decision
        
        # Check if detected types don't include declared type
        if detected_types and declared_type not in detected_types:
            decision['validation_errors'].append(
                f"❌ Document does not match declared type '{declared_type}'"
            )
            decision['validation_errors'].append(
                f"   • Detected as: {', '.join(detected_types) if detected_types else 'Unknown'}"
            )
            decision['fraud_risk'] = 0.8
            decision['recommendation'] = 'reject'
            return decision
        
        # Check confidence threshold
        if declared_type in self.document_signatures:
            threshold = self.document_signatures[declared_type]['confidence_threshold']
            
            if confidence < threshold:
                decision['validation_errors'].append(
                    f"❌ Low confidence ({confidence:.1%}) - below threshold ({threshold:.1%})"
                )
                decision['fraud_risk'] = 0.6
                decision['recommendation'] = 'reject'
                return decision
        
        # Check structure
        if not structure_match:
            structure_issues = validation_result.get('structure_issues', [])
            decision['validation_warnings'].append(
                "⚠️ Document structure doesn't fully match expected format:"
            )
            for issue in structure_issues:
                decision['validation_warnings'].append(f"   • {issue}")
            decision['fraud_risk'] = 0.3
        
        # SUCCESS: All checks passed
        if is_correct_type and confidence >= 0.7 and structure_match:
            decision['recommendation'] = 'approve'
            decision['fraud_risk'] = 0.0
        elif is_correct_type and confidence >= 0.6:
            decision['recommendation'] = 'approve'
            decision['fraud_risk'] = 0.1
            decision['validation_warnings'].append(
                "⚠️ Approved with moderate confidence - consider manual review"
            )
        else:
            decision['recommendation'] = 'manual_review'
            decision['fraud_risk'] = 0.4
            decision['validation_warnings'].append(
                "⚠️ Manual review recommended - confidence borderline"
            )
        
        return decision


# Global instance
enhanced_validator = EnhancedDocumentValidator()
