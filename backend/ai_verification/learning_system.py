"""
🧠 MACHINE LEARNING TRAINING SYSTEM
Continuously learns from document patterns to improve accuracy
Auto-training based on admin approvals/rejections
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import pickle

logger = logging.getLogger(__name__)

class DocumentLearningSystem:
    """
    🎯 Continuous learning system that improves AI accuracy over time
    Learns from admin decisions and user feedback
    """
    
    def __init__(self):
        self.training_data_path = "ai_training_data/"
        self.model_cache_path = "ai_models/"
        self.learning_patterns = {}
        self.confidence_thresholds = {
            'birth_certificate': 0.75,
            'school_id': 0.70,
            'certificate_of_enrollment': 0.80,
            'grade_report_card': 0.85
        }
        self._ensure_directories()
        self._load_learning_patterns()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.training_data_path, exist_ok=True)
        os.makedirs(self.model_cache_path, exist_ok=True)
    
    def record_admin_decision(self, document_id: int, document_type: str, 
                            ocr_results: Dict, admin_decision: str, 
                            admin_notes: str = None) -> None:
        """
        📝 Record admin decisions for training
        
        Args:
            document_id: ID of the document
            document_type: Type of document
            ocr_results: OCR analysis results
            admin_decision: 'approved' or 'rejected'
            admin_notes: Optional admin notes
        """
        training_record = {
            'timestamp': datetime.now().isoformat(),
            'document_id': document_id,
            'document_type': document_type,
            'ocr_results': ocr_results,
            'admin_decision': admin_decision,
            'admin_notes': admin_notes,
            'extracted_text_length': len(ocr_results.get('extracted_text', '')),
            'ocr_similarity': ocr_results.get('similarity_score', 0.0),
            'confidence_level': ocr_results.get('confidence_level', 'low')
        }
        
        # Save training record
        filename = f"{self.training_data_path}training_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{document_id}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(training_record, f, indent=2)
            
            logger.info(f"📚 Training data recorded: Doc {document_id} -> {admin_decision}")
            
            # Update learning patterns
            self._update_learning_patterns(training_record)
            
        except Exception as e:
            logger.error(f"Failed to save training data: {str(e)}")
    
    def _update_learning_patterns(self, record: Dict) -> None:
        """Update learned patterns from admin feedback"""
        doc_type = record['document_type']
        decision = record['admin_decision']
        
        if doc_type not in self.learning_patterns:
            self.learning_patterns[doc_type] = {
                'approved_patterns': [],
                'rejected_patterns': [],
                'optimal_thresholds': {},
                'success_rate': 0.0
            }
        
        pattern_data = {
            'ocr_similarity': record['ocr_results'].get('similarity_score', 0.0),
            'confidence_level': record['ocr_results'].get('confidence_level', 'low'),
            'text_length': record['extracted_text_length'],
            'timestamp': record['timestamp']
        }
        
        if decision == 'approved':
            self.learning_patterns[doc_type]['approved_patterns'].append(pattern_data)
        else:
            self.learning_patterns[doc_type]['rejected_patterns'].append(pattern_data)
        
        # Recalculate optimal thresholds
        self._recalculate_thresholds(doc_type)
        
        # Save updated patterns
        self._save_learning_patterns()
    
    def _recalculate_thresholds(self, doc_type: str) -> None:
        """Recalculate optimal confidence thresholds based on training data"""
        patterns = self.learning_patterns[doc_type]
        
        approved = patterns['approved_patterns']
        rejected = patterns['rejected_patterns']
        
        if len(approved) < 3 or len(rejected) < 3:
            return  # Need more data
        
        # Calculate optimal similarity threshold
        approved_similarities = [p['ocr_similarity'] for p in approved]
        rejected_similarities = [p['ocr_similarity'] for p in rejected]
        
        if approved_similarities and rejected_similarities:
            # Find threshold that maximizes accuracy
            min_approved = min(approved_similarities)
            max_rejected = max(rejected_similarities)
            
            # Optimal threshold is between these values
            optimal_threshold = (min_approved + max_rejected) / 2
            optimal_threshold = max(0.6, min(0.95, optimal_threshold))  # Clamp between 60-95%
            
            patterns['optimal_thresholds']['similarity'] = optimal_threshold
            
            # Update global threshold
            self.confidence_thresholds[doc_type] = optimal_threshold
            
            logger.info(f"📊 Updated {doc_type} threshold: {optimal_threshold:.2%}")
    
    def get_recommendation(self, document_type: str, ocr_results: Dict) -> Dict[str, Any]:
        """
        🎯 Get AI recommendation based on learned patterns
        
        Returns:
            recommendation: 'approve', 'reject', or 'review'
            confidence: confidence in recommendation
            reasoning: explanation of recommendation
        """
        similarity = ocr_results.get('similarity_score', 0.0)
        confidence_level = ocr_results.get('confidence_level', 'low')
        
        # Get learned threshold for this document type
        threshold = self.confidence_thresholds.get(document_type, 0.75)
        
        if document_type in self.learning_patterns:
            patterns = self.learning_patterns[document_type]
            learned_threshold = patterns['optimal_thresholds'].get('similarity', threshold)
            threshold = learned_threshold
        
        # Make recommendation
        if similarity >= threshold and confidence_level == 'high':
            recommendation = 'approve'
            conf = 0.9
            reasoning = f"High OCR similarity ({similarity:.1%}) exceeds learned threshold ({threshold:.1%})"
        elif similarity < 0.4 or confidence_level == 'low':
            recommendation = 'reject'
            conf = 0.8
            reasoning = f"Low OCR similarity ({similarity:.1%}) or poor quality"
        else:
            recommendation = 'review'
            conf = 0.6
            reasoning = f"Moderate similarity ({similarity:.1%}) requires human review"
        
        return {
            'recommendation': recommendation,
            'confidence': conf,
            'reasoning': reasoning,
            'learned_threshold': threshold,
            'training_data_count': len(self.learning_patterns.get(document_type, {}).get('approved_patterns', []))
        }
    
    def analyze_learning_progress(self) -> Dict[str, Any]:
        """Analyze learning progress and accuracy improvements"""
        progress = {
            'document_types': {},
            'overall_accuracy': 0.0,
            'training_samples': 0,
            'recommendations': []
        }
        
        total_correct = 0
        total_decisions = 0
        
        for doc_type, patterns in self.learning_patterns.items():
            approved_count = len(patterns['approved_patterns'])
            rejected_count = len(patterns['rejected_patterns'])
            total_samples = approved_count + rejected_count
            
            # Calculate accuracy based on threshold performance
            threshold = patterns['optimal_thresholds'].get('similarity', 0.75)
            
            correct_approvals = sum(1 for p in patterns['approved_patterns'] 
                                  if p['ocr_similarity'] >= threshold)
            correct_rejections = sum(1 for p in patterns['rejected_patterns'] 
                                   if p['ocr_similarity'] < threshold)
            
            accuracy = (correct_approvals + correct_rejections) / total_samples if total_samples > 0 else 0
            
            progress['document_types'][doc_type] = {
                'approved_samples': approved_count,
                'rejected_samples': rejected_count,
                'accuracy': accuracy,
                'learned_threshold': threshold,
                'confidence': 'high' if total_samples >= 10 else 'low'
            }
            
            total_correct += correct_approvals + correct_rejections
            total_decisions += total_samples
        
        progress['overall_accuracy'] = total_correct / total_decisions if total_decisions > 0 else 0
        progress['training_samples'] = total_decisions
        
        # Generate recommendations
        if total_decisions < 50:
            progress['recommendations'].append("Need more training data for reliable predictions")
        if progress['overall_accuracy'] < 0.8:
            progress['recommendations'].append("Consider reviewing threshold settings")
        if total_decisions >= 100:
            progress['recommendations'].append("Sufficient data for autonomous operation")
        
        return progress
    
    def export_training_report(self) -> str:
        """Generate comprehensive training report"""
        progress = self.analyze_learning_progress()
        
        report = [
            "🧠 AI LEARNING SYSTEM - TRAINING REPORT",
            "=" * 50,
            f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📊 Overall Accuracy: {progress['overall_accuracy']:.1%}",
            f"📚 Training Samples: {progress['training_samples']}",
            "",
            "📋 Document Type Performance:",
        ]
        
        for doc_type, stats in progress['document_types'].items():
            report.extend([
                f"  📄 {doc_type.replace('_', ' ').title()}:",
                f"    • Samples: {stats['approved_samples']} approved, {stats['rejected_samples']} rejected",
                f"    • Accuracy: {stats['accuracy']:.1%}",
                f"    • Threshold: {stats['learned_threshold']:.1%}",
                f"    • Confidence: {stats['confidence']}",
                ""
            ])
        
        if progress['recommendations']:
            report.extend([
                "💡 Recommendations:",
                *[f"  • {rec}" for rec in progress['recommendations']],
                ""
            ])
        
        report.extend([
            "🚀 Next Steps:",
            "  • Continue collecting admin feedback",
            "  • Monitor accuracy improvements",
            "  • Adjust thresholds as needed",
            "  • Consider expanding to new document types"
        ])
        
        return "\n".join(report)
    
    def _load_learning_patterns(self) -> None:
        """Load existing learning patterns from disk"""
        patterns_file = f"{self.model_cache_path}learning_patterns.pkl"
        
        try:
            if os.path.exists(patterns_file):
                with open(patterns_file, 'rb') as f:
                    self.learning_patterns = pickle.load(f)
                logger.info(f"📚 Loaded learning patterns for {len(self.learning_patterns)} document types")
            else:
                logger.info("🆕 Starting with fresh learning patterns")
                
        except Exception as e:
            logger.error(f"Failed to load learning patterns: {str(e)}")
            self.learning_patterns = {}
    
    def _save_learning_patterns(self) -> None:
        """Save learning patterns to disk"""
        patterns_file = f"{self.model_cache_path}learning_patterns.pkl"
        
        try:
            with open(patterns_file, 'wb') as f:
                pickle.dump(self.learning_patterns, f)
                
        except Exception as e:
            logger.error(f"Failed to save learning patterns: {str(e)}")
    
    def record_processing_data(self, document_type: str, verification_results: Dict) -> None:
        """Record processing data for continuous learning"""
        try:
            processing_record = {
                'timestamp': datetime.now().isoformat(),
                'document_type': document_type,
                'confidence_score': verification_results.get('confidence_score', 0.0),
                'processing_time': verification_results.get('processing_time', 0.0),
                'algorithms_used': verification_results.get('algorithms_used', []),
                'vision_ai_used': 'vision_ai_analysis' in verification_results.get('algorithms_used', []),
                'ocr_similarity': verification_results.get('ocr_similarity', 0.0),
                'was_approved': verification_results.get('is_valid_document', False)
            }
            
            # Save for analysis (optional - helps track system performance)
            filename = f"{self.training_data_path}processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(processing_record, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to record processing data: {str(e)}")

# Global instance
learning_system = DocumentLearningSystem()