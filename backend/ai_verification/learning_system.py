"""
Learning System for AI Document Verification
Provides adaptive learning and recommendations for document verification
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LearningSystem:
    """
    Adaptive learning system for document verification
    Tracks verification patterns and provides recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.processing_data = []
        self.recommendations_cache = {}
        
    def get_recommendation(self, document_type: str, ocr_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI recommendation for document verification
        
        Args:
            document_type: Type of document being verified
            ocr_results: OCR extraction results
            
        Returns:
            Dictionary with recommendation and confidence score
        """
        try:
            # Basic recommendation logic
            confidence = 0.7
            
            # Adjust confidence based on OCR quality
            if ocr_results and 'text' in ocr_results:
                text_length = len(ocr_results.get('text', ''))
                if text_length > 100:
                    confidence += 0.1
                if text_length > 500:
                    confidence += 0.1
            
            return {
                'recommended_type': document_type,
                'confidence': min(confidence, 1.0),
                'reasoning': 'Based on OCR analysis and pattern matching'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting recommendation: {str(e)}")
            return {
                'recommended_type': document_type,
                'confidence': 0.5,
                'reasoning': 'Default recommendation'
            }
    
    def record_processing_data(self, document_type: str, result: Dict[str, Any]) -> None:
        """
        Record processing data for learning
        
        Args:
            document_type: Type of document processed
            result: Verification result
        """
        try:
            # Store processing data for future learning
            processing_record = {
                'document_type': document_type,
                'processing_time': result.get('processing_time', 0),
                'confidence': result.get('confidence_score', 0),
                'verified': result.get('verified', False),
                'timestamp': result.get('timestamp')
            }
            
            self.processing_data.append(processing_record)
            
            # Keep only recent records (last 1000)
            if len(self.processing_data) > 1000:
                self.processing_data = self.processing_data[-1000:]
                
            self.logger.debug(f"Recorded processing data for {document_type}")
            
        except Exception as e:
            self.logger.error(f"Error recording processing data: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get learning system statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_records': len(self.processing_data),
            'average_processing_time': sum(r.get('processing_time', 0) for r in self.processing_data) / max(len(self.processing_data), 1),
            'average_confidence': sum(r.get('confidence', 0) for r in self.processing_data) / max(len(self.processing_data), 1)
        }


# Singleton instance
learning_system = LearningSystem()
