"""
Enhanced AI Document Verification - Demo and Test Scenarios
This script demonstrates how the new AI system prevents fraudulent document uploads.
"""

import os
import sys
import django
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFont
import io

# Setup Django environment
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from ai_verification.base_verifier import document_type_detector
from django.core.files.uploadedfile import SimpleUploadedFile


class AIVerificationDemo:
    """Demonstrate the AI verification system capabilities"""
    
    def __init__(self):
        self.demo_files = []
    
    def create_fake_birth_certificate_image(self):
        """Create a fake image that looks like it might be a birth certificate"""
        # Create a simple white image with some text
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to get a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            title_font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Draw fake birth certificate content
        draw.text((200, 50), "BIRTH CERTIFICATE", fill='black', font=title_font)
        draw.text((50, 100), "Republic of the Philippines", fill='black', font=font)
        draw.text((50, 150), "Civil Registry", fill='black', font=font)
        draw.text((50, 200), "Name: JOHN DELA CRUZ", fill='black', font=font)
        draw.text((50, 230), "Date of Birth: January 1, 2000", fill='black', font=font)
        draw.text((50, 260), "Place of Birth: Manila, Philippines", fill='black', font=font)
        draw.text((50, 290), "Father: JUAN DELA CRUZ", fill='black', font=font)
        draw.text((50, 320), "Mother: MARIA SANTOS", fill='black', font=font)
        draw.text((50, 400), "Registry No: 2000-001", fill='black', font=font)
        draw.text((50, 450), "Date Issued: March 15, 2024", fill='black', font=font)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def create_random_image(self):
        """Create a random colorful image (like a photo)"""
        img = Image.new('RGB', (800, 600))
        draw = ImageDraw.Draw(img)
        
        # Fill with random colors to simulate a photo
        import random
        for i in range(100):
            x1 = random.randint(0, 800)
            y1 = random.randint(0, 600)
            x2 = random.randint(x1, 800)
            y2 = random.randint(y1, 600)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.rectangle([x1, y1, x2, y2], fill=color)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def create_school_id_like_image(self):
        """Create an image that looks like a school ID"""
        img = Image.new('RGB', (400, 250), 'lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            title_font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Draw school ID content
        draw.text((50, 20), "TRINITY COLLEGE UNIVERSITY", fill='black', font=title_font)
        draw.text((50, 50), "STUDENT IDENTIFICATION", fill='black', font=font)
        draw.text((50, 90), "Name: MARIA SANTOS", fill='black', font=font)
        draw.text((50, 110), "Student ID: 22-12345", fill='black', font=font)
        draw.text((50, 130), "Course: BSIT", fill='black', font=font)
        draw.text((50, 150), "Valid Until: 2025", fill='black', font=font)
        
        # Draw a rectangle for photo
        draw.rectangle([300, 80, 380, 160], outline='black', width=2)
        draw.text((315, 110), "PHOTO", fill='black')
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def run_verification_demo(self):
        """Run the verification demo with different test cases"""
        print("🎭 AI Document Verification Demo")
        print("=" * 50)
        print("This demo shows how the AI system detects fraudulent uploads")
        print()
        
        # Test Case 1: Fake birth certificate (should pass basic checks)
        print("Test Case 1: Realistic Fake Birth Certificate")
        print("-" * 45)
        
        fake_birth_cert = self.create_fake_birth_certificate_image()
        fake_file = SimpleUploadedFile(
            "birth_certificate.png", 
            fake_birth_cert, 
            content_type="image/png"
        )
        
        # Create a mock document submission
        class MockDocumentSubmission:
            def __init__(self, doc_type):
                self.document_type = doc_type
                self.document_file = fake_file
            
            def get_document_type_display(self):
                return doc_type.replace('_', ' ').title()
        
        mock_birth_cert = MockDocumentSubmission('birth_certificate')
        
        try:
            result = document_type_detector.verify_document_type(mock_birth_cert, fake_file)
            
            print(f"✅ Verification completed")
            print(f"   Document Type Match: {'✅' if result['document_type_match'] else '❌'}")
            print(f"   Confidence Score: {result['confidence_score']:.1%}")
            print(f"   Fraud Detected: {'🚨 YES' if result.get('is_likely_fraud', False) else '✅ NO'}")
            print(f"   Recommendation: {result['recommendation'].upper()}")
            
            if result.get('fraud_indicators'):
                print("   Fraud Indicators:")
                for indicator in result['fraud_indicators'][:3]:
                    print(f"     • {indicator}")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
        
        print()
        
        # Test Case 2: Random image as birth certificate (should be rejected)
        print("Test Case 2: Random Image as Birth Certificate")
        print("-" * 48)
        
        random_img = self.create_random_image()
        random_file = SimpleUploadedFile(
            "my_photo.jpg", 
            random_img, 
            content_type="image/jpeg"
        )
        
        mock_random = MockDocumentSubmission('birth_certificate')
        mock_random.document_file = random_file
        
        try:
            result = document_type_detector.verify_document_type(mock_random, random_file)
            
            print(f"✅ Verification completed")
            print(f"   Document Type Match: {'✅' if result['document_type_match'] else '❌'}")
            print(f"   Confidence Score: {result['confidence_score']:.1%}")
            print(f"   Fraud Detected: {'🚨 YES' if result.get('is_likely_fraud', False) else '✅ NO'}")
            print(f"   Recommendation: {result['recommendation'].upper()}")
            
            if result.get('fraud_indicators'):
                print("   Fraud Indicators:")
                for indicator in result['fraud_indicators'][:3]:
                    print(f"     • {indicator}")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
        
        print()
        
        # Test Case 3: School ID as birth certificate (wrong type)
        print("Test Case 3: School ID Submitted as Birth Certificate")
        print("-" * 52)
        
        school_id_img = self.create_school_id_like_image()
        school_id_file = SimpleUploadedFile(
            "student_id.png", 
            school_id_img, 
            content_type="image/png"
        )
        
        mock_wrong_type = MockDocumentSubmission('birth_certificate')
        mock_wrong_type.document_file = school_id_file
        
        try:
            result = document_type_detector.verify_document_type(mock_wrong_type, school_id_file)
            
            print(f"✅ Verification completed")
            print(f"   Document Type Match: {'✅' if result['document_type_match'] else '❌'}")
            print(f"   Confidence Score: {result['confidence_score']:.1%}")
            print(f"   Fraud Detected: {'🚨 YES' if result.get('is_likely_fraud', False) else '✅ NO'}")
            print(f"   Recommendation: {result['recommendation'].upper()}")
            
            if result.get('fraud_indicators'):
                print("   Fraud Indicators:")
                for indicator in result['fraud_indicators'][:3]:
                    print(f"     • {indicator}")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
        
        print()
        
        # Summary
        print("🎯 DEMO SUMMARY")
        print("=" * 50)
        print("The Enhanced AI Document Verification System:")
        print("✅ Analyzes document content using OCR")
        print("✅ Detects document type mismatches")
        print("✅ Identifies random images and photos")
        print("✅ Validates file integrity and headers")
        print("✅ Provides confidence scores and recommendations")
        print("✅ Automatically approves/rejects based on analysis")
        print()
        print("🛡️ This prevents students from submitting:")
        print("   • Personal photos as official documents")
        print("   • Screenshots from the internet")
        print("   • Wrong document types")
        print("   • Low quality or corrupted files")
        print("   • Fake or manipulated documents")
        
    def show_document_signatures(self):
        """Show the document signatures used for verification"""
        print("\n📋 DOCUMENT VERIFICATION SIGNATURES")
        print("=" * 50)
        
        for doc_type, signature in document_type_detector.document_signatures.items():
            print(f"\n🔍 {doc_type.replace('_', ' ').title()}")
            print(f"   Confidence Threshold: {signature['confidence_threshold']:.0%}")
            
            print("   Primary Keywords:")
            for kw in signature['required_keywords']['primary'][:5]:
                print(f"     • {kw}")
            
            print("   Forbidden Keywords:")
            for kw in signature['forbidden_keywords'][:5]:
                print(f"     • {kw}")
            
            if len(signature['forbidden_keywords']) > 5:
                print(f"     ... and {len(signature['forbidden_keywords']) - 5} more")

def main():
    """Main demo function"""
    print("🎭 Enhanced AI Document Verification - Interactive Demo")
    print("This demo shows how the AI prevents fraudulent document uploads")
    print()
    
    demo = AIVerificationDemo()
    
    try:
        # Show document signatures
        demo.show_document_signatures()
        
        print("\n" + "=" * 60)
        input("Press Enter to run verification tests...")
        
        # Run verification demo
        demo.run_verification_demo()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("\nTo see this system in action:")
        print("1. Start your Django server: python manage.py runserver")
        print("2. Go to the TCU-CEAA frontend")
        print("3. Try uploading different types of files as documents")
        print("4. Watch the AI automatically verify or reject them")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
