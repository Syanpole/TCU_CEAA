"""
Reprocess COE document to extract subjects using updated algorithm.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import DocumentSubmission, CustomUser
from myapp.coe_verification_service import get_coe_verification_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reprocess_coe_for_student():
    """Find and reprocess Sean Paul Feliciano's COE."""
    
    # Find the user
    user = CustomUser.objects.filter(
        first_name__icontains='sean',
        last_name__icontains='feliciano'
    ).first()
    
    if not user:
        logger.error("❌ User not found")
        return
    
    logger.info(f"✅ Found user: {user.get_full_name()} (ID: {user.id})")
    
    # Find COE submissions (document_type is 'certificate_of_enrollment' not 'coe')
    coe_submissions = DocumentSubmission.objects.filter(
        student=user,
        document_type='certificate_of_enrollment'
    ).order_by('-submitted_at')
    
    logger.info(f"📄 Found {coe_submissions.count()} COE submission(s)")
    
    if not coe_submissions.exists():
        logger.error("❌ No COE submissions found")
        return
    
    # Get the most recent COE
    coe = coe_submissions.first()
    logger.info(f"📋 Processing COE ID: {coe.id}")
    logger.info(f"   Status: {coe.status}")
    logger.info(f"   File: {coe.document_file.name}")
    logger.info(f"   Current subjects: {coe.extracted_subjects}")
    logger.info(f"   Current subject count: {coe.subject_count}")
    
    # Get the file path
    file_path = coe.document_file.path
    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return
    
    logger.info(f"✅ File exists: {file_path}")
    
    # Extract subjects using the verification service
    logger.info("🔍 Extracting subjects using COE verification service...")
    coe_service = get_coe_verification_service()
    result = coe_service.extract_subject_list(file_path)
    
    if result['success']:
        logger.info(f"✅ Subject extraction successful!")
        logger.info(f"   Confidence: {result['confidence']:.2%}")
        logger.info(f"   Subjects found: {result['subject_count']}")
        
        for i, subject in enumerate(result['subjects'], 1):
            logger.info(f"   {i}. {subject['subject_code']} - {subject['subject_name']}")
        
        # Update the database
        logger.info("💾 Updating database...")
        coe.extracted_subjects = result['subjects']
        coe.subject_count = result['subject_count']
        coe.save()
        
        logger.info("✅ Database updated successfully!")
        logger.info(f"   New extracted_subjects: {coe.extracted_subjects}")
        logger.info(f"   New subject_count: {coe.subject_count}")
    else:
        logger.error(f"❌ Subject extraction failed")
        for error in result.get('errors', []):
            logger.error(f"   - {error}")

if __name__ == '__main__':
    reprocess_coe_for_student()
