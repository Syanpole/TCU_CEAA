import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import './DocumentRequirements.css';

interface DocumentRequirementsProps {
  darkMode?: boolean;
  schoolYear?: string;
  semester?: string;
  isRenewing?: boolean;
}

interface DocumentSubmission {
  id: number;
  document_type: string;
  document_type_display: string;
  status: string;
  status_display: string;
  submitted_at: string;
  document_file?: string;
  ai_confidence_score?: number;
  ai_analysis_completed?: boolean;
  ai_analysis_notes?: string;
  ai_auto_approved?: boolean;
  ai_identity_verified?: boolean;
  ai_identity_type?: 'student' | 'mother' | 'father' | null;
  ai_document_type_match?: boolean;
  ai_recommendations?: string[];
  reviewed_at?: string;
  extracted_subjects?: any[];
  subject_count?: number;
  description?: string;
}

const DOCUMENT_TYPE_OPTIONS = [
  { label: '[A] Certificate of Enrollment for 1st Semester, S.Y. 2024-2025', value: 'certificate_of_enrollment', hideForRenewing: false },
  { label: '[B] Certificate of Enrollment for 2nd Semester, S.Y. 2024-2025', value: 'certificate_of_enrollment', hideForRenewing: false },
  { label: '[C] Certificate of Grades - Last Semester', value: 'transcript_of_records', hideForRenewing: true },
  { label: "[D] Junior High School Certificate/Grade 10 Report Card (New Applicant)", value: 'grade_10_report_card', hideForRenewing: true },
  { label: "[E] Senior High School Diploma/Grade 12 Report Card (New Applicant)", value: 'grade_12_report_card', hideForRenewing: true },
  { label: '[F] School ID or Valid Government-Issued ID', value: 'school_id', hideForRenewing: false },
  { label: "[G] Parent's Voter Registration - Taguig City", value: 'voter_certification', hideForRenewing: false },
  { label: "[H] Student's Voter Registration - Taguig City (18+ years old)", value: 'voters_id', hideForRenewing: false },
  { label: '[I] Birth Certificate (PSA/NSO/Civil Registry)', value: 'birth_certificate', hideForRenewing: false },
  { label: '[J] Form 137 - Elementary/High School', value: 'form_137', hideForRenewing: true },
  { label: '[K] Certificate of Academic Excellence (Honors Scholars)', value: 'other', hideForRenewing: true }
];

// Create mapping from label to value for backward compatibility
const documentTypeMapping = DOCUMENT_TYPE_OPTIONS.reduce((acc, opt) => {
  acc[opt.label] = opt.value;
  return acc;
}, {} as Record<string, string>);

const DocumentRequirements: React.FC<DocumentRequirementsProps> = ({ darkMode = false, schoolYear = 'S.Y 2025-2026', semester = '1ST SEMESTER', isRenewing = false }) => {
  const [selectedSemester, setSelectedSemester] = useState(semester);
  const [selectedSchoolYear, setSelectedSchoolYear] = useState(schoolYear);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [documentType, setDocumentType] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  // Fetch documents from backend
  const [uploadedDocuments, setUploadedDocuments] = useState<DocumentSubmission[]>([]);
  const [fetchingDocuments, setFetchingDocuments] = useState(true);
  const [selectedDocForDetails, setSelectedDocForDetails] = useState<DocumentSubmission | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<DocumentSubmission | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const availableDocumentTypeOptions = DOCUMENT_TYPE_OPTIONS.filter(option => !(isRenewing && option.hideForRenewing));

  const handleDocumentTypeChange: React.ChangeEventHandler<HTMLSelectElement> = (e) => {
    setDocumentType(e.target.value);
  };

  // Fetch documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setFetchingDocuments(true);
      const response = await apiClient.get<DocumentSubmission[]>('/documents/');
      setUploadedDocuments(response.data || []);
    } catch (err: any) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents');
    } finally {
      setFetchingDocuments(false);
    }
  };

  const handleAddRequirement = () => {
    setShowUploadModal(true);
    setDocumentType('');
    setSelectedFile(null);
    setDescription('');
    setError('');
    setSuccessMessage('');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        setSelectedFile(null);
        return;
      }
      
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
      if (!allowedTypes.includes(file.type)) {
        setError('Only PDF, JPG, and PNG files are allowed');
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setError('');
    }
  };

  const handleUploadDocument = async () => {
    if (!documentType || !selectedFile) {
      setError('Please select document type and file to upload');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');
    setUploadProgress(0);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('document_type', documentTypeMapping[documentType]);
      formData.append('file', selectedFile);
      if (description) {
        formData.append('description', description);
      }

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      console.log('Uploading document...', {
        documentType: documentTypeMapping[documentType],
        fileName: selectedFile.name,
        fileSize: selectedFile.size,
      });

      // Upload to backend
      const response = await apiClient.post('/documents/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      console.log('Upload response:', response.data);

      // Show success message
      setSuccessMessage('✅ Document uploaded successfully! AI is now analyzing your document...');
      
      // Refresh documents list
      await fetchDocuments();

      // Close modal after delay
      setTimeout(() => {
        setShowUploadModal(false);
        setDocumentType('');
        setSelectedFile(null);
        setDescription('');
        setSuccessMessage('');
        setUploadProgress(0);
      }, 2000);

    } catch (error: any) {
      console.error('Error uploading document:', error);
      console.error('Error response:', error.response);
      
      let errorMessage = 'Failed to upload document. Please try again.';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          // Handle field-specific errors
          if (error.response.data.file) {
            errorMessage = Array.isArray(error.response.data.file) 
              ? error.response.data.file[0] 
              : error.response.data.file;
          } else if (error.response.data.document_type) {
            errorMessage = Array.isArray(error.response.data.document_type)
              ? error.response.data.document_type[0]
              : error.response.data.document_type;
          } else if (error.response.data.error || error.response.data.message) {
            errorMessage = error.response.data.error || error.response.data.message;
          } else if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          }
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
      setUploadProgress(0);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseModal = () => {
    if (!loading) {
      setShowUploadModal(false);
      setDocumentType('');
      setSelectedFile(null);
      setDescription('');
      setError('');
      setSuccessMessage('');
      setUploadProgress(0);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return '#10b981';
      case 'pending':
      case 'ai_processing':
        return '#f59e0b';
      case 'rejected':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return '✅';
      case 'pending':
        return '⏳';
      case 'ai_processing':
        return '🤖';
      case 'rejected':
        return '❌';
      default:
        return '📄';
    }
  };

  const handleDeleteDocument = async (doc: DocumentSubmission) => {
    setDocumentToDelete(doc);
    setShowDeleteModal(true);
  };

  const confirmDeleteDocument = async () => {
    if (!documentToDelete) return;

    setIsDeleting(true);
    try {
      await apiClient.delete(`/documents/${documentToDelete.id}/`);
      setSuccessMessage('Document deleted successfully');
      setShowDeleteModal(false);
      setDocumentToDelete(null);
      await fetchDocuments();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      console.error('Error deleting document:', error);
      setError('Failed to delete document');
      setTimeout(() => setError(''), 3000);
    } finally {
      setIsDeleting(false);
    }
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setDocumentToDelete(null);
  };

  const handleViewDocument = (doc: DocumentSubmission) => {
    setSelectedDocForDetails(doc);
  };

  const parseExtractedInfo = (notes: string) => {
    // Try JSON format first (existing format)
    const extractedMatch = notes.match(/Extracted Info:\s*(\{[\s\S]*\})/);
    if (extractedMatch) {
      try {
        const jsonStr = extractedMatch[1].replace(/'/g, '"');
        return JSON.parse(jsonStr);
      } catch (e) {
        }
    }

    // Try new structured text format
    const extractedInfo: any = {};

    // Parse ID Verification status
    const idVerificationMatch = notes.match(/ID Verification \((.*?)\)/);
    if (idVerificationMatch) {
      extractedInfo.verification_status = idVerificationMatch[1];
    }

    // Parse Status
    const statusMatch = notes.match(/Status:\s*(.+)/);
    if (statusMatch) {
      extractedInfo.status = statusMatch[1].trim();
    }

    // Parse Confidence
    const confidenceMatch = notes.match(/Confidence:\s*([\d.]+)%/);
    if (confidenceMatch) {
      extractedInfo.confidence = parseFloat(confidenceMatch[1]);
    }

    // Parse Checks Passed
    const checksMatch = notes.match(/Checks Passed:\s*(\d+)/);
    if (checksMatch) {
      extractedInfo.checks_passed = parseInt(checksMatch[1]);
    }

    // Parse Identity Match
    const identityMatch = notes.match(/Identity Match:\s*(.+)/);
    if (identityMatch) {
      extractedInfo.identity_match = identityMatch[1].trim().toLowerCase() === 'true';
    }

    // Parse Extracted Fields
    const extractedFieldsMatch = notes.match(/Extracted Fields:\s*\n((?:  .+:.+\n?)*)/);
    if (extractedFieldsMatch) {
      const fieldsText = extractedFieldsMatch[1];
      const fieldLines = fieldsText.split('\n').filter(line => line.trim());

      fieldLines.forEach(line => {
        const fieldMatch = line.match(/  (\w+):\s*(.+)/);
        if (fieldMatch) {
          const key = fieldMatch[1];
          const value = fieldMatch[2].trim();

          // Map common field names to our expected format
          switch (key) {
            case 'name':
              extractedInfo.student_name = value;
              break;
            case 'student_number':
              extractedInfo.student_id = value;
              break;
            case 'institution':
              extractedInfo.institution = value;
              break;
            case 'college':
              extractedInfo.program = value;
              break;
            case 'college_code':
              extractedInfo.college_code = value;
              break;
            default:
              extractedInfo[key] = value;
          }
        }
      });
    }

    // Parse Recommendations
    const recommendationsMatch = notes.match(/Recommendations:\s*(.+)/);
    if (recommendationsMatch) {
      extractedInfo.recommendations = recommendationsMatch[1].trim();
    }

    // Return extracted info if we found any data
    if (Object.keys(extractedInfo).length > 0) {
      return extractedInfo;
    }

    return null;
  };

  return (
    <div className={`document-requirements ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Error/Success Messages */}
      {error && (
        <div className="notification-banner error">
          <span className="notification-icon">❌</span>
          <span>{error}</span>
          <button onClick={() => setError('')} className="close-notification">×</button>
        </div>
      )}
      
      {successMessage && (
        <div className="notification-banner success">
          <span className="notification-icon">✅</span>
          <span>{successMessage}</span>
          <button onClick={() => setSuccessMessage('')} className="close-notification">×</button>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="upload-modal-overlay" onClick={handleCloseModal}>
          <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Upload Document</h2>
              <button className="close-modal-btn" onClick={handleCloseModal} disabled={loading}>×</button>
            </div>
            
            <div className="modal-body">
              {error && (
                <div className="inline-error">
                  <span className="error-icon">⚠️</span>
                  <span>{error}</span>
                </div>
              )}

              {successMessage && (
                <div className="inline-success">
                  <span className="success-icon">✅</span>
                  <span>{successMessage}</span>
                </div>
              )}

              <div className="form-group">
                <label>Document Type <span className="required">*</span></label>
                <select 
                  value={documentType}
                  onChange={handleDocumentTypeChange}
                  className="document-type-select"
                  disabled={loading}
                  title="Select the type of document to upload"
                >
                  <option value="">Select Document Type</option>
                  {availableDocumentTypeOptions.map((option) => (
                    <option key={option.label} value={option.label}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Upload File <span className="required">*</span></label>
                <div className="file-upload-area">
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={handleFileChange}
                    className="file-input"
                    id="file-upload"
                    disabled={loading}
                  />
                  <label htmlFor="file-upload" className="file-upload-label">
                    <span className="upload-icon">📁</span>
                    <span className="upload-text">
                      {selectedFile
                        ? `${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(2)} MB)`
                        : 'Click to browse or drag file here'}
                    </span>
                    <span className="upload-hint">Supported: PDF, JPG, PNG • Max 10MB</span>
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label>Description (Optional)</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="description-textarea"
                  placeholder="Add any notes about this document..."
                  rows={3}
                  disabled={loading}
                />
              </div>

              {loading && uploadProgress > 0 && (
                <div className="upload-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <span className="progress-text">
                    {uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Processing with AI...'}
                  </span>
                </div>
              )}

              <div className="ai-info-box">
                <div className="ai-info-text">
                  <strong>AI Verification:</strong>
                  <p>Your document will be automatically analyzed by our AI system for authenticity and compliance.</p>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-cancel" onClick={handleCloseModal} disabled={loading}>
                Cancel
              </button>
              <button 
                className="btn-upload" 
                onClick={handleUploadDocument}
                disabled={loading || !documentType || !selectedFile}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Uploading...
                  </>
                ) : (
                  <>
                    Upload Document
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="requirements-header">
        <div className="header-left">
          <h1>Submission of Requirements</h1>
          <p className="header-subtitle">Upload and manage your scholarship documents</p>
        </div>
        <div className="header-right">
          <button className="refresh-btn" onClick={fetchDocuments} disabled={fetchingDocuments} title="Refresh documents">
            <span className={`refresh-icon ${fetchingDocuments ? 'spinning' : ''}`}>🔄</span>
            Refresh
          </button>
          <button className="add-document-btn" onClick={handleAddRequirement}>
            <span className="btn-plus">+</span>
            Add Document
          </button>
        </div>
      </div>

      <div className="documents-container">
        {fetchingDocuments ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading your documents...</p>
          </div>
        ) : uploadedDocuments.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📄</div>
            <h3>No Documents Uploaded Yet</h3>
            <p>Start by uploading your required documents for the scholarship application.</p>
            <p className="empty-hint">
              💡 Tip: All documents will be automatically verified by our AI system for authenticity.
            </p>
            <button className="btn-upload-first" onClick={handleAddRequirement}>
              <span className="btn-icon">+</span>
              Upload Your First Document
            </button>
          </div>
        ) : (
          <div className="documents-grid">
            {uploadedDocuments.map((doc) => (
              <div key={doc.id} className="document-card">
                <div className="card-header">
                  <div className="document-icon">
                    {getStatusIcon(doc.status)}
                  </div>
                  <button 
                    className="delete-btn"
                    onClick={() => handleDeleteDocument(doc)}
                    title="Delete document"
                  >
                    ×
                  </button>
                </div>
                
                <div className="card-body">
                  <h3 className="document-title">{doc.document_type_display}</h3>
                  
                  <div className="document-info">
                    <div className="info-item">
                      <span className="info-icon">📅</span>
                      <span className="info-text">
                        {new Date(doc.submitted_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-icon">ℹ️</span>
                      <span className="info-text">
                        Status: <span style={{ color: getStatusColor(doc.status), fontWeight: 600 }}>
                          {doc.status_display}
                        </span>
                      </span>
                    </div>
                    {doc.ai_confidence_score !== undefined && doc.ai_confidence_score !== null && (
                      <div className="info-item">
                        <span className="info-text">
                          AI Confidence: <strong>{(doc.ai_confidence_score * 100).toFixed(1)}%</strong>
                        </span>
                      </div>
                    )}
                    {doc.ai_analysis_completed && (
                      <div className="info-item ai-badge">
                        <span className="ai-verified">✓ AI Verified</span>
                      </div>
                    )}
                  </div>

                  {doc.ai_analysis_notes && (
                    <div className="ai-notes">
                      <strong>AI Analysis:</strong>
                      <p>{doc.ai_analysis_notes.substring(0, 100)}{doc.ai_analysis_notes.length > 100 ? '...' : ''}</p>
                    </div>
                  )}
                </div>

                <div className="card-footer">
                  <button 
                    className="btn-view-document"
                    onClick={() => handleViewDocument(doc)}
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && documentToDelete && (
        <div className="delete-modal-overlay" onClick={cancelDelete}>
          <div className="delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="delete-modal-icon">
              <span className="warning-icon">⚠️</span>
            </div>
            
            <h2 className="delete-modal-title">Delete Document?</h2>
            <p className="delete-modal-message">
              Are you sure you want to delete <strong>{documentToDelete.document_type_display}</strong>?
            </p>
            <p className="delete-modal-warning">
              This action cannot be undone.
            </p>

            <div className="delete-modal-actions">
              <button 
                className="btn-cancel-delete"
                onClick={cancelDelete}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button 
                className="btn-confirm-delete"
                onClick={confirmDeleteDocument}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <>
                    <span className="spinner-small"></span>
                    Deleting...
                  </>
                ) : (
                  <>
                    <span className="delete-icon">🗑️</span>
                    Delete
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modern AI Analysis Details Modal */}
      {selectedDocForDetails && (
        <div className="doc-modal-overlay" onClick={() => setSelectedDocForDetails(null)}>
          <div className="doc-modal-modern" onClick={(e) => e.stopPropagation()}>
            {/* Close Button */}
            <button 
              className="doc-modal-close-btn"
              onClick={() => setSelectedDocForDetails(null)}
              aria-label="Close modal"
            >
              ×
            </button>

            {/* Modal Content */}
            <div className="doc-modal-content">
              {/* Header Section */}
              <div className="doc-modal-header-section">
                <div className="doc-modal-icon-wrapper">
                  <span className="doc-modal-emoji">🤖</span>
                </div>
                <h2 className="doc-modal-heading">AI Analysis Report</h2>
                <p className="doc-modal-subheading">{selectedDocForDetails.document_type_display}</p>
              </div>

              {/* Status Badge */}
              <div className="doc-status-badge-container">
                <span className={`doc-status-badge-modern status-${selectedDocForDetails.status}`}>
                  {selectedDocForDetails.status === 'approved' && '✅ '}
                  {selectedDocForDetails.status === 'rejected' && '❌ '}
                  {selectedDocForDetails.status === 'pending' && '⏳ '}
                  {selectedDocForDetails.status_display}
                </span>
              </div>

              {/* Main Info Grid */}
              <div className="doc-modal-info-grid">
                <div className="doc-modal-info-box">
                  <div className="doc-info-box-label">Submitted</div>
                  <div className="doc-info-box-value">
                    {new Date(selectedDocForDetails.submitted_at).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric', 
                      year: 'numeric' 
                    })}
                  </div>
                </div>

                {selectedDocForDetails.ai_confidence_score !== undefined && (
                  <div className="doc-modal-info-box">
                    <div className="doc-info-box-label">AI Confidence</div>
                    <div className="doc-info-box-value doc-confidence-value">
                      {(selectedDocForDetails.ai_confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
              </div>

              {/* Confidence Progress Bar */}
              {selectedDocForDetails.ai_confidence_score !== undefined && (
                <div className="doc-confidence-container">
                  <div className="doc-progress-bar-modern">
                    <div 
                      className="doc-progress-fill-modern"
                      style={{ 
                        width: `${selectedDocForDetails.ai_confidence_score * 100}%`,
                        backgroundColor: selectedDocForDetails.ai_confidence_score >= 0.8 ? '#10b981' : 
                                       selectedDocForDetails.ai_confidence_score >= 0.6 ? '#f59e0b' : '#ef4444'
                      }}
                    />
                  </div>
                  <div className="doc-confidence-status">
                    {selectedDocForDetails.ai_confidence_score >= 0.8 ? 'High Confidence' : 
                     selectedDocForDetails.ai_confidence_score >= 0.6 ? 'Medium Confidence' : 'Low Confidence'}
                  </div>
                </div>
              )}

              {/* AI Decision */}
              {typeof selectedDocForDetails.ai_auto_approved !== 'undefined' && (
                <div className="doc-modal-info-grid">
                  <div className="doc-modal-info-box">
                    <div className="doc-info-box-label">AI Decision</div>
                    <div className={`doc-info-box-value ${selectedDocForDetails.ai_auto_approved ? 'status-approved' : 'status-pending'}`}>
                      {selectedDocForDetails.ai_auto_approved ? 'Auto-Approved' : 'Manual Review Required'}
                    </div>
                  </div>
                  {selectedDocForDetails.ai_identity_verified && (
                    <div className="doc-modal-info-box">
                      <div className="doc-info-box-label">Identity Source</div>
                      <div className="doc-info-box-value">
                        {selectedDocForDetails.ai_identity_type === 'student' && 'Student'}
                        {selectedDocForDetails.ai_identity_type === 'mother' && 'Mother'}
                        {selectedDocForDetails.ai_identity_type === 'father' && 'Father'}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Analysis Details */}
              {selectedDocForDetails.ai_analysis_notes && (
                <div className="doc-analysis-section">
                  <h3 className="doc-section-title">Analysis Details</h3>
                  <div className="doc-analysis-content">
                    {(() => {
                      const extractedInfo = parseExtractedInfo(selectedDocForDetails.ai_analysis_notes);
                      if (extractedInfo) {
                        return (
                          <div className="dr-extracted-info">
                            <h4>Extracted Information</h4>

                            {/* Verification Status */}
                            {extractedInfo.verification_status && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Verification:</span>
                                <span className="dr-info-value">{extractedInfo.verification_status}</span>
                              </div>
                            )}

                            {/* Status */}
                            {extractedInfo.status && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Status:</span>
                                <span className="dr-info-value">{extractedInfo.status}</span>
                              </div>
                            )}

                            {/* Confidence */}
                            {extractedInfo.confidence && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Confidence:</span>
                                <span className="dr-info-value">{extractedInfo.confidence}%</span>
                              </div>
                            )}

                            {/* Checks Passed */}
                            {extractedInfo.checks_passed && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Checks Passed:</span>
                                <span className="dr-info-value">{extractedInfo.checks_passed}</span>
                              </div>
                            )}

                            {/* Identity Match */}
                            {typeof extractedInfo.identity_match === 'boolean' && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Identity Match:</span>
                                <span className="dr-info-value">{extractedInfo.identity_match ? 'Yes' : 'No'}</span>
                              </div>
                            )}

                            {/* Student Info */}
                            {extractedInfo.student_name && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Student Name:</span>
                                <span className="dr-info-value">{extractedInfo.student_name}</span>
                              </div>
                            )}

                            {extractedInfo.student_id && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Student ID:</span>
                                <span className="dr-info-value">{extractedInfo.student_id}</span>
                              </div>
                            )}

                            {extractedInfo.institution && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Institution:</span>
                                <span className="dr-info-value">{extractedInfo.institution}</span>
                              </div>
                            )}

                            {extractedInfo.program && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Program:</span>
                                <span className="dr-info-value">{extractedInfo.program}</span>
                              </div>
                            )}

                            {extractedInfo.college_code && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">College Code:</span>
                                <span className="dr-info-value">{extractedInfo.college_code}</span>
                              </div>
                            )}

                            {/* Legacy fields for backward compatibility */}
                            {extractedInfo.year_level && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Year Level:</span>
                                <span className="dr-info-value">{extractedInfo.year_level}</span>
                              </div>
                            )}

                            {extractedInfo.semester && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Semester:</span>
                                <span className="dr-info-value">{extractedInfo.semester}</span>
                              </div>
                            )}

                            {extractedInfo.enrollment_date && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Enrollment Date:</span>
                                <span className="dr-info-value">{extractedInfo.enrollment_date}</span>
                              </div>
                            )}

                            {extractedInfo.subject_count && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Subject Count:</span>
                                <span className="dr-info-value">{extractedInfo.subject_count}</span>
                              </div>
                            )}

                            {extractedInfo.subjects && extractedInfo.subjects.length > 0 && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Subjects:</span>
                                <div className="dr-info-value">
                                  {extractedInfo.subjects.map((subject: any, index: number) => (
                                    <div key={index} className="dr-subject-item">
                                      <strong>{subject.subject_code}</strong> - {subject.subject_name}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Recommendations */}
                            {extractedInfo.recommendations && (
                              <div className="dr-info-item">
                                <span className="dr-info-label">Recommendations:</span>
                                <span className="dr-info-value">{extractedInfo.recommendations}</span>
                              </div>
                            )}
                          </div>
                        );
                      } else {
                        return <pre>{selectedDocForDetails.ai_analysis_notes}</pre>;
                      }
                    })()}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {selectedDocForDetails.ai_recommendations && selectedDocForDetails.ai_recommendations.length > 0 && (
                <div className="doc-analysis-section">
                  <h3 className="doc-section-title">Recommendations</h3>
                  <ul className="doc-recommendations-list">
                    {selectedDocForDetails.ai_recommendations.map((rec: any, i: number) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Button */}
              <button 
                className="doc-modal-action-btn"
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

export default DocumentRequirements;
