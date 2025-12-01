"""
Quick Face Verification System Check
Tests all components of the face verification system
"""

import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
import django
django.setup()

from myapp.face_comparison_service import FaceComparisonService
from django.conf import settings

def check_service():
    """Check if face verification service is ready"""
    print("="*70)
    print("FACE VERIFICATION SYSTEM CHECK")
    print("="*70)
    
    # Initialize service
    print("\n1. Initializing Face Comparison Service...")
    try:
        service = FaceComparisonService()
        print("   ✅ Service initialized successfully")
    except Exception as e:
        print(f"   ❌ Service initialization failed: {e}")
        return False
    
    # Check YOLO
    print("\n2. Checking Face Detector (YOLO/Haar Cascade)...")
    if service.face_detector is not None:
        detector_type = "YOLO" if hasattr(service.face_detector, 'predict') else "Haar Cascade"
        print(f"   ✅ Face detector loaded: {detector_type}")
    else:
        print("   ❌ No face detector loaded")
        return False
    
    # Check InsightFace
    print("\n3. Checking Face Recognizer (InsightFace)...")
    if service.face_recognizer is not None:
        print("   ✅ InsightFace recognizer loaded (buffalo_l)")
    else:
        print("   ❌ InsightFace recognizer not loaded")
        return False
    
    # Check settings
    print("\n4. Checking Configuration...")
    print(f"   Similarity Threshold: {service.SIMILARITY_THRESHOLD}")
    print(f"   AWS Rekognition Enabled: {getattr(settings, 'VERIFICATION_SERVICE_ENABLED', False)}")
    
    # Check model directory
    print("\n5. Checking Model Directory...")
    models_dir = os.path.join(os.path.dirname(__file__), 'ai_models')
    if os.path.exists(models_dir):
        files = os.listdir(models_dir)
        if files:
            print(f"   ✅ Model directory exists: {len(files)} file(s)")
            for f in files:
                if not f.startswith('__'):
                    print(f"      - {f}")
        else:
            print("   ⚠️  Model directory empty (using fallback)")
    else:
        print("   ⚠️  Model directory not found (using fallback)")
    
    # Check InsightFace models
    print("\n6. Checking InsightFace Models...")
    home_dir = os.path.expanduser("~")
    insightface_dir = os.path.join(home_dir, ".insightface", "models", "buffalo_l")
    if os.path.exists(insightface_dir):
        models = [f for f in os.listdir(insightface_dir) if f.endswith('.onnx')]
        print(f"   ✅ InsightFace models found: {len(models)} ONNX file(s)")
        for model in models:
            print(f"      - {model}")
    else:
        print("   ❌ InsightFace models not found")
        return False
    
    print("\n" + "="*70)
    print("✅ SYSTEM STATUS: READY")
    print("="*70)
    print("\nFace verification system is operational!")
    print("You can now test the frontend integration.")
    print("\nNext Steps:")
    print("1. Start backend: python manage.py runserver")
    print("2. Start frontend: npm start (in frontend directory)")
    print("3. Test face verification in the application")
    
    return True

if __name__ == "__main__":
    try:
        success = check_service()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
