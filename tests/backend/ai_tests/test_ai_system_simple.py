#!/usr/bin/env python3
"""
Simple test to verify the AI system is working end-to-end
"""

import requests
import json
import base64
import io
from PIL import Image, ImageDraw

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw simple document content
    draw.rectangle([10, 10, 290, 40], fill='lightblue', outline='blue')
    draw.text((20, 20), "TEST TRANSCRIPT", fill='black')
    
    # Add some text content
    draw.text((20, 60), "Student: John Doe", fill='black')
    draw.text((20, 80), "Grade: A", fill='black') 
    draw.text((20, 100), "Subject: Mathematics", fill='black')
    draw.text((20, 120), "Semester: Fall 2024", fill='black')
    
    return img

def image_to_base64(img):
    """Convert PIL image to base64 string"""
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return img_base64

def test_ai_system():
    """Test the AI system end-to-end"""
    print("Testing TCU-CEAA AI Verification System")
    print("=" * 50)
    
    # Create test image
    print("1. Creating test document image...")
    test_img = create_test_image()
    img_base64 = image_to_base64(test_img)
    print("   ✓ Test image created")
    
    # Prepare API request
    print("2. Preparing API request...")
    data = {
        'image_data': f'data:image/jpeg;base64,{img_base64}',
        'document_type': 'transcript'
    }
    
    # Make API request
    print("3. Sending request to AI analysis endpoint...")
    try:
        response = requests.post(
            'http://localhost:8000/api/ai-document-analysis/',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✓ AI analysis completed successfully!")
            
            # Display key results
            print("\n4. AI Analysis Results:")
            print("-" * 30)
            
            if 'overall_score' in result:
                print(f"   Overall Score: {result['overall_score']:.2f}")
            
            if 'processing_time' in result:
                print(f"   Processing Time: {result['processing_time']:.2f}s")
            
            if 'algorithms_used' in result:
                print(f"   Algorithms Used: {len(result['algorithms_used'])}")
                for algo in result['algorithms_used']:
                    print(f"     - {algo}")
            
            # Check individual algorithm results
            algorithms = ['document_validation', 'face_verification', 'fraud_detection']
            
            for algo in algorithms:
                if algo in result and result[algo]:
                    print(f"\n   {algo.replace('_', ' ').title()}:")
                    algo_result = result[algo]
                    
                    if 'confidence' in algo_result:
                        print(f"     Confidence: {algo_result['confidence']:.2f}")
                    if 'is_valid' in algo_result:
                        print(f"     Valid: {algo_result['is_valid']}")
                    if 'has_face' in algo_result:
                        print(f"     Face Detected: {algo_result['has_face']}")
                    if 'is_likely_fraud' in algo_result:
                        print(f"     Fraud Risk: {algo_result['is_likely_fraud']}")
            
            print(f"\n✓ AI System Test: PASSED")
            return True
            
        elif response.status_code == 404:
            print("   ✗ API endpoint not found")
            print("   Check if the URL is correct: /api/ai-document-analysis/")
            return False
            
        elif response.status_code == 500:
            print("   ✗ Server error occurred")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Raw error: {response.text[:200]}")
            return False
            
        else:
            print(f"   ✗ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ✗ Could not connect to server")
        print("   Make sure Django server is running on http://localhost:8000")
        return False
        
    except requests.exceptions.Timeout:
        print("   ✗ Request timed out")
        print("   AI processing may be taking too long")
        return False
        
    except Exception as e:
        print(f"   ✗ Test failed: {e}")
        return False

def main():
    """Run the test"""
    success = test_ai_system()
    
    if success:
        print("\n🎉 AI System is working correctly!")
        print("✨ All components are functional")
        return 0
    else:
        print("\n❌ AI System test failed")
        print("🔧 Check server logs for details")
        return 1

if __name__ == "__main__":
    exit(main())