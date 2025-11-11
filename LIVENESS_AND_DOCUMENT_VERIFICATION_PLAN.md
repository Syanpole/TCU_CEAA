# 🎯 Liveness Detection & Document Verification Enhancement Plan

**Date**: November 11, 2025  
**Status**: Planning Phase  
**Priority**: High

---

## 📋 Overview

Enhance the TCU-CEAA system with:
1. **Liveness Detection** - Verify user is physically present (not a photo/video)
2. **Face Matching** - Compare live face to submitted ID photo
3. **New Document Types** - Voter's Certificate & Birth Certificate verification

---

## 🆕 New Document Types to Add

### 1. Voter's Certificate Verification Service
**File**: `backend/myapp/voters_certificate_verification_service.py`

**Training Data Location**:
```
backend/ai_model_data/
├── yolo_models/
│   └── voters_certificate_yolo.pt  (To be trained)
├── document_templates/
│   └── voters_certificate_layout.json
└── training_images/
    └── voters_certificates/
        ├── sample_001.jpg
        ├── sample_002.jpg
        └── ... (your training data)
```

**Expected Elements to Detect**:
- COMELEC Logo
- Voter's name
- Voter's ID number
- Precinct number
- Barangay/City
- Validity period
- QR code (optional)

**OCR Fields to Extract**:
```python
{
    'voter_name': str,
    'voter_id': str,
    'precinct_number': str,
    'barangay': str,
    'city': 'Taguig City',
    'valid_until': date,
    'registration_date': date
}
```

---

### 2. Birth Certificate Verification Service
**File**: `backend/myapp/birth_certificate_verification_service.py`

**Training Data Location**:
```
backend/ai_model_data/
├── yolo_models/
│   └── birth_certificate_yolo.pt  (To be trained)
├── document_templates/
│   └── birth_certificate_layout.json
└── training_images/
    └── birth_certificates/
        ├── sample_001.jpg
        ├── sample_002.jpg
        └── ... (your training data)
```

**Expected Elements to Detect**:
- PSA Logo
- Document security features
- Registration number
- Child's name
- Date of birth
- Place of birth
- Parents' names
- Civil registrar signature

**OCR Fields to Extract**:
```python
{
    'full_name': str,
    'date_of_birth': date,
    'place_of_birth': str,
    'registration_number': str,
    'father_name': str,
    'mother_name': str,
    'date_registered': date,
    'registry_number': str
}
```

---

## 🔴 Liveness Detection System

### Architecture

```
┌─────────────────┐
│   Frontend      │
│ (Camera Capture)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Liveness Detection API        │
│   /api/liveness-check/          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Liveness Verification Service  │
│  - Blink detection              │
│  - Head movement                │
│  - Anti-spoofing checks         │
│  - Face quality assessment      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Face Matching Service          │
│  - Extract face from live video │
│  - Extract face from ID document│
│  - Compare embeddings           │
│  - Calculate similarity score   │
└─────────────────────────────────┘
```

---

## 🎥 Liveness Detection Implementation

### Backend Service: `backend/myapp/liveness_detection_service.py`

```python
import cv2
import numpy as np
from deepface import DeepFace
import dlib
from imutils import face_utils
import logging

logger = logging.getLogger(__name__)

class LivenessDetectionService:
    """
    Real-time liveness detection to prevent spoofing attacks.
    Ensures the user is physically present (not a photo/video).
    """
    
    def __init__(self):
        # Load face detector
        self.face_detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        
        # Blink detection parameters
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 3
        self.blink_counter = 0
        self.total_blinks = 0
    
    def check_liveness(self, video_frames: list) -> dict:
        """
        Analyze multiple video frames for liveness indicators.
        
        Args:
            video_frames: List of frames from live camera feed
            
        Returns:
            {
                'is_live': bool,
                'confidence': float,
                'checks_passed': {
                    'blink_detected': bool,
                    'movement_detected': bool,
                    'face_quality': float,
                    'anti_spoofing': bool
                },
                'message': str
            }
        """
        results = {
            'is_live': False,
            'confidence': 0.0,
            'checks_passed': {},
            'message': ''
        }
        
        try:
            # 1. Blink Detection
            blinks_detected = self._detect_blinks(video_frames)
            results['checks_passed']['blink_detected'] = blinks_detected >= 2
            
            # 2. Head Movement Detection
            movement_detected = self._detect_head_movement(video_frames)
            results['checks_passed']['movement_detected'] = movement_detected
            
            # 3. Face Quality Check
            face_quality = self._check_face_quality(video_frames[-1])
            results['checks_passed']['face_quality'] = face_quality > 0.7
            
            # 4. Anti-Spoofing (texture analysis)
            is_not_spoofed = self._anti_spoofing_check(video_frames[-1])
            results['checks_passed']['anti_spoofing'] = is_not_spoofed
            
            # Calculate overall confidence
            checks_passed = sum(results['checks_passed'].values())
            results['confidence'] = checks_passed / 4.0
            results['is_live'] = checks_passed >= 3  # At least 3/4 checks
            
            if results['is_live']:
                results['message'] = 'Liveness verified - user is physically present'
            else:
                failed = [k for k, v in results['checks_passed'].items() if not v]
                results['message'] = f'Liveness check failed: {", ".join(failed)}'
            
            logger.info(f"Liveness check: {results['is_live']} (confidence: {results['confidence']:.2%})")
            
        except Exception as e:
            logger.error(f"Liveness detection error: {e}")
            results['message'] = f'Error during liveness detection: {str(e)}'
        
        return results
    
    def _detect_blinks(self, frames: list) -> int:
        """Detect number of blinks in video frames"""
        # Implementation using eye aspect ratio
        pass
    
    def _detect_head_movement(self, frames: list) -> bool:
        """Detect head movement across frames"""
        # Implementation using facial landmarks tracking
        pass
    
    def _check_face_quality(self, frame) -> float:
        """Check if face image quality is sufficient"""
        # Check brightness, blur, resolution
        pass
    
    def _anti_spoofing_check(self, frame) -> bool:
        """Check for spoofing attempts (photos, screens)"""
        # Texture analysis, Moiré pattern detection
        pass
    
    def compare_faces(self, live_face_image: str, id_document_path: str, user_data: dict) -> dict:
        """
        Compare live captured face with face on ID document.
        
        Args:
            live_face_image: Base64 or path to live captured face
            id_document_path: Path to submitted ID document
            user_data: User information for additional validation
            
        Returns:
            {
                'faces_match': bool,
                'similarity_score': float,
                'confidence': float,
                'live_face_quality': float,
                'id_face_quality': float,
                'verification_passed': bool,
                'message': str
            }
        """
        result = {
            'faces_match': False,
            'similarity_score': 0.0,
            'confidence': 0.0,
            'verification_passed': False
        }
        
        try:
            # 1. Extract face from live image
            live_face = self._extract_face(live_face_image)
            
            # 2. Extract face from ID document
            id_face = self._extract_face_from_id(id_document_path)
            
            # 3. Compare faces using DeepFace
            comparison = DeepFace.verify(
                img1_path=live_face,
                img2_path=id_face,
                model_name='VGG-Face',
                enforce_detection=True
            )
            
            result['faces_match'] = comparison['verified']
            result['similarity_score'] = 1 - comparison['distance']  # Convert distance to similarity
            result['confidence'] = result['similarity_score']
            
            # 4. Quality checks
            result['live_face_quality'] = self._check_face_quality(live_face)
            result['id_face_quality'] = self._check_face_quality(id_face)
            
            # 5. Final verification decision
            result['verification_passed'] = (
                result['faces_match'] and
                result['similarity_score'] > 0.70 and  # 70% similarity threshold
                result['live_face_quality'] > 0.6 and
                result['id_face_quality'] > 0.6
            )
            
            if result['verification_passed']:
                result['message'] = f"Face match verified ({result['similarity_score']:.1%} similarity)"
            else:
                result['message'] = f"Face verification failed (similarity: {result['similarity_score']:.1%})"
            
            logger.info(f"Face matching: {result['verification_passed']} (similarity: {result['similarity_score']:.2%})")
            
        except Exception as e:
            logger.error(f"Face matching error: {e}")
            result['message'] = f'Error during face matching: {str(e)}'
        
        return result


# Singleton instance
_liveness_service = None

def get_liveness_detection_service():
    global _liveness_service
    if _liveness_service is None:
        _liveness_service = LivenessDetectionService()
    return _liveness_service
```

---

## 🎨 Frontend Implementation

### Update: `frontend/src/components/FaceVerification.tsx`

**Key Changes**:
1. Replace mock verification with real API calls
2. Add liveness detection (blink detection, head movement)
3. Capture multiple frames for video analysis
4. Show real-time feedback to user

**API Endpoints to Call**:
```typescript
// 1. Liveness check
POST /api/liveness-check/
Body: {
  video_frames: [base64_frame1, base64_frame2, ...],
  user_id: number
}

// 2. Face matching
POST /api/face-match/
Body: {
  live_face_image: base64_string,
  document_id: number,  // ID document to compare against
  user_id: number
}
```

---

## 📦 Required Python Packages

Add to `requirements.txt`:
```
deepface==0.0.79          # Face recognition and verification
dlib==19.24.0             # Facial landmark detection
imutils==0.5.4            # Image processing utilities
opencv-python==4.8.1.78   # Already installed
tf-keras==2.15.0          # DeepFace dependency
```

---

## 🔧 Backend API Views

### Add to `backend/myapp/views.py`:

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from myapp.liveness_detection_service import get_liveness_detection_service
import base64
import tempfile
import os

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def liveness_check(request):
    """
    Check if user is live (not a photo/video replay).
    Requires multiple video frames from camera.
    """
    try:
        video_frames_b64 = request.data.get('video_frames', [])
        
        if not video_frames_b64 or len(video_frames_b64) < 5:
            return Response({
                'success': False,
                'error': 'At least 5 video frames required for liveness detection'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Decode frames
        video_frames = []
        for frame_b64 in video_frames_b64:
            frame_data = base64.b64decode(frame_b64.split(',')[1] if ',' in frame_b64 else frame_b64)
            # Convert to numpy array/image
            # ... (implementation)
            video_frames.append(frame_data)
        
        # Run liveness detection
        liveness_service = get_liveness_detection_service()
        result = liveness_service.check_liveness(video_frames)
        
        # Log the check
        audit_logger.log(
            user=request.user,
            action_type='liveness_check',
            action_description=f"Liveness check: {'PASSED' if result['is_live'] else 'FAILED'}",
            severity='info' if result['is_live'] else 'warning',
            metadata=result,
            request=request
        )
        
        return Response({
            'success': True,
            'liveness_result': result
        })
        
    except Exception as e:
        logger.error(f"Liveness check error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def face_match_verification(request):
    """
    Compare live captured face with face on submitted ID document.
    """
    try:
        live_face_b64 = request.data.get('live_face_image')
        document_id = request.data.get('document_id')
        
        if not live_face_b64 or not document_id:
            return Response({
                'success': False,
                'error': 'live_face_image and document_id required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the ID document
        document = DocumentSubmission.objects.get(
            id=document_id,
            student=request.user,
            document_type__in=['student_id', 'government_id', 'school_id']
        )
        
        # Run face matching
        liveness_service = get_liveness_detection_service()
        result = liveness_service.compare_faces(
            live_face_image=live_face_b64,
            id_document_path=document.document_file.path,
            user_data={'name': request.user.get_full_name(), 'student_id': request.user.student_id}
        )
        
        # Update document with face verification result
        document.face_verification_passed = result['verification_passed']
        document.face_match_confidence = result['confidence']
        document.save()
        
        # Log the verification
        audit_logger.log(
            user=request.user,
            action_type='face_verification',
            action_description=f"Face match: {'PASSED' if result['verification_passed'] else 'FAILED'}",
            severity='success' if result['verification_passed'] else 'warning',
            target_model='DocumentSubmission',
            target_object_id=document.id,
            metadata=result,
            request=request
        )
        
        return Response({
            'success': True,
            'face_match_result': result
        })
        
    except DocumentSubmission.DoesNotExist:
        return Response({
            'success': False,
            'error': 'ID document not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Face matching error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

## 🗺️ URL Routing

Add to `backend/myapp/urls.py`:
```python
path('liveness-check/', views.liveness_check, name='liveness-check'),
path('face-match/', views.face_match_verification, name='face-match'),
```

---

## 📊 Database Schema Updates

Add to `DocumentSubmission` model in `backend/myapp/models.py`:
```python
class DocumentSubmission(models.Model):
    # ... existing fields ...
    
    # Liveness & Face Verification
    liveness_check_passed = models.BooleanField(default=False)
    liveness_confidence = models.FloatField(null=True, blank=True)
    face_verification_passed = models.BooleanField(default=False)
    face_match_confidence = models.FloatField(null=True, blank=True)
    liveness_checked_at = models.DateTimeField(null=True, blank=True)
    face_verified_at = models.DateTimeField(null=True, blank=True)
```

Run migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🧪 Testing Plan

### 1. Test Liveness Detection
- ✅ User blinks naturally
- ❌ User shows a photo of face
- ❌ User shows video on phone screen
- ✅ User moves head slightly

### 2. Test Face Matching
- ✅ Same person (live vs ID)
- ❌ Different person
- ❌ Blurry/poor quality image
- ✅ With glasses/without glasses

### 3. Integration Test
- Complete flow: Submit ID → Liveness check → Face match → Approval

---

## 📅 Implementation Timeline

### Phase 1: Training Data Preparation (Current)
- [ ] Collect voter's certificate samples
- [ ] Collect birth certificate samples
- [ ] Label images for YOLO training
- [ ] Train YOLO models

### Phase 2: Liveness Detection (Week 1)
- [ ] Install DeepFace, dlib dependencies
- [ ] Implement LivenessDetectionService
- [ ] Create API endpoints
- [ ] Update FaceVerification frontend component
- [ ] Test with real users

### Phase 3: Document Services (Week 2)
- [ ] Create voters_certificate_verification_service.py
- [ ] Create birth_certificate_verification_service.py
- [ ] Integrate with existing verification flow
- [ ] Add to serializers.py routing

### Phase 4: Testing & Refinement (Week 3)
- [ ] End-to-end testing
- [ ] Adjust confidence thresholds
- [ ] UI/UX improvements
- [ ] Performance optimization

---

## 🎯 Success Metrics

**Liveness Detection**:
- False Acceptance Rate (FAR): < 1%
- False Rejection Rate (FRR): < 5%
- Average verification time: < 5 seconds

**Face Matching**:
- Accuracy: > 95%
- Same-person match rate: > 98%
- Different-person rejection rate: > 99%

**New Document Types**:
- Voter's Certificate accuracy: > 85%
- Birth Certificate accuracy: > 85%

---

## 📝 Notes

1. **Privacy**: Liveness video frames are NOT stored, only results
2. **Performance**: Face matching runs on GPU if available
3. **Fallback**: System gracefully degrades if liveness fails (manual review)
4. **Security**: Anti-spoofing prevents photo/video replay attacks

---

## 🔗 Resources

- **DeepFace**: https://github.com/serengil/deepface
- **dlib**: http://dlib.net/
- **YOLO Training**: https://docs.ultralytics.com/
- **Face Anti-Spoofing**: https://arxiv.org/abs/2007.12342

---

**Status**: Ready to implement after training data preparation is complete! 🚀
