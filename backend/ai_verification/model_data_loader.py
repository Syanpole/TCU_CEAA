"""
🤖 AI Model Data Loader
Utility for loading reference documents, templates, and trained models
for the TCU-CEAA AI Document Verification System
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import joblib
import logging
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class AIModelDataLoader:
    """
    Central loader for all AI model data, templates, and reference materials
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize the model data loader"""
        if base_path is None:
            # Default to ai_model_data directory in backend folder
            self.base_path = Path(__file__).parent.parent / 'ai_model_data'
        else:
            self.base_path = Path(base_path)
            
        self.config = self._load_config()
        self._cache = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load the main configuration file"""
        config_path = self.base_path / 'config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Config file not found at {config_path}")
            return {}
    
    def get_document_template(self, document_type: str) -> Dict[str, Any]:
        """Load document template configuration"""
        cache_key = f"template_{document_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        template_file = self.config.get('supported_document_types', {}).get(
            document_type, {}
        ).get('template_file')
        
        if not template_file:
            logger.error(f"No template file configured for document type: {document_type}")
            return {}
            
        template_path = self.base_path / 'document_templates' / template_file
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                template = json.load(f)
                self._cache[cache_key] = template
                return template
        else:
            logger.error(f"Template file not found: {template_path}")
            return {}
    
    def get_reference_documents(self, document_type: str) -> List[Path]:
        """Get list of reference document samples for a document type"""
        ref_dir = self.base_path / 'reference_documents' / document_type
        
        if not ref_dir.exists():
            logger.warming(f"Reference directory not found: {ref_dir}")
            return []
            
        # Return all image and PDF files in the reference directory
        extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        reference_files = []
        
        for ext in extensions:
            reference_files.extend(ref_dir.glob(f'*{ext}'))
            reference_files.extend(ref_dir.glob(f'*{ext.upper()}'))
            
        return reference_files
    
    def load_watermark_template(self, watermark_name: str) -> Optional[np.ndarray]:
        """Load watermark template for comparison"""
        cache_key = f"watermark_{watermark_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        watermark_path = self.base_path / 'watermarks' / watermark_name
        
        if watermark_path.exists():
            try:
                # Load as OpenCV image for template matching
                watermark = cv2.imread(str(watermark_path), cv2.IMREAD_GRAYSCALE)
                self._cache[cache_key] = watermark
                return watermark
            except Exception as e:
                logger.error(f"Error loading watermark {watermark_name}: {e}")
                return None
        else:
            logger.warning(f"Watermark template not found: {watermark_path}")
            return None
    
    def load_trained_model(self, model_type: str, model_name: str):
        """Load a trained machine learning model"""
        cache_key = f"model_{model_type}_{model_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        model_info = self.config.get('ai_models', {}).get(model_type, {})
        model_file = model_info.get(model_name)
        
        if not model_file:
            logger.error(f"Model file not configured: {model_type}.{model_name}")
            return None
            
        model_path = self.base_path / model_file
        
        if model_path.exists():
            try:
                model = joblib.load(model_path)
                self._cache[cache_key] = model
                logger.info(f"Loaded model: {model_type}.{model_name}")
                return model
            except Exception as e:
                logger.error(f"Error loading model {model_path}: {e}")
                return None
        else:
            logger.warning(f"Model file not found: {model_path}")
            return None
    
    def get_document_signatures(self, document_type: str) -> Dict[str, Any]:
        """Load document signatures and patterns"""
        signatures_file = self.base_path / 'signatures' / f'{document_type}_patterns.json'
        
        if signatures_file.exists():
            with open(signatures_file, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Signatures file not found: {signatures_file}")
            return {}
    
    def get_validation_dataset(self, document_type: str, dataset_type: str = 'authentic') -> List[Path]:
        """Get validation dataset files"""
        dataset_dir = self.base_path / 'validation_datasets' / dataset_type / document_type
        
        if not dataset_dir.exists():
            logger.warning(f"Dataset directory not found: {dataset_dir}")
            return []
            
        # Return all files in the dataset directory
        return list(dataset_dir.rglob('*.*'))
    
    def get_confidence_threshold(self, document_type: str) -> float:
        """Get confidence threshold for a document type"""
        doc_config = self.config.get('supported_document_types', {}).get(document_type, {})
        return doc_config.get('confidence_threshold', 
                            self.config.get('validation_settings', {}).get('default_confidence_threshold', 0.8))
    
    def get_supported_document_types(self) -> List[str]:
        """Get list of all supported document types"""
        return list(self.config.get('supported_document_types', {}).keys())
    
    def validate_document_format(self, file_path: Path) -> bool:
        """Validate if file format is supported"""
        supported_formats = self.config.get('validation_settings', {}).get('supported_formats', [])
        file_extension = file_path.suffix.lower().lstrip('.')
        return file_extension in supported_formats
    
    def get_processing_settings(self) -> Dict[str, Any]:
        """Get processing and performance settings"""
        return self.config.get('performance_settings', {})
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security and fraud detection settings"""
        return self.config.get('security_settings', {})


class DocumentTemplateValidator:
    """
    Validates documents against their templates
    """
    
    def __init__(self, model_loader: AIModelDataLoader):
        self.model_loader = model_loader
        
    def validate_document_structure(self, document_type: str, extracted_text: str, 
                                  image: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Validate document structure against template"""
        template = self.model_loader.get_document_template(document_type)
        
        if not template:
            return {'valid': False, 'error': 'Template not found'}
            
        validation_result = {
            'document_type': document_type,
            'valid': True,
            'confidence': 0.0,
            'field_validations': {},
            'missing_fields': [],
            'security_features': {}
        }
        
        required_fields = template.get('required_fields', {})
        total_confidence = 0.0
        valid_fields = 0
        
        # Validate each required field
        for field_name, field_config in required_fields.items():
            field_validation = self._validate_field(field_name, field_config, extracted_text)
            validation_result['field_validations'][field_name] = field_validation
            
            if field_validation['found']:
                total_confidence += field_validation['confidence']
                valid_fields += 1
            elif field_config.get('required', False):
                validation_result['missing_fields'].append(field_name)
        
        # Calculate overall confidence
        if len(required_fields) > 0:
            validation_result['confidence'] = total_confidence / len(required_fields)
        
        # Check if document meets minimum requirements
        min_confidence = template.get('validation_rules', {}).get('overall_confidence_threshold', 0.8)
        validation_result['valid'] = (
            validation_result['confidence'] >= min_confidence and 
            len(validation_result['missing_fields']) == 0
        )
        
        return validation_result
    
    def _validate_field(self, field_name: str, field_config: Dict[str, Any], 
                       extracted_text: str) -> Dict[str, Any]:
        """Validate a single field against its configuration"""
        import re
        
        result = {
            'field_name': field_name,
            'found': False,
            'confidence': 0.0,
            'matched_patterns': [],
            'extracted_value': None
        }
        
        text_patterns = field_config.get('text_patterns', [])
        format_regex = field_config.get('format_regex')
        confidence_threshold = field_config.get('confidence_threshold', 0.7)
        
        # Check for text patterns
        for pattern in text_patterns:
            if pattern.lower() in extracted_text.lower():
                result['matched_patterns'].append(pattern)
                result['confidence'] += 0.3
        
        # If patterns found, look for associated values
        if result['matched_patterns']:
            result['found'] = True
            
            # Try to extract specific value if regex provided
            if format_regex:
                regex_matches = re.findall(format_regex, extracted_text, re.IGNORECASE)
                if regex_matches:
                    result['extracted_value'] = regex_matches[0]
                    result['confidence'] += 0.4
                else:
                    result['confidence'] += 0.2  # Pattern found but no valid format match
            else:
                result['confidence'] += 0.4
        
        # Normalize confidence to 0-1 range
        result['confidence'] = min(result['confidence'], 1.0)
        
        return result


# Convenience functions for easy integration
def get_model_loader() -> AIModelDataLoader:
    """Get the default model data loader instance"""
    return AIModelDataLoader()

def load_document_template(document_type: str) -> Dict[str, Any]:
    """Quick function to load a document template"""
    loader = get_model_loader()
    return loader.get_document_template(document_type)

def validate_document_against_template(document_type: str, extracted_text: str) -> Dict[str, Any]:
    """Quick function to validate document against template"""
    loader = get_model_loader()
    validator = DocumentTemplateValidator(loader)
    return validator.validate_document_structure(document_type, extracted_text)


if __name__ == "__main__":
    # Test the model data loader
    print("🤖 Testing AI Model Data Loader...")
    
    loader = AIModelDataLoader()
    
    # Test configuration loading
    print(f"✅ Configuration loaded: {len(loader.config)} sections")
    
    # Test supported document types
    doc_types = loader.get_supported_document_types()
    print(f"✅ Supported document types: {doc_types}")
    
    # Test template loading
    for doc_type in doc_types[:3]:  # Test first 3 types
        template = loader.get_document_template(doc_type)
        if template:
            print(f"✅ Template loaded for {doc_type}: {len(template.get('required_fields', {}))} fields")
    
    print("🎉 AI Model Data Loader test completed!")