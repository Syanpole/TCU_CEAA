"""
Test Advanced OCR Service
==========================

Management command to test the Advanced OCR service configuration
and verify that document processing is working correctly.

Usage:
    python manage.py test_advanced_ocr
    python manage.py test_advanced_ocr --file path/to/document.pdf
"""

from django.core.management.base import BaseCommand
from myapp.advanced_ocr_service import get_advanced_ocr_service
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Test Advanced OCR Service configuration and functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to a test document file',
            default=None
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        self.stdout.write(self.style.HTTP_INFO('ADVANCED OCR SERVICE TEST'))
        self.stdout.write(self.style.HTTP_INFO('=' * 70))
        
        # Get OCR service
        ocr_service = get_advanced_ocr_service()
        
        # Check configuration
        self.stdout.write('\n📋 Configuration Status:')
        self.stdout.write(f'   USE_ADVANCED_OCR: {settings.USE_ADVANCED_OCR}')
        self.stdout.write(f'   OCR Region: {settings.ADVANCED_OCR_REGION}')
        self.stdout.write(f'   Confidence Threshold: {settings.OCR_CONFIDENCE_THRESHOLD}%')
        self.stdout.write(f'   Service Enabled: {ocr_service.is_enabled()}')
        
        if not ocr_service.is_enabled():
            self.stdout.write(self.style.WARNING(
                '\n⚠️  Advanced OCR is not enabled or not configured properly.'
            ))
            self.stdout.write('\nTo enable Advanced OCR:')
            self.stdout.write('1. Set USE_ADVANCED_OCR=True in .env')
            self.stdout.write('2. Configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY')
            self.stdout.write('3. Ensure your AWS account has OCR service permissions')
            return
        
        self.stdout.write(self.style.SUCCESS('\n✅ Advanced OCR Service is enabled and configured'))
        
        # Test with file if provided
        test_file = options.get('file')
        if test_file:
            if not os.path.exists(test_file):
                self.stdout.write(self.style.ERROR(f'\n❌ File not found: {test_file}'))
                return
            
            self.stdout.write(f'\n🔍 Testing OCR with file: {test_file}')
            
            try:
                with open(test_file, 'rb') as f:
                    file_bytes = f.read()
                
                # Test text extraction
                self.stdout.write('\n📄 Extracting text...')
                result = ocr_service.extract_text(file_bytes)
                
                if result['success']:
                    self.stdout.write(self.style.SUCCESS('✅ Text extraction successful'))
                    self.stdout.write(f'   Confidence: {result["confidence"]:.2f}%')
                    self.stdout.write(f'   Blocks found: {result["block_count"]}')
                    self.stdout.write(f'\n   Extracted text preview:')
                    preview = result['text'][:200] + '...' if len(result['text']) > 200 else result['text']
                    self.stdout.write(f'   {preview}')
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Text extraction failed: {result["error"]}'))
                
                # Test table extraction
                self.stdout.write('\n📊 Extracting tables...')
                table_result = ocr_service.extract_tables(file_bytes)
                
                if table_result['success']:
                    table_count = len(table_result['tables'])
                    self.stdout.write(self.style.SUCCESS(f'✅ Found {table_count} table(s)'))
                    for i, table in enumerate(table_result['tables'][:2], 1):
                        self.stdout.write(f'   Table {i}: {table["row_count"]} rows x {table["col_count"]} cols')
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Table extraction: {table_result["error"]}'))
                
                # Test form extraction
                self.stdout.write('\n📝 Extracting form fields...')
                form_result = ocr_service.extract_forms(file_bytes)
                
                if form_result['success']:
                    field_count = len(form_result['fields'])
                    self.stdout.write(self.style.SUCCESS(f'✅ Found {field_count} form field(s)'))
                    for field in form_result['fields'][:5]:
                        self.stdout.write(f'   {field["key"]}: {field["value"]} ({field["confidence"]:.1f}%)')
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Form extraction: {form_result["error"]}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n❌ Test failed: {str(e)}'))
        else:
            self.stdout.write('\n💡 Tip: Use --file flag to test with a specific document')
            self.stdout.write('   Example: python manage.py test_advanced_ocr --file grades.pdf')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Test complete\n'))
