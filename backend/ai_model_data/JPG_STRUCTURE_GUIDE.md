# Recommended Directory Structure for JPG Files

## Current Structure Enhancement

```
ai_model_data/
└── reference_documents/
    ├── birth_certificates/
    │   ├── high_quality/
    │   │   ├── birth_cert_psa_high_001_300dpi_front.jpg
    │   │   ├── birth_cert_psa_high_002_300dpi_front.jpg
    │   │   ├── birth_cert_nso_high_001_300dpi_front.jpg
    │   │   └── birth_cert_civil_high_001_300dpi_front.jpg
    │   ├── medium_quality/
    │   │   ├── birth_cert_psa_medium_001_200dpi_front.jpg
    │   │   ├── birth_cert_nso_medium_001_200dpi_front.jpg
    │   │   └── birth_cert_civil_medium_001_200dpi_front.jpg
    │   ├── low_quality/
    │   │   ├── birth_cert_psa_low_001_150dpi_front.jpg
    │   │   └── birth_cert_nso_low_001_150dpi_front.jpg
    │   └── damaged_samples/
    │       ├── birth_cert_psa_damaged_001_100dpi_blurred.jpg
    │       └── birth_cert_fake_damaged_001_72dpi_suspicious.jpg
    │
    ├── school_ids/
    │   ├── high_quality/
    │   │   ├── school_id_tcu_high_001_300dpi_front.jpg
    │   │   ├── school_id_tcu_high_001_300dpi_back.jpg
    │   │   ├── school_id_up_high_001_300dpi_front.jpg
    │   │   └── school_id_ateneo_high_001_300dpi_front.jpg
    │   ├── medium_quality/
    │   │   ├── school_id_tcu_medium_001_200dpi_front.jpg
    │   │   ├── school_id_public_medium_001_200dpi_front.jpg
    │   │   └── school_id_private_medium_001_200dpi_front.jpg
    │   ├── low_quality/
    │   │   ├── school_id_tcu_low_001_150dpi_front.jpg
    │   │   └── school_id_generic_low_001_150dpi_front.jpg
    │   └── damaged_samples/
    │       ├── school_id_fake_damaged_001_72dpi_poor.jpg
    │       └── school_id_torn_damaged_001_100dpi_ripped.jpg
    │
    ├── report_cards/
    │   ├── high_quality/
    │   │   ├── report_card_elementary_high_001_300dpi_full.jpg
    │   │   ├── report_card_highschool_high_001_300dpi_page1.jpg
    │   │   ├── report_card_college_high_001_600dpi_transcript.jpg
    │   │   └── form137_deped_high_001_300dpi_complete.jpg
    │   ├── medium_quality/
    │   │   ├── report_card_elementary_medium_001_200dpi_full.jpg
    │   │   ├── report_card_highschool_medium_001_200dpi_grades.jpg
    │   │   └── transcript_college_medium_001_200dpi_page1.jpg
    │   ├── low_quality/
    │   │   ├── report_card_elementary_low_001_150dpi_faded.jpg
    │   │   └── form137_old_low_001_150dpi_yellowed.jpg
    │   └── damaged_samples/
    │       ├── report_card_fake_damaged_001_72dpi_altered.jpg
    │       └── transcript_suspicious_damaged_001_100dpi_modified.jpg
    │
    └── government_ids/
        ├── high_quality/
        │   ├── drivers_license_lto_high_001_300dpi_front.jpg
        │   ├── drivers_license_lto_high_001_300dpi_back.jpg
        │   ├── voters_id_comelec_high_001_300dpi_front.jpg
        │   ├── passport_dfa_high_001_600dpi_photo_page.jpg
        │   └── national_id_psa_high_001_300dpi_front.jpg
        ├── medium_quality/
        │   ├── drivers_license_lto_medium_001_200dpi_front.jpg
        │   ├── voters_id_comelec_medium_001_200dpi_front.jpg
        │   └── umid_sss_medium_001_200dpi_front.jpg
        ├── low_quality/
        │   ├── drivers_license_old_low_001_150dpi_worn.jpg
        │   └── voters_id_faded_low_001_150dpi_old.jpg
        └── damaged_samples/
            ├── drivers_license_fake_damaged_001_72dpi_suspicious.jpg
            └── voters_id_altered_damaged_001_100dpi_modified.jpg
```

## File Organization Benefits

### 1. **Quality-Based Training**
- Train AI with **high-quality** samples for accuracy
- Use **medium-quality** for real-world scenarios  
- Include **low-quality** for edge case handling
- Add **damaged samples** for fraud detection

### 2. **Easy Dataset Creation**
```python
# Load training sets by quality
high_quality_samples = load_images("*/high_quality/*.jpg")
medium_quality_samples = load_images("*/medium_quality/*.jpg") 
fraud_detection_samples = load_images("*/damaged_samples/*.jpg")
```

### 3. **Scalable Structure**
- Add new institutions easily
- Maintain quality consistency
- Support multiple document variants
- Enable automated validation

## Usage in AI Training

```python
# Example usage in your AI system
DATASET_PATHS = {
    'birth_certificates': {
        'high': 'reference_documents/birth_certificates/high_quality/',
        'medium': 'reference_documents/birth_certificates/medium_quality/', 
        'low': 'reference_documents/birth_certificates/low_quality/',
        'fraud': 'reference_documents/birth_certificates/damaged_samples/'
    },
    'school_ids': {
        'high': 'reference_documents/school_ids/high_quality/',
        'medium': 'reference_documents/school_ids/medium_quality/',
        'low': 'reference_documents/school_ids/low_quality/', 
        'fraud': 'reference_documents/school_ids/damaged_samples/'
    }
}
```