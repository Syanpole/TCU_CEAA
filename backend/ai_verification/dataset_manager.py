"""
📊 Dataset Collection and Management System
Automated system for collecting, labeling, and managing AI training datasets
Part of the TCU-CEAA AI Document Verification System
"""

import os
import json
import shutil
import requests
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from urllib.parse import urlparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatasetMetadata:
    """Metadata for dataset samples"""
    file_id: str
    original_filename: str
    file_path: str
    file_size: int
    file_hash: str
    content_type: str  # 'image', 'document', 'text'
    is_ai_generated: bool
    ai_generator: Optional[str] = None
    confidence_level: float = 1.0
    source: str = "unknown"  # 'web_scraping', 'manual', 'synthetic', etc.
    collection_date: str = None
    labels: List[str] = None
    quality_score: float = 1.0
    verification_status: str = "unverified"  # 'verified', 'unverified', 'disputed'
    
    def __post_init__(self):
        if self.collection_date is None:
            self.collection_date = datetime.now().isoformat()
        if self.labels is None:
            self.labels = []

class DatasetManager:
    """Manages training dataset collection and organization"""
    
    def __init__(self, dataset_root: str = "training_datasets"):
        self.dataset_root = Path(dataset_root)
        self.dataset_root.mkdir(exist_ok=True)
        
        # Create organized directory structure
        self.create_directory_structure()
        
        # Initialize database
        self.db_path = self.dataset_root / "dataset_metadata.db"
        self.init_database()
        
        # Dataset statistics
        self.stats = {
            'total_samples': 0,
            'real_samples': 0,
            'ai_samples': 0,
            'verified_samples': 0,
            'by_generator': {},
            'by_content_type': {}
        }
        self.update_stats()
    
    def create_directory_structure(self):
        """Create organized directory structure for datasets"""
        structure = {
            'real': {
                'images': ['photos', 'documents', 'screenshots'],
                'documents': ['pdf', 'text', 'office'],
                'verified': []
            },
            'ai_generated': {
                'images': [
                    'midjourney', 'dalle', 'stable_diffusion', 'firefly',
                    'canva', 'other_generators'
                ],
                'text': ['gpt', 'claude', 'copilot', 'gemini', 'other_llms'],
                'documents': ['ai_pdf', 'ai_reports'],
                'verified': []
            },
            'synthetic': {
                'generated_training': [],
                'augmented': [],
                'simulated': []
            },
            'validation': {
                'test_set': [],
                'holdout': []
            }
        }
        
        for category, subcats in structure.items():
            cat_path = self.dataset_root / category
            cat_path.mkdir(exist_ok=True)
            
            if isinstance(subcats, dict):
                for subcat, subfolders in subcats.items():
                    subcat_path = cat_path / subcat
                    subcat_path.mkdir(exist_ok=True)
                    
                    for folder in subfolders:
                        folder_path = subcat_path / folder
                        folder_path.mkdir(exist_ok=True)
    
    def init_database(self):
        """Initialize SQLite database for metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dataset_samples (
                    file_id TEXT PRIMARY KEY,
                    original_filename TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    file_hash TEXT,
                    content_type TEXT,
                    is_ai_generated BOOLEAN,
                    ai_generator TEXT,
                    confidence_level REAL,
                    source TEXT,
                    collection_date TEXT,
                    labels TEXT,
                    quality_score REAL,
                    verification_status TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time TEXT,
                    end_time TEXT,
                    source TEXT,
                    samples_collected INTEGER,
                    success_rate REAL,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_generator ON dataset_samples(ai_generator);
                CREATE INDEX IF NOT EXISTS idx_content_type ON dataset_samples(content_type);
                CREATE INDEX IF NOT EXISTS idx_verification ON dataset_samples(verification_status);
            """)
    
    def add_sample(self, file_path: str, metadata: DatasetMetadata) -> bool:
        """Add a sample to the dataset"""
        try:
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Check for duplicates
            if self._is_duplicate(file_hash):
                logger.warning(f"Duplicate file detected: {file_path}")
                return False
            
            # Generate file ID
            file_id = f"{metadata.content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash[:8]}"
            metadata.file_id = file_id
            metadata.file_hash = file_hash
            metadata.file_size = os.path.getsize(file_path)
            
            # Determine target directory
            target_dir = self._get_target_directory(metadata)
            target_path = target_dir / f"{file_id}{Path(file_path).suffix}"
            
            # Copy file to organized location
            shutil.copy2(file_path, target_path)
            metadata.file_path = str(target_path)
            
            # Save metadata to database
            self._save_metadata(metadata)
            
            logger.info(f"Added sample: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add sample {file_path}: {e}")
            return False
    
    def collect_web_samples(self, sources: Dict[str, List[str]], max_per_source: int = 100) -> int:
        """Collect samples from web sources"""
        session_id = f"web_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        collected = 0
        
        logger.info(f"Starting web collection session: {session_id}")
        
        for source_name, urls in sources.items():
            logger.info(f"Collecting from {source_name}...")
            
            for url in urls[:max_per_source]:
                try:
                    # Download file
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        # Determine content type
                        content_type = self._detect_content_type_from_url(url)
                        
                        # Create temporary file
                        temp_file = self.dataset_root / "temp" / f"temp_{collected}{self._get_extension_from_url(url)}"
                        temp_file.parent.mkdir(exist_ok=True)
                        
                        with open(temp_file, 'wb') as f:
                            f.write(response.content)
                        
                        # Create metadata
                        is_ai = self._is_ai_source(source_name, url)
                        ai_generator = self._detect_generator_from_source(source_name, url) if is_ai else None
                        
                        metadata = DatasetMetadata(
                            file_id="",
                            original_filename=Path(urlparse(url).path).name,
                            file_path="",
                            file_size=0,
                            file_hash="",
                            content_type=content_type,
                            is_ai_generated=is_ai,
                            ai_generator=ai_generator,
                            source=f"web_{source_name}",
                            confidence_level=0.8  # Lower confidence for web sources
                        )
                        
                        # Add to dataset
                        if self.add_sample(str(temp_file), metadata):
                            collected += 1
                        
                        # Clean up temp file
                        temp_file.unlink(missing_ok=True)
                        
                except Exception as e:
                    logger.error(f"Failed to collect from {url}: {e}")
        
        logger.info(f"Web collection completed. Collected: {collected} samples")
        return collected
    
    def generate_synthetic_samples(self, count: int = 1000, sample_types: List[str] = None) -> int:
        """Generate synthetic training samples"""
        if sample_types is None:
            sample_types = ['natural_images', 'ai_like_images', 'mixed_documents']
        
        logger.info(f"Generating {count} synthetic samples...")
        generated = 0
        
        for sample_type in sample_types:
            type_count = count // len(sample_types)
            
            for i in range(type_count):
                try:
                    # Generate synthetic sample
                    file_path = self._generate_synthetic_sample(sample_type, i)
                    
                    if file_path:
                        # Create metadata
                        is_ai = 'ai' in sample_type
                        metadata = DatasetMetadata(
                            file_id="",
                            original_filename=f"synthetic_{sample_type}_{i}",
                            file_path="",
                            file_size=0,
                            file_hash="",
                            content_type='image' if 'image' in sample_type else 'document',
                            is_ai_generated=is_ai,
                            ai_generator='synthetic' if is_ai else None,
                            source='synthetic_generation',
                            confidence_level=1.0
                        )
                        
                        # Add to dataset
                        if self.add_sample(file_path, metadata):
                            generated += 1
                        
                        # Clean up temp file
                        os.unlink(file_path)
                
                except Exception as e:
                    logger.error(f"Failed to generate synthetic sample {i}: {e}")
        
        logger.info(f"Generated {generated} synthetic samples")
        return generated
    
    def _generate_synthetic_sample(self, sample_type: str, index: int) -> Optional[str]:
        """Generate a single synthetic sample"""
        temp_dir = self.dataset_root / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        if sample_type == 'natural_images':
            return self._generate_natural_looking_image(temp_dir, index)
        elif sample_type == 'ai_like_images':
            return self._generate_ai_like_image(temp_dir, index)
        elif sample_type == 'mixed_documents':
            return self._generate_mixed_document(temp_dir, index)
        
        return None
    
    def _generate_natural_looking_image(self, temp_dir: Path, index: int) -> str:
        """Generate natural-looking image with realistic characteristics"""
        # Create base image
        width, height = np.random.choice([(800, 600), (1024, 768), (1200, 900)])
        
        # Generate natural scene
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient background (sky-like)
        for y in range(height):
            sky_intensity = int(200 - (y / height) * 50)
            image[y, :] = [sky_intensity, sky_intensity + 20, 255]
        
        # Add ground
        ground_start = int(height * 0.7)
        for y in range(ground_start, height):
            ground_intensity = int(100 + (y - ground_start) / (height - ground_start) * 50)
            image[y, :] = [ground_intensity - 20, ground_intensity, ground_intensity - 30]
        
        # Add random natural elements (trees, clouds, etc.)
        for _ in range(np.random.randint(5, 15)):
            # Random shapes with natural variations
            x = np.random.randint(0, width - 50)
            y = np.random.randint(0, height - 50)
            w = np.random.randint(20, 100)
            h = np.random.randint(20, 100)
            
            color = (
                np.random.randint(50, 200),
                np.random.randint(50, 200),
                np.random.randint(50, 200)
            )
            
            cv2.ellipse(image, (x + w//2, y + h//2), (w//2, h//2), 
                       np.random.randint(0, 360), 0, 360, color, -1)
        
        # Add realistic noise
        noise = np.random.normal(0, 8, image.shape).astype(np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Add slight blur (camera imperfection)
        image = cv2.GaussianBlur(image, (3, 3), 0.5)
        
        # Save image
        filename = temp_dir / f"natural_{index}.jpg"
        cv2.imwrite(str(filename), image, [cv2.IMWRITE_JPEG_QUALITY, np.random.randint(85, 98)])
        
        return str(filename)
    
    def _generate_ai_like_image(self, temp_dir: Path, index: int) -> str:
        """Generate AI-like image with suspicious characteristics"""
        width, height = np.random.choice([(512, 512), (768, 768), (1024, 1024)])  # Square formats common in AI
        
        # Create perfectly smooth gradients (typical of AI)
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Perfect radial gradient
        center_x, center_y = width // 2, height // 2
        for y in range(height):
            for x in range(width):
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                normalized_distance = distance / (max(width, height) / 2)
                
                # Over-saturated colors (typical of AI)
                r = int(255 * (1 - normalized_distance) * 1.2)
                g = int(200 * np.sin(normalized_distance * np.pi))
                b = int(180 * np.cos(normalized_distance * np.pi))
                
                image[y, x] = [
                    max(0, min(255, b)),
                    max(0, min(255, g)),
                    max(0, min(255, r))
                ]
        
        # Add perfect symmetrical elements (AI tends to create symmetrical content)
        for _ in range(np.random.randint(3, 8)):
            x = np.random.randint(width // 4, 3 * width // 4)
            y = np.random.randint(height // 4, 3 * height // 4)
            size = np.random.randint(30, 80)
            
            # Create symmetrical shapes
            cv2.circle(image, (x, y), size, (255, 255, 255), 2)
            cv2.circle(image, (width - x, y), size, (255, 255, 255), 2)  # Mirror
        
        # Add over-smoothing (remove natural texture)
        image = cv2.bilateralFilter(image, 15, 80, 80)
        
        # Add artificial sharpening artifacts
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        image = cv2.filter2D(image, -1, kernel * 0.1)
        
        # Save with high compression (AI images often over-compressed)
        filename = temp_dir / f"ai_like_{index}.jpg"
        cv2.imwrite(str(filename), image, [cv2.IMWRITE_JPEG_QUALITY, np.random.randint(60, 85)])
        
        return str(filename)
    
    def _generate_mixed_document(self, temp_dir: Path, index: int) -> str:
        """Generate document with mixed natural/AI characteristics"""
        # Create document image
        width, height = 800, 1000
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Add text content
        try:
            # Try to load a font, fall back to default if not available
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add title
        title = "SAMPLE DOCUMENT FOR AI DETECTION TRAINING"
        if font:
            draw.text((50, 50), title, fill='black', font=font)
        else:
            draw.text((50, 50), title, fill='black')
        
        # Add body text with some AI-like characteristics
        ai_phrases = [
            "As an AI assistant, I can provide information about...",
            "Based on my training data, I understand that...",
            "I don't have access to real-time information, but...",
            "According to my knowledge cutoff date...",
        ]
        
        natural_phrases = [
            "The weather today is quite pleasant.",
            "Our company has been serving customers since 1995.",
            "Please contact us at the number below for assistance.",
            "This document contains important information about...",
        ]
        
        y_position = 100
        for i in range(10):
            if np.random.random() > 0.7:  # 30% AI phrases
                text = np.random.choice(ai_phrases)
            else:
                text = np.random.choice(natural_phrases)
            
            if font:
                draw.text((50, y_position), text, fill='black', font=font)
            else:
                draw.text((50, y_position), text, fill='black')
            y_position += 40
        
        # Save document
        filename = temp_dir / f"document_{index}.png"
        image.save(filename)
        
        return str(filename)
    
    def augment_dataset(self, augmentation_factor: int = 2) -> int:
        """Apply data augmentation to existing samples"""
        logger.info(f"Applying data augmentation with factor {augmentation_factor}...")
        
        augmented = 0
        samples = self.get_all_samples()
        
        for sample in samples:
            if sample['content_type'] == 'image':
                for i in range(augmentation_factor):
                    try:
                        augmented_path = self._apply_image_augmentation(sample['file_path'], i)
                        
                        if augmented_path:
                            # Create metadata for augmented sample
                            metadata = DatasetMetadata(
                                file_id="",
                                original_filename=f"aug_{sample['file_id']}_{i}",
                                file_path="",
                                file_size=0,
                                file_hash="",
                                content_type=sample['content_type'],
                                is_ai_generated=sample['is_ai_generated'],
                                ai_generator=sample['ai_generator'],
                                source=f"augmented_{sample['source']}",
                                confidence_level=sample['confidence_level']
                            )
                            
                            if self.add_sample(augmented_path, metadata):
                                augmented += 1
                            
                            os.unlink(augmented_path)
                    
                    except Exception as e:
                        logger.error(f"Augmentation failed for {sample['file_id']}: {e}")
        
        logger.info(f"Created {augmented} augmented samples")
        return augmented
    
    def _apply_image_augmentation(self, image_path: str, aug_index: int) -> Optional[str]:
        """Apply augmentation to a single image"""
        temp_dir = self.dataset_root / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Apply random augmentations
            augmentations = [
                self._rotate_image,
                self._flip_image,
                self._adjust_brightness,
                self._add_noise,
                self._adjust_contrast,
                self._gaussian_blur
            ]
            
            # Randomly select 1-3 augmentations
            selected_augs = np.random.choice(
                augmentations, 
                size=np.random.randint(1, 4), 
                replace=False
            )
            
            for aug_func in selected_augs:
                image = aug_func(image)
            
            # Save augmented image
            filename = temp_dir / f"aug_{aug_index}_{os.path.basename(image_path)}"
            cv2.imwrite(str(filename), image)
            
            return str(filename)
        
        except Exception as e:
            logger.error(f"Image augmentation failed: {e}")
            return None
    
    def _rotate_image(self, image: np.ndarray) -> np.ndarray:
        """Rotate image by small angle"""
        angle = np.random.uniform(-15, 15)
        center = (image.shape[1] // 2, image.shape[0] // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))
    
    def _flip_image(self, image: np.ndarray) -> np.ndarray:
        """Flip image horizontally or vertically"""
        flip_code = np.random.choice([1, 0])  # 1=horizontal, 0=vertical
        return cv2.flip(image, flip_code)
    
    def _adjust_brightness(self, image: np.ndarray) -> np.ndarray:
        """Adjust image brightness"""
        brightness = np.random.uniform(0.7, 1.3)
        return cv2.convertScaleAbs(image, alpha=1, beta=brightness * 50 - 50)
    
    def _add_noise(self, image: np.ndarray) -> np.ndarray:
        """Add random noise"""
        noise = np.random.normal(0, 10, image.shape).astype(np.int16)
        return np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    def _adjust_contrast(self, image: np.ndarray) -> np.ndarray:
        """Adjust image contrast"""
        contrast = np.random.uniform(0.8, 1.2)
        return cv2.convertScaleAbs(image, alpha=contrast, beta=0)
    
    def _gaussian_blur(self, image: np.ndarray) -> np.ndarray:
        """Apply Gaussian blur"""
        kernel_size = np.random.choice([3, 5])
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    def get_training_split(self, train_ratio: float = 0.7, val_ratio: float = 0.2) -> Dict[str, List[str]]:
        """Get stratified train/validation/test split"""
        samples = self.get_all_samples()
        
        # Separate by class
        real_samples = [s for s in samples if not s['is_ai_generated']]
        ai_samples = [s for s in samples if s['is_ai_generated']]
        
        # Split each class
        splits = {'train': [], 'validation': [], 'test': []}
        
        for sample_group in [real_samples, ai_samples]:
            n_samples = len(sample_group)
            n_train = int(n_samples * train_ratio)
            n_val = int(n_samples * val_ratio)
            
            # Shuffle samples
            np.random.shuffle(sample_group)
            
            splits['train'].extend([s['file_path'] for s in sample_group[:n_train]])
            splits['validation'].extend([s['file_path'] for s in sample_group[n_train:n_train+n_val]])
            splits['test'].extend([s['file_path'] for s in sample_group[n_train+n_val:]])
        
        return splits
    
    def get_all_samples(self) -> List[Dict]:
        """Get all samples from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM dataset_samples")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_dataset_statistics(self) -> Dict:
        """Get comprehensive dataset statistics"""
        self.update_stats()
        return self.stats
    
    def update_stats(self):
        """Update dataset statistics"""
        samples = self.get_all_samples()
        
        self.stats = {
            'total_samples': len(samples),
            'real_samples': sum(1 for s in samples if not s['is_ai_generated']),
            'ai_samples': sum(1 for s in samples if s['is_ai_generated']),
            'verified_samples': sum(1 for s in samples if s['verification_status'] == 'verified'),
            'by_generator': {},
            'by_content_type': {}
        }
        
        # Count by generator
        for sample in samples:
            if sample['ai_generator']:
                generator = sample['ai_generator']
                self.stats['by_generator'][generator] = self.stats['by_generator'].get(generator, 0) + 1
        
        # Count by content type
        for sample in samples:
            content_type = sample['content_type']
            self.stats['by_content_type'][content_type] = self.stats['by_content_type'].get(content_type, 0) + 1
    
    def export_dataset(self, export_format: str = 'json', output_path: str = None) -> str:
        """Export dataset metadata"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.dataset_root / f"dataset_export_{timestamp}.{export_format}"
        
        samples = self.get_all_samples()
        
        if export_format == 'json':
            with open(output_path, 'w') as f:
                json.dump({
                    'metadata': {
                        'export_date': datetime.now().isoformat(),
                        'total_samples': len(samples),
                        'statistics': self.stats
                    },
                    'samples': samples
                }, f, indent=2)
        
        elif export_format == 'csv':
            import pandas as pd
            df = pd.DataFrame(samples)
            df.to_csv(output_path, index=False)
        
        logger.info(f"Dataset exported to {output_path}")
        return str(output_path)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _is_duplicate(self, file_hash: str) -> bool:
        """Check if file hash already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dataset_samples WHERE file_hash = ?", (file_hash,))
            return cursor.fetchone()[0] > 0
    
    def _get_target_directory(self, metadata: DatasetMetadata) -> Path:
        """Determine target directory for file"""
        if metadata.is_ai_generated:
            if metadata.content_type == 'image':
                generator = metadata.ai_generator or 'other_generators'
                return self.dataset_root / 'ai_generated' / 'images' / generator
            elif metadata.content_type == 'document':
                return self.dataset_root / 'ai_generated' / 'documents'
            else:
                generator = metadata.ai_generator or 'other_llms'
                return self.dataset_root / 'ai_generated' / 'text' / generator
        else:
            if metadata.content_type == 'image':
                return self.dataset_root / 'real' / 'images' / 'photos'
            elif metadata.content_type == 'document':
                return self.dataset_root / 'real' / 'documents' / 'pdf'
            else:
                return self.dataset_root / 'real' / 'documents' / 'text'
    
    def _save_metadata(self, metadata: DatasetMetadata):
        """Save metadata to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO dataset_samples VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.file_id,
                metadata.original_filename,
                metadata.file_path,
                metadata.file_size,
                metadata.file_hash,
                metadata.content_type,
                metadata.is_ai_generated,
                metadata.ai_generator,
                metadata.confidence_level,
                metadata.source,
                metadata.collection_date,
                json.dumps(metadata.labels),
                metadata.quality_score,
                metadata.verification_status
            ))
    
    def _detect_content_type_from_url(self, url: str) -> str:
        """Detect content type from URL"""
        url_lower = url.lower()
        
        if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            return 'image'
        elif any(ext in url_lower for ext in ['.pdf', '.doc', '.docx', '.txt']):
            return 'document'
        else:
            return 'image'  # Default assumption
    
    def _get_extension_from_url(self, url: str) -> str:
        """Get file extension from URL"""
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix
        return ext if ext else '.jpg'
    
    def _is_ai_source(self, source_name: str, url: str) -> bool:
        """Determine if source contains AI-generated content"""
        ai_indicators = [
            'midjourney', 'dalle', 'openai', 'stability', 'replicate',
            'ai-generated', 'synthetic', 'artificial', 'generated'
        ]
        
        combined_text = f"{source_name} {url}".lower()
        return any(indicator in combined_text for indicator in ai_indicators)
    
    def _detect_generator_from_source(self, source_name: str, url: str) -> Optional[str]:
        """Detect AI generator from source"""
        combined_text = f"{source_name} {url}".lower()
        
        generators = {
            'midjourney': ['midjourney', 'mj'],
            'dalle': ['dall-e', 'dalle', 'openai'],
            'stable_diffusion': ['stability', 'stable-diffusion', 'hugging'],
            'firefly': ['adobe', 'firefly'],
            'canva': ['canva']
        }
        
        for generator, keywords in generators.items():
            if any(keyword in combined_text for keyword in keywords):
                return generator
        
        return 'unknown'

# Export main classes
__all__ = ['DatasetManager', 'DatasetMetadata']

if __name__ == "__main__":
    print("Dataset Collection and Management System")
    print("Use this module to collect and organize training datasets")
    print("\nExample usage:")
    print("manager = DatasetManager()")
    print("manager.generate_synthetic_samples(1000)")
    print("manager.augment_dataset(2)")
    print("splits = manager.get_training_split()")