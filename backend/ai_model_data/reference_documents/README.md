# AI Reference Documents

This directory contains reference/template documents used by the AI verification system to validate submitted documents.

## Directory Structure

```
reference_documents/
├── birth_certificates/          # NSO/PSA Birth Certificates
├── school_ids/                  # College IDs (CAS, CBM, CCI, CICT)
├── government_ids/              # Government-issued IDs (Voter's Certificate, etc.)
├── certificates_of_enrollment/  # COE templates (General formats)
├── transcripts/                 # TOR templates
├── report_cards/                # Grade 10/12 Report Cards
└── README.md                    # This file
```

## Current Template Files

### Birth Certificates
- `NSO_BIRTH_CERTIFICATE_TEMPLATE 1.jpg` - Standard NSO/PSA birth certificate format

### School IDs
- `CAS_ID_TEMPLATE 1.jpg` - College of Arts & Sciences ID
- `CBM_ID_TEMPLATE 1.jpg` - College of Business & Management ID
- `CCJ_ID_TEMPLATE 1.jpg` - College of Criminal Justice ID
- `CICT_ID_TEMPLATE 1.jpg` - College of ICT ID

### Government IDs
- `VOTERS_CERTIFICATE_TEMPLATE 1.jpg` - Voter's Certificate/Registration

### Certificates of Enrollment
- `GENERAL_COE_FORMAT 1.jpg` - Standard COE format
- `GENERAL_COE_FORMAT 2.jpg` - Alternative COE format

### Transcripts
- `TOR_TEMPLATE 1.jpg` - Transcript of Records template

## How the AI Uses These Templates

1. **Feature Extraction**: AI extracts visual features (layout, seals, fonts, logos)
2. **Pattern Recognition**: Compares submitted documents against reference templates
3. **Anomaly Detection**: Flags documents that don't match expected patterns
4. **Confidence Scoring**: Assigns confidence scores based on similarity
5. **Auto-Approval**: High-confidence matches can be auto-approved

## Adding New Templates

1. Place document images in the appropriate folder
2. Use high-quality scans (300 DPI recommended)
3. Name files descriptively: `{TYPE}_TEMPLATE_{NUMBER}.jpg`
4. Include multiple variations if document formats changed over time

## File Format Requirements

- **Supported formats**: JPG, PNG, PDF
- **Resolution**: Minimum 300 DPI for best results
- **File size**: Up to 5MB per file
- **Color**: Both color and grayscale acceptable

## Privacy & Security

⚠️ **IMPORTANT**: All reference documents should be:
- Anonymized (remove personal information)
- From consenting individuals or public samples
- Stored securely with appropriate access controls
- Compliant with data protection regulations (DPA, GDPR)

## Integration Points

### Backend
- Location: `backend/ai_model_data/reference_documents/`
- AI Verifier: Uses these templates in `ai_verification/` modules
- Models: `DocumentSubmission` includes AI analysis fields

### Frontend
- Service: `frontend/src/services/documentService.ts`
- Components: Document upload/verification UI components
- AI Dashboard: Shows verification results and confidence scores

## Document Type Mapping

| Template Location | Document Type Code | Frontend Label |
|------------------|-------------------|----------------|
| birth_certificates/ | `birth_certificate` | Birth Certificate (PSA/NSO) |
| school_ids/ | `school_id` | School ID or Valid Gov ID |
| government_ids/ | `voters_id`, `philsys_id`, etc. | Various Gov IDs |
| certificates_of_enrollment/ | `certificate_of_enrollment` | Certificate of Enrollment |
| transcripts/ | `transcript_of_records` | Transcript of Records |
| report_cards/ | `grade_10_report_card`, `grade_12_report_card` | Report Cards |

## Last Updated
October 14, 2025
