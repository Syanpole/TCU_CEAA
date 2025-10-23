/**
 * 🤖 AI Document Processor
 * Integrates AI verification into document submission workflow
 * Provides real-time AI analysis during document upload
 */

import React, { useState, useEffect } from 'react';
import { aiService, AIStatus, AIAnalysisResult } from '../services/aiService';
import AIVerificationDashboard from './AIVerificationDashboard';
import './AIDocumentProcessor.css';

interface AIDocumentProcessorProps {
  documentId?: number;
  onAIAnalysisComplete?: (results: AIAnalysisResult, autoApproved: boolean) => void;
  showFullDashboard?: boolean;
  autoStart?: boolean;
}

const AIDocumentProcessor: React.FC<AIDocumentProcessorProps> = ({
  documentId,
  onAIAnalysisComplete,
  showFullDashboard = false,
  autoStart = false
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [processingError, setProcessingError] = useState<string>('');
  const [processingStep, setProcessingStep] = useState<string>('');
  
  // Algorithm processing steps
  const processingSteps = [
    '🤖 Initializing AI verification system...',
    '📄 Document Validator - OCR analysis with Pytesseract...',
    '🔍 Cross-Document Matcher - Fuzzy string matching...',
    '📊 Grade Verifier - GWA calculation & pattern detection...',
    '👤 Face Verifier - OpenCV face detection...',
    '🛡️ Fraud Detector - Metadata & tampering analysis...',
    '⚙️ AI Verification Manager - Weighted scoring...',
    '✅ AI analysis complete!'
  ];

  useEffect(() => {
    if (autoStart && documentId && !aiStatus?.ai_completed) {
      handleStartAIProcessing();
    }
  }, [documentId, autoStart, aiStatus?.ai_completed]);

  const handleStartAIProcessing = async () => {
    if (!documentId || isProcessing) return;

    try {
      setIsProcessing(true);
      setProcessingError('');
      
      // Simulate step-by-step processing
      for (let i = 0; i < processingSteps.length - 1; i++) {
        setProcessingStep(processingSteps[i]);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Run actual AI analysis
      const result = await aiService.analyzeDocument(documentId);
      
      setProcessingStep(processingSteps[processingSteps.length - 1]);
      
      // Get final status
      const finalStatus = await aiService.getAnalysisStatus(documentId);
      setAiStatus(finalStatus);

      // Notify parent component
      if (onAIAnalysisComplete) {
        onAIAnalysisComplete(result.results, result.auto_approved);
      }

    } catch (error: any) {
      setProcessingError(`AI processing failed: ${error.message}`);
      setProcessingStep('❌ AI processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRetryProcessing = () => {
    setProcessingError('');
    setProcessingStep('');
    handleStartAIProcessing();
  };

  if (!documentId) {
    return (
      <div className="ai-processor-placeholder">
        <div className="ai-processor-icon">🤖</div>
        <h3>AI Document Verification Ready</h3>
        <p>Upload a document to enable AI-powered verification with our 6-algorithm system.</p>
        <div className="ai-algorithms-list">
          <div className="ai-algorithm-item">📄 Document Validator (OCR)</div>
          <div className="ai-algorithm-item">🔍 Cross-Document Matcher</div>
          <div className="ai-algorithm-item">📊 Grade Verifier</div>
          <div className="ai-algorithm-item">👤 Face Verifier</div>
          <div className="ai-algorithm-item">🛡️ Fraud Detector</div>
          <div className="ai-algorithm-item">⚙️ AI Verification Manager</div>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-document-processor">
      <div className="ai-processor-header">
        <h3>🤖 AI Document Verification</h3>
        <div className="ai-processor-controls">
          {!isProcessing && !aiStatus?.ai_completed && (
            <button 
              className="ai-btn primary"
              onClick={handleStartAIProcessing}
              disabled={isProcessing}
            >
              ⚡ Start AI Analysis
            </button>
          )}
          {processingError && (
            <button 
              className="ai-btn retry"
              onClick={handleRetryProcessing}
            >
              🔄 Retry
            </button>
          )}
        </div>
      </div>

      {/* Processing Status */}
      {(isProcessing || processingStep) && (
        <div className="ai-processing-status">
          <div className="ai-processing-header">
            <div className={`ai-processing-icon ${isProcessing ? 'spinning' : ''}`}>
              {isProcessing ? '⚙️' : processingError ? '❌' : '✅'}
            </div>
            <div className="ai-processing-text">
              <div className="ai-current-step">{processingStep}</div>
              {isProcessing && (
                <div className="ai-processing-bar">
                  <div className="ai-processing-fill"></div>
                </div>
              )}
            </div>
          </div>
          
          {processingError && (
            <div className="ai-error-message">
              <strong>Error:</strong> {processingError}
            </div>
          )}
        </div>
      )}

      {/* AI Analysis Results */}
      {aiStatus?.ai_completed && (
        <div className="ai-results-summary">
          <div className="ai-results-header">
            <div className="ai-results-icon">
              {aiStatus.auto_approved ? '✅' : aiStatus.confidence_score > 0.6 ? '⚠️' : '❌'}
            </div>
            <div className="ai-results-content">
              <h4>AI Analysis Complete</h4>
              <div className="ai-results-stats">
                <div className="ai-stat-item">
                  <span className="ai-stat-label">Confidence:</span>
                  <span className={`ai-stat-value ${getConfidenceClass(aiStatus.confidence_score)}`}>
                    {(aiStatus.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="ai-stat-item">
                  <span className="ai-stat-label">Status:</span>
                  <span className={`ai-stat-value ${aiStatus.auto_approved ? 'approved' : 'pending'}`}>
                    {aiStatus.auto_approved ? 'Auto-Approved' : 'Manual Review Required'}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {aiStatus.analysis_notes && (
            <div className="ai-analysis-notes">
              <strong>📝 Analysis Notes:</strong> {aiStatus.analysis_notes}
            </div>
          )}
          
          {aiStatus.recommendations && aiStatus.recommendations.length > 0 && (
            <div className="ai-recommendations">
              <strong>🎯 Recommendations:</strong>
              <ul>
                {aiStatus.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Full Dashboard */}
      {showFullDashboard && (
        <div className="ai-full-dashboard">
          <AIVerificationDashboard 
            documentId={documentId}
            showFullDashboard={true}
          />
        </div>
      )}
    </div>
  );

  function getConfidenceClass(confidence: number): string {
    if (confidence >= 0.85) return 'high';
    if (confidence >= 0.65) return 'medium';
    if (confidence >= 0.35) return 'low';
    return 'critical';
  }
};

export default AIDocumentProcessor;