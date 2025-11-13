import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import './DocumentsManagement.css';

interface Document {
  id: number;
  student_name: string;
  student_id: string;
  document_type: string;
  document_type_display: string;
  status: string;
  status_display: string;
  submitted_at: string;
  document_file?: string;
  ai_confidence_score?: number;
  ai_auto_approved?: boolean;
  ai_analysis_notes?: string;
}

interface AIDetails {
  document_id: number;
  student: {
    name: string;
    student_id: string;
    email: string;
  };
  document_type: string;
  document_type_display: string;
  status: string;
  submitted_at: string;
  ai_analysis: {
    completed: boolean;
    confidence_score: number;
    document_type_match: boolean;
    auto_approved: boolean;
    analysis_notes: string;
    algorithms_results: any;
    overall_analysis: any;
    extracted_text: string;
    recommendations: any[];
  };
  review_info: {
    reviewed_at: string | null;
    reviewed_by: string | null;
    admin_notes: string;
  };
}

interface DocumentsManagementProps {
  onViewChange?: (view: string) => void;
}

const DocumentsManagement: React.FC<DocumentsManagementProps> = ({ onViewChange }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [actionLoading, setActionLoading] = useState<{ [key: string]: boolean }>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [aiDetails, setAiDetails] = useState<AIDetails | null>(null);
  const [loadingAiDetails, setLoadingAiDetails] = useState(false);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get<Document[]>('/documents/');
        setDocuments(response.data);
      } catch (err) {
        console.error('Error fetching documents:', err);
        setError('Failed to load documents. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  // Function to refresh documents data
  const refreshDocuments = async () => {
    try {
      const response = await apiClient.get<Document[]>('/documents/');
      setDocuments(response.data);
    } catch (error) {
      console.error('Error refreshing documents:', error);
    }
  };

  // Handle document actions (approve, reject, delete)
  const handleDocumentAction = async (documentId: number, action: string, adminNotes?: string) => {
    const actionKey = `${action}_${documentId}`;
    
    try {
      setActionLoading(prev => ({ ...prev, [actionKey]: true }));
      
      if (action === 'delete') {
        if (!window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
          return;
        }
        await apiClient.delete(`/documents/${documentId}/`);
        setSuccessMessage('Document deleted successfully!');
      } else {
        // For approve/reject actions
        const payload = { 
          status: action === 'approve' ? 'approved' : 'rejected',
          admin_notes: adminNotes || `Document ${action}d by admin`
        };
        await apiClient.post(`/documents/${documentId}/review/`, payload);
        setSuccessMessage(`Document ${action}d successfully!`);
      }
      
      // Refresh documents list
      await refreshDocuments();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
      
    } catch (error) {
      console.error(`Error ${action}ing document:`, error);
      alert(`Failed to ${action} document. Please try again.`);
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  // Handle view document
  const handleViewDocument = async (document: Document) => {
    setSelectedDocument(document);
    setShowDocumentModal(true);
    
    // Fetch AI details
    if (document.ai_confidence_score && document.ai_confidence_score > 0) {
      setLoadingAiDetails(true);
      try {
        const response = await apiClient.get<AIDetails>(`/documents/${document.id}/ai_details/`);
        setAiDetails(response.data);
      } catch (error) {
        console.error('Error fetching AI details:', error);
        setAiDetails(null);
      } finally {
        setLoadingAiDetails(false);
      }
    }
  };

  // Close document modal
  const closeDocumentModal = () => {
    setShowDocumentModal(false);
    setSelectedDocument(null);
    setAiDetails(null);
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.document_type_display.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === '' || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2 className="loading-title">Loading Documents</h2>
          <p className="loading-text">Please wait...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-content">
          <div className="error-icon">⚠</div>
          <h2 className="error-title">Error Loading Documents</h2>
          <p className="error-message">{error}</p>
          <button 
            className="retry-btn"
            onClick={() => window.location.reload()}
          >
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="documents-management-container">
      <div className="documents-management-content">
        {/* Success Message */}
        {successMessage && (
          <div className="success-message">
            ✅ {successMessage}
          </div>
        )}

        {/* Header */}
        <div className="management-header">
          <div className="header-content">
            <h1>Documents Management</h1>
            <p>Review and manage all document submissions in the TCU-CEAA system</p>
          </div>
          
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-number">{documents.length}</div>
              <div className="stat-label">Total Documents</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{documents.filter(d => d.status === 'pending').length}</div>
              <div className="stat-label">Pending Review</div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="management-controls">
          <div className="search-section">
            <div className="search-input-container">
              <svg viewBox="0 0 24 24" fill="currentColor" className="search-icon">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search by student name, ID, or document type..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
              title="Filter by status"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>

        {/* Documents List */}
        <div className="documents-list">
          {filteredDocuments.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h3>No Documents Found</h3>
              <p>
                {searchTerm || statusFilter 
                  ? `No documents match your filters`
                  : 'No documents have been submitted yet.'
                }
              </p>
              {(searchTerm || statusFilter) && (
                <button 
                  className="clear-filters-btn"
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('');
                  }}
                >
                  Clear Filters
                </button>
              )}
            </div>
          ) : (
            filteredDocuments.map((doc) => (
              <div key={doc.id} className="document-card">
                <div className="document-header">
                  <div className="document-info">
                    <h3 className="document-type">{doc.document_type_display}</h3>
                    <p className="student-info">
                      Submitted by: <strong>{doc.student_name}</strong> (ID: {doc.student_id})
                    </p>
                  </div>
                  <div className="document-status">
                    <span 
                      className={`status-badge status-badge-${doc.status}`}
                    >
                      {doc.status_display}
                    </span>
                  </div>
                </div>

                <div className="document-details">
                  <div className="detail-row">
                    <span className="detail-label">Submitted:</span>
                    <span className="detail-value">{formatDate(doc.submitted_at)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Document ID:</span>
                    <span className="detail-value">#{doc.id}</span>
                  </div>
                </div>

                <div className="document-actions">
                  <button 
                    className="action-btn view-btn"
                    onClick={() => handleViewDocument(doc)}
                    disabled={actionLoading[`view_${doc.id}`]}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                    </svg>
                    {actionLoading[`view_${doc.id}`] ? 'Loading...' : 'View Document'}
                  </button>
                  
                  {doc.status === 'pending' && (
                    <>
                      <button 
                        className="action-btn approve-btn"
                        onClick={() => handleDocumentAction(doc.id, 'approve')}
                        disabled={actionLoading[`approve_${doc.id}`]}
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {actionLoading[`approve_${doc.id}`] ? 'Approving...' : 'Approve'}
                      </button>
                      <button 
                        className="action-btn reject-btn"
                        onClick={() => handleDocumentAction(doc.id, 'reject')}
                        disabled={actionLoading[`reject_${doc.id}`]}
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {actionLoading[`reject_${doc.id}`] ? 'Rejecting...' : 'Reject'}
                      </button>
                    </>
                  )}
                  
                  {/* Delete button - available for all documents */}
                  <button 
                    className="action-btn delete-btn"
                    onClick={() => handleDocumentAction(doc.id, 'delete')}
                    disabled={actionLoading[`delete_${doc.id}`]}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path fillRule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clipRule="evenodd" />
                    </svg>
                    {actionLoading[`delete_${doc.id}`] ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Document View Modal */}
        {showDocumentModal && selectedDocument && (
          <div className="modal-overlay" onClick={closeDocumentModal}>
            <div className="modal-content modal-content-large" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Document Details</h2>
                <button className="modal-close" onClick={closeDocumentModal} title="Close">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="modal-body">
                {/* Basic Document Information */}
                <div className="document-info-section">
                  <h3>📄 Basic Information</h3>
                  <div className="document-info-grid">
                    <div className="info-row">
                      <label>Document Type:</label>
                      <span>{selectedDocument.document_type_display}</span>
                    </div>
                    <div className="info-row">
                      <label>Student Name:</label>
                      <span>{selectedDocument.student_name}</span>
                    </div>
                    <div className="info-row">
                      <label>Student ID:</label>
                      <span>{selectedDocument.student_id}</span>
                    </div>
                    <div className="info-row">
                      <label>Status:</label>
                      <span 
                        className={`status-badge status-badge-${selectedDocument.status}`}
                      >
                        {selectedDocument.status_display}
                      </span>
                    </div>
                    <div className="info-row">
                      <label>Submitted:</label>
                      <span>{formatDate(selectedDocument.submitted_at)}</span>
                    </div>
                    <div className="info-row">
                      <label>Document ID:</label>
                      <span>#{selectedDocument.id}</span>
                    </div>
                  </div>
                </div>

                {/* AI Analysis Details */}
                {loadingAiDetails && (
                  <div className="ai-details-loading">
                    <p>Loading AI analysis details...</p>
                  </div>
                )}

                {!loadingAiDetails && aiDetails && aiDetails.ai_analysis.completed && (
                  <div className="ai-analysis-section">
                    <h3>🤖 AI Analysis Results</h3>
                    
                    {/* Overall AI Summary */}
                    <div className="ai-summary-card">
                      <div className="ai-stat">
                        <label>Confidence Score:</label>
                        <span className={`confidence-score ${aiDetails.ai_analysis.confidence_score >= 0.85 ? 'high' : aiDetails.ai_analysis.confidence_score >= 0.70 ? 'medium' : 'low'}`}>
                          {(aiDetails.ai_analysis.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="ai-stat">
                        <label>Auto-Approved:</label>
                        <span className={aiDetails.ai_analysis.auto_approved ? 'match-yes' : 'match-no'}>
                          {aiDetails.ai_analysis.auto_approved ? '✅ Yes' : '❌ No'}
                        </span>
                      </div>
                    </div>

                    {/* Analysis Notes */}
                    {aiDetails.ai_analysis.analysis_notes && (
                      <div className="ai-notes-section">
                        <h4>📝 Analysis Notes</h4>
                        <div className="ai-notes-content" dangerouslySetInnerHTML={{ __html: aiDetails.ai_analysis.analysis_notes.replace(/\n/g, '<br/>') }} />
                      </div>
                    )}

                    {/* Recommendations */}
                    {aiDetails.ai_analysis.recommendations && aiDetails.ai_analysis.recommendations.length > 0 && (
                      <div className="ai-recommendations-section">
                        <h4>💡 AI Recommendations</h4>
                        <ul className="recommendations-list">
                          {aiDetails.ai_analysis.recommendations.map((rec: any, index: number) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Algorithm Results */}
                    {aiDetails.ai_analysis.algorithms_results && Object.keys(aiDetails.ai_analysis.algorithms_results).length > 0 && (
                      <div className="algorithms-section">
                        <h4>🔬 Algorithm Results</h4>
                        <div className="algorithms-grid">
                          {Object.entries(aiDetails.ai_analysis.algorithms_results).map(([key, value]: [string, any]) => (
                            <div key={key} className="algorithm-card">
                              <h5>{key.replace(/_/g, ' ').toUpperCase()}</h5>
                              <div className="algorithm-details">
                                {typeof value === 'object' ? (
                                  <pre>{JSON.stringify(value, null, 2)}</pre>
                                ) : (
                                  <span>{String(value)}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Quality Assessment - Field Matches */}
                    {aiDetails.ai_analysis.overall_analysis?.quality_assessment?.field_matches && 
                     Object.keys(aiDetails.ai_analysis.overall_analysis.quality_assessment.field_matches).length > 0 && (
                      <div className="field-matches-section">
                        <h4>✓ Field Comparison with Application</h4>
                        <div className="field-matches-grid">
                          {Object.entries(aiDetails.ai_analysis.overall_analysis.quality_assessment.field_matches).map(([field, data]: [string, any]) => (
                            <div key={field} className={`field-match-card ${data.match ? 'match-success' : 'match-fail'}`}>
                              <div className="field-name">{field.replace(/_/g, ' ').toUpperCase()}</div>
                              <div className="field-match-status">
                                {data.match ? '✅ Match' : '❌ No Match'} 
                                <span className="match-score">({(data.score * 100).toFixed(1)}%)</span>
                              </div>
                              <div className="field-values">
                                <div className="field-value-item">
                                  <label>Extracted:</label>
                                  <span>{data.extracted}</span>
                                </div>
                                <div className="field-value-item">
                                  <label>Application:</label>
                                  <span>{data.application}</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Extracted Text Preview */}
                    {aiDetails.ai_analysis.extracted_text && (
                      <details className="extracted-text-section">
                        <summary>📄 View Extracted Text (OCR)</summary>
                        <pre className="extracted-text-content">{aiDetails.ai_analysis.extracted_text}</pre>
                      </details>
                    )}
                  </div>
                )}

                {!loadingAiDetails && selectedDocument.ai_confidence_score === 0 && (
                  <div className="no-ai-analysis">
                    <p>ℹ️ No AI analysis available for this document.</p>
                  </div>
                )}

                {/* Document File */}
                {selectedDocument.document_file && (
                  <div className="document-preview">
                    <h3>📎 Document File</h3>
                    <div className="file-preview">
                      <a 
                        href={selectedDocument.document_file}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="file-link"
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                        </svg>
                        View Document File
                      </a>
                    </div>
                  </div>
                )}

                {/* Review Information */}
                {aiDetails?.review_info && (aiDetails.review_info.reviewed_at || aiDetails.review_info.admin_notes) && (
                  <div className="review-info-section">
                    <h3>👤 Review Information</h3>
                    <div className="document-info-grid">
                      {aiDetails.review_info.reviewed_by && (
                        <div className="info-row">
                          <label>Reviewed By:</label>
                          <span>{aiDetails.review_info.reviewed_by}</span>
                        </div>
                      )}
                      {aiDetails.review_info.reviewed_at && (
                        <div className="info-row">
                          <label>Reviewed At:</label>
                          <span>{formatDate(aiDetails.review_info.reviewed_at)}</span>
                        </div>
                      )}
                      {aiDetails.review_info.admin_notes && (
                        <div className="info-row full-width">
                          <label>Admin Notes:</label>
                          <span>{aiDetails.review_info.admin_notes}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="modal-actions">
                {selectedDocument.status === 'pending' && (
                  <>
                    <button 
                      className="modal-btn approve-btn"
                      onClick={() => {
                        handleDocumentAction(selectedDocument.id, 'approve');
                        closeDocumentModal();
                      }}
                      disabled={actionLoading[`approve_${selectedDocument.id}`]}
                    >
                      Approve Document
                    </button>
                    <button 
                      className="modal-btn reject-btn"
                      onClick={() => {
                        handleDocumentAction(selectedDocument.id, 'reject');
                        closeDocumentModal();
                      }}
                      disabled={actionLoading[`reject_${selectedDocument.id}`]}
                    >
                      Reject Document
                    </button>
                  </>
                )}
                <button className="modal-btn cancel-btn" onClick={closeDocumentModal}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentsManagement;
