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
    <div className={`documents-page ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      <div className="page-header">
        <h1>Document Submission</h1>
        <p>Upload your required documents to proceed with your application</p>
      </div>

      {/* Upload Summary */}
      {documents.length > 0 && (
        <div className="uploaded-documents">
          <h3>Your Uploaded Documents ({documents.length})</h3>
          <div className="document-list">
            {documents.map((doc, index) => (
              <div key={doc.id} className="document-item">
                <span className="document-icon">
                  {getStatusIcon(doc.status)}
                </span>
                <div className="document-info">
                  <span className="document-name">{doc.document_type_display}</span>
                  <span className="document-date">
                    {new Date(doc.submitted_at).toLocaleDateString()}
                  </span>
                </div>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(doc.status) }}
                >
                  {doc.status_display}
                </span>
                {doc.ai_analysis_notes && (
                  <button 
                    className="ai-details-button"
                    onClick={() => setSelectedDocForDetails(doc)}
                    title="View AI Analysis Details"
                  >
                    AI Details
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Upload Button */}
      <div className="upload-section">
        <div className="upload-card">
          <div className="upload-icon">📁</div>
          <h2>Upload Documents</h2>
          <p>Click the button below to submit your required documents</p>
          <button 
            className="main-upload-button"
            onClick={() => setShowDocumentForm(true)}
          >
            Upload Documents
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
        <div className="ai-details-modal-overlay" onClick={() => setSelectedDocForDetails(null)}>
          <div className="ai-details-modal" onClick={(e) => e.stopPropagation()}>
            <div className="ai-modal-header">
              <h2>🤖 AI Document Analysis</h2>
              <button 
                className="close-button"
                onClick={() => setSelectedDocForDetails(null)}
              >
                ✕
              </button>
            </div>
            
            <div className="ai-modal-content">
              <div className="ai-doc-info">
                <h3>{selectedDocForDetails.document_type_display}</h3>
                <div className="ai-doc-meta">
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
                <div className="ai-analysis-details">
                  <pre className="ai-notes-text">{selectedDocForDetails.ai_analysis_notes}</pre>
                </div>
              )}

              <div className="ai-modal-footer">
                <button 
                  className="close-ai-modal-button"
                  onClick={() => setSelectedDocForDetails(null)}
                >
                  Close
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