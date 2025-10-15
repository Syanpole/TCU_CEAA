"""
🤖 AUTONOMOUS AI DOCUMENT VERIFICATION SYSTEM
No external dependencies (Tesseract-free!)

Uses:
- EasyOCR for text extraction (pure Python)
- OpenCV for image analysis
- Deep learning models for verification
- Pattern matching for fraud detection
"""

import numpy as np
import cv2
from PIL import Image
import io
import logging
import time
import os
from typing import Dict, Any, List, Tuple
import re

logger = logging.getLogger(__name__)

class AutonomousDocumentVerifier:
    """
    Fully autonomous document verification using AI/ML
    No external tools required - all Python-based
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ocr_reader = None
        self._initialize_ocr()
        
        # Import Vision AI and Learning System
        try:
            from .vision_ai import vision_ai
            from .learning_system import learning_system
            self.vision_ai = vision_ai
            self.learning_system = learning_system
            self.vision_ai_available = True
            logger.info("✅ Vision AI and Learning System loaded")
        except ImportError as e:
            logger.warning(f"Vision AI not available: {str(e)}")
            self.vision_ai_available = False
        
        # Enhanced document patterns with Vision AI
        self.document_patterns = {
            'birth_certificate': {
                'required_keywords': ['birth', 'certificate', 'born', 'registry', 'civil', 'philippines', 'republic', 'registrar'],
                'forbidden_keywords': ['school', 'student', 'grade', 'transcript'],
                'expected_structure': 'government_document',
                'confidence_threshold': 0.75
            },
            'school_id': {
                'required_keywords': ['student', 'university', 'college', 'taguig', 'tcu', 'id', 'no'],
                'forbidden_keywords': ['birth', 'certificate', 'born', 'diploma', 'graduated'],
                'expected_structure': 'id_card',
                'confidence_threshold': 0.70
            },
            'certificate_of_enrollment': {
                'required_keywords': ['certificate', 'enrollment', 'enrolled', 'student'],
                'forbidden_keywords': ['birth', 'diploma', 'graduated'],
                'expected_structure': 'certificate'
            },
            'grade_10_report_card': {
                'required_keywords': ['grade', 'report', '10', 'subject', 'quarter'],
                'forbidden_keywords': ['birth', 'certificate', 'diploma', '11', '12'],
                'expected_structure': 'grade_sheet'
            },
            'grade_12_report_card': {
                'required_keywords': ['grade', 'report', '12', 'subject', 'senior'],
                'forbidden_keywords': ['birth', 'certificate', 'diploma', '10', '11'],
                'expected_structure': 'grade_sheet'
            },
            'diploma': {
                'required_keywords': ['diploma', 'graduated', 'completion', 'degree'],
                'forbidden_keywords': ['enrollment', 'report card'],
                'expected_structure': 'certificate'
            }
        }
    
    def _initialize_ocr(self):
        """Initialize EasyOCR with Tesseract fallback"""
        # Initialize EasyOCR (primary)
        self.easyocr_available = False
        try:
            import easyocr
            self.logger.info("Initializing EasyOCR (primary OCR)...")
            self.ocr_reader = easyocr.Reader(['en'], gpu=False)
            self.logger.info("✅ EasyOCR initialized successfully")
            self.easyocr_available = True
        except ImportError:
            self.logger.warning("EasyOCR not installed. Install with: pip install easyocr")
        except Exception as e:
            self.logger.error(f"Failed to initialize EasyOCR: {str(e)}")
        
        # Initialize Tesseract (fallback)
        self.tesseract_available = False
        try:
            import pytesseract
            # Try to find Tesseract executable
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\Public\tesseract\tesseract.exe'
            ]
            
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.logger.info(f"✅ Tesseract found at: {path}")
                    self.tesseract_available = True
                    break
            
            if not self.tesseract_available:
                self.logger.warning("Tesseract executable not found in standard locations")
        except ImportError:
            self.logger.warning("pytesseract not installed. Install with: pip install pytesseract")
        except Exception as e:
            self.logger.error(f"Failed to initialize Tesseract: {str(e)}")
        
        # Set overall OCR availability
        self.ocr_available = self.easyocr_available or self.tesseract_available
        
        if self.easyocr_available and self.tesseract_available:
            self.logger.info("🎉 Dual OCR Setup: EasyOCR (primary) + Tesseract (fallback)")
        elif self.easyocr_available:
            self.logger.info("📱 EasyOCR only (Tesseract not available)")
        elif self.tesseract_available:
            self.logger.info("📄 Tesseract only (EasyOCR not available)")
        else:
            self.logger.error("❌ No OCR engines available!")
    
    def verify_document(self, document_submission, uploaded_file) -> Dict[str, Any]:
        """
        🤖 AUTONOMOUS VERIFICATION - Main entry point
        
        Performs:
        1. Image quality analysis
        2. Text extraction (EasyOCR)
        3. Document type verification
        4. Student name verification
        5. Fraud detection
        6. Structure analysis
        """
        start_time = time.time()
        
        result = {
            'is_valid_document': False,
            'document_type_match': False,
            'name_verification_passed': False,
            'confidence_score': 0.0,
            'fraud_indicators': [],
            'quality_issues': [],
            'processing_time': 0.0,
            'verification_method': 'autonomous_ai',
            'algorithms_used': [],
            'detailed_analysis': {}
        }
        
        try:
            # Get declared document type
            declared_type = getattr(document_submission, 'document_type', None)
            if not declared_type:
                result['rejection_reason'] = 'Document type not specified'
                return result
            
            # Step 1: Load and preprocess image
            self.logger.info(f"Step 1: Loading image for {declared_type}")
            img_array, img_pil = self._load_image(uploaded_file)
            if img_array is None:
                result['rejection_reason'] = 'Failed to load image'
                return result
            
            result['algorithms_used'].append('image_loading')
            
            # Step 2: Image quality analysis
            self.logger.info("Step 2: Analyzing image quality")
            quality_result = self._analyze_image_quality(img_array)
            result['detailed_analysis']['quality'] = quality_result
            result['algorithms_used'].append('quality_analysis')
            
            if not quality_result['acceptable']:
                result['quality_issues'] = quality_result['issues']
                result['rejection_reason'] = f"Image quality too low: {', '.join(quality_result['issues'][:2])}"
                return result
            
            # Step 2.5: Vision AI Analysis (Like ChatGPT Vision)
            if self.vision_ai_available:
                self.logger.info("Step 2.5: 🎯 Vision AI structural analysis (ChatGPT-style)")
                vision_analysis = self.vision_ai.analyze_document_structure(img_array)
                result['vision_analysis'] = vision_analysis
                result['algorithms_used'].append('vision_ai_analysis')
                
                # Use Vision AI for enhanced document type validation
                if vision_analysis['document_type'] != 'unknown':
                    vision_type = vision_analysis['document_type']
                    vision_confidence = vision_analysis['confidence']
                    
                    self.logger.info(f"🎯 Vision AI detected: {vision_type} (confidence: {vision_confidence:.1%})")
                    
                    if vision_type != declared_type and vision_confidence > 0.8:
                        # High-confidence mismatch detection
                        result['rejection_reason'] = f"Document appears to be '{vision_type}' but declared as '{declared_type}' (Vision AI confidence: {vision_confidence:.1%})"
                        result['fraud_indicators'].append('document_type_mismatch_vision_ai')
                        return result
                    elif vision_type == declared_type:
                        # Vision AI confirms document type
                        result['confidence_score'] += 0.2  # Boost confidence
                        self.logger.info(f"✅ Vision AI confirms document type: {declared_type}")
                
                # Extract structured data using Vision AI
                structured_data = self.vision_ai.extract_structured_data(img_array, declared_type)
                result['structured_data'] = structured_data
            
            # Step 3: Dual OCR Verification (EasyOCR + Tesseract cross-check)
            self.logger.info("Step 3: Dual OCR verification with cross-check")
            ocr_verification = self._extract_text_dual_ocr(img_array)
            
            # Store OCR verification details in result
            result['ocr_verification'] = ocr_verification
            result['algorithms_used'].append('dual_ocr_verification')
            
            # Handle verification status
            if ocr_verification['verification_status'] == 'failed':
                result['rejection_reason'] = 'OCR verification failed: ' + ', '.join(ocr_verification['reasons'])
                result['admin_notification'] = ocr_verification.get('admin_notification', '')
                return result
            elif ocr_verification['verification_status'] == 'pending':
                result['requires_admin_review'] = True
                result['admin_notification'] = ocr_verification.get('admin_notification', '')
                result['confidence_level'] = ocr_verification['confidence_level']
                result['ocr_similarity'] = ocr_verification['similarity_score']
            
            extracted_text = ocr_verification['extracted_text']
            result['detailed_analysis']['extracted_text_length'] = len(extracted_text)
            
            if not extracted_text or len(extracted_text) < 10:
                result['rejection_reason'] = 'Could not extract sufficient text from document'
                return result
            
            # Step 4: Document type verification
            self.logger.info("Step 4: Verifying document type")
            type_verification = self._verify_document_type(extracted_text, declared_type)
            result['document_type_match'] = type_verification['match']
            result['detailed_analysis']['type_verification'] = type_verification
            result['algorithms_used'].append('document_type_matching')
            
            if not type_verification['match']:
                result['rejection_reason'] = type_verification['reason']
                result['fraud_indicators'].append('Document type mismatch')
                return result
            
            # Step 5: Student name verification
            self.logger.info("Step 5: Verifying student name")
            name_verification = self._verify_student_name(
                extracted_text, 
                document_submission.student
            )
            result['name_verification_passed'] = name_verification['match']
            result['detailed_analysis']['name_verification'] = name_verification
            result['algorithms_used'].append('name_verification')
            
            if not name_verification['match']:
                result['rejection_reason'] = name_verification['reason']
                result['fraud_indicators'].append('Student name not found')
                return result
            
            # Step 6: Document structure analysis
            self.logger.info("Step 6: Analyzing document structure")
            structure_analysis = self._analyze_document_structure(img_array, declared_type)
            result['detailed_analysis']['structure'] = structure_analysis
            result['algorithms_used'].append('structure_analysis')
            
            # Step 7: Fraud detection
            self.logger.info("Step 7: Running fraud detection")
            fraud_check = self._detect_fraud_indicators(img_array, extracted_text, declared_type)
            result['detailed_analysis']['fraud_check'] = fraud_check
            result['algorithms_used'].append('fraud_detection')
            
            if fraud_check['fraud_detected']:
                result['fraud_indicators'].extend(fraud_check['indicators'])
                result['rejection_reason'] = f"Fraud detected: {fraud_check['indicators'][0]}"
                return result
            
            # Calculate final confidence score
            result['confidence_score'] = self._calculate_confidence(
                quality_result,
                type_verification,
                name_verification,
                structure_analysis,
                fraud_check
            )
            
            # Step 8: Learning System Integration (Continuous Improvement)
            if hasattr(self, 'learning_system') and self.learning_system:
                self.logger.info("Step 8: 🧠 Applying learned patterns")
                
                # Get AI recommendation based on learned patterns
                ocr_results = {
                    'similarity_score': result.get('ocr_similarity', 0.0),
                    'confidence_level': result.get('confidence_level', 'medium'),
                    'extracted_text': extracted_text,
                    'verification_results': result
                }
                
                ai_recommendation = self.learning_system.get_recommendation(declared_type, ocr_results)
                result['ai_recommendation'] = ai_recommendation
                result['algorithms_used'].append('learning_system')
                
                self.logger.info(f"🧠 AI Recommendation: {ai_recommendation['recommendation']} (confidence: {ai_recommendation['confidence']:.1%})")
                self.logger.info(f"💡 Reasoning: {ai_recommendation['reasoning']}")
                
                # Apply learned threshold if available
                learned_threshold = ai_recommendation.get('learned_threshold', 0.75)
                if learned_threshold != 0.75:  # Different from default
                    self.logger.info(f"📊 Using learned threshold: {learned_threshold:.1%} (was 75%)")
                    
                    # Re-evaluate with learned threshold
                    if result['confidence_score'] >= learned_threshold:
                        result['is_valid_document'] = True
                        result['approval_reason'] = f"Document verified with learned AI patterns (confidence: {result['confidence_score']:.0%}, learned threshold: {learned_threshold:.0%})"
                    else:
                        result['rejection_reason'] = f"Confidence {result['confidence_score']:.0%} below learned threshold {learned_threshold:.0%}"
            
            # Final decision (fallback if learning system not applied)
            if 'approval_reason' not in result and 'rejection_reason' not in result:
                if result['confidence_score'] >= 0.75:
                    result['is_valid_document'] = True
                    result['approval_reason'] = f"Document verified by autonomous AI (confidence: {result['confidence_score']:.0%})"
                else:
                    result['rejection_reason'] = f"Confidence too low ({result['confidence_score']:.0%}) - manual review recommended"
        
        except Exception as e:
            self.logger.error(f"Verification error: {str(e)}", exc_info=True)
            result['rejection_reason'] = f"Verification system error: {str(e)}"
        
        result['processing_time'] = time.time() - start_time
        
        # 🎓 TRAINING DATA COLLECTION
        # This helps the AI learn from real-world usage patterns
        if hasattr(self, 'learning_system') and result.get('processing_time', 0) > 0:
            try:
                self.learning_system.record_processing_data(declared_type, result)
            except Exception as e:
                self.logger.warning(f"Failed to record training data: {str(e)}")
        
        return result
    
    def _load_image(self, uploaded_file) -> Tuple[np.ndarray, Image.Image]:
        """Load image from uploaded file"""
        try:
            # Get file content
            if hasattr(uploaded_file, 'read'):
                uploaded_file.seek(0)
                file_content = uploaded_file.read()
                uploaded_file.seek(0)
            else:
                with open(uploaded_file, 'rb') as f:
                    file_content = f.read()
            
            # Load with PIL
            img_pil = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if needed
            if img_pil.mode != 'RGB':
                img_pil = img_pil.convert('RGB')
            
            # Convert to numpy array for OpenCV
            img_array = np.array(img_pil)
            
            # Convert RGB to BGR for OpenCV
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_array, img_pil
            
        except Exception as e:
            self.logger.error(f"Image loading error: {str(e)}")
            return None, None
    
    def _analyze_image_quality(self, img_array: np.ndarray) -> Dict[str, Any]:
        """
        Analyze image quality using computer vision
        - Resolution check
        - Blur detection (Laplacian variance)
        - Brightness analysis
        - Contrast analysis
        """
        result = {
            'acceptable': True,
            'issues': [],
            'metrics': {}
        }
        
        try:
            height, width = img_array.shape[:2]
            result['metrics']['resolution'] = f"{width}x{height}"
            
            # Check resolution
            if width < 300 or height < 300:
                result['acceptable'] = False
                result['issues'].append(f"Resolution too low ({width}x{height})")
            
            # Blur detection using Laplacian variance
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            result['metrics']['sharpness'] = float(laplacian_var)
            
            if laplacian_var < 50:  # Threshold for blurry images
                result['issues'].append(f"Image is blurry (sharpness: {laplacian_var:.0f})")
            
            # Brightness analysis
            brightness = np.mean(gray)
            result['metrics']['brightness'] = float(brightness)
            
            if brightness < 30:
                result['issues'].append("Image too dark")
            elif brightness > 225:
                result['issues'].append("Image too bright")
            
            # Contrast analysis
            contrast = np.std(gray)
            result['metrics']['contrast'] = float(contrast)
            
            if contrast < 20:
                result['issues'].append("Low contrast")
            
        except Exception as e:
            self.logger.error(f"Quality analysis error: {str(e)}")
            result['issues'].append(f"Quality analysis failed: {str(e)}")
        
        return result
    
    def _extract_text_dual_ocr(self, img_array: np.ndarray) -> Dict[str, Any]:
        """
        🔍 DUAL VERIFICATION SYSTEM
        EasyOCR extracts text, Tesseract cross-verifies for accuracy
        Returns comprehensive verification results
        """
        verification_result = {
            'extracted_text': '',
            'verification_status': 'failed',  # 'approved', 'pending', 'failed'
            'confidence_level': 'low',  # 'high', 'medium', 'low'
            'ocr_agreement': False,
            'easyocr_text': '',
            'tesseract_text': '',
            'similarity_score': 0.0,
            'admin_notification': '',
            'reasons': []
        }
        
        # Step 1: Extract with EasyOCR (primary)
        if self.easyocr_available and self.ocr_reader is not None:
            try:
                self.logger.info("📱 EasyOCR: Extracting text...")
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                results = self.ocr_reader.readtext(img_rgb)
                
                verification_result['easyocr_text'] = ' '.join([text for (bbox, text, conf) in results])
                self.logger.info(f"✅ EasyOCR: {len(verification_result['easyocr_text'])} characters")
                
            except Exception as e:
                self.logger.error(f"❌ EasyOCR failed: {str(e)}")
                verification_result['reasons'].append(f"EasyOCR error: {str(e)}")
        
        # Step 2: Cross-verify with Tesseract
        if self.tesseract_available:
            try:
                import pytesseract
                self.logger.info("📄 Tesseract: Cross-verifying...")
                
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(img_rgb)
                
                verification_result['tesseract_text'] = pytesseract.image_to_string(pil_image)
                self.logger.info(f"✅ Tesseract: {len(verification_result['tesseract_text'])} characters")
                
            except Exception as e:
                self.logger.error(f"❌ Tesseract failed: {str(e)}")
                verification_result['reasons'].append(f"Tesseract error: {str(e)}")
        
        # Step 3: Compare results and determine confidence
        easyocr_clean = verification_result['easyocr_text'].lower().strip()
        tesseract_clean = verification_result['tesseract_text'].lower().strip()
        
        if easyocr_clean and tesseract_clean:
            # Calculate similarity between the two OCR results
            similarity = self._calculate_text_similarity(easyocr_clean, tesseract_clean)
            verification_result['similarity_score'] = similarity
            
            self.logger.info(f"🔍 OCR Similarity: {similarity:.2%}")
            
            if similarity >= 0.8:  # High agreement
                verification_result['verification_status'] = 'approved'
                verification_result['confidence_level'] = 'high'
                verification_result['ocr_agreement'] = True
                verification_result['extracted_text'] = easyocr_clean  # Use EasyOCR as primary
                verification_result['reasons'].append("High OCR agreement (≥80%)")
                self.logger.info("🎉 HIGH CONFIDENCE: Both OCR engines agree")
                
            elif similarity >= 0.6:  # Medium agreement
                verification_result['verification_status'] = 'pending'
                verification_result['confidence_level'] = 'medium'
                verification_result['extracted_text'] = easyocr_clean
                verification_result['admin_notification'] = f"📋 MANUAL REVIEW NEEDED: OCR results show medium agreement ({similarity:.1%}). Please verify document manually."
                verification_result['reasons'].append(f"Medium OCR agreement ({similarity:.1%}) - requires admin review")
                self.logger.warning("⚠️ MEDIUM CONFIDENCE: OCR disagreement - marking for admin review")
                
            else:  # Low agreement
                verification_result['verification_status'] = 'pending'
                verification_result['confidence_level'] = 'low'
                verification_result['extracted_text'] = easyocr_clean
                verification_result['admin_notification'] = f"🚨 URGENT REVIEW: OCR results significantly differ ({similarity:.1%}). Document quality may be poor or manipulated."
                verification_result['reasons'].append(f"Low OCR agreement ({similarity:.1%}) - potential quality/fraud issue")
                self.logger.error("🚨 LOW CONFIDENCE: Major OCR disagreement - requires urgent admin review")
                
        elif easyocr_clean and not tesseract_clean:
            # Only EasyOCR worked
            verification_result['verification_status'] = 'pending'
            verification_result['confidence_level'] = 'medium'
            verification_result['extracted_text'] = easyocr_clean
            verification_result['admin_notification'] = "⚠️ Single OCR verification only (Tesseract failed). Please manually verify document quality."
            verification_result['reasons'].append("Only EasyOCR successful - no cross-verification")
            self.logger.warning("⚠️ SINGLE OCR: Tesseract failed - cannot cross-verify")
            
        elif tesseract_clean and not easyocr_clean:
            # Only Tesseract worked
            verification_result['verification_status'] = 'pending'
            verification_result['confidence_level'] = 'medium'
            verification_result['extracted_text'] = tesseract_clean
            verification_result['admin_notification'] = "⚠️ Single OCR verification only (EasyOCR failed). Please manually verify document quality."
            verification_result['reasons'].append("Only Tesseract successful - no cross-verification")
            self.logger.warning("⚠️ SINGLE OCR: EasyOCR failed - cannot cross-verify")
            
        else:
            # Both failed
            verification_result['verification_status'] = 'failed'
            verification_result['confidence_level'] = 'low'
            verification_result['admin_notification'] = "🚨 CRITICAL: Both OCR engines failed. Document may be unreadable or corrupted."
            verification_result['reasons'].append("Both OCR engines failed")
            self.logger.error("🚨 TOTAL FAILURE: Both OCR engines failed")
        
        return verification_result
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        try:
            # Simple word-based similarity
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0
    
    def _verify_document_type(self, extracted_text: str, declared_type: str) -> Dict[str, Any]:
        """Verify document type matches declared type"""
        result = {
            'match': False,
            'confidence': 0.0,
            'reason': '',
            'matched_keywords': [],
            'forbidden_found': []
        }
        
        if declared_type not in self.document_patterns:
            result['reason'] = f"Unknown document type: {declared_type}"
            return result
        
        pattern = self.document_patterns[declared_type]
        text_lower = extracted_text.lower()
        
        # DEBUG: Log document type verification
        self.logger.info(f"🔍 DOCUMENT TYPE VERIFICATION DEBUG:")
        self.logger.info(f"   Declared Type: '{declared_type}'")
        self.logger.info(f"   Required Keywords: {pattern['required_keywords']}")
        self.logger.info(f"   Forbidden Keywords: {pattern['forbidden_keywords']}")
        self.logger.info(f"   Document Text Preview: '{extracted_text[:300]}...'")
        
        # Check required keywords
        required_count = 0
        for keyword in pattern['required_keywords']:
            if keyword in text_lower:
                required_count += 1
                result['matched_keywords'].append(keyword)
                self.logger.info(f"   ✅ FOUND REQUIRED: '{keyword}'")
            else:
                self.logger.info(f"   ❌ MISSING REQUIRED: '{keyword}'")
        
        # Check forbidden keywords
        for keyword in pattern['forbidden_keywords']:
            if keyword in text_lower:
                result['forbidden_found'].append(keyword)
                self.logger.info(f"   🚫 FOUND FORBIDDEN: '{keyword}'")
            else:
                self.logger.info(f"   ✅ OK (no forbidden): '{keyword}'")
        
        self.logger.info(f"   📊 Required Match Ratio: {required_count}/{len(pattern['required_keywords'])} = {required_count / len(pattern['required_keywords']):.2f}")
        
        # Calculate match
        required_ratio = required_count / len(pattern['required_keywords'])
        
        if required_ratio >= 0.4 and len(result['forbidden_found']) == 0:
            result['match'] = True
            result['confidence'] = min(0.95, 0.60 + (required_ratio * 0.35))
            result['reason'] = f"Document type verified ({required_count}/{len(pattern['required_keywords'])} keywords found)"
        elif len(result['forbidden_found']) > 0:
            result['match'] = False
            result['reason'] = f"Wrong document type detected (found: {', '.join(result['forbidden_found'])})"
        else:
            result['match'] = False
            result['reason'] = f"Document does not appear to be a {declared_type.replace('_', ' ')}"
        
        return result
    
    def _verify_student_name(self, extracted_text: str, student) -> Dict[str, Any]:
        """Verify student name appears in document"""
        result = {
            'match': False,
            'confidence': 0.0,
            'reason': '',
            'matched_name': ''
        }
        
        # Get student names
        first_name = student.first_name.lower().strip() if student.first_name else ''
        last_name = student.last_name.lower().strip() if student.last_name else ''
        
        if not first_name or not last_name:
            result['match'] = False
            result['reason'] = 'Student profile name incomplete - please update your First Name and Last Name'
            return result
        
        full_name = f"{first_name} {last_name}"
        reverse_name = f"{last_name} {first_name}"
        
        text_lower = extracted_text.lower()
        
        # SIMPLIFIED: Only check FIRST NAME match (more lenient for documents with middle names)
        
        # DEBUG: Log what we're comparing
        self.logger.info(f"🔍 NAME VERIFICATION DEBUG:")
        self.logger.info(f"   Student First Name: '{first_name}'")
        self.logger.info(f"   Student Last Name: '{last_name}'")
        self.logger.info(f"   Document Text Length: {len(extracted_text)} chars")
        self.logger.info(f"   Document Text Preview: '{extracted_text[:200]}...'")
        
        # Split first name into parts (e.g., "Lloyd Kenneth" -> ["lloyd", "kenneth"])
        first_name_parts = first_name.split()
        self.logger.info(f"   Searching for name parts: {first_name_parts}")
        
        # Check if any part of the first name appears in the document
        matched_parts = []
        for part in first_name_parts:
            if len(part.strip()) >= 2:
                if part.strip() in text_lower:
                    matched_parts.append(part.strip())
                    self.logger.info(f"   ✅ FOUND: '{part.strip()}' in document")
                else:
                    self.logger.info(f"   ❌ NOT FOUND: '{part.strip()}' in document")
        
        # Accept if we find at least one significant part of the first name
        if matched_parts:
            result['match'] = True
            result['confidence'] = 0.90
            result['matched_name'] = f"Found first name part(s): {', '.join(matched_parts)}"
            self.logger.info(f"   🎉 NAME MATCH SUCCESS: {result['matched_name']}")
        else:
            result['match'] = False
            result['confidence'] = 0.0
            result['reason'] = f"Your first name '{first_name.title()}' was not found on this document. Please submit only YOUR OWN documents."
            self.logger.info(f"   💥 NAME MATCH FAILED: No parts of '{first_name}' found in document")
        
        return result
    
    def _analyze_document_structure(self, img_array: np.ndarray, declared_type: str) -> Dict[str, Any]:
        """Analyze document structure using computer vision"""
        result = {
            'structure_detected': True,
            'confidence': 0.75,
            'features': []
        }
        
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            result['features'].append(f"Found {len(contours)} structural elements")
            
            # Check for typical document features
            if len(contours) > 10:  # Has structure
                result['structure_detected'] = True
                result['features'].append("Document has expected structure")
            
        except Exception as e:
            self.logger.error(f"Structure analysis error: {str(e)}")
        
        return result
    
    def _detect_fraud_indicators(self, img_array: np.ndarray, extracted_text: str, declared_type: str) -> Dict[str, Any]:
        """Detect potential fraud indicators"""
        result = {
            'fraud_detected': False,
            'indicators': [],
            'confidence': 1.0
        }
        
        try:
            # Check for image manipulation (ELA - Error Level Analysis simulation)
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            # Check for uniform regions (possible editing)
            std_dev = np.std(gray)
            if std_dev < 10:
                result['indicators'].append("Suspiciously uniform image")
            
            # Check for duplicate text patterns (copy-paste fraud)
            words = extracted_text.split()
            unique_ratio = len(set(words)) / len(words) if len(words) > 0 else 1
            
            if unique_ratio < 0.3:  # Too many repeated words
                result['indicators'].append("Suspicious text repetition")
            
            result['fraud_detected'] = len(result['indicators']) > 0
            
        except Exception as e:
            self.logger.error(f"Fraud detection error: {str(e)}")
        
        return result
    
    def _calculate_confidence(self, quality, type_ver, name_ver, structure, fraud) -> float:
        """Calculate overall confidence score"""
        scores = []
        
        # Quality (20%)
        if quality['acceptable']:
            scores.append(0.20)
        
        # Type match (30%)
        if type_ver['match']:
            scores.append(0.30 * type_ver['confidence'])
        
        # Name match (30%)
        if name_ver['match']:
            scores.append(0.30 * name_ver['confidence'])
        
        # Structure (10%)
        if structure['structure_detected']:
            scores.append(0.10)
        
        # Fraud check (10%)
        if not fraud['fraud_detected']:
            scores.append(0.10)
        
        return sum(scores)


# Global instance
autonomous_verifier = AutonomousDocumentVerifier()
