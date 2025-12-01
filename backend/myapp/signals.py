"""
Django signals for automatic document processing.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
import logging

from .models import DocumentSubmission

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=DocumentSubmission)
def cache_previous_status(sender, instance, **kwargs):
    """
    Cache the previous status before saving to detect status changes.
    """
    if instance.pk:  # Only for existing documents
        try:
            previous = DocumentSubmission.objects.get(pk=instance.pk)
            cache.set(f'doc_prev_status_{instance.pk}', previous.status, timeout=60)
        except DocumentSubmission.DoesNotExist:
            pass


@receiver(post_save, sender=DocumentSubmission)
def archive_old_documents_and_extract_coe(sender, instance, created, **kwargs):
    """
    1. Archive older approved documents of the same type when a new one is approved
    2. Automatically extract subjects from COE when it's approved
    """
    # Only process when status is approved
    if instance.status != 'approved':
        return
    
    # Check if status just changed to approved
    previous_status = cache.get(f'doc_prev_status_{instance.pk}')
    if previous_status == 'approved' and not created:
        # Already was approved, skip processing
        return
    
    # TASK 1: Archive older approved documents of the same type
    try:
        # Find all other approved documents of the same type for this student
        older_docs = DocumentSubmission.objects.filter(
            student=instance.student,
            document_type=instance.document_type,
            status='approved',
            is_active=True
        ).exclude(pk=instance.pk)
        
        if older_docs.exists():
            count = older_docs.count()
            older_docs.update(is_active=False)
            logger.info(f"📦 Archived {count} older {instance.document_type} document(s) for student {instance.student.student_id}")
    except Exception as e:
        logger.error(f"❌ Error archiving old documents: {str(e)}")
    
    # TASK 2: Extract COE subjects (only for COE documents)
    if instance.document_type != 'certificate_of_enrollment':
        return
    
    # Check if status just changed to approved (not already approved)
    previous_status = cache.get(f'doc_prev_status_{instance.pk}')
    if previous_status == 'approved' and not created:
        # Already was approved, don't re-extract
        return
    
    # Check if subjects already extracted
    if instance.extracted_subjects and instance.subject_count > 0:
        logger.info(f"COE {instance.id} already has {instance.subject_count} subjects extracted")
        return
    
    # Extract subjects
    logger.info(f"🔄 Auto-extracting subjects from newly approved COE {instance.id}")
    
    try:
        from .coe_verification_service import get_coe_verification_service
        coe_service = get_coe_verification_service()
        
        # Get the file path (handle both local and S3 storage)
        file_path = None
        try:
            if hasattr(instance.document_file, 'path'):
                file_path = instance.document_file.path
            elif hasattr(instance.document_file, 'file'):
                # For S3 or other storage backends
                file_path = instance.document_file.file.name
        except Exception as path_error:
            logger.warning(f"Could not get file path: {str(path_error)}")
        
        if not file_path:
            logger.error(f"❌ No file path available for COE document {instance.id}")
            return
        
        logger.info(f"📄 File path: {file_path}")
        
        # Extract subjects
        subject_result = coe_service.extract_subject_list(file_path)
        
        if subject_result['success'] and subject_result['subjects']:
            # Update the instance (avoid triggering signal again)
            DocumentSubmission.objects.filter(pk=instance.pk).update(
                extracted_subjects=subject_result['subjects'],
                subject_count=subject_result['subject_count']
            )
            logger.info(f"✅ Auto-extracted {subject_result['subject_count']} subjects from COE {instance.id}")
        else:
            logger.warning(f"⚠️ Could not extract subjects from COE {instance.id}: {subject_result.get('errors')}")
    
    except Exception as e:
        logger.error(f"❌ Error auto-extracting subjects from COE {instance.id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
