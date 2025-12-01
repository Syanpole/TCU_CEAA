import React, { useState } from 'react';
import './DocumentVerificationCard.css';

interface DocumentVerificationCardProps {
  id: number;
  documentType: string;
  documentTypeDisplay: string;
  status: 'approved' | 'rejected' | 'pending';
  submittedAt: string;
  aiConfidenceScore?: number;
  aiAnalysisNotes?: string;
  aiAutoApproved?: boolean;
  onDelete?: (id: number) => void;
  onViewDetails?: () => void;
}

const DocumentVerificationCard: React.FC<DocumentVerificationCardProps> = ({
  id,
  documentType,
  documentTypeDisplay,
  status,
  submittedAt,
  aiConfidenceScore,
  aiAnalysisNotes,
  aiAutoApproved,
  onDelete,
  onViewDetails
}) => {
  const [isAccordionOpen, setIsAccordionOpen] = useState(false);

  // Get status icon
  const getStatusIcon = () => {
    switch (status) {
      case 'approved':
        return (
          <div className="dvc-status-icon approved">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" fill="#10B981"/>
              <path d="M8 12L11 15L16 9" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        );
      case 'rejected':
        return (
          <div className="dvc-status-icon rejected">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" fill="#EF4444"/>
              <path d="M9 9L15 15M15 9L9 15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
        );
      case 'pending':
      default:
        return (
          <div className="dvc-status-icon pending">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" fill="#F59E0B"/>
              <path d="M12 7V12L15 15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
        );
    }
  };

  // Get status text
  const getStatusText = () => {
    switch (status) {
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      case 'pending':
        return 'Pending';
      default:
        return 'Unknown';
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: '2-digit', 
      day: '2-digit', 
      year: 'numeric' 
    });
  };

  // Parse AI analysis for accordion
  const parseAIAnalysis = () => {
    if (!aiAnalysisNotes) return null;

    // Try to extract key information
    const lines = aiAnalysisNotes.split('\n').filter(line => line.trim());
    
    return {
      summary: lines[0] || 'AI analysis completed',
      details: lines.slice(1).join('\n') || 'No additional details available'
    };
  };

  const aiAnalysis = parseAIAnalysis();

  return (
    <div className={`dvc-card dvc-status-${status}`}>
      {/* Delete Button */}
      {onDelete && (
        <button 
          className="dvc-delete-btn"
          onClick={() => onDelete(id)}
          aria-label="Delete document"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
      )}

      {/* Status Icon at Top */}
      <div className="dvc-icon-wrapper">
        {getStatusIcon()}
      </div>

      {/* Document Title */}
      <h3 className="dvc-title">{documentTypeDisplay}</h3>

      {/* Information List */}
      <div className="dvc-info-list">
        {/* Date Submitted */}
        <div className="dvc-info-row">
          <span className="dvc-info-icon">📅</span>
          <span className="dvc-info-value">{formatDate(submittedAt)}</span>
        </div>

        {/* Status */}
        <div className="dvc-info-row">
          <span className="dvc-info-icon">ℹ️</span>
          <span className={`dvc-info-value dvc-status-text-${status}`}>
            Status: <strong>{getStatusText()}</strong>
          </span>
        </div>

        {/* AI Confidence */}
        {aiConfidenceScore !== undefined && aiConfidenceScore > 0 && (
          <div className="dvc-info-row">
            <span className="dvc-info-icon">🤖</span>
            <span className="dvc-info-value">
              AI Confidence: <strong>{(aiConfidenceScore * 100).toFixed(1)}%</strong>
            </span>
          </div>
        )}
      </div>

      {/* AI Verified Badge */}
      {aiAutoApproved && (
        <div className="dvc-badge-wrapper">
          <div className="dvc-ai-badge">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M3 6L5 8L9 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            AI Verified
          </div>
        </div>
      )}

      {/* AI Analysis Accordion */}
      {aiAnalysisNotes && aiAnalysis && (
        <div className="dvc-accordion">
          <button 
            className={`dvc-accordion-trigger ${isAccordionOpen ? 'open' : ''}`}
            onClick={() => setIsAccordionOpen(!isAccordionOpen)}
          >
            <span>AI Analysis</span>
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 16 16" 
              fill="none"
              className={`dvc-accordion-icon ${isAccordionOpen ? 'rotated' : ''}`}
            >
              <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          
          {isAccordionOpen && (
            <div className="dvc-accordion-content">
              <p className="dvc-analysis-summary">{aiAnalysis.summary}</p>
              {aiAnalysis.details && (
                <div className="dvc-analysis-details">
                  {aiAnalysis.details}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* View Details Button */}
      <button 
        className="dvc-details-btn"
        onClick={onViewDetails}
      >
        View Details
      </button>
    </div>
  );
};

export default DocumentVerificationCard;
