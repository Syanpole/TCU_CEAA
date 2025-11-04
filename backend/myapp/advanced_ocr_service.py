"""
Advanced OCR Service
====================

This module provides advanced Optical Character Recognition (OCR) capabilities
for processing documents with high accuracy using state-of-the-art AI models.

Features:
- High-accuracy text extraction from images and PDFs
- Automatic layout analysis and text positioning
- Form field detection and key-value pair extraction
- Table detection and structured data extraction
- Confidence scoring for extracted text
- Multi-language support

Author: TCU CEAA Development Team
Date: November 2025
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from django.conf import settings
from io import BytesIO
import json

logger = logging.getLogger(__name__)


class AdvancedOCRService:
    """
    Advanced OCR Service using enterprise-grade AI for superior text extraction.
    
    This service provides high-accuracy text extraction from documents using
    state-of-the-art machine learning models.
    """
    
    def __init__(self):
        """Initialize the Advanced OCR service."""
        self.enabled = getattr(settings, 'USE_ADVANCED_OCR', False)
        self.region = getattr(settings, 'ADVANCED_OCR_REGION', 'us-east-1')
        self.confidence_threshold = getattr(settings, 'OCR_CONFIDENCE_THRESHOLD', 80)
        
        if self.enabled:
            try:
                import boto3
                self._ocr_client = boto3.client(
                    'textract',
                    region_name=self.region,
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
                )
                logger.info("Advanced OCR Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Advanced OCR Service: {str(e)}")
                self.enabled = False
                self._ocr_client = None
        else:
            self._ocr_client = None
            logger.info("Advanced OCR Service disabled (using local OCR)")
    
    def is_enabled(self) -> bool:
        """Check if Advanced OCR is enabled and configured."""
        return self.enabled and self._ocr_client is not None
    
    def extract_text(self, file_bytes: bytes, document_type: str = 'IMAGE') -> Dict[str, Any]:
        """
        Extract text from a document using Advanced OCR.
        
        Args:
            file_bytes: Document content as bytes
            document_type: Type of document ('IMAGE' or 'PDF')
        
        Returns:
            Dictionary containing:
                - text: Extracted text content
                - confidence: Average confidence score (0-100)
                - blocks: Detailed text blocks with positions
                - success: Boolean indicating success
                - error: Error message if failed
        """
        if not self.is_enabled():
            return {
                'success': False,
                'error': 'Advanced OCR is not enabled. Please configure service credentials.',
                'text': '',
                'confidence': 0,
                'blocks': []
            }
        
        try:
            response = self._ocr_client.detect_document_text(
                Document={'Bytes': file_bytes}
            )
            
            text_blocks = []
            full_text = []
            total_confidence = 0
            confidence_count = 0
            
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    text = block.get('Text', '')
                    confidence = block.get('Confidence', 0)
                    
                    full_text.append(text)
                    text_blocks.append({
                        'text': text,
                        'confidence': confidence,
                        'geometry': block.get('Geometry', {})
                    })
                    
                    total_confidence += confidence
                    confidence_count += 1
            
            avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
            extracted_text = '\n'.join(full_text)
            
            logger.info(f"Advanced OCR completed: {len(text_blocks)} blocks, {avg_confidence:.2f}% confidence")
            
            return {
                'success': True,
                'text': extracted_text,
                'confidence': avg_confidence,
                'blocks': text_blocks,
                'block_count': len(text_blocks),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Advanced OCR extraction failed: {str(e)}")
            return {
                'success': False,
                'error': f'OCR processing failed: {str(e)}',
                'text': '',
                'confidence': 0,
                'blocks': []
            }
    
    def extract_tables(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extract tables from a document using Advanced OCR.
        
        Args:
            file_bytes: Document content as bytes
        
        Returns:
            Dictionary containing:
                - tables: List of extracted tables with cells
                - success: Boolean indicating success
                - error: Error message if failed
        """
        if not self.is_enabled():
            return {
                'success': False,
                'error': 'Advanced OCR is not enabled',
                'tables': []
            }
        
        try:
            response = self._ocr_client.analyze_document(
                Document={'Bytes': file_bytes},
                FeatureTypes=['TABLES']
            )
            
            tables = []
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'TABLE':
                    table_data = self._parse_table(block, response.get('Blocks', []))
                    tables.append(table_data)
            
            logger.info(f"Advanced OCR table extraction: {len(tables)} tables found")
            
            return {
                'success': True,
                'tables': tables,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Advanced OCR table extraction failed: {str(e)}")
            return {
                'success': False,
                'error': f'Table extraction failed: {str(e)}',
                'tables': []
            }
    
    def extract_forms(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extract form fields and key-value pairs from a document.
        
        Args:
            file_bytes: Document content as bytes
        
        Returns:
            Dictionary containing:
                - fields: List of form fields with keys and values
                - success: Boolean indicating success
                - error: Error message if failed
        """
        if not self.is_enabled():
            return {
                'success': False,
                'error': 'Advanced OCR is not enabled',
                'fields': []
            }
        
        try:
            response = self._ocr_client.analyze_document(
                Document={'Bytes': file_bytes},
                FeatureTypes=['FORMS']
            )
            
            fields = self._parse_form_fields(response.get('Blocks', []))
            
            logger.info(f"Advanced OCR form extraction: {len(fields)} fields found")
            
            return {
                'success': True,
                'fields': fields,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Advanced OCR form extraction failed: {str(e)}")
            return {
                'success': False,
                'error': f'Form extraction failed: {str(e)}',
                'fields': []
            }
    
    def _parse_table(self, table_block: Dict, all_blocks: List[Dict]) -> Dict:
        """Parse table structure from OCR blocks."""
        # Create a mapping of block IDs to blocks
        block_map = {block['Id']: block for block in all_blocks}
        
        rows = {}
        for relationship in table_block.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                for cell_id in relationship['Ids']:
                    cell = block_map.get(cell_id)
                    if cell and cell['BlockType'] == 'CELL':
                        row_index = cell.get('RowIndex', 0)
                        col_index = cell.get('ColumnIndex', 0)
                        
                        if row_index not in rows:
                            rows[row_index] = {}
                        
                        # Get cell text
                        cell_text = self._get_cell_text(cell, block_map)
                        rows[row_index][col_index] = cell_text
        
        # Convert to 2D array
        table_array = []
        for row_idx in sorted(rows.keys()):
            row_data = []
            for col_idx in sorted(rows[row_idx].keys()):
                row_data.append(rows[row_idx][col_idx])
            table_array.append(row_data)
        
        return {
            'rows': table_array,
            'row_count': len(table_array),
            'col_count': len(table_array[0]) if table_array else 0
        }
    
    def _get_cell_text(self, cell: Dict, block_map: Dict) -> str:
        """Extract text from a table cell."""
        text_parts = []
        for relationship in cell.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child = block_map.get(child_id)
                    if child and child['BlockType'] == 'WORD':
                        text_parts.append(child.get('Text', ''))
        return ' '.join(text_parts)
    
    def _parse_form_fields(self, blocks: List[Dict]) -> List[Dict]:
        """Parse form fields from OCR blocks."""
        block_map = {block['Id']: block for block in blocks}
        fields = []
        
        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET':
                entity_types = block.get('EntityTypes', [])
                if 'KEY' in entity_types:
                    key_text = self._get_text_for_block(block, block_map)
                    value_text = self._get_value_for_key(block, block_map)
                    
                    if key_text:
                        fields.append({
                            'key': key_text,
                            'value': value_text,
                            'confidence': block.get('Confidence', 0)
                        })
        
        return fields
    
    def _get_text_for_block(self, block: Dict, block_map: Dict) -> str:
        """Get text content for a block."""
        text_parts = []
        for relationship in block.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child = block_map.get(child_id)
                    if child and child['BlockType'] == 'WORD':
                        text_parts.append(child.get('Text', ''))
        return ' '.join(text_parts)
    
    def _get_value_for_key(self, key_block: Dict, block_map: Dict) -> str:
        """Get value text for a key block."""
        for relationship in key_block.get('Relationships', []):
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = block_map.get(value_id)
                    if value_block:
                        return self._get_text_for_block(value_block, block_map)
        return ''
    
    def process_grade_document(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Process a grade document with comprehensive analysis.
        
        This is a convenience method that extracts text, tables, and forms
        from a grade document in one call.
        
        Args:
            file_bytes: Grade document content as bytes
        
        Returns:
            Dictionary containing all extracted data
        """
        result = {
            'text_extraction': self.extract_text(file_bytes),
            'table_extraction': self.extract_tables(file_bytes),
            'form_extraction': self.extract_forms(file_bytes),
            'overall_success': False
        }
        
        # Check if at least one extraction method succeeded
        result['overall_success'] = any([
            result['text_extraction']['success'],
            result['table_extraction']['success'],
            result['form_extraction']['success']
        ])
        
        return result


# Singleton instance
_ocr_service = None

def get_advanced_ocr_service() -> AdvancedOCRService:
    """Get or create the singleton Advanced OCR service instance."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = AdvancedOCRService()
    return _ocr_service
