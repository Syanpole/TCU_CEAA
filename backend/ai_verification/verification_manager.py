"""
Enhanced AI Verification Manager
Integrates advanced document type detection with the existing TCU-CEAA system
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from .base_verifier import document_type_detector


class DocumentVerificationManager:
    """
    Manages the complete document verification process with enhanced AI capabilities
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def verify_document_submission(self, document_submission) -> Dict[str, Any]:
        """
        Complete verification process for a document submission
        Integrates with the enhanced AI document type detection
        """
        verification_result = {
            'status': 'pending',
            'ai_verification_completed': False,
            'verification_confidence': 0.0,
            'verification_notes': [],
            'recommendation': 'manual_review',
            'auto_decision': False,
            'fraud_detected': False,
            'quality_acceptable': True,
            'type_match_verified': False
        }
        
        try:
            self.logger.info(f"Starting verification for document {document_submission.id}")
            
            # Step 1: Enhanced AI Document Type Verification
            ai_verification = document_type_detector.verify_document_type(
                document_submission, 
                document_submission.document_file
            )
            
            # Step 2: Process AI verification results
            processed_results = self._process_ai_verification_results(
                ai_verification, document_submission
            )
            verification_result.update(processed_results)
            
            # Step 3: Make final decision and update document status
            final_decision = self._make_final_verification_decision(
                verification_result, document_submission
            )
            verification_result.update(final_decision)
            
            # Step 4: Update document submission with verification results
            self._update_document_submission(document_submission, verification_result)
            
            self.logger.info(
                f"Verification completed for document {document_submission.id}. "
                f"Status: {verification_result['status']}, "
                f"Confidence: {verification_result['verification_confidence']:.1%}"
            )
            
        except Exception as e:
            self.logger.error(f"Verification error for document {document_submission.id}: {str(e)}")
            verification_result.update({
                'status': 'error',
                'verification_notes': [f"Verification system error: {str(e)}"],
                'recommendation': 'manual_review',
                'auto_decision': False
            })
            
            # Still update the document with error status
            self._update_document_submission_error(document_submission, verification_result)
        
        return verification_result

    def _process_ai_verification_results(self, ai_verification: Dict, document_submission) -> Dict[str, Any]:
        """Process the AI verification results into manageable format"""
        processed = {
            'ai_verification_completed': True,
            'verification_confidence': ai_verification.get('confidence_score', 0.0),
            'type_match_verified': ai_verification.get('document_type_match', False),
            'fraud_detected': ai_verification.get('is_likely_fraud', False),
            'quality_acceptable': ai_verification.get('is_acceptable_quality', True),
            'verification_notes': []
        }
        
        # Build comprehensive verification notes
        notes = []
        notes.append("🤖 Enhanced AI Document Verification Report")
        notes.append("=" * 50)
        notes.append(f"Document Type: {document_submission.get_document_type_display()}")
        notes.append(f"Verification Confidence: {processed['verification_confidence']:.1%}")
        notes.append("")
        
        # Document type matching results
        if processed['type_match_verified']:
            notes.append("✅ DOCUMENT TYPE VERIFICATION: PASSED")
            notes.append(f"   ✓ Document confirmed as {document_submission.get_document_type_display()}")
        else:
            notes.append("❌ DOCUMENT TYPE VERIFICATION: FAILED")
            notes.append(f"   ✗ Document does not match declared type: {document_submission.get_document_type_display()}")
        
        # Fraud detection results
        fraud_indicators = ai_verification.get('fraud_indicators', [])
        if processed['fraud_detected']:
            notes.append("\n🚨 FRAUD DETECTION: HIGH RISK")
            notes.append("   Potential fraud indicators detected:")
            for indicator in fraud_indicators[:3]:  # Show top 3 indicators
                notes.append(f"   • {indicator}")
        elif fraud_indicators:
            notes.append("\n⚠️ FRAUD DETECTION: LOW RISK")
            notes.append("   Minor concerns detected:")
            for indicator in fraud_indicators[:2]:  # Show top 2 indicators
                notes.append(f"   • {indicator}")
        else:
            notes.append("\n✅ FRAUD DETECTION: PASSED")
            notes.append("   No fraud indicators detected")
        
        # Quality assessment
        quality_issues = ai_verification.get('quality_issues', [])
        if not processed['quality_acceptable']:
            notes.append("\n📊 QUALITY ASSESSMENT: POOR")
            for issue in quality_issues[:3]:
                notes.append(f"   • {issue}")
        elif quality_issues:
            notes.append("\n📊 QUALITY ASSESSMENT: ACCEPTABLE")
            notes.append("   Minor quality concerns:")
            for issue in quality_issues[:2]:
                notes.append(f"   • {issue}")
        else:
            notes.append("\n📊 QUALITY ASSESSMENT: EXCELLENT")
            notes.append("   Document quality meets all standards")
        
        # Technical details
        extracted_features = ai_verification.get('extracted_features', {})
        if extracted_features.get('extracted_text'):
            text_length = len(extracted_features['extracted_text'])
            notes.append(f"\n🔍 TEXT EXTRACTION: {text_length} characters extracted")
            
            # Show text confidence if available
            text_confidence = extracted_features.get('text_confidence', 0)
            if text_confidence > 0:
                notes.append(f"   OCR Confidence: {text_confidence:.1f}%")
        
        # Keyword analysis
        keyword_analysis = ai_verification.get('keyword_analysis', {})
        if keyword_analysis:
            notes.append("\n🔤 KEYWORD ANALYSIS:")
            primary_score = keyword_analysis.get('primary_score', 0)
            notes.append(f"   Primary keywords match: {primary_score:.1%}")
            
            found_keywords = keyword_analysis.get('found_keywords', {})
            if found_keywords.get('primary'):
                notes.append(f"   Found keywords: {', '.join(found_keywords['primary'][:5])}")
        
        # Final AI recommendation
        recommendation = ai_verification.get('recommendation', 'manual_review')
        notes.append(f"\n🎯 AI RECOMMENDATION: {recommendation.upper()}")
        
        # Add verification timestamp
        notes.append(f"\nVerification completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        processed['verification_notes'] = notes
        processed['ai_detailed_results'] = ai_verification  # Store full results for debugging
        
        return processed

    def _make_final_verification_decision(self, verification_result: Dict, document_submission) -> Dict[str, Any]:
        """Make final decision based on all verification factors"""
        decision = {
            'status': 'pending',
            'recommendation': 'manual_review',
            'auto_decision': False,
            'decision_reasoning': []
        }
        
        confidence = verification_result['verification_confidence']
        type_match = verification_result['type_match_verified']
        fraud_detected = verification_result['fraud_detected']
        quality_acceptable = verification_result['quality_acceptable']
        
        reasoning = []
        
        # Critical failure conditions - Automatic rejection
        if fraud_detected:
            decision.update({
                'status': 'rejected',
                'recommendation': 'reject',
                'auto_decision': True
            })
            reasoning.append("🚨 AUTOMATIC REJECTION: Fraud indicators detected")
            reasoning.append("Document appears to be fraudulent or manipulated")
            
        elif not type_match and confidence < 0.3:
            decision.update({
                'status': 'rejected',
                'recommendation': 'reject',
                'auto_decision': True
            })
            reasoning.append("❌ AUTOMATIC REJECTION: Document type mismatch")
            reasoning.append(f"Document does not match declared type: {document_submission.get_document_type_display()}")
            
        elif not quality_acceptable and confidence < 0.4:
            decision.update({
                'status': 'rejected',
                'recommendation': 'reject',
                'auto_decision': True
            })
            reasoning.append("📊 AUTOMATIC REJECTION: Poor document quality")
            reasoning.append("Document quality insufficient for verification")
        
        # Automatic approval conditions
        elif type_match and confidence >= 0.8 and quality_acceptable and not fraud_detected:
            decision.update({
                'status': 'approved',
                'recommendation': 'auto_approve',
                'auto_decision': True
            })
            reasoning.append("✅ AUTOMATIC APPROVAL: High confidence verification")
            reasoning.append(f"All verification checks passed with {confidence:.1%} confidence")
            
        elif type_match and confidence >= 0.6 and quality_acceptable and not fraud_detected:
            decision.update({
                'status': 'approved',
                'recommendation': 'auto_approve',
                'auto_decision': True
            })
            reasoning.append("✅ AUTOMATIC APPROVAL: Good confidence verification")
            reasoning.append(f"Document verified with {confidence:.1%} confidence")
            
        # Enhanced auto-approval for borderline cases (autonomous processing)
        elif type_match and confidence >= 0.4 and not fraud_detected:
            decision.update({
                'status': 'approved',
                'recommendation': 'auto_approve_conditional',
                'auto_decision': True
            })
            reasoning.append("✅ CONDITIONAL APPROVAL: Acceptable verification")
            reasoning.append(f"Document approved with {confidence:.1%} confidence")
            reasoning.append("⚠️ Consider improving document quality for future submissions")
            
        # Manual review needed
        else:
            decision.update({
                'status': 'pending',
                'recommendation': 'manual_review',
                'auto_decision': False
            })
            reasoning.append("👤 MANUAL REVIEW REQUIRED")
            
            if confidence < 0.5:
                reasoning.append(f"Low verification confidence: {confidence:.1%}")
            if not type_match:
                reasoning.append("Document type could not be confirmed")
            if not quality_acceptable:
                reasoning.append("Document quality concerns")
        
        decision['decision_reasoning'] = reasoning
        return decision

    def _update_document_submission(self, document_submission, verification_result: Dict):
        """Update the document submission with verification results"""
        try:
            # Update AI analysis fields
            document_submission.ai_analysis_completed = verification_result['ai_verification_completed']
            document_submission.ai_confidence_score = verification_result['verification_confidence']
            document_submission.ai_document_type_match = verification_result['type_match_verified']
            
            # Store detailed verification results
            document_submission.ai_key_information = verification_result.get('ai_detailed_results', {})
            
            # Build comprehensive AI analysis notes
            all_notes = []
            all_notes.extend(verification_result['verification_notes'])
            all_notes.append("")
            all_notes.extend(verification_result['decision_reasoning'])
            
            document_submission.ai_analysis_notes = "\n".join(all_notes)
            
            # Set recommendations
            ai_detailed = verification_result.get('ai_detailed_results', {})
            document_submission.ai_recommendations = ai_detailed.get('recommendations', [])
            
            # Set status based on decision
            if verification_result['auto_decision']:
                document_submission.status = verification_result['status']
                document_submission.ai_auto_approved = (verification_result['status'] == 'approved')
                
                if verification_result['status'] == 'approved':
                    document_submission.reviewed_at = timezone.now()
                    document_submission.admin_notes = (
                        f"✅ Auto-approved by Enhanced AI Verification System\n"
                        f"Confidence Score: {verification_result['verification_confidence']:.1%}\n"
                        f"Verification completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"{document_submission.admin_notes or ''}"
                    )
                elif verification_result['status'] == 'rejected':
                    document_submission.reviewed_at = timezone.now()
                    document_submission.admin_notes = (
                        f"❌ Auto-rejected by Enhanced AI Verification System\n"
                        f"Rejection reason: {'; '.join(verification_result['decision_reasoning'])}\n"
                        f"Verification completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"Please submit a correct {document_submission.get_document_type_display()} document.\n"
                        f"{document_submission.admin_notes or ''}"
                    )
            else:
                # Keep as pending for manual review
                document_submission.status = 'pending'
                document_submission.admin_notes = (
                    f"⏳ Pending Manual Review - AI Analysis Complete\n"
                    f"AI Confidence: {verification_result['verification_confidence']:.1%}\n"
                    f"Manual review recommended due to: {'; '.join(verification_result['decision_reasoning'])}\n\n"
                    f"{document_submission.admin_notes or ''}"
                )
            
            # Save the updated document submission
            document_submission.save()
            
            self.logger.info(
                f"Document {document_submission.id} updated. "
                f"Status: {document_submission.status}, "
                f"Auto-decided: {verification_result['auto_decision']}"
            )
            
        except Exception as e:
            self.logger.error(f"Error updating document {document_submission.id}: {str(e)}")
            raise

    def _update_document_submission_error(self, document_submission, verification_result: Dict):
        """Update document submission when verification encounters an error"""
        try:
            document_submission.ai_analysis_completed = False
            document_submission.ai_confidence_score = 0.0
            document_submission.ai_analysis_notes = "\n".join(verification_result['verification_notes'])
            document_submission.status = 'pending'
            document_submission.admin_notes = (
                f"⚠️ Verification System Error - Manual Review Required\n"
                f"Error: {verification_result['verification_notes'][0] if verification_result['verification_notes'] else 'Unknown error'}\n"
                f"Please have an administrator review this document manually.\n\n"
                f"{document_submission.admin_notes or ''}"
            )
            
            document_submission.save()
            
        except Exception as e:
            self.logger.error(f"Error updating document {document_submission.id} with error status: {str(e)}")

    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get verification system statistics"""
        try:
            from myapp.models import DocumentSubmission
            
            # Get recent documents (last 30 days)
            from datetime import timedelta
            recent_date = timezone.now() - timedelta(days=30)
            
            recent_docs = DocumentSubmission.objects.filter(submitted_at__gte=recent_date)
            
            stats = {
                'total_documents': recent_docs.count(),
                'ai_processed': recent_docs.filter(ai_analysis_completed=True).count(),
                'auto_approved': recent_docs.filter(ai_auto_approved=True).count(),
                'auto_rejected': recent_docs.filter(
                    ai_analysis_completed=True, 
                    status='rejected', 
                    reviewed_at__isnull=False
                ).count(),
                'manual_review': recent_docs.filter(
                    ai_analysis_completed=True, 
                    status='pending'
                ).count(),
                'average_confidence': 0.0
            }
            
            # Calculate average confidence
            confidence_scores = recent_docs.filter(
                ai_analysis_completed=True,
                ai_confidence_score__gt=0
            ).values_list('ai_confidence_score', flat=True)
            
            if confidence_scores:
                stats['average_confidence'] = sum(confidence_scores) / len(confidence_scores)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting verification statistics: {str(e)}")
            return {
                'total_documents': 0,
                'ai_processed': 0,
                'auto_approved': 0,
                'auto_rejected': 0,
                'manual_review': 0,
                'average_confidence': 0.0,
                'error': str(e)
            }


# Global instance
verification_manager = DocumentVerificationManager()