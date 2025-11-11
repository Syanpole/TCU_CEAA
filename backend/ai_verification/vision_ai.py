"""
Vision AI Module - Mock/Stub for CI compatibility
This module provides graceful fallback when OCR dependencies are not available.
"""

import logging

logger = logging.getLogger(__name__)

# Check for optional OCR dependencies
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not available. OCR features will be disabled.")

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("Pytesseract not available. OCR features will be disabled.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Computer vision features will be disabled.")


class VisionAI:
    """
    Vision AI class with graceful fallback for missing dependencies.
    Provides OCR and computer vision capabilities when dependencies are available.
    """
    
    def __init__(self):
        """Initialize Vision AI with available engines."""
        self.easyocr_available = EASYOCR_AVAILABLE
        self.pytesseract_available = PYTESSERACT_AVAILABLE
        self.cv2_available = CV2_AVAILABLE
        
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['en'])
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
                self.easyocr_available = False
        
        if not any([self.easyocr_available, self.pytesseract_available]):
            logger.warning("No OCR engines available! Vision AI features will be limited.")
    
    def extract_text(self, image_path):
        """
        Extract text from image using available OCR engine.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Extracted text or empty string if OCR not available
        """
        if self.easyocr_available:
            try:
                result = self.reader.readtext(image_path)
                text = ' '.join([detection[1] for detection in result])
                return text
            except Exception as e:
                logger.error(f"EasyOCR extraction failed: {e}")
        
        if self.pytesseract_available and self.cv2_available:
            try:
                import cv2
                import pytesseract
                
                image = cv2.imread(image_path)
                text = pytesseract.image_to_string(image)
                return text
            except Exception as e:
                logger.error(f"Pytesseract extraction failed: {e}")
        
        logger.warning(f"OCR not available for {image_path}. Returning empty text.")
        return ""
    
    def detect_faces(self, image_path):
        """
        Detect faces in image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict: Face detection results or empty dict if CV not available
        """
        if not self.cv2_available:
            logger.warning("OpenCV not available. Face detection disabled.")
            return {
                'faces_detected': 0,
                'confidence': 0.0,
                'available': False
            }
        
        try:
            import cv2
            
            # Load cascade classifier for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Read image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return {
                'faces_detected': len(faces),
                'confidence': 1.0 if len(faces) > 0 else 0.0,
                'available': True,
                'face_locations': [(x, y, w, h) for (x, y, w, h) in faces]
            }
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return {
                'faces_detected': 0,
                'confidence': 0.0,
                'available': False,
                'error': str(e)
            }
    
    def is_available(self):
        """Check if any vision AI capabilities are available."""
        return any([
            self.easyocr_available,
            self.pytesseract_available,
            self.cv2_available
        ])
    
    def get_available_engines(self):
        """Get list of available OCR/CV engines."""
        engines = []
        if self.easyocr_available:
            engines.append('EasyOCR')
        if self.pytesseract_available:
            engines.append('Pytesseract')
        if self.cv2_available:
            engines.append('OpenCV')
        return engines
    
    def analyze_document_structure(self, img_array):
        """
        Analyze document structure (stub for compatibility).
        
        Args:
            img_array: NumPy array of the image
            
        Returns:
            dict: Document structure analysis results
        """
        logger.debug("analyze_document_structure called (using fallback)")
        
        return {
            'document_type': 'unknown',
            'confidence': 0.5,
            'layout_detected': False,
            'available': False,
            'note': 'Vision AI structure analysis not available - using basic validation'
        }
    
    def extract_structured_data(self, img_array, declared_type):
        """
        Extract structured data from document (stub for compatibility).
        
        Args:
            img_array: NumPy array of the image
            declared_type: Declared document type
            
        Returns:
            dict: Extracted structured data
        """
        logger.debug("extract_structured_data called (using fallback)")
        
        return {
            'extracted_fields': {},
            'confidence': 0.0,
            'available': False,
            'note': 'Structured data extraction not available - using basic OCR only'
        }
        engines = []
        if self.easyocr_available:
            engines.append('easyocr')
        if self.pytesseract_available:
            engines.append('pytesseract')
        if self.cv2_available:
            engines.append('opencv')
        return engines


# Create default instance
default_vision_ai = VisionAI()

# Export alias for backwards compatibility
vision_ai = default_vision_ai


def get_vision_ai():
    """Get the default Vision AI instance."""
    return default_vision_ai
