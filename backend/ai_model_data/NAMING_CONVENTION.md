# AI Model Data Naming Conventions

## Document Templates
- Format: `{document_type}_{institution}_{version}.json`
- Examples: `birth_certificate_psa_v1.json`, `school_id_university_v1.json`

## Reference Documents (JPG/PNG Files)
- **Format**: `{document_type}_{quality}_{number}_{resolution}.{ext}`
- **Examples**: 
  - `birth_cert_high_001_300dpi.jpg`
  - `school_id_medium_002_200dpi.jpg` 
  - `report_card_low_003_150dpi.png`
  - `transcript_high_001_600dpi.jpg`

### Image Quality Classifications:
- `high` = 300+ DPI, perfect lighting, no blur
- `medium` = 200-299 DPI, good lighting, slight blur acceptable  
- `low` = 150-199 DPI, poor lighting, training negatives
- `damaged` = Any DPI, intentionally poor quality for fraud detection

## Signatures & Patterns
- Format: `{signature_type}_{source}_{version}.{ext}` 
- Examples: `psa_seal_pattern_v1.pkl`, `registrar_signature_v1.pkl`

## Validation Sets
- Format: `{category}_validation_set_{version}.json`
- Examples: `academic_docs_validation_set_v1.json`

## Version Control
- Use semantic versioning: v1, v2, v3
- Include creation date in metadata
- Archive old versions in `archived/` subdirectories

## Image File Specifications (JPG/PNG)

### File Naming Pattern:
```
{document_type}_{institution}_{quality}_{number}_{resolution}_{variant}.{ext}

Components:
- document_type: birth_cert, school_id, report_card, transcript, etc.
- institution: psa, nso, tcu, deped, etc. (optional)
- quality: high, medium, low, damaged
- number: 001-999 (zero-padded)
- resolution: 150dpi, 200dpi, 300dpi, 600dpi
- variant: front, back, cropped, full (optional)
- ext: jpg, png
```

### Examples:
```
# Birth Certificates
birth_cert_psa_high_001_300dpi_front.jpg
birth_cert_psa_high_001_300dpi_back.jpg  
birth_cert_nso_medium_002_200dpi_full.jpg
birth_cert_civil_low_003_150dpi_cropped.png

# School IDs  
school_id_tcu_high_001_300dpi_front.jpg
school_id_tcu_high_001_300dpi_back.jpg
school_id_private_medium_002_200dpi_front.jpg
school_id_public_damaged_003_150dpi_front.jpg

# Report Cards
report_card_elementary_high_001_300dpi_full.jpg
report_card_highschool_medium_002_200dpi_page1.jpg
report_card_college_high_003_600dpi_transcript.jpg

# Government IDs
drivers_license_lto_high_001_300dpi_front.jpg
voters_id_comelec_medium_002_200dpi_front.jpg
passport_dfa_high_003_600dpi_photo_page.jpg
```

### Image Quality Standards:
- **High Quality (300+ DPI)**:
  - Professional scanner/camera
  - Perfect lighting, no shadows
  - All text clearly readable
  - Colors accurate, no distortion
  - File size: 2-5MB per image

- **Medium Quality (200-299 DPI)**:
  - Mobile phone camera (good quality)
  - Good lighting conditions
  - Text mostly readable
  - Minor blur acceptable
  - File size: 1-3MB per image

- **Low Quality (150-199 DPI)**:
  - Basic mobile phone camera
  - Poor lighting, some shadows
  - Text partially readable
  - Used for training edge cases
  - File size: 500KB-1.5MB per image

- **Damaged Quality (Any DPI)**:
  - Intentionally poor quality
  - Heavy blur, poor lighting
  - Used for fraud detection training
  - Simulates real-world submission issues
  - File size: Variable

### Special Naming Cases:
```
# Multiple pages
transcript_college_high_001_300dpi_page1.jpg
transcript_college_high_001_300dpi_page2.jpg
transcript_college_high_001_300dpi_page3.jpg

# Different angles/crops
school_id_tcu_high_001_300dpi_full_card.jpg
school_id_tcu_high_001_300dpi_photo_only.jpg
school_id_tcu_high_001_300dpi_name_section.jpg

# Validation sets
birth_cert_validation_set_high_001_300dpi.jpg
school_id_test_set_medium_002_200dpi.jpg
report_card_training_set_low_003_150dpi.jpg
```