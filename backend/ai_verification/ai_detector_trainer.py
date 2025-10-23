"""
🤖 Production-Ready AI Generated Content Detector Training System
Advanced training framework for building robust AI detection models
Part of the TCU-CEAA AI Document Verification System
"""

import os
import sys
import json
import pickle
import hashlib
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import cv2
from PIL import Image, ImageStat
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, IsolationForest, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, precision_recall_curve, accuracy_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatasetSample:
    """Structure for dataset samples"""
    file_path: str
    content_type: str  # 'image', 'document', 'text'
    is_ai_generated: bool
    ai_generator: Optional[str] = None  # 'midjourney', 'dalle', 'gpt', etc.
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    features: Dict[str, float] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.features is None:
            self.features = {}

@dataclass
class ModelPerformance:
    """Structure for model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: List[List[int]]
    feature_importance: Dict[str, float]
    cross_val_scores: List[float]
    training_time: float
    
class FeatureExtractor:
    """Advanced feature extraction for AI detection"""
    
    def __init__(self):
        self.feature_names = []
        self._initialize_feature_names()
    
    def _initialize_feature_names(self):
        """Initialize feature names for consistency"""
        # Basic statistics (5 features)
        self.feature_names.extend([
            'mean_brightness', 'std_brightness', 'variance_brightness',
            'skewness_brightness', 'kurtosis_brightness'
        ])
        
        # Color features (15 features)
        for channel in ['r', 'g', 'b']:
            for stat in ['mean', 'std', 'min', 'max', 'range']:
                self.feature_names.append(f'{channel}_{stat}')
        
        # Edge features (5 features)
        self.feature_names.extend([
            'edge_density', 'edge_variance', 'edge_mean_length',
            'edge_consistency', 'corner_count'
        ])
        
        # Texture features (10 features)
        self.feature_names.extend([
            'lbp_uniformity', 'lbp_variance', 'gabor_mean', 'gabor_std',
            'contrast', 'dissimilarity', 'homogeneity', 'energy',
            'correlation', 'entropy'
        ])
        
        # Frequency domain features (8 features)
        self.feature_names.extend([
            'fft_energy_low', 'fft_energy_mid', 'fft_energy_high',
            'fft_peak_frequency', 'fft_spectral_centroid', 'fft_spectral_rolloff',
            'dct_energy', 'wavelet_energy'
        ])
        
        # Compression features (6 features)
        self.feature_names.extend([
            'jpeg_quality_estimate', 'compression_artifacts', 'block_variance',
            'quantization_noise', 'ringing_artifacts', 'blocking_artifacts'
        ])
        
        # AI-specific features (10 features)
        self.feature_names.extend([
            'symmetry_score', 'perfectness_score', 'unnaturalness_score',
            'oversaturation_score', 'oversmoothing_score', 'artifact_density',
            'generation_fingerprint', 'neural_residuals', 'gan_artifacts',
            'diffusion_noise'
        ])
    
    def extract_image_features(self, image_path: str) -> np.ndarray:
        """Extract comprehensive features from an image"""
        try:
            # Load image
            pil_image = Image.open(image_path)
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            features = []
            
            # Basic statistics
            features.extend(self._extract_basic_stats(cv_image))
            
            # Color features
            features.extend(self._extract_color_features(cv_image))
            
            # Edge features
            features.extend(self._extract_edge_features(cv_image))
            
            # Texture features
            features.extend(self._extract_texture_features(cv_image))
            
            # Frequency domain features
            features.extend(self._extract_frequency_features(cv_image))
            
            # Compression features
            features.extend(self._extract_compression_features(cv_image, image_path))
            
            # AI-specific features
            features.extend(self._extract_ai_specific_features(cv_image))
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Feature extraction failed for {image_path}: {e}")
            return np.zeros(len(self.feature_names), dtype=np.float32)
    
    def _extract_basic_stats(self, image: np.ndarray) -> List[float]:
        """Extract basic statistical features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        var_val = np.var(gray)
        
        # Calculate skewness and kurtosis manually
        normalized = (gray - mean_val) / (std_val + 1e-6)
        skewness = np.mean(normalized ** 3)
        kurtosis = np.mean(normalized ** 4) - 3
        
        return [float(mean_val), float(std_val), float(var_val), 
                float(skewness), float(kurtosis)]
    
    def _extract_color_features(self, image: np.ndarray) -> List[float]:
        """Extract color-based features"""
        features = []
        
        # RGB channel statistics
        for channel in range(3):
            ch_data = image[:, :, channel].flatten()
            features.extend([
                np.mean(ch_data),
                np.std(ch_data), 
                np.min(ch_data),
                np.max(ch_data),
                np.ptp(ch_data)  # range (max - min)
            ])
        
        return [float(f) for f in features]
    
    def _extract_edge_features(self, image: np.ndarray) -> List[float]:
        """Extract edge-based features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Edge variance and statistics
        edge_variance = np.var(edges)
        
        # Contour analysis
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            edge_lengths = [cv2.arcLength(contour, True) for contour in contours]
            mean_length = np.mean(edge_lengths) if edge_lengths else 0
        else:
            mean_length = 0
        
        # Edge consistency (using Sobel)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        edge_consistency = np.std(gradient_magnitude) / (np.mean(gradient_magnitude) + 1e-6)
        
        # Corner detection
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
        corner_count = len(corners) if corners is not None else 0
        
        return [float(edge_density), float(edge_variance), float(mean_length),
                float(edge_consistency), float(corner_count)]
    
    def _extract_texture_features(self, image: np.ndarray) -> List[float]:
        """Extract texture-based features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simplified Local Binary Pattern
        lbp = self._calculate_lbp(gray)
        lbp_uniformity = np.std(lbp) / (np.mean(lbp) + 1e-6)
        lbp_variance = np.var(lbp)
        
        # Gabor filter responses (simplified)
        kernel = cv2.getGaborKernel((21, 21), 8, 0, 10, 0.5, 0, ktype=cv2.CV_32F)
        gabor_response = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
        gabor_mean = np.mean(gabor_response)
        gabor_std = np.std(gabor_response)
        
        # GLCM-inspired features (simplified)
        # Calculate co-occurrence statistics
        dx, dy = 1, 0  # horizontal offset
        h, w = gray.shape
        
        if h > 1 and w > 1:
            # Create pairs of adjacent pixels
            pairs = []
            for i in range(h - dy):
                for j in range(w - dx):
                    pairs.append((gray[i, j], gray[i + dy, j + dx]))
            
            if pairs:
                pairs = np.array(pairs)
                contrast = np.var(pairs[:, 0] - pairs[:, 1])
                dissimilarity = np.mean(np.abs(pairs[:, 0] - pairs[:, 1]))
                homogeneity = np.mean(1 / (1 + np.abs(pairs[:, 0] - pairs[:, 1])))
                energy = np.mean(pairs**2)
                correlation = np.corrcoef(pairs[:, 0], pairs[:, 1])[0, 1]
                if np.isnan(correlation):
                    correlation = 0
            else:
                contrast = dissimilarity = homogeneity = energy = correlation = 0
        else:
            contrast = dissimilarity = homogeneity = energy = correlation = 0
        
        # Entropy
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist / (np.sum(hist) + 1e-6)
        entropy = -np.sum(hist * np.log2(hist + 1e-6))
        
        return [float(lbp_uniformity), float(lbp_variance), float(gabor_mean), 
                float(gabor_std), float(contrast), float(dissimilarity),
                float(homogeneity), float(energy), float(correlation), float(entropy)]
    
    def _calculate_lbp(self, image: np.ndarray, radius: int = 1, n_points: int = 8) -> np.ndarray:
        """Calculate Local Binary Pattern"""
        h, w = image.shape
        lbp = np.zeros((h-2*radius, w-2*radius))
        
        for i in range(radius, h-radius):
            for j in range(radius, w-radius):
                center = image[i, j]
                binary_string = ""
                
                for p in range(n_points):
                    angle = 2 * np.pi * p / n_points
                    x = int(round(i + radius * np.cos(angle)))
                    y = int(round(j + radius * np.sin(angle)))
                    
                    x = max(0, min(h-1, x))
                    y = max(0, min(w-1, y))
                    
                    if image[x, y] >= center:
                        binary_string += "1"
                    else:
                        binary_string += "0"
                
                lbp[i-radius, j-radius] = int(binary_string, 2)
        
        return lbp
    
    def _extract_frequency_features(self, image: np.ndarray) -> List[float]:
        """Extract frequency domain features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # FFT analysis
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # Energy in different frequency bands
        h, w = magnitude_spectrum.shape
        center_y, center_x = h // 2, w // 2
        
        # Low, mid, high frequency energy
        low_freq = magnitude_spectrum[center_y-h//8:center_y+h//8, center_x-w//8:center_x+w//8]
        mid_freq = magnitude_spectrum[center_y-h//4:center_y+h//4, center_x-w//4:center_x+w//4]
        
        energy_low = np.mean(low_freq)
        energy_mid = np.mean(mid_freq) - energy_low
        energy_high = np.mean(magnitude_spectrum) - np.mean(mid_freq)
        
        # Peak frequency
        peak_freq = np.unravel_index(np.argmax(magnitude_spectrum), magnitude_spectrum.shape)
        peak_frequency = np.sqrt((peak_freq[0] - center_y)**2 + (peak_freq[1] - center_x)**2)
        
        # Spectral centroid and rolloff (simplified)
        freqs = np.arange(len(magnitude_spectrum.flatten()))
        magnitudes = magnitude_spectrum.flatten()
        spectral_centroid = np.sum(freqs * magnitudes) / (np.sum(magnitudes) + 1e-6)
        
        # Spectral rolloff (frequency below which 85% of energy is contained)
        cumsum_mag = np.cumsum(magnitudes)
        rolloff_idx = np.where(cumsum_mag >= 0.85 * cumsum_mag[-1])[0]
        spectral_rolloff = rolloff_idx[0] if len(rolloff_idx) > 0 else len(magnitudes)
        
        # DCT energy
        dct_coeffs = cv2.dct(gray.astype(np.float32))
        dct_energy = np.mean(dct_coeffs**2)
        
        # Wavelet energy (simplified using filters)
        kernel_h = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]]) / 3
        kernel_v = kernel_h.T
        wavelet_h = cv2.filter2D(gray, -1, kernel_h)
        wavelet_v = cv2.filter2D(gray, -1, kernel_v)
        wavelet_energy = np.mean(wavelet_h**2 + wavelet_v**2)
        
        return [float(energy_low), float(energy_mid), float(energy_high),
                float(peak_frequency), float(spectral_centroid), float(spectral_rolloff),
                float(dct_energy), float(wavelet_energy)]
    
    def _extract_compression_features(self, image: np.ndarray, image_path: str) -> List[float]:
        """Extract compression-related features"""
        # JPEG quality estimation (simplified)
        try:
            file_size = os.path.getsize(image_path)
            image_area = image.shape[0] * image.shape[1]
            bits_per_pixel = (file_size * 8) / image_area
            
            # Rough JPEG quality estimate
            if bits_per_pixel > 24:
                jpeg_quality = 100
            elif bits_per_pixel > 16:
                jpeg_quality = 95
            elif bits_per_pixel > 8:
                jpeg_quality = 85
            elif bits_per_pixel > 4:
                jpeg_quality = 75
            elif bits_per_pixel > 2:
                jpeg_quality = 50
            else:
                jpeg_quality = 25
        except:
            jpeg_quality = 75
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Compression artifacts detection
        # Look for 8x8 block patterns
        block_variance = []
        for i in range(0, gray.shape[0] - 8, 8):
            for j in range(0, gray.shape[1] - 8, 8):
                block = gray[i:i+8, j:j+8]
                block_variance.append(np.var(block))
        
        compression_artifacts = np.std(block_variance) / (np.mean(block_variance) + 1e-6)
        block_var_mean = np.mean(block_variance) if block_variance else 0
        
        # Quantization noise
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        quantization_noise = np.std(laplacian)
        
        # Ringing artifacts (simplified)
        kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        edges = cv2.filter2D(gray, -1, kernel)
        ringing_artifacts = np.mean(np.abs(edges))
        
        # Blocking artifacts
        diff_h = np.mean(np.abs(np.diff(gray, axis=0)))
        diff_v = np.mean(np.abs(np.diff(gray, axis=1)))
        blocking_artifacts = (diff_h + diff_v) / 2
        
        return [float(jpeg_quality), float(compression_artifacts), float(block_var_mean),
                float(quantization_noise), float(ringing_artifacts), float(blocking_artifacts)]
    
    def _extract_ai_specific_features(self, image: np.ndarray) -> List[float]:
        """Extract AI-specific generation features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Symmetry score
        h, w = gray.shape
        left_half = gray[:, :w//2]
        right_half = gray[:, w//2:]
        right_half_flipped = np.fliplr(right_half)
        
        # Resize to match if necessary
        min_w = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_w]
        right_half_flipped = right_half_flipped[:, :min_w]
        
        if left_half.shape == right_half_flipped.shape:
            symmetry_score = 1.0 - np.mean(np.abs(left_half - right_half_flipped)) / 255.0
        else:
            symmetry_score = 0.0
        
        # Perfectness score (too perfect gradients)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        perfectness_score = 1.0 - np.std(gradient_magnitude) / (np.mean(gradient_magnitude) + 1e-6)
        
        # Unnaturalness score (based on color distribution)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        unnaturalness_score = min(1.0, np.mean(saturation) / 200.0)
        
        # Oversaturation score
        oversaturation_score = max(0, (np.mean(saturation) - 128) / 127.0)
        
        # Oversmoothing score
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        oversmoothing_score = max(0, (500 - laplacian_var) / 500.0)
        
        # Artifact density (high frequency noise patterns)
        high_freq = cv2.GaussianBlur(gray, (5, 5), 0)
        artifacts = np.abs(gray.astype(np.float32) - high_freq.astype(np.float32))
        artifact_density = np.mean(artifacts) / 255.0
        
        # Generation fingerprint (pattern repetition)
        autocorr = cv2.matchTemplate(gray, gray[:50, :50], cv2.TM_CCOEFF_NORMED)
        generation_fingerprint = np.max(autocorr) if autocorr.size > 0 else 0
        
        # Neural residuals (high frequency patterns typical of neural nets)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        neural_filtered = cv2.filter2D(gray, -1, kernel)
        neural_residuals = np.std(neural_filtered) / 255.0
        
        # GAN artifacts (checkerboard patterns)
        kernel_checkerboard = np.array([[1, -1], [-1, 1]])
        gan_response = cv2.filter2D(gray, -1, kernel_checkerboard)
        gan_artifacts = np.mean(np.abs(gan_response)) / 255.0
        
        # Diffusion noise (specific noise patterns from diffusion models)
        noise_kernel = np.random.randn(3, 3) * 0.1
        diffusion_response = cv2.filter2D(gray, -1, noise_kernel)
        diffusion_noise = np.std(diffusion_response) / 255.0
        
        return [float(symmetry_score), float(perfectness_score), float(unnaturalness_score),
                float(oversaturation_score), float(oversmoothing_score), float(artifact_density),
                float(generation_fingerprint), float(neural_residuals), 
                float(gan_artifacts), float(diffusion_noise)]

class AIDetectorTrainer:
    """Production-ready AI detector training system"""
    
    def __init__(self, models_dir: str = "models", data_dir: str = "training_data"):
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Model configurations
        self.models = {}
        self.best_model = None
        self.model_performances = {}
        
        # Training history
        self.training_history = []
        
    def collect_training_data(self, data_sources: Dict[str, List[str]]) -> List[DatasetSample]:
        """
        Collect and organize training data from various sources
        
        Args:
            data_sources: Dictionary with 'real' and 'ai_generated' lists of file paths
        """
        logger.info("Collecting training data...")
        samples = []
        
        # Process real samples
        for file_path in data_sources.get('real', []):
            if self._is_valid_file(file_path):
                sample = DatasetSample(
                    file_path=file_path,
                    content_type=self._detect_content_type(file_path),
                    is_ai_generated=False,
                    confidence=1.0
                )
                samples.append(sample)
        
        # Process AI-generated samples
        ai_files = data_sources.get('ai_generated', [])
        for file_path in ai_files:
            if self._is_valid_file(file_path):
                # Try to detect AI generator from filename/path
                ai_generator = self._detect_ai_generator(file_path)
                
                sample = DatasetSample(
                    file_path=file_path,
                    content_type=self._detect_content_type(file_path),
                    is_ai_generated=True,
                    ai_generator=ai_generator,
                    confidence=1.0
                )
                samples.append(sample)
        
        logger.info(f"Collected {len(samples)} training samples")
        logger.info(f"Real samples: {sum(1 for s in samples if not s.is_ai_generated)}")
        logger.info(f"AI samples: {sum(1 for s in samples if s.is_ai_generated)}")
        
        return samples
    
    def extract_features_from_samples(self, samples: List[DatasetSample]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features from all samples"""
        logger.info("Extracting features from samples...")
        
        features_list = []
        labels = []
        
        for i, sample in enumerate(samples):
            if i % 100 == 0:
                logger.info(f"Processing sample {i+1}/{len(samples)}")
            
            try:
                if sample.content_type == 'image':
                    features = self.feature_extractor.extract_image_features(sample.file_path)
                    features_list.append(features)
                    labels.append(1 if sample.is_ai_generated else 0)
                # Add document feature extraction later
                
            except Exception as e:
                logger.error(f"Failed to extract features from {sample.file_path}: {e}")
        
        X = np.array(features_list)
        y = np.array(labels)
        
        logger.info(f"Extracted features: {X.shape}")
        logger.info(f"Feature dimensions: {len(self.feature_extractor.feature_names)}")
        
        return X, y
    
    def train_models(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2):
        """Train multiple models and compare performance"""
        logger.info("Training AI detection models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Define models to train
        model_configs = {
            'random_forest': {
                'model': RandomForestClassifier(
                    n_estimators=100, 
                    max_depth=20, 
                    random_state=42,
                    n_jobs=-1
                ),
                'use_scaled': False
            },
            'svm': {
                'model': SVC(
                    kernel='rbf', 
                    probability=True, 
                    random_state=42
                ),
                'use_scaled': True
            }
        }
        
        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            model_configs['xgboost'] = {
                'model': xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    eval_metric='logloss'
                ),
                'use_scaled': False
            }
        
        # Train each model
        best_score = 0
        for name, config in model_configs.items():
            logger.info(f"Training {name}...")
            
            start_time = datetime.now()
            
            # Choose scaled or unscaled data
            X_train_model = X_train_scaled if config['use_scaled'] else X_train
            X_test_model = X_test_scaled if config['use_scaled'] else X_test
            
            # Train model
            model = config['model']
            model.fit(X_train_model, y_train)
            
            # Predict
            y_pred = model.predict(X_test_model)
            y_pred_proba = model.predict_proba(X_test_model)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_model, y_train, cv=5)
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(
                    self.feature_extractor.feature_names,
                    model.feature_importances_
                ))
            else:
                feature_importance = {}
            
            # Classification report
            report = classification_report(y_test, y_pred, output_dict=True)
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Store performance
            performance = ModelPerformance(
                accuracy=accuracy,
                precision=report['1']['precision'],
                recall=report['1']['recall'],
                f1_score=report['1']['f1-score'],
                roc_auc=roc_auc,
                confusion_matrix=confusion_matrix(y_test, y_pred).tolist(),
                feature_importance=feature_importance,
                cross_val_scores=cv_scores.tolist(),
                training_time=training_time
            )
            
            self.models[name] = {
                'model': model,
                'use_scaled': config['use_scaled'],
                'performance': performance
            }
            self.model_performances[name] = performance
            
            logger.info(f"{name} - Accuracy: {accuracy:.4f}, ROC-AUC: {roc_auc:.4f}")
            
            # Track best model
            if roc_auc > best_score:
                best_score = roc_auc
                self.best_model = name
        
        # Create ensemble model
        if len(self.models) > 1:
            self._create_ensemble_model(X_train_scaled, y_train, X_test_scaled, y_test)
        
        logger.info(f"Best model: {self.best_model} (ROC-AUC: {best_score:.4f})")
    
    def _create_ensemble_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                              X_test: np.ndarray, y_test: np.ndarray):
        """Create ensemble model from trained models"""
        logger.info("Creating ensemble model...")
        
        # Prepare estimators for ensemble
        estimators = []
        for name, model_data in self.models.items():
            if name != 'ensemble':  # Avoid recursion
                estimators.append((name, model_data['model']))
        
        # Create voting classifier
        ensemble = VotingClassifier(
            estimators=estimators,
            voting='soft'  # Use probabilities
        )
        
        # Train ensemble
        ensemble.fit(X_train, y_train)
        
        # Evaluate ensemble
        y_pred = ensemble.predict(X_test)
        y_pred_proba = ensemble.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        report = classification_report(y_test, y_pred, output_dict=True)
        
        performance = ModelPerformance(
            accuracy=accuracy,
            precision=report['1']['precision'],
            recall=report['1']['recall'],
            f1_score=report['1']['f1-score'],
            roc_auc=roc_auc,
            confusion_matrix=confusion_matrix(y_test, y_pred).tolist(),
            feature_importance={},
            cross_val_scores=[],
            training_time=0
        )
        
        self.models['ensemble'] = {
            'model': ensemble,
            'use_scaled': True,  # Ensemble uses scaled features
            'performance': performance
        }
        self.model_performances['ensemble'] = performance
        
        logger.info(f"Ensemble - Accuracy: {accuracy:.4f}, ROC-AUC: {roc_auc:.4f}")
    
    def save_models(self):
        """Save trained models and scalers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, model_data in self.models.items():
            model_path = self.models_dir / f"{name}_model_{timestamp}.pkl"
            
            # Save model with metadata
            save_data = {
                'model': model_data['model'],
                'use_scaled': model_data['use_scaled'],
                'performance': asdict(model_data['performance']),
                'feature_names': self.feature_extractor.feature_names,
                'scaler': self.scaler if model_data['use_scaled'] else None,
                'timestamp': timestamp
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            logger.info(f"Saved {name} model to {model_path}")
        
        # Save training history
        history_path = self.models_dir / f"training_history_{timestamp}.json"
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
    
    def generate_evaluation_report(self) -> str:
        """Generate comprehensive evaluation report"""
        report = []
        report.append("="*80)
        report.append("AI GENERATED CONTENT DETECTOR - TRAINING REPORT")
        report.append("="*80)
        report.append(f"Training completed at: {datetime.now()}")
        report.append(f"Number of models trained: {len(self.models)}")
        report.append(f"Best performing model: {self.best_model}")
        report.append("")
        
        # Model comparison table
        report.append("MODEL PERFORMANCE COMPARISON")
        report.append("-" * 50)
        report.append(f"{'Model':<15} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1':<10} {'ROC-AUC':<10}")
        report.append("-" * 70)
        
        for name, performance in self.model_performances.items():
            report.append(
                f"{name:<15} "
                f"{performance.accuracy:<10.4f} "
                f"{performance.precision:<10.4f} "
                f"{performance.recall:<10.4f} "
                f"{performance.f1_score:<10.4f} "
                f"{performance.roc_auc:<10.4f}"
            )
        
        report.append("")
        
        # Feature importance for best model
        if self.best_model and self.best_model in self.models:
            best_perf = self.model_performances[self.best_model]
            if best_perf.feature_importance:
                report.append("TOP 10 MOST IMPORTANT FEATURES")
                report.append("-" * 40)
                
                sorted_features = sorted(
                    best_perf.feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]
                
                for feature, importance in sorted_features:
                    report.append(f"{feature:<30} {importance:.4f}")
        
        return "\n".join(report)
    
    def _is_valid_file(self, file_path: str) -> bool:
        """Check if file is valid for processing"""
        path = Path(file_path)
        return path.exists() and path.is_file()
    
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
    
    def _detect_ai_generator(self, file_path: str) -> Optional[str]:
        """Try to detect AI generator from filename/path"""
        path_lower = str(file_path).lower()
        
        generators = {
            'midjourney': ['midjourney', 'mj'],
            'dalle': ['dall-e', 'dalle', 'openai'],
            'stable_diffusion': ['stable_diffusion', 'sd', 'automatic1111'],
            'gpt': ['gpt', 'chatgpt'],
            'copilot': ['copilot'],
            'canva': ['canva']
        }
        
        for generator, keywords in generators.items():
            if any(keyword in path_lower for keyword in keywords):
                return generator
        
        return None

# Export main classes
__all__ = ['AIDetectorTrainer', 'FeatureExtractor', 'DatasetSample', 'ModelPerformance']

if __name__ == "__main__":
    print("AI Generated Content Detector Trainer")
    print("Use this module to train production-ready AI detection models")
    print("\nExample usage:")
    print("trainer = AIDetectorTrainer()")
    print("samples = trainer.collect_training_data({'real': [...], 'ai_generated': [...]})")
    print("X, y = trainer.extract_features_from_samples(samples)")
    print("trainer.train_models(X, y)")
    print("trainer.save_models()")