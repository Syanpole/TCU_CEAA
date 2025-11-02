# 🤖 AI Model Data Directory Structure

This directory contains all the reference materials, templates, and trained models that the AI verification system uses to validate and compare user-submitted documents.

## 📁 Directory Structure

```
ai_model_data/
├── reference_documents/          # Official document samples for comparison
├── document_templates/           # Standard document templates and layouts
├── watermarks/                   # Official watermarks and security features
├── trained_models/               # Pre-trained ML models and classifiers
├── validation_datasets/          # Training and testing datasets
├── signatures/                   # Document signatures and patterns
└── README.md                     # This file
```

---

## 📄 **reference_documents/**
Store official document samples from legitimate sources for format comparison.

### Recommended Structure:
```
reference_documents/
├── birth_certificates/
│   ├── psa_format_2020.pdf
│   ├── psa_format_2021.pdf
│   ├── civil_registry_format.pdf
│   └── regional_variations/
├── school_ids/
│   ├── tcu_student_id_2024.jpg
│   ├── high_school_formats/
│   └── university_formats/
├── report_cards/
│   ├── deped_grade10_format.pdf
│   ├── deped_grade12_format.pdf
│   ├── tesda_format.pdf
│   └── college_transcript_formats/
├── government_ids/
│   ├── umid_format.jpg
│   ├── drivers_license_format.jpg
│   ├── passport_format.jpg
│   └── philsys_id_format.jpg
└── certificates/
    ├── graduation_diploma_formats/
    ├── als_certificate_formats/
    └── training_certificate_formats/
```

---

## 🎨 **document_templates/**
Standard templates and layout patterns for document structure validation.

### Recommended Structure:
```
document_templates/
├── birth_certificate_layout.json
├── school_id_layout.json
├── report_card_layout.json
├── diploma_layout.json
├── government_id_layout.json
└── templates_config.json
```

### Example Template JSON:
```json
{
  "document_type": "birth_certificate",
  "required_fields": {
    "header": {"region": [0, 0, 1.0, 0.2], "text_patterns": ["REPUBLIC OF THE PHILIPPINES"]},
    "name_field": {"region": [0.1, 0.3, 0.9, 0.4], "text_patterns": ["NAME:", "FULL NAME:"]},
    "date_field": {"region": [0.1, 0.5, 0.9, 0.6], "text_patterns": ["DATE OF BIRTH:", "BORN ON:"]},
    "place_field": {"region": [0.1, 0.6, 0.9, 0.7], "text_patterns": ["PLACE OF BIRTH:"]}
  },
  "security_features": ["watermark", "seal", "signature"],
  "quality_requirements": {"min_resolution": 300, "min_contrast": 0.7}
}
```

---

## 🔐 **watermarks/**
Official watermarks, seals, and security features for authenticity verification.

### Recommended Structure:
```
watermarks/
├── government_seals/
│   ├── psa_seal.png
│   ├── civil_registry_seal.png
│   ├── deped_seal.png
│   └── dfa_seal.png
├── institutional_logos/
│   ├── tcu_logo.png
│   ├── university_logos/
│   └── government_agency_logos/
├── security_patterns/
│   ├── psa_watermark_pattern.png
│   ├── bank_security_patterns/
│   └── official_document_backgrounds/
└── digital_signatures/
    ├── official_signature_samples/
    └── authorized_signatory_samples/
```

---

## 🧠 **trained_models/**
Pre-trained machine learning models and AI classifiers.

### Recommended Structure:
```
trained_models/
├── document_classifier/
│   ├── document_type_classifier.pkl
│   ├── model_metadata.json
│   └── feature_extractors/
├── fraud_detection/
│   ├── tampering_detector.pkl
│   ├── metadata_analyzer.pkl
│   └── suspicious_pattern_detector.pkl
├── ocr_models/
│   ├── custom_tesseract_config/
│   ├── specialized_fonts/
│   └── language_models/
├── face_recognition/
│   ├── face_encoder.pkl
│   ├── face_classifier.pkl
│   └── quality_assessor.pkl
└── text_similarity/
    ├── tfidf_vectorizer.pkl
    ├── document_embeddings.pkl
    └── similarity_thresholds.json
```

---

## 📊 **validation_datasets/**
Training and testing datasets for model validation and improvement.

### Recommended Structure:
```
validation_datasets/
├── authentic_samples/
│   ├── birth_certificates/
│   ├── school_ids/
│   ├── report_cards/
│   └── government_ids/
├── fraudulent_samples/
│   ├── tampered_documents/
│   ├── fake_documents/
│   └── suspicious_patterns/
├── test_cases/
│   ├── edge_cases/
│   ├── quality_variations/
│   └── regional_variations/
└── annotations/
    ├── ground_truth_labels.json
    ├── bounding_boxes.json
    └── classification_labels.json
```

---

## ✏️ **signatures/**
Document signatures, hash patterns, and unique identifiers.

### Recommended Structure:
```
signatures/
├── document_hashes/
│   ├── psa_birth_cert_patterns.json
│   ├── deped_report_card_patterns.json
│   └── government_id_patterns.json
├── text_patterns/
│   ├── official_phrases.json
│   ├── mandatory_disclaimers.json
│   └── legal_text_patterns.json
├── layout_signatures/
│   ├── document_structure_hashes.json
│   └── geometric_patterns.json
└── digital_signatures/
    ├── certificate_authorities.json
    └── trusted_issuers.json
```

---

## 🔧 **Usage in AI Verification System**

### Loading Reference Documents:
```python
import os
from pathlib import Path

AI_MODEL_DATA_PATH = Path(__file__).parent / 'ai_model_data'

class DocumentValidator:
    def __init__(self):
        self.reference_docs_path = AI_MODEL_DATA_PATH / 'reference_documents'
        self.templates_path = AI_MODEL_DATA_PATH / 'document_templates'
        self.watermarks_path = AI_MODEL_DATA_PATH / 'watermarks'
        
    def load_reference_document(self, doc_type):
        """Load reference document for comparison"""
        ref_path = self.reference_docs_path / doc_type
        return self._load_document_samples(ref_path)
        
    def load_template(self, doc_type):
        """Load document template for structure validation"""
        template_file = self.templates_path / f"{doc_type}_layout.json"
        with open(template_file, 'r') as f:
            return json.load(f)
```

### Watermark Detection:
```python
class WatermarkDetector:
    def __init__(self):
        self.watermarks_path = AI_MODEL_DATA_PATH / 'watermarks'
        
    def detect_official_seal(self, document_image, doc_type):
        """Detect official seals and watermarks"""
        seal_templates = self._load_seal_templates(doc_type)
        return self._match_watermarks(document_image, seal_templates)
```

### Model Loading:
```python
import joblib

class AIModelLoader:
    def __init__(self):
        self.models_path = AI_MODEL_DATA_PATH / 'trained_models'
        
    def load_fraud_detector(self):
        """Load pre-trained fraud detection model"""
        model_path = self.models_path / 'fraud_detection' / 'tampering_detector.pkl'
        return joblib.load(model_path)
```

---

## 📋 **Setup Instructions**

1. **Collect Reference Documents:**
   - Obtain official samples from legitimate sources
   - Ensure proper permissions for use
   - Organize by document type and format

2. **Create Templates:**
   - Analyze document structures
   - Define field regions and patterns
   - Set quality requirements

3. **Gather Security Features:**
   - Extract official seals and watermarks
   - Document security patterns
   - Create detection templates

4. **Train Models:**
   - Use validation datasets
   - Train document classifiers
   - Validate fraud detection accuracy

5. **Update AI System:**
   - Configure paths in AI algorithms
   - Update reference loading logic
   - Test with real documents

---

## 🚨 **Security Considerations**

- **Access Control:** Restrict access to sensitive reference materials
- **Data Privacy:** Ensure compliance with privacy regulations
- **Version Control:** Track changes to reference documents
- **Backup:** Maintain secure backups of model data
- **Updates:** Regularly update templates and models

---

## 📈 **Maintenance**

- **Regular Updates:** Keep reference documents current
- **Performance Monitoring:** Track AI accuracy metrics
- **Model Retraining:** Update models with new data
- **Template Validation:** Verify template accuracy
- **Security Reviews:** Regular security audits

---

## 🤝 **Contributing**

When adding new reference materials:
1. Follow the directory structure
2. Include metadata and documentation
3. Test with AI validation system
4. Update configuration files
5. Document any new patterns or features