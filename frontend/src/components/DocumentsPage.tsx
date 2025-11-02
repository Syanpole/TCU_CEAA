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
    </div>
  );
};

export default DocumentsPage;