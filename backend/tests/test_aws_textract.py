"""
Test AWS Textract Connection
Verify AWS credentials and Textract service availability
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

import django
django.setup()

from myapp.advanced_ocr_service import get_advanced_ocr_service
from PIL import Image
import io

def test_aws_textract():
    """Test AWS Textract connection and functionality."""
    
    print("=" * 80)
    print("AWS TEXTRACT CONNECTION TEST")
    print("=" * 80)
    
    # Initialize service
    service = get_advanced_ocr_service()
    
    print(f"\n✅ Service initialized")
    print(f"   - Enabled: {service.is_enabled()}")
    print(f"   - Region: {service.region}")
    print(f"   - Confidence Threshold: {service.confidence_threshold}")
    
    if not service.is_enabled():
        print("\n❌ Advanced OCR is NOT enabled!")
        print("   Check your .env file for:")
        print("   - USE_ADVANCED_OCR=True")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY")
        return
    
    # Create a simple test image with text
    print("\n🔍 Creating test image...")
    img = Image.new('RGB', (400, 100), color='white')
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    print("📄 Testing text extraction...")
    try:
        result = service.extract_text(img_bytes)
        
        if result['success']:
            print("\n✅ AWS TEXTRACT IS WORKING!")
            print(f"   - Confidence: {result['confidence']:.2f}%")
            print(f"   - Blocks found: {result.get('block_count', 0)}")
            print(f"   - Text extracted: {len(result['text'])} characters")
            if result['text']:
                print(f"   - Sample text: {result['text'][:100]}")
        else:
            print(f"\n❌ Text extraction failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    test_aws_textract()
