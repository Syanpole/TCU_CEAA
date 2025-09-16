import React from 'react';
import './AIAnalysisDisplay.css';

interface AIAnalysisDisplayProps {
  analysis: {
    ai_analysis_completed?: boolean;
    ai_confidence_score?: number;
    ai_document_type_match?: boolean;
    ai_recommendations?: string[];
    ai_analysis_notes?: string;
    ai_auto_approved?: boolean;
    ai_evaluation_completed?: boolean;
    ai_extracted_grades?: any;
    ai_grade_validation?: any;
    qualifies_for_basic_allowance?: boolean;
    qualifies_for_merit_incentive?: boolean;
  };
  type: 'document' | 'grade';
}

const AIAnalysisDisplay: React.FC<AIAnalysisDisplayProps> = ({ analysis, type }) => {
  if (!analysis.ai_analysis_completed && !analysis.ai_evaluation_completed) {
    return (
      <div className="ai-analysis-display pending">
        <div className="ai-status-header">
          <span className="ai-icon">🤖</span>
          <h4>AI Analysis Pending</h4>
          <div className="loading-spinner"></div>
        </div>
        <p>Your {type} is being analyzed by our AI system...</p>
      </div>
    );
  }

  const confidenceScore = analysis.ai_confidence_score || 0;
  const confidenceLevel = confidenceScore >= 0.8 ? 'high' : confidenceScore >= 0.6 ? 'medium' : 'low';

  return (
    <div className={`ai-analysis-display completed ${confidenceLevel}`}>
      <div className="ai-status-header">
        <span className="ai-icon">🤖</span>
        <h4>AI Analysis Complete</h4>
        <div className={`confidence-badge ${confidenceLevel}`}>
          {(confidenceScore * 100).toFixed(0)}% Confidence
        </div>
      </div>

      {/* Document-specific analysis */}
      {type === 'document' && (
        <div className="document-analysis">
          <div className="analysis-row">
            <span className="label">Document Type Match:</span>
            <span className={`status ${analysis.ai_document_type_match ? 'match' : 'no-match'}`}>
              {analysis.ai_document_type_match ? '✅ Verified' : '⚠️ Needs Review'}
            </span>
          </div>
          
          {analysis.ai_auto_approved && (
            <div className="analysis-row">
              <span className="label">Auto-Approval:</span>
              <span className="status approved">✅ Automatically Approved</span>
            </div>
          )}
        </div>
      )}

      {/* Grade-specific analysis */}
      {type === 'grade' && (
        <div className="grade-analysis">
          <div className="allowance-status">
            <div className="allowance-item">
              <span className="allowance-label">Basic Allowance (₱5,000):</span>
              <span className={`allowance-status ${analysis.qualifies_for_basic_allowance ? 'qualified' : 'not-qualified'}`}>
                {analysis.qualifies_for_basic_allowance ? '✅ Qualified' : '❌ Not Qualified'}
              </span>
            </div>
            <div className="allowance-item">
              <span className="allowance-label">Merit Incentive (₱5,000):</span>
              <span className={`allowance-status ${analysis.qualifies_for_merit_incentive ? 'qualified' : 'not-qualified'}`}>
                {analysis.qualifies_for_merit_incentive ? '✅ Qualified' : '❌ Not Qualified'}
              </span>
            </div>
          </div>

          {analysis.ai_extracted_grades && Object.keys(analysis.ai_extracted_grades).length > 0 && (
            <div className="extracted-info">
              <h5>📊 AI Extracted Information:</h5>
              <div className="extracted-details">
                {analysis.ai_extracted_grades.gwa_found && analysis.ai_extracted_grades.gwa_found.length > 0 && (
                  <div className="extracted-item">
                    <span>GWA Found: {analysis.ai_extracted_grades.gwa_found.join(', ')}%</span>
                  </div>
                )}
                {analysis.ai_extracted_grades.swa_found && analysis.ai_extracted_grades.swa_found.length > 0 && (
                  <div className="extracted-item">
                    <span>SWA Found: {analysis.ai_extracted_grades.swa_found.join(', ')}%</span>
                  </div>
                )}
                {analysis.ai_extracted_grades.subjects_found && analysis.ai_extracted_grades.subjects_found.length > 0 && (
                  <div className="extracted-item">
                    <span>Subjects Detected: {analysis.ai_extracted_grades.subjects_found.length}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* AI Recommendations */}
      {analysis.ai_recommendations && analysis.ai_recommendations.length > 0 && (
        <div className="ai-recommendations">
          <h5>💡 AI Recommendations:</h5>
          <ul>
            {analysis.ai_recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Analysis Notes */}
      {analysis.ai_analysis_notes && (
        <div className="analysis-notes">
          <details>
            <summary>📋 Detailed Analysis Notes</summary>
            <pre className="notes-content">{analysis.ai_analysis_notes}</pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default AIAnalysisDisplay;
