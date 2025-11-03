"""
Migrate Files to Cloud Storage
===============================

Management command to migrate existing local files to cloud storage (S3).
This is useful when enabling cloud storage on an existing system.

Usage:
    python manage.py migrate_to_cloud_storage
    python manage.py migrate_to_cloud_storage --dry-run
    python manage.py migrate_to_cloud_storage --batch-size 50
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from myapp.models import CustomUser, DocumentSubmission, GradeSubmission
from myapp.storage_backends import (
    ProfileImageStorage, DocumentStorage, GradeSheetStorage
)
import os
import boto3
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Migrate local files to cloud storage (S3)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually migrating',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of files to process in each batch',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('CLOUD STORAGE MIGRATION'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No files will be migrated'))
        
        # Check if cloud storage is enabled
        if not settings.USE_CLOUD_STORAGE:
            self.stdout.write(self.style.ERROR(
                '\n❌ Cloud storage is not enabled. Set USE_CLOUD_STORAGE=True in .env'
            ))
            return
        
        self.stdout.write(self.style.SUCCESS('\n✅ Cloud storage is enabled'))
        self.stdout.write(f'   Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
        self.stdout.write(f'   Region: {settings.AWS_S3_REGION_NAME}')
        
        # Initialize counters
        total_migrated = 0
        total_failed = 0
        total_skipped = 0
        
        # Migrate profile images
        self.stdout.write('\n📸 Migrating profile images...')
        stats = self._migrate_model_files(
            CustomUser.objects.exclude(profile_image=''),
            'profile_image',
            ProfileImageStorage(),
            dry_run,
            batch_size
        )
        total_migrated += stats['migrated']
        total_failed += stats['failed']
        total_skipped += stats['skipped']
        
        # Migrate document submissions
        self.stdout.write('\n📄 Migrating document submissions...')
        stats = self._migrate_model_files(
            DocumentSubmission.objects.exclude(document_file=''),
            'document_file',
            DocumentStorage(),
            dry_run,
            batch_size
        )
        total_migrated += stats['migrated']
        total_failed += stats['failed']
        total_skipped += stats['skipped']
        
        # Migrate grade submissions
        self.stdout.write('\n📊 Migrating grade submissions...')
        stats = self._migrate_model_files(
            GradeSubmission.objects.exclude(grade_sheet=''),
            'grade_sheet',
            GradeSheetStorage(),
            dry_run,
            batch_size
        )
        total_migrated += stats['migrated']
        total_failed += stats['failed']
        total_skipped += stats['skipped']
        
        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.HTTP_INFO('MIGRATION SUMMARY'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'✅ Successfully migrated: {total_migrated}')
        self.stdout.write(f'⏭️  Skipped: {total_skipped}')
        self.stdout.write(f'❌ Failed: {total_failed}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\n💡 This was a dry run. Run without --dry-run to perform actual migration.'
            ))
        elif total_migrated > 0:
            self.stdout.write(self.style.SUCCESS(
                '\n🎉 Migration completed successfully!'
            ))
        
        self.stdout.write('')
    
    def _migrate_model_files(self, queryset, field_name, storage, dry_run, batch_size):
        """Migrate files for a specific model queryset."""
        migrated = 0
        failed = 0
        skipped = 0
        total = queryset.count()
        
        self.stdout.write(f'   Found {total} file(s) to process')
        
        if total == 0:
            return {'migrated': 0, 'failed': 0, 'skipped': 0}
        
        for obj in queryset.iterator(chunk_size=batch_size):
            try:
                file_field = getattr(obj, field_name)
                
                if not file_field:
                    skipped += 1
                    continue
                
                # Get local file path
                local_path = file_field.path if hasattr(file_field, 'path') else None
                
                if not local_path or not os.path.exists(local_path):
                    self.stdout.write(f'   ⏭️  Skipped: {file_field.name} (not found locally)')
                    skipped += 1
                    continue
                
                # Check if already in cloud
                if 'amazonaws.com' in str(file_field.url):
                    self.stdout.write(f'   ⏭️  Skipped: {file_field.name} (already in cloud)')
                    skipped += 1
                    continue
                
                if dry_run:
                    self.stdout.write(f'   📦 Would migrate: {file_field.name}')
                    migrated += 1
                else:
                    # Upload to S3
                    with open(local_path, 'rb') as f:
                        file_content = f.read()
                        file_name = os.path.basename(file_field.name)
                        cloud_path = storage.save(file_name, f)
                        
                        # Update model field
                        setattr(obj, field_name, cloud_path)
                        obj.save(update_fields=[field_name])
                        
                        self.stdout.write(f'   ✅ Migrated: {file_field.name} → {cloud_path}')
                        migrated += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Failed: {file_field.name} - {str(e)}'))
                failed += 1
        
        return {'migrated': migrated, 'failed': failed, 'skipped': skipped}
