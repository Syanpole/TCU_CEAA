"""
Quick Test: Identity Verification
==================================

Test the identity verification with a simple example.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.id_verification_service import IDVerificationService
from myapp.models import CustomUser


def quick_test():
    """Quick test of identity verification."""
    print("\n" + "="*60)
    print("🔒 IDENTITY VERIFICATION - QUICK TEST")
    print("="*60 + "\n")
    
    # Get test user
    try:
        user = CustomUser.objects.get(username='lloyd.ramos')
        print(f"✅ Test User: {user.first_name} {user.middle_initial} {user.last_name}")
        print(f"   Student ID: {user.student_id}\n")
    except CustomUser.DoesNotExist:
        print("❌ Test user not found. Run test_identity_verification.py first.\n")
        return
    
    # Find test image
    test_image = Path(BASE_DIR) / 'media' / 'documents' / '2025' / '09' / 'ID_PIC_g7t6DG3.jpg'
    if not test_image.exists():
        print(f"❌ Test image not found: {test_image}\n")
        return
    
    # Initialize service
    service = IDVerificationService()
    
    # Test with user
    print("📷 Testing ID verification WITH user identity check...")
    result = service.verify_id_card(str(test_image), user=user)
    
    print(f"\n📊 Result:")
    print(f"   Status: {result['status']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    print(f"   Checks: {result['checks_passed']}/{len(result['validation_checks'])}")
    
    identity = result.get('identity_verification', {})
    if identity:
        print(f"\n👤 Identity Match:")
        print(f"   Name: {'✅ MATCH' if identity.get('name_match') else '❌ MISMATCH'}")
        print(f"   Student #: {'✅ MATCH' if identity.get('student_number_match') else '❌ MISMATCH'}")
        print(f"   Overall: {'✅ VERIFIED' if identity.get('match') else '❌ FAILED'}")
    
    print("\n" + "="*60)
    if result['status'] == 'VALID' and identity.get('match'):
        print("🎉 IDENTITY VERIFICATION WORKING!")
    else:
        print("❌ IDENTITY VERIFICATION FAILED!")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        quick_test()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
