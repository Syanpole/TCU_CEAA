import React, { useState } from 'react';
import DocumentSubmissionForm from './DocumentSubmissionForm';
import { CheckIcon } from './Icons';
import './DocumentsPage.css';

interface DocumentSubmission {
  id: number;
  document_type: string;
  document_type_display: string;
  status: string;
  status_display: string;
  submitted_at: string;
  ai_analysis_notes?: string;
  ai_confidence_score?: number;
  ai_auto_approved?: boolean;
}

interface DocumentsPageProps {
  documents: DocumentSubmission[];
  darkMode: boolean;
  onDocumentSubmissionSuccess: () => void;
}

const DocumentsPage: React.FC<DocumentsPageProps> = ({ 
  documents, 
  darkMode, 
  onDocumentSubmissionSuccess 
}) => {
  const [showDocumentForm, setShowDocumentForm] = useState(false);
  const [selectedDocForDetails, setSelectedDocForDetails] = useState<DocumentSubmission | null>(null);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckIcon size={16} className="status-approved" />;
      case 'pending':
        return '⏳';
      case 'rejected':
        return '❌';
      default:
        return <CheckIcon size={16} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return '#10b981';
      case 'pending':
        return '#f59e0b';
      case 'rejected':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const handleFormSuccess = () => {
    setShowDocumentForm(false);
    onDocumentSubmissionSuccess();
  };

  return (
    <div className={`dp-container ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      <div className="dp-header">
        <div className="dp-header-content">
          <h1>📄 My Documents</h1>
          <p>View and manage your submitted documents</p>
        </div>
        <button 
          className="dp-upload-button"
          onClick={() => setShowDocumentForm(true)}
        >
          <span className="upload-icon">+</span>
          Upload Document
        </button>
      </div>

      {/* Documents Grid - Horizontal Cards */}
      {documents.length > 0 ? (
        <div className="dp-documents-grid">
          {documents.map((doc) => (
            <div key={doc.id} className={`dp-document-card ${doc.status}`}>
              {/* Card Header */}
              <div className="dp-card-header">
                <div className="dp-doc-icon">
                  {getStatusIcon(doc.status)}
                </div>
                <div className="dp-card-actions">
                  <button 
                    className="dp-delete-btn"
                    onClick={() => {/* Add delete functionality */}}
                    title="Delete document"
                  >
                    ×
                  </button>
                </div>
              </div>

              {/* Document Name */}
              <div className="dp-doc-name">
                {doc.document_type_display}
              </div>

              {/* Document Meta Info */}
              <div className="dp-doc-meta">
                <div className="dp-meta-item">
                  <span className="dp-meta-icon">📅</span>
                  <span className="dp-meta-text">
                    {new Date(doc.submitted_at).toLocaleDateString('en-US', { 
                      month: 'numeric', 
                      day: 'numeric', 
                      year: 'numeric' 
                    })}
                  </span>
                </div>
              </div>

              {/* Status Badge */}
              <div className="dp-status-section">
                <span 
                  className={`dp-status-badge status-${doc.status}`}
                >
                  {doc.status === 'pending' ? 'Processing' : 
                   doc.status === 'approved' ? 'Approved' : 
                   doc.status === 'rejected' ? 'Rejected' : doc.status_display}
                </span>
              </div>

              {/* AI Confidence */}
              {doc.ai_confidence_score !== undefined && doc.ai_confidence_score > 0 && (
                <div className="dp-ai-section">
                  <div className="dp-ai-label">
                    <span>
                      <span className="dp-ai-icon">🤖</span>
                      AI Confidence
                    </span>
                    <span className="dp-confidence-text">
                      {(doc.ai_confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="dp-confidence-bar">
                    <div 
                      className="dp-confidence-fill"
                      style={{ 
                        width: `${doc.ai_confidence_score * 100}%`,
                        backgroundColor: doc.ai_confidence_score >= 0.8 ? '#10b981' : doc.ai_confidence_score >= 0.6 ? '#f59e0b' : '#ef4444'
                      }}
                    ></div>
                  </div>
                </div>
              )}

              {/* View Details Button */}
              {doc.ai_analysis_notes && (
                <button 
                  className="dp-view-details-btn"
                  onClick={() => setSelectedDocForDetails(doc)}
                >
                  <span className="details-icon">👁️</span>
                  View Details
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="dp-empty-state">
          <h3>No Documents Yet</h3>
          <p>Upload your first document to get started</p>
          <button 
            className="dp-upload-button-large"
            onClick={() => setShowDocumentForm(true)}
          >
            <span className="upload-icon">+</span>
            Upload Your First Document
          </button>
        </div>
      )}

      {/* Document Submission Form Modal */}
      {showDocumentForm && (
        <DocumentSubmissionForm
          onCancel={() => setShowDocumentForm(false)}
          onSubmissionSuccess={handleFormSuccess}
        />
      )}

      {/* Modern AI Analysis Details Modal */}
      {selectedDocForDetails && (
        <div className="dp-modal-overlay" onClick={() => setSelectedDocForDetails(null)}>
          <div className="dp-modal-modern" onClick={(e) => e.stopPropagation()}>
            {/* Close Button */}
            <button 
              className="dp-modal-close-btn"
              onClick={() => setSelectedDocForDetails(null)}
              aria-label="Close modal"
            >
              ×
            </button>

            {/* Modal Content */}
            <div className="dp-modal-content">
              {/* Header Section */}
              <div className="dp-modal-header-section">
                <div className="dp-modal-icon-wrapper">
                  <span className="dp-modal-emoji">🤖</span>
                </div>
                <h2 className="dp-modal-heading">AI Analysis Report</h2>
                <p className="dp-modal-subheading">{selectedDocForDetails.document_type_display}</p>
              </div>

              {/* Status Badge */}
              <div className="dp-status-badge-container">
                <span className={`dp-status-badge-modern status-${selectedDocForDetails.status}`}>
                  {selectedDocForDetails.status === 'approved' && '✅ '}
                  {selectedDocForDetails.status === 'rejected' && '❌ '}
                  {selectedDocForDetails.status === 'pending' && '⏳ '}
                  {selectedDocForDetails.status_display}
                </span>
              </div>

              {/* Main Info Grid */}
              <div className="dp-modal-info-grid">
                <div className="dp-modal-info-box">
                  <div className="dp-info-box-label">Submitted</div>
                  <div className="dp-info-box-value">
                    {new Date(selectedDocForDetails.submitted_at).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric', 
                      year: 'numeric' 
                    })}
                  </div>
                </div>

                {selectedDocForDetails.ai_confidence_score !== undefined && (
                  <div className="dp-modal-info-box">
                    <div className="dp-info-box-label">AI Confidence</div>
                    <div className="dp-info-box-value dp-confidence-value">
                      {(selectedDocForDetails.ai_confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
              </div>

              {/* Confidence Progress Bar */}
              {selectedDocForDetails.ai_confidence_score !== undefined && (
                <div className="dp-confidence-container">
                  <div className="dp-progress-bar-modern">
                    <div 
                      className="dp-progress-fill-modern"
                      style={{ 
                        width: `${selectedDocForDetails.ai_confidence_score * 100}%`,
                        backgroundColor: selectedDocForDetails.ai_confidence_score >= 0.8 ? '#10b981' : 
                                       selectedDocForDetails.ai_confidence_score >= 0.6 ? '#f59e0b' : '#ef4444'
                      }}
                    />
                  </div>
                  <div className="dp-confidence-status">
                    {selectedDocForDetails.ai_confidence_score >= 0.8 ? 'High Confidence' : 
                     selectedDocForDetails.ai_confidence_score >= 0.6 ? 'Medium Confidence' : 'Low Confidence'}
                  </div>
                </div>
              )}

              {/* Analysis Details */}
              {selectedDocForDetails.ai_analysis_notes && (
                <div className="dp-analysis-section">
                  <h3 className="dp-section-title">Analysis Details</h3>
                  <div className="dp-analysis-content">
                    {selectedDocForDetails.ai_analysis_notes}
                  </div>
                </div>
              )}

              {/* Auto-Approval Notice */}
              {selectedDocForDetails.ai_auto_approved && (
                <div className="dp-success-notice">
                  <span className="dp-notice-icon">✓</span>
                  <div className="dp-notice-text">
                    <strong>Auto-Approved</strong>
                    <span>Automatically verified by AI</span>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <button 
                className="dp-modal-action-btn"
                onClick={() => setSelectedDocForDetails(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;