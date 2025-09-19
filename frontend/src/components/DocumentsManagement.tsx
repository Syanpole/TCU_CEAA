import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
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
}

interface DocumentsManagementProps {
  onViewChange?: (view: string) => void;
}

const DocumentsManagement: React.FC<DocumentsManagementProps> = ({ onViewChange }) => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [actionLoading, setActionLoading] = useState<{ [key: string]: boolean }>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(null);

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
    if (!document.document_file) {
      setError('No document file available for viewing.');
      return;
    }
    
    try {
      // Open the document in a new tab/window
      const fileUrl = document.document_file.startsWith('http') 
        ? document.document_file 
        : `${window.location.origin}${document.document_file}`;
      window.open(fileUrl, '_blank');
    } catch (err) {
      console.error('Error viewing document:', err);
      setError('Failed to open document. Please try again.');
    }
  };

  // Show document details in modal
  const handleShowDocumentModal = (document: Document) => {
    setSelectedDocument(document);
    setShowDocumentModal(true);
  };

  // Close document modal
  const closeDocumentModal = () => {
    setShowDocumentModal(false);
    setSelectedDocument(null);
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.document_type_display.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === '' || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDeleteClick = (document: Document) => {
    setDocumentToDelete(document);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!documentToDelete) return;

    try {
      await apiClient.delete(`/documents/${documentToDelete.id}/`);
      setDocuments(documents.filter(doc => doc.id !== documentToDelete.id));
      setShowDeleteModal(false);
      setDocumentToDelete(null);
    } catch (err) {
      console.error('Error deleting document:', err);
      setError('Failed to delete document. Please try again.');
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setDocumentToDelete(null);
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
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: '#10b981',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: 1000,
            animation: 'slideIn 0.3s ease-out'
          }}>
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
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(doc.status) }}
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
                    disabled={!doc.document_file}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                    </svg>
                    View
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
                  <button 
                    className="action-btn delete-btn"
                    onClick={() => handleDeleteClick(doc)}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path fillRule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.393 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.607-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clipRule="evenodd" />
                    </svg>
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Document View Modal */}
        {showDocumentModal && selectedDocument && (
          <div className="modal-overlay" onClick={closeDocumentModal}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Document Details</h2>
                <button className="modal-close" onClick={closeDocumentModal}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="modal-body">
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
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(selectedDocument.status) }}
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

                {selectedDocument.document_file && (
                  <div className="document-preview">
                    <label>Document File:</label>
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

      {/* Delete Confirmation Modal */}
      {showDeleteModal && documentToDelete && (
        <div className="modal-overlay" onClick={handleDeleteCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Delete Document</h3>
              <button className="modal-close" onClick={handleDeleteCancel}>
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="warning-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path fillRule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="modal-text">
                <h4>Are you sure you want to delete this document?</h4>
                <p>
                  <strong>{documentToDelete.document_type_display}</strong><br />
                  Submitted by: {documentToDelete.student_name} (ID: {documentToDelete.student_id})<br />
                  <span className="warning-text">This action cannot be undone.</span>
                </p>
              </div>
            </div>
            
            <div className="modal-footer">
              <button className="modal-btn cancel-btn" onClick={handleDeleteCancel}>
                Cancel
              </button>
              <button className="modal-btn delete-btn-confirm" onClick={handleDeleteConfirm}>
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path fillRule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.393 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.607-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clipRule="evenodd" />
                </svg>
                Delete Document
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsManagement;
