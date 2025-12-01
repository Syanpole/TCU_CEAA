"""
Debug AWS Rekognition Face Liveness Results
============================================
This script checks:
1. AWS credentials configuration
2. Rekognition API connectivity
3. Session status and results
4. Detailed failure reasons
"""

import os
import sys
import django
import logging

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.conf import settings
from myapp.rekognition_service import BiometricVerificationService
from myapp.models import FaceVerificationSession, CustomUser
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_aws_config():
    """Check AWS configuration"""
    print("\n" + "="*70)
    print("1. AWS CONFIGURATION CHECK")
    print("="*70)
    
    checks = {
        'VERIFICATION_SERVICE_ENABLED': getattr(settings, 'VERIFICATION_SERVICE_ENABLED', False),
        'AWS_ACCESS_KEY_ID': getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        'AWS_SECRET_ACCESS_KEY': bool(getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)),
        'VERIFICATION_SERVICE_REGION': getattr(settings, 'VERIFICATION_SERVICE_REGION', 'us-east-1'),
        'VERIFICATION_SERVICE_MIN_CONFIDENCE': getattr(settings, 'VERIFICATION_SERVICE_MIN_CONFIDENCE', 80),
        'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None),
    }
    
    for key, value in checks.items():
        if key == 'AWS_SECRET_ACCESS_KEY':
            status_icon = "✓" if value else "✗"
            print(f"  {status_icon} {key}: {'*' * 20} (present: {value})")
        else:
            status_icon = "✓" if value else "✗"
            print(f"  {status_icon} {key}: {value}")
    
    return all([
        checks['VERIFICATION_SERVICE_ENABLED'],
        checks['AWS_ACCESS_KEY_ID'],
        checks['AWS_SECRET_ACCESS_KEY']
    ])


def test_rekognition_connection():
    """Test connection to AWS Rekognition"""
    print("\n" + "="*70)
    print("2. AWS REKOGNITION CONNECTION TEST")
    print("="*70)
    
    try:
        service = BiometricVerificationService()
        
        if not service.enabled:
            print("  ✗ Service not enabled or boto3 not available")
            return False
        
        print(f"  ✓ Service initialized")
        print(f"  ✓ Region: {service.region}")
        print(f"  ✓ Min confidence: {service.min_confidence}%")
        print(f"  ✓ Similarity threshold: {service.similarity_threshold}%")
        
        # Try to create a test session
        print("\n  Testing session creation...")
        result = service.create_liveness_session()
        
        if result['success']:
            print(f"  ✓ Successfully created test session: {result['session_id']}")
            return True
        else:
            print(f"  ✗ Failed to create session: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_recent_sessions(username=None):
    """Check recent verification sessions"""
    print("\n" + "="*70)
    print("3. RECENT VERIFICATION SESSIONS")
    print("="*70)
    
    # Get recent sessions
    sessions = FaceVerificationSession.objects.all().order_by('-created_at')[:10]
    
    if username:
        try:
            user = CustomUser.objects.get(username=username)
            sessions = sessions.filter(user=user)
            print(f"\n  Filtering for user: {username}")
        except CustomUser.DoesNotExist:
            print(f"\n  ⚠ User '{username}' not found, showing all sessions")
    
    if not sessions:
        print("\n  No verification sessions found")
        return
    
    print(f"\n  Found {sessions.count()} recent sessions:\n")
    
    for session in sessions:
        print(f"  Session ID: {session.session_id}")
        print(f"  User: {session.user.username} (ID: {session.user.id})")
        print(f"  Status: {session.status}")
        print(f"  Created: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Expires: {session.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Expired: {'Yes' if session.is_expired() else 'No'}")
        print(f"  Liveness Score: {session.liveness_score if session.liveness_score else 'N/A'}")
        print(f"  Is Live: {session.is_live}")
        print(f"  Fraud Score: {session.fraud_risk_score}")
        print(f"  Device: {session.device_fingerprint[:16]}...")
        print(f"  IP: {session.ip_address}")
        
        if session.fraud_flags:
            print(f"  Fraud Flags: {session.fraud_flags}")
        
        if session.aws_response:
            print(f"\n  AWS Response Details:")
            print(f"    Status: {session.aws_response.get('status', 'N/A')}")
            print(f"    Confidence: {session.aws_response.get('confidence', 'N/A')}")
            
        print("\n" + "-"*70)


def analyze_session_details(session_id):
    """Analyze specific session in detail"""
    print("\n" + "="*70)
    print(f"4. DETAILED SESSION ANALYSIS: {session_id}")
    print("="*70)
    
    try:
        session = FaceVerificationSession.objects.get(session_id=session_id)
    except FaceVerificationSession.DoesNotExist:
        print(f"  ✗ Session {session_id} not found")
        return
    
    print(f"\n  📋 Session Information:")
    print(f"  ├─ ID: {session.session_id}")
    print(f"  ├─ User: {session.user.username} ({session.user.email})")
    print(f"  ├─ Status: {session.get_status_display()}")
    print(f"  ├─ Type: {session.verification_type}")
    print(f"  ├─ Created: {session.created_at}")
    print(f"  ├─ Expires: {session.expires_at}")
    print(f"  └─ Expired: {'✗ YES' if session.is_expired() else '✓ NO'}")
    
    print(f"\n  📊 Verification Scores:")
    print(f"  ├─ Overall Confidence: {session.confidence_score if session.confidence_score else 'N/A'}")
    print(f"  ├─ Liveness Score: {session.liveness_score if session.liveness_score else 'N/A'}")
    print(f"  ├─ Similarity Score: {session.similarity_score if session.similarity_score else 'N/A'}")
    print(f"  ├─ Is Live: {'✓ YES' if session.is_live else '✗ NO'}")
    print(f"  └─ Face Match: {'✓ YES' if session.face_match else '✗ NO'}")
    
    print(f"\n  🛡️ Security Metadata:")
    print(f"  ├─ Device Fingerprint: {session.device_fingerprint}")
    print(f"  ├─ IP Address: {session.ip_address}")
    print(f"  ├─ User Agent: {session.user_agent[:80]}...")
    print(f"  ├─ Geolocation: {session.geolocation_city}, {session.geolocation_region}, {session.geolocation_country}")
    print(f"  ├─ Is Philippines: {'✓ YES' if session.is_philippines else '✗ NO'}")
    print(f"  ├─ VPN Detected: {'⚠ YES' if session.is_vpn else '✓ NO'}")
    print(f"  ├─ Fraud Risk Score: {session.fraud_risk_score}/100")
    print(f"  ├─ Attempt Number: {session.attempt_number}")
    print(f"  └─ Daily Attempt Count: {session.daily_attempt_count}")
    
    if session.fraud_flags:
        print(f"\n  🚨 Fraud Flags ({len(session.fraud_flags)}):")
        for i, flag in enumerate(session.fraud_flags, 1):
            print(f"  {i}. {flag.get('type')}: {flag.get('description')} (Severity: {flag.get('severity')})")
    
    print(f"\n  🔍 AWS Rekognition Response:")
    if session.aws_response:
        import json
        print(json.dumps(session.aws_response, indent=4))
        
        # Analyze why it might have failed
        print(f"\n  💡 Analysis:")
        
        aws_status = session.aws_response.get('status', '')
        confidence = session.aws_response.get('confidence', 0)
        
        if aws_status == 'SUCCEEDED':
            print(f"  ✓ AWS status: SUCCEEDED")
        else:
            print(f"  ✗ AWS status: {aws_status}")
            print(f"    Possible reasons:")
            print(f"    - Session may have failed during face detection")
            print(f"    - User may have closed the camera too early")
            print(f"    - Poor lighting conditions")
            print(f"    - Camera permissions denied")
        
        min_conf = getattr(settings, 'VERIFICATION_SERVICE_MIN_CONFIDENCE', 80)
        if confidence < min_conf:
            print(f"  ✗ Confidence too low: {confidence}% (minimum: {min_conf}%)")
            print(f"    Possible reasons:")
            print(f"    - Poor lighting or image quality")
            print(f"    - Face not clearly visible")
            print(f"    - Movement during capture")
            print(f"    - Presentation attack detected (photo/video)")
        else:
            print(f"  ✓ Confidence acceptable: {confidence}%")
            
        if not session.is_live:
            print(f"  ✗ Liveness check failed")
            print(f"    User needs to:")
            print(f"    - Ensure good lighting (face clearly visible)")
            print(f"    - Look directly at camera")
            print(f"    - Follow on-screen movement prompts")
            print(f"    - Don't use photos or videos (will be detected)")
    else:
        print(f"  ⚠ No AWS response data stored")
        print(f"    This means the session was created but results never retrieved")
    
    if session.reference_image_url:
        print(f"\n  📸 Reference Image: {session.reference_image_url}")
    
    if session.audit_image_url:
        print(f"  📸 Audit Image: {session.audit_image_url}")


def get_recommendations(session_id=None):
    """Get recommendations for improving success rate"""
    print("\n" + "="*70)
    print("5. RECOMMENDATIONS")
    print("="*70)
    
    print("\n  💡 For Users:")
    print("  1. Ensure good lighting (face should be clearly visible)")
    print("  2. Look directly at the camera")
    print("  3. Follow on-screen facial movement prompts")
    print("  4. Stay still during capture")
    print("  5. Remove glasses if causing glare")
    print("  6. Use a stable internet connection")
    print("  7. Don't use photos or videos (will be detected as spoofing)")
    
    print("\n  💡 For Administrators:")
    print("  1. Check AWS Rekognition IAM permissions")
    print("  2. Verify S3 bucket access for audit images")
    print("  3. Monitor fraud detection scores")
    print("  4. Review failed sessions for patterns")
    print("  5. Ensure Cognito Identity Pool is properly configured")
    print("  6. Check CloudWatch for API errors")
    
    print("\n  💡 Common Issues:")
    print("  - Session expired: User took too long (>5 minutes)")
    print("  - Low confidence: Poor lighting or image quality")
    print("  - Status FAILED: User closed camera or denied permissions")
    print("  - Device mismatch: Security check detected different device")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Debug AWS Rekognition Face Liveness')
    parser.add_argument('--session-id', help='Specific session ID to analyze')
    parser.add_argument('--username', help='Filter sessions by username')
    parser.add_argument('--full', action='store_true', help='Run all checks')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🔍 AWS REKOGNITION FACE LIVENESS DEBUGGER")
    print("="*70)
    
    # Run checks
    config_ok = check_aws_config()
    
    if config_ok:
        connection_ok = test_rekognition_connection()
    else:
        print("\n⚠ Cannot test connection - AWS configuration incomplete")
        connection_ok = False
    
    check_recent_sessions(args.username)
    
    if args.session_id:
        analyze_session_details(args.session_id)
    elif args.full:
        # Analyze the most recent session
        latest = FaceVerificationSession.objects.order_by('-created_at').first()
        if latest:
            analyze_session_details(latest.session_id)
    
    get_recommendations()
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print("\nUsage:")
    print("  python debug_face_liveness.py --session-id <session-id>  # Analyze specific session")
    print("  python debug_face_liveness.py --username <username>      # Filter by user")
    print("  python debug_face_liveness.py --full                     # Full analysis")
    print("")
