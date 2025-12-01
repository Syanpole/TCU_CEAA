"""
Inspect the voter certificate YOLO model to see actual class names
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from ultralytics import YOLO
from pathlib import Path
from django.conf import settings

model_path = Path(settings.BASE_DIR) / 'ai_model_data' / 'trained_models' / 'yolov8_voters_certification_detection.pt'

print(f"Loading model from: {model_path}")
model = YOLO(str(model_path))

print("\n" + "="*80)
print("MODEL CLASS NAMES")
print("="*80)

if hasattr(model, 'names'):
    print(f"\nTotal classes: {len(model.names)}\n")
    for class_id, class_name in model.names.items():
        print(f"   Class {class_id}: {class_name}")
else:
    print("Could not retrieve class names from model")

print("\n" + "="*80)

# Test on an image to see what gets detected
test_image = "media/documents/2025/11/IMG20251111053744.jpg"
if os.path.exists(test_image):
    print(f"\nTesting detection on: {test_image}")
    results = model(test_image, conf=0.5, verbose=False)
    
    if len(results) > 0 and len(results[0].boxes) > 0:
        print(f"\nDetected {len(results[0].boxes)} objects:\n")
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names.get(class_id, f'Unknown-{class_id}')
            print(f"   - Class {class_id} ({class_name}): {confidence:.2%}")
    else:
        print("\nNo objects detected")
else:
    print(f"\nTest image not found: {test_image}")
