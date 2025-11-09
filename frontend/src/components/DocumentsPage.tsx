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
          <div className="dp-header-text">
            <h1>📄 Submission of Requirements</h1>
            <p>Upload your required documents to proceed with your application</p>
          </div>
        </div>
      </div>

      {/* Upload Summary */}
      {documents.length > 0 && (
        <div className="dp-uploaded-documents">
          <h3>Your Uploaded Documents ({documents.length})</h3>
          <div className="dp-document-list">
            {documents.map((doc, index) => (
              <div key={doc.id} className="dp-document-item">
                <span className="dp-document-icon">
                  {getStatusIcon(doc.status)}
                </span>
                <div className="dp-document-info">
                  <span className="dp-document-name">{doc.document_type_display}</span>
                  <span className="dp-document-date">
                    {new Date(doc.submitted_at).toLocaleDateString()}
                  </span>
                </div>
                <span 
                  className="dp-status-badge"
                  style={{ backgroundColor: getStatusColor(doc.status) }}
                >
                  {doc.status_display}
                </span>
                {doc.ai_analysis_notes && (
                  <button 
                    className="dp-ai-details-button"
                    onClick={() => setSelectedDocForDetails(doc)}
                    title="View AI Analysis Details"
                  >
                    🤖 AI Details
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Upload Button */}
      <div className="dp-upload-section">
        <div className="dp-upload-card">
          <div className="dp-upload-icon">📁</div>
          <h2>Upload Documents</h2>
          <p>Click the button below to submit your required documents</p>
          <button 
            className="dp-main-upload-button"
            onClick={() => setShowDocumentForm(true)}
          >
            📤 Upload Documents
          </button>
        </div>
      </div>

      {/* Document Submission Form Modal */}
      {showDocumentForm && (
        <DocumentSubmissionForm
          onCancel={() => setShowDocumentForm(false)}
          onSubmissionSuccess={handleFormSuccess}
        />
      )}

      {/* AI Analysis Details Modal */}
      {selectedDocForDetails && (
        <div className="dp-ai-details-modal-overlay" onClick={() => setSelectedDocForDetails(null)}>
          <div className="dp-ai-details-modal" onClick={(e) => e.stopPropagation()}>
            <div className="dp-ai-modal-header">
              <h2>🤖 AI Document Analysis</h2>
              <button 
                className="dp-close-button"
                onClick={() => setSelectedDocForDetails(null)}
              >
                ✕
              </button>
            </div>
            
            <div className="dp-ai-modal-content">
              <div className="dp-ai-doc-info">
                <h3>{selectedDocForDetails.document_type_display}</h3>
                <div className="dp-ai-doc-meta">
                  <span>📅 Submitted: {new Date(selectedDocForDetails.submitted_at).toLocaleString()}</span>
                  {selectedDocForDetails.ai_auto_approved !== undefined && (
                    <span>🔄 {selectedDocForDetails.ai_auto_approved ? 'Auto-Approved by AI' : 'Auto-Rejected by AI'}</span>
                  )}
                  {selectedDocForDetails.ai_confidence_score !== undefined && (
                    <span>📊 Confidence: {(selectedDocForDetails.ai_confidence_score * 100).toFixed(1)}%</span>
                  )}
                </div>
              </div>

              {selectedDocForDetails.ai_analysis_notes && (
                <div className="dp-ai-analysis-details">
                  <pre className="dp-ai-notes-text">{selectedDocForDetails.ai_analysis_notes}</pre>
                </div>
              )}

              <div className="dp-ai-modal-footer">
                <button 
                  className="dp-close-ai-modal-button"
                  onClick={() => setSelectedDocForDetails(null)}
                >
                  ✕ Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;