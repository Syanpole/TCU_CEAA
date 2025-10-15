## Moved to ai_detection/ai_generated_detector.py

# (Original file content will be inserted here in the next step)
"""
🤖 AI-Generated Content Detector
Advanced detection system for identifying AI-generated images and documents
Part of the TCU-CEAA AI Document Verification System
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json
from PIL import Image, ImageStat, ImageFilter
from PIL.ExifTags import TAGS
import hashlib
import os
from datetime import datetime

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: Scikit-learn not available - some AI detection features disabled")

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("WARNING: TensorFlow not available - deep learning detection disabled")

logger = logging.getLogger(__name__)

class AIGeneratedDetector:
    """
    Comprehensive AI-generated content detection system
    Uses multiple detection methods for high accuracy
    """
    
    def __init__(self):
        self.detection_methods = {
            'metadata_analysis': True,
            'statistical_analysis': True,
            'frequency_analysis': True,
            'compression_artifacts': True,
            'pixel_patterns': True,
            'noise_analysis': True,
            'edge_consistency': True,
            'color_distribution': True,
            'ml_classifier': ML_AVAILABLE,
            'deep_learning': TF_AVAILABLE
        }
        
        # Known AI generation signatures
        self.ai_signatures = {
            'midjourney': ['midjourney', 'mj', 'discord', 'blend'],
            'dalle': ['dall-e', 'dalle', 'openai', 'chatgpt'],
            'stable_diffusion': ['stable diffusion', 'sd', 'automatic1111', 'invoke'],
            'gpt': ['gpt', 'chatgpt', 'openai', 'assistant'],
            'copilot': ['copilot', 'microsoft', 'bing'],
            'claude': ['claude', 'anthropic'],
            'gemini': ['gemini', 'bard', 'google'],
            'canva': ['canva', 'magic', 'ai'],
            'photoshop': ['adobe', 'photoshop', 'firefly', 'generative'],
            'other_ai': ['artificial', 'generated', 'synthetic', 'neural', 'ai']
        }
        
        # Suspicious patterns in AI-generated content
        self.suspicious_patterns = {
            'perfect_symmetry': 0.7,
            'unrealistic_details': 0.6,
            'inconsistent_lighting': 0.8,
            'artifact_patterns': 0.75,
            'compression_anomalies': 0.65,
            'statistical_outliers': 0.7
        }
        
        # Initialize ML classifier if available
        self.ml_classifier = None
        self.scaler = None
        if ML_AVAILABLE:
            self._initialize_ml_classifier()
    
    def detect_ai_generated(self, file_path: str, content_type: str = 'auto') -> Dict[str, Any]:
        """
        Main detection function - analyzes file for AI generation indicators
        """
        result = {
            'file_path': file_path,
            'content_type': content_type,
            'is_ai_generated': False,
            'confidence_score': 0.0,
            'ai_probability': 0.0,
            'detection_methods': {},
            'suspicious_indicators': [],
            'metadata_analysis': {},
            'technical_analysis': {},
            'recommendations': []
        }
        
        try:
            # Determine content type
            if content_type == 'auto':
                content_type = self._detect_content_type(file_path)
            result['content_type'] = content_type
            
            # Run detection methods based on content type
            if content_type in ['image', 'photo']:
                result = self._analyze_image(file_path, result)
            elif content_type in ['document', 'pdf', 'text']:
                result = self._analyze_document(file_path, result)
            else:
                result['error'] = f"Unsupported content type: {content_type}"
                return result
            
            # Calculate overall AI probability
            result['ai_probability'] = self._calculate_ai_probability(result)
            result['is_ai_generated'] = result['ai_probability'] >= 0.7
            result['confidence_score'] = min(result['ai_probability'] * 1.2, 1.0)
            
            # Generate recommendations
            result['recommendations'] = self._generate_recommendations(result)
            
        except Exception as e:
            logger.error(f"AI detection error for {file_path}: {e}")
            result['error'] = str(e)
        
        return result
    
    def _analyze_image(self, image_path: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive image analysis for AI generation detection"""
        
        # Load image
        try:
            pil_image = Image.open(image_path)
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                # Try with PIL conversion
                cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            result['error'] = f"Could not load image: {e}"
            return result
        
        detection_scores = {}
        
        # 1. Metadata Analysis
        metadata_result = self._analyze_image_metadata(pil_image, image_path)
        result['metadata_analysis'] = metadata_result
        detection_scores['metadata'] = metadata_result.get('ai_score', 0.0)
        
        # 2. Statistical Analysis
        stats_result = self._analyze_image_statistics(pil_image, cv_image)
        detection_scores['statistics'] = stats_result.get('ai_score', 0.0)
        
        # 3. Frequency Domain Analysis
        freq_result = self._analyze_frequency_domain(cv_image)
        detection_scores['frequency'] = freq_result.get('ai_score', 0.0)
        
        # 4. Compression Artifacts Analysis
        compression_result = self._analyze_compression_artifacts(cv_image)
        detection_scores['compression'] = compression_result.get('ai_score', 0.0)
        
        # 5. Pixel Pattern Analysis
        pattern_result = self._analyze_pixel_patterns(cv_image)
        detection_scores['patterns'] = pattern_result.get('ai_score', 0.0)
        
        # 6. Noise Analysis
        noise_result = self._analyze_noise_patterns(cv_image)
        detection_scores['noise'] = noise_result.get('ai_score', 0.0)
        
        # 7. Edge Consistency Analysis
        edge_result = self._analyze_edge_consistency(cv_image)
        detection_scores['edges'] = edge_result.get('ai_score', 0.0)
        
        # 8. Color Distribution Analysis
        color_result = self._analyze_color_distribution(pil_image, cv_image)
        detection_scores['colors'] = color_result.get('ai_score', 0.0)
        
        # 9. ML Classifier (if available)
        if self.ml_classifier is not None:
            ml_result = self._ml_classify_image(cv_image)
            detection_scores['ml_classifier'] = ml_result.get('ai_score', 0.0)
        
        # Store detailed results
        result['detection_methods'] = {
            'metadata_analysis': metadata_result,
            'statistical_analysis': stats_result,
            'frequency_analysis': freq_result,
            'compression_analysis': compression_result,
            'pattern_analysis': pattern_result,
            'noise_analysis': noise_result,
            'edge_analysis': edge_result,
            'color_analysis': color_result
        }
        
        result['technical_analysis'] = {
            'image_dimensions': f"{cv_image.shape[1]}x{cv_image.shape[0]}",
            'color_channels': cv_image.shape[2] if len(cv_image.shape) > 2 else 1,
            'file_size': os.path.getsize(image_path),
            'detection_scores': detection_scores
        }
        
        return result
    
    def _analyze_image_metadata(self, pil_image: Image.Image, image_path: str) -> Dict[str, Any]:
        """Analyze image metadata for AI generation indicators"""
        result = {
            'ai_score': 0.0,
            'suspicious_metadata': [],
            'exif_data': {},
            'creation_software': None,
            'ai_indicators': []
        }
        
        try:
            # Extract EXIF data
            exif_data = pil_image._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    result['exif_data'][tag] = str(value)
                    
                    # Check for AI generation indicators in metadata
                    value_str = str(value).lower()
                    for ai_type, keywords in self.ai_signatures.items():
                        for keyword in keywords:
                            if keyword in value_str:
                                result['ai_indicators'].append({
                                    'type': ai_type,
                                    'field': tag,
                                    'value': value_str,
                                    'keyword': keyword
                                })
                                result['ai_score'] += 0.3
            
            # Check filename for AI indicators
            filename = Path(image_path).name.lower()
            for ai_type, keywords in self.ai_signatures.items():
                for keyword in keywords:
                    if keyword in filename:
                        result['ai_indicators'].append({
                            'type': ai_type,
                            'field': 'filename',
                            'value': filename,
                            'keyword': keyword
                        })
                        result['ai_score'] += 0.2
            
            # Check for missing or suspicious metadata
            software = result['exif_data'].get('Software', '').lower()
            if software:
                result['creation_software'] = software
                # Check for AI software indicators
                for ai_type, keywords in self.ai_signatures.items():
                    for keyword in keywords:
                        if keyword in software:
                            result['ai_score'] += 0.4
                            result['suspicious_metadata'].append(f"AI software detected: {software}")
            
            # Missing metadata can be suspicious for AI-generated images
            expected_fields = ['DateTime', 'Software', 'ColorSpace']
            missing_fields = [field for field in expected_fields if field not in result['exif_data']]
            if len(missing_fields) >= 2:
                result['ai_score'] += 0.1
                result['suspicious_metadata'].append(f"Missing metadata fields: {missing_fields}")
                
        except Exception as e:
            logger.warning(f"Metadata analysis error: {e}")
        
        result['ai_score'] = min(result['ai_score'], 1.0)
        return result
    
    def _analyze_image_statistics(self, pil_image: Image.Image, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze statistical properties that may indicate AI generation"""
        result = {
            'ai_score': 0.0,
            'statistics': {},
            'anomalies': []
        }
        
        try:
            # Color statistics
            stat = ImageStat.Stat(pil_image)
            result['statistics'] = {
                'mean': stat.mean,
                'median': stat.median,
                'stddev': stat.stddev,
                'variance': stat.var
            }
            
            # Check for unrealistic color distributions
            if len(stat.mean) >= 3:  # RGB
                color_variance = np.var(stat.mean)
                if color_variance < 10:  # Very uniform colors
                    result['ai_score'] += 0.2
                    result['anomalies'].append("Suspiciously uniform color distribution")
                
                # Check standard deviation patterns
                std_variance = np.var(stat.stddev)
                if std_variance < 5:  # Very uniform noise
                    result['ai_score'] += 0.15
                    result['anomalies'].append("Uniform noise pattern detected")
            
            # Histogram analysis
            if len(cv_image.shape) == 3:
                for i, color in enumerate(['blue', 'green', 'red']):
                    hist = cv2.calcHist([cv_image], [i], None, [256], [0, 256])
                    hist_peaks = len([x for x in hist if x[0] > np.mean(hist) + 2 * np.std(hist)])
                    
                    # AI-generated images often have unusual histogram patterns
                    if hist_peaks < 5 or hist_peaks > 50:
                        result['ai_score'] += 0.1
                        result['anomalies'].append(f"Unusual {color} channel histogram: {hist_peaks} peaks")
            
        except Exception as e:
            logger.warning(f"Statistical analysis error: {e}")
        
        return result
    
    def _analyze_frequency_domain(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze frequency domain characteristics"""
        result = {
            'ai_score': 0.0,
            'frequency_analysis': {},
            'anomalies': []
        }
        
        try:
            # Convert to grayscale for FFT analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Perform FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # Analyze frequency distribution
            center_y, center_x = np.array(magnitude_spectrum.shape) // 2
            center_region = magnitude_spectrum[center_y-20:center_y+20, center_x-20:center_x+20]
            edge_region = magnitude_spectrum[:20, :20]  # Corner region
            
            center_energy = np.mean(center_region)
            edge_energy = np.mean(edge_region)
            energy_ratio = center_energy / (edge_energy + 1e-6)
            
            result['frequency_analysis'] = {
                'center_energy': float(center_energy),
                'edge_energy': float(edge_energy),
                'energy_ratio': float(energy_ratio)
            }
            
            # AI-generated images often have unusual frequency distributions
            if energy_ratio > 15 or energy_ratio < 0.5:
                result['ai_score'] += 0.2
                result['anomalies'].append(f"Unusual frequency distribution ratio: {energy_ratio:.2f}")
            
            # Check for repetitive patterns (common in AI generation)
            autocorr = cv2.matchTemplate(gray, gray[10:50, 10:50], cv2.TM_CCOEFF_NORMED)
            max_correlation = np.max(autocorr)
            if max_correlation > 0.95:
                result['ai_score'] += 0.15
                result['anomalies'].append(f"High self-similarity detected: {max_correlation:.3f}")
                
        except Exception as e:
            logger.warning(f"Frequency analysis error: {e}")
        
        return result
    
    def _analyze_compression_artifacts(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze compression artifacts that may indicate AI generation"""
        result = {
            'ai_score': 0.0,
            'artifacts': {},
            'anomalies': []
        }
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect blocking artifacts (8x8 DCT blocks)
            block_variance = []
            for y in range(0, gray.shape[0] - 8, 8):
                for x in range(0, gray.shape[1] - 8, 8):
                    block = gray[y:y+8, x:x+8]
                    block_variance.append(np.var(block))
            
            if block_variance:
                variance_uniformity = np.std(block_variance) / (np.mean(block_variance) + 1e-6)
                result['artifacts']['block_variance_uniformity'] = float(variance_uniformity)
                
                # AI-generated images often have too uniform compression artifacts
                if variance_uniformity < 0.3:
                    result['ai_score'] += 0.15
                    result['anomalies'].append(f"Suspiciously uniform compression blocks: {variance_uniformity:.3f}")
            
            # Edge gradient analysis
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # AI images often have unnatural gradient distributions
            grad_mean = np.mean(gradient_magnitude)
            grad_std = np.std(gradient_magnitude)
            grad_ratio = grad_std / (grad_mean + 1e-6)
            
            result['artifacts']['gradient_ratio'] = float(grad_ratio)
            
            if grad_ratio < 0.5 or grad_ratio > 3.0:
                result['ai_score'] += 0.1
                result['anomalies'].append(f"Unusual gradient distribution: {grad_ratio:.3f}")
                
        except Exception as e:
            logger.warning(f"Compression analysis error: {e}")
        
        return result
    
    def _analyze_pixel_patterns(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze pixel-level patterns for AI generation indicators"""
        result = {
            'ai_score': 0.0,
            'patterns': {},
            'anomalies': []
        }
        
        try:
            # Convert to grayscale for pattern analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern analysis
            def calculate_lbp(image, radius=1, n_points=8):
                """Simplified LBP calculation"""
                lbp = np.zeros_like(image)
                for i in range(radius, image.shape[0] - radius):
                    for j in range(radius, image.shape[1] - radius):
                        center = image[i, j]
                        binary_string = ""
                        for k in range(n_points):
                            angle = 2 * np.pi * k / n_points
                            x = int(round(i + radius * np.cos(angle)))
                            y = int(round(j + radius * np.sin(angle)))
                            if image[x, y] >= center:
                                binary_string += "1"
                            else:
                                binary_string += "0"
                        lbp[i, j] = int(binary_string, 2)
                return lbp
            
            # Calculate LBP for small region (computationally intensive for full image)
            sample_region = gray[100:200, 100:200] if gray.shape[0] > 200 and gray.shape[1] > 200 else gray
            lbp = calculate_lbp(sample_region)
            
            # Analyze LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=256)
            lbp_uniformity = np.max(lbp_hist) / (np.sum(lbp_hist) + 1e-6)
            
            result['patterns']['lbp_uniformity'] = float(lbp_uniformity)
            
            # AI-generated images often have too uniform or too random patterns
            if lbp_uniformity > 0.15 or lbp_uniformity < 0.002:
                result['ai_score'] += 0.15
                result['anomalies'].append(f"Unusual texture uniformity: {lbp_uniformity:.4f}")
            
            # Pixel intensity distribution analysis
            intensity_diff = np.diff(gray.ravel())
            intensity_variance = np.var(intensity_diff)
            
            result['patterns']['intensity_variance'] = float(intensity_variance)
            
            # Check for unnatural smoothness (over-smoothed AI outputs)
            if intensity_variance < 100:
                result['ai_score'] += 0.1
                result['anomalies'].append(f"Image appears over-smoothed: {intensity_variance:.2f}")
                
        except Exception as e:
            logger.warning(f"Pattern analysis error: {e}")
        
        return result
    
    def _analyze_noise_patterns(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze noise characteristics"""
        result = {
            'ai_score': 0.0,
            'noise': {},
            'anomalies': []
        }
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur and subtract to isolate noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = gray.astype(np.float32) - blurred.astype(np.float32)
            
            # Analyze noise statistics
            noise_mean = np.mean(noise)
            noise_std = np.std(noise)
            noise_variance = np.var(noise)
            
            result['noise'] = {
                'mean': float(noise_mean),
                'std': float(noise_std),
                'variance': float(noise_variance)
            }
            
            # Real photos have natural noise, AI images often have too little or artificial noise
            if abs(noise_mean) > 5:  # Noise should be roughly zero-mean
                result['ai_score'] += 0.1
                result['anomalies'].append(f"Non-zero mean noise: {noise_mean:.2f}")
            
            if noise_std < 2:  # Too little noise
                result['ai_score'] += 0.2
                result['anomalies'].append(f"Suspiciously low noise level: {noise_std:.2f}")
            
            if noise_std > 20:  # Too much noise (possibly added artificially)
                result['ai_score'] += 0.15
                result['anomalies'].append(f"Excessive noise level: {noise_std:.2f}")
                
        except Exception as e:
            logger.warning(f"Noise analysis error: {e}")
        
        return result
    
    def _analyze_edge_consistency(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze edge consistency and artifacts"""
        result = {
            'ai_score': 0.0,
            'edges': {},
            'anomalies': []
        }
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect edges using Canny
            edges = cv2.Canny(gray, 50, 150)
            
            # Count edge pixels
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Analyze edge thickness consistency
            kernel = np.ones((3, 3), np.uint8)
            dilated_edges = cv2.dilate(edges, kernel, iterations=1)
            edge_thickness_ratio = np.sum(dilated_edges > 0) / (np.sum(edges > 0) + 1e-6)
            
            result['edges'] = {
                'density': float(edge_density),
                'thickness_ratio': float(edge_thickness_ratio)
            }
            
            # AI-generated images often have either too clean or too messy edges
            if edge_density < 0.05:  # Too few edges (over-smoothed)
                result['ai_score'] += 0.15
                result['anomalies'].append(f"Suspiciously few edges: {edge_density:.4f}")
            
            if edge_density > 0.3:  # Too many edges (artifacts)
                result['ai_score'] += 0.1
                result['anomalies'].append(f"Excessive edge artifacts: {edge_density:.4f}")
            
            # Check edge consistency
            if edge_thickness_ratio > 2.5:  # Inconsistent edge thickness
                result['ai_score'] += 0.1
                result['anomalies'].append(f"Inconsistent edge thickness: {edge_thickness_ratio:.2f}")
                
        except Exception as e:
            logger.warning(f"Edge analysis error: {e}")
        
        return result
    
    def _analyze_color_distribution(self, pil_image: Image.Image, cv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution characteristics"""
        result = {
            'ai_score': 0.0,
            'colors': {},
            'anomalies': []
        }
        
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
            
            # Analyze color saturation
            saturation = hsv[:, :, 1]
            sat_mean = np.mean(saturation)
            sat_std = np.std(saturation)
            
            # Analyze color distribution in LAB space
            l_channel = lab[:, :, 0]  # Lightness
            a_channel = lab[:, :, 1]  # Green-Red
            b_channel = lab[:, :, 2]  # Blue-Yellow
            
            result['colors'] = {
                'saturation_mean': float(sat_mean),
                'saturation_std': float(sat_std),
                'lightness_mean': float(np.mean(l_channel)),
                'a_channel_std': float(np.std(a_channel)),
                'b_channel_std': float(np.std(b_channel))
            }
            
            # AI-generated images often have unrealistic color distributions
            if sat_mean > 200:  # Over-saturated
                result['ai_score'] += 0.15
                result['anomalies'].append(f"Over-saturated colors: {sat_mean:.1f}")
            
            if sat_std < 20:  # Too uniform saturation
                result['ai_score'] += 0.1
                result['anomalies'].append(f"Uniform color saturation: {sat_std:.1f}")
            
            # Check for unnatural color balance
            color_balance = np.std([np.mean(cv_image[:, :, 0]), 
                                 np.mean(cv_image[:, :, 1]), 
                                 np.mean(cv_image[:, :, 2])])
            
            if color_balance < 5:  # Too balanced
                result['ai_score'] += 0.1
                result['anomalies'].append(f"Artificially balanced colors: {color_balance:.2f}")
                
        except Exception as e:
            logger.warning(f"Color analysis error: {e}")
        
        return result
    
    def _ml_classify_image(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Use ML classifier to detect AI generation"""
        result = {
            'ai_score': 0.0,
            'ml_prediction': {},
            'features': {}
        }
        
        if not ML_AVAILABLE or self.ml_classifier is None:
            return result
        
        try:
            # Extract features for ML classification
            features = self._extract_ml_features(cv_image)
            
            # Scale features
            if self.scaler is not None:
                features_scaled = self.scaler.transform([features])
            else:
                features_scaled = [features]
            
            # Predict using classifier
            prediction = self.ml_classifier.predict(features_scaled)[0]
            prediction_proba = self.ml_classifier.predict_proba(features_scaled)[0]
            
            result['ml_prediction'] = {
                'prediction': int(prediction),
                'probabilities': prediction_proba.tolist(),
                'confidence': float(np.max(prediction_proba))
            }
            
            # AI class is typically class 1
            if len(prediction_proba) > 1:
                result['ai_score'] = float(prediction_proba[1])
            
            result['features'] = {f'feature_{i}': float(f) for i, f in enumerate(features)}
            
        except Exception as e:
            logger.warning(f"ML classification error: {e}")
        
        return result
    
    def _extract_ml_features(self, cv_image: np.ndarray) -> List[float]:
        """Extract features for ML classification"""
        features = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Basic statistics
            features.extend([
                np.mean(gray),
                np.std(gray),
                np.var(gray),
                np.min(gray),
                np.max(gray)
            ])
            
            # Edge features
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            features.append(edge_density)
            
            # Texture features (simplified)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            features.append(laplacian_var)
            
            # Color features
            if len(cv_image.shape) == 3:
                for channel in range(3):
                    features.extend([
                        np.mean(cv_image[:, :, channel]),
                        np.std(cv_image[:, :, channel])
                    ])
            
        except Exception as e:
            logger.warning(f"Feature extraction error: {e}")
            # Return dummy features if extraction fails
            features = [0.0] * 13
        
        return features
    
    def _analyze_document(self, document_path: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documents for AI generation (simplified for now)"""
        
        # For now, focus on text-based detection
        detection_scores = {}
        
        try:
            # Read document content (basic implementation)
            with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for AI text indicators
            ai_text_score = self._analyze_text_for_ai(content)
            detection_scores['text_analysis'] = ai_text_score
            
            result['detection_methods'] = {
                'text_analysis': {'ai_score': ai_text_score}
            }
            
        except Exception as e:
            logger.warning(f"Document analysis error: {e}")
            detection_scores['text_analysis'] = 0.0
        
        result['technical_analysis'] = {
            'detection_scores': detection_scores
        }
        
        return result
    
    def _analyze_text_for_ai(self, text: str) -> float:
        """Analyze text for AI generation indicators"""
        ai_score = 0.0
        
        # Check for common AI text patterns
        ai_phrases = [
            "as an ai", "i'm an ai", "as an artificial intelligence",
            "i'm a language model", "as a large language model",
            "i don't have personal", "i don't have access to",
            "as of my last update", "my knowledge cutoff",
            "i'm not able to", "i cannot provide", "i'm programmed to"
        ]
        
        text_lower = text.lower()
        for phrase in ai_phrases:
            if phrase in text_lower:
                ai_score += 0.3
        
        # Check for repetitive patterns (common in AI text)
        words = text.split()
        if len(words) > 10:
            word_repetition = len(words) / len(set(words))
            if word_repetition > 3:
                ai_score += 0.2
        
        return min(ai_score, 1.0)
    
    def _calculate_ai_probability(self, result: Dict[str, Any]) -> float:
        """Calculate overall AI generation probability"""
        detection_scores = result.get('technical_analysis', {}).get('detection_scores', {})
        
        if not detection_scores:
            return 0.0
        
        # Weighted average of detection scores
        weights = {
            'metadata': 0.2,
            'statistics': 0.15,
            'frequency': 0.1,
            'compression': 0.1,
            'patterns': 0.15,
            'noise': 0.1,
            'edges': 0.1,
            'colors': 0.1,
            'ml_classifier': 0.3 if ML_AVAILABLE else 0.0,
            'text_analysis': 0.4  # For documents
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for method, score in detection_scores.items():
            if method in weights and weights[method] > 0:
                weighted_sum += score * weights[method]
                total_weight += weights[method]
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0.0
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on detection results"""
        recommendations = []
        
        ai_probability = result.get('ai_probability', 0.0)
        
        if ai_probability >= 0.9:
            recommendations.append("HIGH RISK: Strong indicators of AI generation detected")
            recommendations.append("Recommend immediate manual review and additional verification")
        elif ai_probability >= 0.7:
            recommendations.append("MEDIUM RISK: Multiple AI generation indicators found")
            recommendations.append("Recommend thorough manual review before acceptance")
        elif ai_probability >= 0.4:
            recommendations.append("LOW RISK: Some suspicious patterns detected")
            recommendations.append("Consider additional verification if document is critical")
        else:
            recommendations.append("APPEARS AUTHENTIC: No significant AI generation indicators")
            recommendations.append("Document passes automated AI detection screening")
        
        # Add specific recommendations based on detected anomalies
        for method_name, method_result in result.get('detection_methods', {}).items():
            anomalies = method_result.get('anomalies', [])
            for anomaly in anomalies:
                recommendations.append(f"Note: {anomaly}")
        
        return recommendations
    
    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type from file extension"""
        ext = Path(file_path).suffix.lower()
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        document_extensions = ['.pdf', '.txt', '.doc', '.docx']
        
        if ext in image_extensions:
            return 'image'
        elif ext in document_extensions:
            return 'document'
        else:
            return 'unknown'
    
    def _initialize_ml_classifier(self):
        """Initialize ML classifier for AI detection"""
        if not ML_AVAILABLE:
            return
        
        try:
            # For now, use Isolation Forest as an anomaly detector
            # In production, you would train this on real vs AI-generated samples
            self.ml_classifier = IsolationForest(
                contamination=0.1,  # Assume 10% of images might be AI-generated
                random_state=42
            )
            
            self.scaler = StandardScaler()
            
            # TODO: Load pre-trained model if available
            # For now, create a dummy classifier
            dummy_features = np.random.rand(100, 13)  # 100 samples, 13 features
            dummy_labels = np.random.choice([0, 1], 100)  # 0=real, 1=AI
            
            self.scaler.fit(dummy_features)
            self.ml_classifier.fit(dummy_features)
            
        except Exception as e:
            logger.warning(f"ML classifier initialization error: {e}")
            self.ml_classifier = None
            self.scaler = None


# Export main class
__all__ = ['AIGeneratedDetector']

if __name__ == "__main__":
    # Test the AI detection system
    print("Testing AI-Generated Content Detector...")
    
    detector = AIGeneratedDetector()
    
    print(f"AI Detection System initialized")
    print(f"   Available methods: {sum(detector.detection_methods.values())}/{len(detector.detection_methods)}")
    print(f"   ML Classification: {'YES' if detector.ml_classifier else 'NO'}")
    print(f"   Deep Learning: {'YES' if TF_AVAILABLE else 'NO'}")
    
    print("\nAI-Generated Content Detector ready for use!")