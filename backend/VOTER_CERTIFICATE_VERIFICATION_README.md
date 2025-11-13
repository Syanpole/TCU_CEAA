# Voter Certificate Verification Service

## Overview

The **Voter Certificate Verification Service** is a comprehensive AI-powered document verification system that validates Philippine voter certificates (Voter's ID/Voter's Certification) using advanced computer vision and OCR technologies.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Voter Certificate Upload                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            YOLO v8 Element Detection (60%)                  │
│  • COMELEC Logo Detection                                   │
│  • Voter Registration Text Detection                        │
│  • Official Seal Detection                                  │
│  • Signature Area Detection                                 │
│  • Photo Area Detection                                     │
│  • QR Code Detection                                        │
│  • Watermark Detection                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           Advanced OCR Text Extraction (40%)                │
│  Primary: AWS Textract (95-98% accuracy)                    │
│  Fallback: Tesseract OCR (85-90% accuracy)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Intelligent Field Extraction                   │
│  • Voter Name                                               │
│  • Registration Number                                      │
│  • Precinct Number                                          │
│  • Address                                                  │
│  • Date of Birth                                            │
│  • Registration Date                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Validation & Confidence Scoring                │
│  Status: VALID / QUESTIONABLE / INVALID                     │
│  Confidence: 0-100%                                         │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. YOLOv8 Element Detection
- **Model**: `yolov8_voters_certification_detection.pt`
- **Detectable Elements**:
  - COMELEC Logo (Required)
  - Voter Registration Text (Required)
  - Official Seal (Required)
  - Signature Area (Optional)
  - Photo Area (Optional)
  - QR Code (Optional)
  - Watermark (Optional)

### 2. Advanced OCR with AWS Textract
- **Primary**: AWS Textract (95-98% accuracy)
- **Fallback**: Tesseract OCR (85-90% accuracy)
- **Image Preprocessing**:
  - Grayscale conversion
  - Denoising with fastNlMeansDenoising
  - CLAHE contrast enhancement
  - Adaptive thresholding

### 3. Intelligent Field Extraction
Uses regex patterns and natural language processing to extract:
- **Voter Name**: Multiple pattern matching including "Lastname, Firstname" format
- **Registration Number**: Formats like "0000-0000-0000"
- **Precinct Number**: 4-digit alphanumeric codes
- **Address**: Barangay, city identification
- **Date of Birth**: Multiple date formats
- **Registration Date**: Date pattern matching

### 4. Validation Checks
- ✅ All required elements present (COMELEC logo, voter text, official seal)
- ✅ High detection confidence (>50% per element)
- ✅ OCR confidence score (>70%)
- ✅ Successful field extraction

### 5. Confidence Scoring

**With OCR (Recommended)**:
```
Confidence = 60% (YOLO) + 40% (OCR)

YOLO Component (60%):
  - Detection confidence: 40%
  - Required elements: 30%
  - Optional elements: 15%
  - Validation checks: 15%

OCR Component (40%):
  - Text extraction confidence
```

**Without OCR**:
```
Confidence = 100% (YOLO only)

  - Detection confidence: 50%
  - Required elements: 30%
  - Validation checks: 20%
```

## Installation

### Prerequisites
```bash
# Python packages
pip install ultralytics opencv-python-headless pytesseract boto3 numpy pillow

# System dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr libgl1

# AWS Credentials (for Textract)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Django Settings
```python
# settings.py
USE_ADVANCED_OCR = True  # Enable AWS Textract
ADVANCED_OCR_REGION = 'us-east-1'
OCR_CONFIDENCE_THRESHOLD = 80
```

## Usage

### 1. Python API

```python
from myapp.voter_certificate_verification_service import get_voter_certificate_verification_service

# Initialize service
service = get_voter_certificate_verification_service()

# Check service status
status = service.get_verification_status()
print(f"Service operational: {status['fully_operational']}")
print(f"OCR method: {status['ocr_method']}")

# Verify document
result = service.verify_voter_certificate_document(
    image_path='path/to/voter_certificate.jpg',
    confidence_threshold=0.5,
    include_ocr=True
)

# Check results
if result['success']:
    print(f"Status: {result['status']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Valid: {result['is_valid']}")
    
    # Access extracted information
    info = result['extracted_info']
    print(f"Voter Name: {info['voter_name']}")
    print(f"Registration Number: {info['registration_number']}")
    print(f"Precinct: {info['precinct_number']}")
```

### 2. REST API

**Endpoint**: `POST /api/ai-document-analysis/`

**Request**:
```json
{
  "document_id": 123,
  "document_type": "voters_certificate"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Voter Certificate verification completed: VALID",
  "ai_analysis": {
    "document_id": 123,
    "document_type": "voters_certificate",
    "processing_timestamp": "2025-11-13T10:30:00Z",
    "service_used": "Voter Certificate Verification Service (YOLO + Advanced OCR + Field Extraction)",
    "verification_result": {
      "success": true,
      "is_valid": true,
      "confidence": 0.92,
      "status": "VALID",
      "detected_elements": {
        "comelec_logo": {"present": true, "confidence": 0.95},
        "voter_registration_text": {"present": true, "confidence": 0.89},
        "official_seal": {"present": true, "confidence": 0.91}
      },
      "extracted_info": {
        "voter_name": "DELA CRUZ, JUAN A.",
        "registration_number": "1234-5678-9012",
        "precinct_number": "0123A",
        "address": "Barangay Taguig, Taguig City",
        "date_of_birth": "01/15/1990",
        "registration_date": "10/20/2020"
      }
    }
  }
}
```

### 3. Command Line Test

```bash
# Test the service
python backend/test_voter_certificate_service.py "path/to/voter_certificate.jpg"

# Output will include:
# - Service status
# - YOLO detections
# - Validation checks
# - OCR results
# - Extracted fields
# - Final verdict
# - JSON export
```

## Model Training

### Dataset Requirements
To train or fine-tune the YOLOv8 model:

1. **Collect Images**: 500-1000 voter certificate images
2. **Annotate Elements**: Using tools like Roboflow, LabelImg
   - COMELEC Logo
   - Voter Registration Text
   - Official Seal
   - Signature Area
   - Photo Area
   - QR Code
   - Watermark

3. **Data Split**:
   - Training: 70% (350-700 images)
   - Validation: 20% (100-200 images)
   - Testing: 10% (50-100 images)

4. **Train Model**:
```python
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8n.pt')

# Train
results = model.train(
    data='voter_certificate_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    patience=20,
    device=0  # GPU
)

# Save
model.save('yolov8_voters_certification_detection.pt')
```

## Performance Metrics

### Current Performance (Expected)
- **YOLO Detection Accuracy**: 85-90%
- **OCR Accuracy**: 95-98% (AWS Textract), 85-90% (Tesseract)
- **Field Extraction**: 80-85% accuracy
- **Overall Confidence**: 85-92% for valid documents
- **Processing Time**: 2-4 seconds per document

### Validation Thresholds
- **VALID**: Confidence ≥ 85%, all required elements present
- **QUESTIONABLE**: Confidence 70-84%, some elements missing
- **INVALID**: Confidence < 70% or required elements missing

## Error Handling

### Common Errors

1. **Model Not Found**
```
⚠️ Voter Certificate YOLO model not found at: ai_model_data/trained_models/yolov8_voters_certification_detection.pt
```
**Solution**: Ensure model file exists or train new model

2. **OCR Service Unavailable**
```
⚠️ OCR service not available
```
**Solution**: Install pytesseract and tesseract-ocr

3. **AWS Textract Not Configured**
```
ℹ️ Advanced OCR (AWS Textract) not configured, using Tesseract fallback
```
**Solution**: Configure AWS credentials and enable in settings

4. **No Elements Detected**
```
❌ No voter certificate elements detected in image
```
**Solution**: Ensure image quality, proper lighting, and document is visible

## Best Practices

### For Optimal Results

1. **Image Quality**:
   - Minimum resolution: 800x600 pixels
   - Format: JPG, PNG
   - File size: < 10MB
   - Clear, well-lit photos

2. **Document Positioning**:
   - Full document visible
   - Minimal background
   - No obstructions
   - Flat surface, no wrinkles

3. **Lighting**:
   - Even lighting
   - Avoid glare/reflections
   - No shadows
   - Natural or white light preferred

## Security Considerations

1. **Data Privacy**: Voter information is sensitive
   - Encrypt data at rest and in transit
   - Implement access controls
   - Log all access attempts
   - Comply with Data Privacy Act

2. **AWS Textract**:
   - Data is processed in AWS cloud
   - Enable encryption
   - Use IAM roles with minimal permissions
   - Monitor API usage

3. **Model Security**:
   - Store model files securely
   - Version control trained models
   - Validate model integrity

## Troubleshooting

### Low Confidence Scores
1. Check image quality (resolution, clarity)
2. Verify proper lighting
3. Ensure document is complete and visible
4. Retrain model with more diverse data

### Field Extraction Failures
1. Review OCR output quality
2. Adjust regex patterns for Philippine formats
3. Add more pattern variations
4. Improve image preprocessing

### YOLO Detection Issues
1. Verify model file exists and is correct version
2. Check GPU/CPU availability
3. Adjust confidence threshold
4. Retrain with more annotated data

## API Reference

### `VoterCertificateVerificationService`

#### Methods

**`__init__()`**
Initialize the service, load YOLO model and OCR components.

**`get_verification_status() -> Dict`**
Check service operational status.
- Returns: Status dictionary with component availability

**`verify_voter_certificate_document(image_path, confidence_threshold=0.5, include_ocr=True) -> Dict`**
Main verification method.
- **image_path**: Path to voter certificate image
- **confidence_threshold**: Minimum detection confidence (0.0-1.0)
- **include_ocr**: Enable OCR text extraction
- Returns: Comprehensive verification results

**`extract_voter_certificate_text(image_path) -> Dict`**
Extract text fields from document.
- **image_path**: Path to image
- Returns: OCR results with extracted fields

### Response Schema

```python
{
    'success': bool,              # Verification completed
    'is_valid': bool,             # Document is valid
    'confidence': float,          # Overall confidence (0.0-1.0)
    'status': str,                # VALID/QUESTIONABLE/INVALID
    'detections': List[Dict],     # YOLO detections
    'detected_elements': Dict,    # Element presence
    'validation_checks': Dict,    # Individual checks
    'ocr_data': Dict,             # OCR results
    'extracted_info': Dict,       # Parsed fields
    'recommendations': List[str], # Suggestions
    'errors': List[str]           # Error messages
}
```

## Future Enhancements

1. **Liveness Detection**: Verify photo authenticity
2. **Database Validation**: Check against COMELEC registry (if API available)
3. **QR Code Reading**: Extract embedded data
4. **Signature Verification**: Match signatures
5. **Mobile App Integration**: React Native/Flutter support
6. **Batch Processing**: Process multiple documents
7. **Real-time Streaming**: Live camera verification

## Support

For issues, questions, or contributions:
- **Project**: TCU CEAA Scholarship Application System
- **Team**: TCU CEAA Development Team
- **Date**: November 13, 2025

## License

Proprietary - Taguig City University CEAA Scholarship Program
