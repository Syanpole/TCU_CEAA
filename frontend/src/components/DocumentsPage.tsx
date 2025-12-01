import React, { useState } from 'react';
import DocumentSubmissionForm from './DocumentSubmissionForm';
import DocumentVerificationCard from './DocumentVerificationCard';
import { CheckIcon } from './Icons';
import { PageGuideBanner, HelpTooltip, InfoNote } from './TutorialSystem';
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

  const parseExtractedInfo = (notes: string) => {
    // Try JSON format first (existing format)
    const extractedMatch = notes.match(/Extracted Info:\s*(\{[\s\S]*\})/);
    if (extractedMatch) {
      try {
        const jsonStr = extractedMatch[1].replace(/'/g, '"');
        return JSON.parse(jsonStr);
      } catch (e) {
        // Continue to other formats
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

      {/* Page Guide Banner */}
      <PageGuideBanner 
        icon="📤"
        title="Upload Required Documents"
        text="Submit clear, readable copies of your Birth Certificate, School ID, Certificate of Enrollment, and Voter's Certificate. All documents will be verified by our AI system and admin staff."
      />

      {documents.length === 0 && (
        <InfoNote 
          title="Get Started"
          text="Click the 'Upload Document' button above to submit your first document. You'll need to upload all required documents to proceed to the next step."
        />
      )}

      {/* Documents Grid - Modern Vertical Cards */}
      {documents.length > 0 ? (
        <div className="dvc-grid">
          {documents.map((doc) => (
            <DocumentVerificationCard
              key={doc.id}
              id={doc.id}
              documentType={doc.document_type}
              documentTypeDisplay={doc.document_type_display}
              status={doc.status as 'approved' | 'rejected' | 'pending'}
              submittedAt={doc.submitted_at}
              aiConfidenceScore={doc.ai_confidence_score}
              aiAnalysisNotes={doc.ai_analysis_notes}
              aiAutoApproved={doc.ai_auto_approved}
              onDelete={(id) => {/* Add delete functionality */}}
              onViewDetails={() => setSelectedDocForDetails(doc)}
            />
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
                    {(() => {
                      const extractedInfo = parseExtractedInfo(selectedDocForDetails.ai_analysis_notes);
                      if (extractedInfo) {
                        return (
                          <div className="dp-extracted-info">
                            {/* Verification Status */}
                            {extractedInfo.verification_status && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Verification:</span>
                                <span className="dp-info-value">{extractedInfo.verification_status}</span>
                              </div>
                            )}

                            {/* Status */}
                            {extractedInfo.status && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Status:</span>
                                <span className="dp-info-value">{extractedInfo.status}</span>
                              </div>
                            )}

                            {/* Confidence */}
                            {extractedInfo.confidence && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Confidence:</span>
                                <span className="dp-info-value">{extractedInfo.confidence}%</span>
                              </div>
                            )}

                            {/* Checks Passed */}
                            {extractedInfo.checks_passed && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Checks Passed:</span>
                                <span className="dp-info-value">{extractedInfo.checks_passed}</span>
                              </div>
                            )}

                            {/* Identity Match */}
                            {typeof extractedInfo.identity_match === 'boolean' && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Identity Match:</span>
                                <span className="dp-info-value">{extractedInfo.identity_match ? 'Yes' : 'No'}</span>
                              </div>
                            )}

                            {/* Student Info */}
                            {extractedInfo.student_name && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Student Name:</span>
                                <span className="dp-info-value">{extractedInfo.student_name}</span>
                              </div>
                            )}

                            {extractedInfo.student_id && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Student ID:</span>
                                <span className="dp-info-value">{extractedInfo.student_id}</span>
                              </div>
                            )}

                            {extractedInfo.institution && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Institution:</span>
                                <span className="dp-info-value">{extractedInfo.institution}</span>
                              </div>
                            )}

                            {extractedInfo.program && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Program:</span>
                                <span className="dp-info-value">{extractedInfo.program}</span>
                              </div>
                            )}

                            {extractedInfo.college_code && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">College Code:</span>
                                <span className="dp-info-value">{extractedInfo.college_code}</span>
                              </div>
                            )}

                            {/* Legacy fields for backward compatibility */}
                            {extractedInfo.year_level && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Year Level:</span>
                                <span className="dp-info-value">{extractedInfo.year_level}</span>
                              </div>
                            )}

                            {extractedInfo.semester && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Semester:</span>
                                <span className="dp-info-value">{extractedInfo.semester}</span>
                              </div>
                            )}

                            {extractedInfo.enrollment_date && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Enrollment Date:</span>
                                <span className="dp-info-value">{extractedInfo.enrollment_date}</span>
                              </div>
                            )}

                            {extractedInfo.subject_count && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Subject Count:</span>
                                <span className="dp-info-value">{extractedInfo.subject_count}</span>
                              </div>
                            )}

                            {extractedInfo.subjects && extractedInfo.subjects.length > 0 && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Subjects:</span>
                                <div className="dp-subjects-list">
                                  {extractedInfo.subjects.map((subject: any, index: number) => (
                                    <div key={index} className="dp-subject-item">
                                      <span className="dp-subject-code">{subject.subject_code}</span>
                                      <span className="dp-subject-name">{subject.subject_name}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Recommendations */}
                            {extractedInfo.recommendations && (
                              <div className="dp-info-item">
                                <span className="dp-info-label">Recommendations:</span>
                                <span className="dp-info-value">{extractedInfo.recommendations}</span>
                              </div>
                            )}
                          </div>
                        );
                      } else {
                        return <div>{selectedDocForDetails.ai_analysis_notes}</div>;
                      }
                    })()}
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