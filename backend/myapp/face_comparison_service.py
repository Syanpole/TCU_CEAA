"""
Face Comparison Service using YOLO for face detection and InsightFace for embeddings
Implements liveness verification and face matching for ID verification
"""

import os
import logging
from typing import Dict, Tuple, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy imports - will be imported when class is instantiated
cv2 = None
np = None


class FaceComparisonService:
    """
    Service for detecting faces, extracting embeddings, and comparing faces
    using YOLO for detection and InsightFace for feature extraction.
    
    Thresholds account for natural facial changes:
    - Weight gain/loss (cheeks, jawline changes)
    - Facial hair growth (beard, mustache)
    - Aging (skin texture, wrinkles)
    - Hairstyle changes
    - Makeup differences
    - Lighting and angle variations
    """
    
    # More lenient threshold to account for natural changes
    SIMILARITY_THRESHOLD = 0.50  # Cosine similarity threshold for match (0.0 to 1.0)
    # Note: 0.50-0.60 = Same person with natural changes
    #       0.40-0.50 = Uncertain - may need manual review
    #       < 0.40 = Likely different person (fraud)
    
    def __init__(self):
        """Initialize face detection and recognition models."""
        # Lazy import heavy ML libraries only when needed
        global cv2, np
        if cv2 is None:
            import cv2 as _cv2
            cv2 = _cv2
        if np is None:
            import numpy as _np
            np = _np
            
        self.face_detector = None
        self.face_recognizer = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize YOLO and InsightFace models."""
        try:
            # Try to import and initialize YOLO
            try:
                from ultralytics import YOLO
                # Load YOLOv8 face detection model
                model_path = os.path.join('ai_models', 'yolov8n-face.pt')
                if os.path.exists(model_path):
                    self.face_detector = YOLO(model_path)
                    logger.info("YOLO face detector loaded successfully")
                else:
                    logger.warning(f"YOLO model not found at {model_path}, using fallback")
            except Exception as yolo_error:
                logger.warning(f"YOLO initialization failed: {yolo_error}")
            
            # Try to import and initialize InsightFace
            try:
                import insightface
                from insightface.app import FaceAnalysis
                
                # Initialize InsightFace
                self.face_recognizer = FaceAnalysis(
                    name='buffalo_l',
                    providers=['CPUExecutionProvider']  # Use CPU, change to CUDAExecutionProvider for GPU
                )
                self.face_recognizer.prepare(ctx_id=0, det_size=(640, 640))
                logger.info("InsightFace recognizer loaded successfully")
            except Exception as insight_error:
                logger.warning(f"InsightFace initialization failed: {insight_error}")
            
            # Fallback to OpenCV Haar Cascade if YOLO fails
            if self.face_detector is None:
                try:
                    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    self.face_detector = cv2.CascadeClassifier(cascade_path)
                    logger.info("Fallback to OpenCV Haar Cascade for face detection")
                except Exception as cv_error:
                    logger.error(f"Failed to load face detection model: {cv_error}")
                    
        except Exception as e:
            logger.error(f"Model initialization error: {e}")
    
    def verify_id_with_selfie(
        self, 
        id_image_path: str, 
        selfie_image_path: str,
        liveness_data: Optional[Dict] = None
    ) -> Dict:
        """
        Complete verification flow: detect faces, extract embeddings, compare.
        
        Args:
            id_image_path: Path to ID document image
            selfie_image_path: Path to live selfie image
            liveness_data: Optional liveness verification data from frontend
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Step 1: Verify liveness data if provided
            if liveness_data:
                liveness_valid = self._verify_liveness_data(liveness_data)
                if not liveness_valid:
                    return {
                        'success': False,
                        'match': False,
                        'error': 'Liveness verification failed',
                        'liveness_passed': False
                    }
            
            # Step 2: Detect and extract face from ID
            id_face, id_bbox = self._detect_face_yolo(id_image_path)
            if id_face is None:
                return {
                    'success': False,
                    'match': False,
                    'error': 'No face detected in ID document',
                    'id_face_detected': False
                }
            
            # Step 3: Extract embeddings from ID face
            id_embedding = self._extract_face_embedding(id_face)
            if id_embedding is None:
                return {
                    'success': False,
                    'match': False,
                    'error': 'Failed to extract ID face features',
                    'id_embedding_extracted': False
                }
            
            # Step 4: Detect and extract face from selfie
            selfie_face, selfie_bbox = self._detect_face_yolo(selfie_image_path)
            if selfie_face is None:
                return {
                    'success': False,
                    'match': False,
                    'error': 'No face detected in selfie',
                    'selfie_face_detected': False
                }
            
            # Step 5: Extract embeddings from selfie
            selfie_embedding = self._extract_face_embedding(selfie_face)
            if selfie_embedding is None:
                return {
                    'success': False,
                    'match': False,
                    'error': 'Failed to extract selfie face features',
                    'selfie_embedding_extracted': False
                }
            
            # Step 6: Compare embeddings using cosine similarity
            similarity = self._calculate_cosine_similarity(id_embedding, selfie_embedding)
            is_match = similarity >= self.SIMILARITY_THRESHOLD
            
            # Step 7: Return comprehensive results
            return {
                'success': True,
                'match': is_match,
                'similarity_score': float(similarity),
                'threshold': self.SIMILARITY_THRESHOLD,
                'confidence': self._calculate_confidence(similarity),
                'id_face_detected': True,
                'selfie_face_detected': True,
                'id_embedding_extracted': True,
                'selfie_embedding_extracted': True,
                'liveness_passed': liveness_data is not None,
                'id_face_bbox': id_bbox,
                'selfie_face_bbox': selfie_bbox
            }
            
        except Exception as e:
            logger.error(f"Face verification error: {str(e)}")
            return {
                'success': False,
                'match': False,
                'error': str(e)
            }
    
    def _verify_liveness_data(self, liveness_data: Dict) -> bool:
        """
        Verify liveness data from frontend challenges.
        
        Args:
            liveness_data: Dictionary containing liveness challenge results
            
        Returns:
            Boolean indicating if liveness is verified
        """
        try:
            # Check color flash challenge
            color_flash = liveness_data.get('colorFlash', {})
            if not color_flash.get('passed', False):
                logger.warning("Color flash liveness check failed")
                return False
            
            # Check blink challenge
            blink = liveness_data.get('blink', {})
            if not blink.get('passed', False):
                logger.warning("Blink detection liveness check failed")
                return False
            
            # Check movement challenge
            movement = liveness_data.get('movement', {})
            if not movement.get('passed', False):
                logger.warning("Movement detection liveness check failed")
                return False
            
            logger.info("All liveness checks passed")
            return True
            
        except Exception as e:
            logger.error(f"Liveness verification error: {e}")
            return False
    
    def _detect_face_yolo(self, image_path: str) -> Tuple[Optional[np.ndarray], Optional[Dict]]:
        """
        Detect face using YOLO and extract face region.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (face_image, bounding_box_dict) or (None, None)
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None, None
            
            # Try YOLO detection first
            if self.face_detector is not None and hasattr(self.face_detector, 'predict'):
                try:
                    results = self.face_detector.predict(image, conf=0.5, verbose=False)
                    
                    if len(results) > 0 and len(results[0].boxes) > 0:
                        # Get the first (most confident) face detection
                        box = results[0].boxes[0]
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        
                        # Extract face region with padding
                        padding = 20
                        h, w = image.shape[:2]
                        y1 = max(0, y1 - padding)
                        y2 = min(h, y2 + padding)
                        x1 = max(0, x1 - padding)
                        x2 = min(w, x2 + padding)
                        
                        face = image[y1:y2, x1:x2]
                        bbox = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                        
                        logger.info(f"YOLO detected face at {bbox}")
                        return face, bbox
                        
                except Exception as yolo_error:
                    logger.warning(f"YOLO detection failed: {yolo_error}")
            
            # Fallback to Haar Cascade
            if isinstance(self.face_detector, cv2.CascadeClassifier):
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_detector.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    # Get the largest face
                    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                    
                    # Extract face region with padding
                    padding = 20
                    img_h, img_w = image.shape[:2]
                    y1 = max(0, y - padding)
                    y2 = min(img_h, y + h + padding)
                    x1 = max(0, x - padding)
                    x2 = min(img_w, x + w + padding)
                    
                    face = image[y1:y2, x1:x2]
                    bbox = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                    
                    logger.info(f"Haar Cascade detected face at {bbox}")
                    return face, bbox
            
            logger.warning(f"No face detected in {image_path}")
            return None, None
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return None, None
    
    def _extract_face_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding using InsightFace.
        
        Args:
            face_image: Face image as numpy array
            
        Returns:
            Face embedding vector or None
        """
        try:
            if self.face_recognizer is None:
                logger.error("Face recognizer not initialized")
                return None
            
            # Ensure image is in RGB format
            if len(face_image.shape) == 2:
                face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
            elif face_image.shape[2] == 4:
                face_image = cv2.cvtColor(face_image, cv2.COLOR_BGRA2RGB)
            elif face_image.shape[2] == 3:
                face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Get face embedding
            faces = self.face_recognizer.get(face_image)
            
            if len(faces) > 0:
                # Return embedding of first face
                embedding = faces[0].embedding
                logger.info(f"Extracted embedding with shape {embedding.shape}")
                return embedding
            else:
                logger.warning("InsightFace could not extract features from face")
                return None
                
        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            return None
    
    def _calculate_cosine_similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            # Normalize embeddings
            embedding1_norm = embedding1 / np.linalg.norm(embedding1)
            embedding2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1_norm, embedding2_norm)
            
            # Convert to 0-1 range (from -1 to 1)
            similarity = (similarity + 1) / 2
            
            logger.info(f"Calculated similarity: {similarity:.4f}")
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0
    
    def _calculate_confidence(self, similarity: float) -> str:
        """
        Convert similarity score to confidence level.
        Accounts for natural facial changes over time.
        
        Args:
            similarity: Similarity score (0.0 to 1.0)
            
        Returns:
            Confidence level string
        """
        if similarity >= 0.85:
            return "very_high"  # Excellent match, minimal changes
        elif similarity >= 0.70:
            return "high"  # Strong match, some natural changes possible
        elif similarity >= 0.55:
            return "medium"  # Good match, natural changes likely (weight, facial hair)
        elif similarity >= 0.45:
            return "low"  # Weak match, significant changes or uncertain
        else:
            return "very_low"  # Poor match, likely different person
    
    def extract_and_save_id_face(self, id_image_path: str, output_path: str) -> bool:
        """
        Extract face from ID and save it separately for later comparison.
        
        Args:
            id_image_path: Path to ID document
            output_path: Path to save extracted face
            
        Returns:
            Boolean indicating success
        """
        try:
            face, bbox = self._detect_face_yolo(id_image_path)
            if face is not None:
                cv2.imwrite(output_path, face)
                logger.info(f"Saved ID face to {output_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving ID face: {e}")
            return False
