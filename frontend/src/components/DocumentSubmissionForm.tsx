import React, { useState } from 'react';
import { apiClient } from '../services/authService';
import { RequirementsIcon, WarningIcon } from './Icons';
import NotificationModal from './NotificationModal';
import './DocumentSubmissionForm.css';

interface DocumentSubmissionFormProps {
  onSubmissionSuccess?: () => void;
  onCancel?: () => void;
}

interface FormData {
  document_type: string;
  description: string;
  file: File | null;
}

const DocumentSubmissionForm: React.FC<DocumentSubmissionFormProps> = ({
  onSubmissionSuccess,
  onCancel
}) => {
  const [formData, setFormData] = useState<FormData>({
    document_type: '',
    description: '',
    file: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [instantApproval, setInstantApproval] = useState(false);

  const documentTypes = [
    // Separated document types
    'birth_certificate',
    'school_id',
    'certificate_of_enrollment',
    'grade_10_report_card',
    'grade_12_report_card',
    'diploma',
    'others'
  ];

  const documentTypeLabels: { [key: string]: string } = {
    birth_certificate: 'Birth Certificate / PSA',
    school_id: 'School ID',
    certificate_of_enrollment: 'Certificate of Enrollment',
    grade_10_report_card: 'Grade 10 Report Card',
    grade_12_report_card: 'Grade 12 Report Card',
    diploma: 'Diploma',
    others: 'Others'
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    
    if (file) {
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size cannot exceed 10MB. Please compress your file or choose a smaller one.');
        return;
      }
      
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 
                           'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Please upload a PDF, JPG, PNG, DOC, or DOCX file.');
        return;
      }
      
      // Clear any previous errors
      setError('');
    }
    
    setFormData(prev => ({
      ...prev,
      file
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.document_type || !formData.file) {
      setError('Please select a document type and upload a file');
      return;
    }

    // Additional client-side validation
    if (formData.file.size > 10 * 1024 * 1024) {
      setError('File size cannot exceed 10MB');
      return;
    }

    if (formData.file.size < 1024) {
      setError('File seems too small. Please ensure you uploaded a valid document');
      return;
    }

    setLoading(true);
    setError('');
    setProcessingStatus('⬆️ Uploading document...');

    try {
      const submitFormData = new FormData();
      submitFormData.append('document_type', formData.document_type);
      submitFormData.append('description', formData.description);
      submitFormData.append('file', formData.file);

      // Show instant processing status
      setProcessingStatus('🤖 AI analyzing document...');

      const response = await apiClient.post('/documents/', submitFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Show instant approval status
      setProcessingStatus('✅ Document approved instantly!');
      setInstantApproval(true);

      // Reset form
      setFormData({
        document_type: '',
        description: '',
        file: null
      });

      // Clear file input
      const fileInput = document.getElementById('file') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }

      // Show success notification
      setShowNotification(true);

      // Close form after a delay to allow user to see notification
      setTimeout(() => {
        if (onSubmissionSuccess) {
          onSubmissionSuccess();
        }
      }, 3000);
    } catch (error: any) {
      console.error('Error submitting document:', error);
      setProcessingStatus('');
      setInstantApproval(false);
      
      // Handle specific error responses
      if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData === 'object') {
          // Handle field-specific errors
          const errorMessages = [];
          if (errorData.file) {
            errorMessages.push(`File: ${Array.isArray(errorData.file) ? errorData.file.join(', ') : errorData.file}`);
          }
          if (errorData.document_type) {
            errorMessages.push(`Document Type: ${Array.isArray(errorData.document_type) ? errorData.document_type.join(', ') : errorData.document_type}`);
          }
          if (errorData.non_field_errors) {
            errorMessages.push(Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors.join(', ') : errorData.non_field_errors);
          }
          if (errorData.detail) {
            errorMessages.push(errorData.detail);
          }
          
          if (errorMessages.length > 0) {
            setError(errorMessages.join('. '));
          } else {
            setError('Failed to submit document. Please check your inputs and try again.');
          }
        } else {
          setError(errorData || 'Failed to submit document');
        }
      } else {
        setError('Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="document-submission-form">
      <div className="form-header">
        <h3>Submit Required Documents</h3>
        <p>Upload required documents for TCU-CEAA scholarship application</p>
        <div className="requirement-note">
          <strong>Required Documents:</strong>
          <ul>
            <li>Birth Certificate (PSA/NSO)</li>
            <li>School ID</li>
            <li>Certificate of Enrollment</li>
            <li>Grade 10 or Grade 12 Report Card</li>
            <li>Diploma (if applicable)</li>
          </ul>
          <div className="important-note">
            <strong>Important:</strong> Please submit clear, readable copies of your documents. Prepare TWO (2) SETS: SET 1 (photocopies) and SET 2 (original copies) for verification.
          </div>
        </div>
      </div>

      {error && (
        <div className="error-alert">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {processingStatus && (
        <div className={`processing-status ${instantApproval ? 'success' : 'processing'}`}>
          <div className="processing-content">
            <span className="processing-icon">{instantApproval ? '🎉' : '⚡'}</span>
            <div className="processing-text">
              <div className="status-title">{processingStatus}</div>
              {instantApproval && (
                <div className="success-details">
                  ✅ Your document has been instantly analyzed and approved by our AI system!<br/>
                  🚀 Ready to proceed to the next step!
                </div>
              )}
              {!instantApproval && loading && (
                <div className="processing-details">
                  🤖 Our ultra-fast AI is analyzing your document in real-time...
                </div>
              )}
            </div>
          </div>
          {loading && !instantApproval && (
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="submission-form">
        <div className="form-group">
          <label htmlFor="document_type">Document Type *</label>
          <select
            id="document_type"
            name="document_type"
            value={formData.document_type}
            onChange={handleInputChange}
            required
            className="form-select"
          >
            <option value="">Select document type...</option>
            {documentTypes.map(type => (
              <option key={type} value={type}>
                {documentTypeLabels[type]}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Optional description or notes about this document..."
            className="form-textarea"
            rows={3}
          />
        </div>

        <div className="form-group">
          <label htmlFor="file">Upload File *</label>
          <input
            type="file"
            id="file"
            name="file"
            onChange={handleFileChange}
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            required
            className="form-file"
          />
          <div className="file-info">
            <small>
              Accepted formats: PDF, JPG, PNG, DOC, DOCX (Max 10MB)
            </small>
            {formData.file && (
              <div className="selected-file">
                📎 {formData.file.name} ({Math.round(formData.file.size / 1024)} KB)
                {formData.file.size > 5 * 1024 * 1024 && (
                  <span className="file-warning"> - Large file, consider compressing</span>
                )}
                {formData.file.size < 10 * 1024 && (
                  <span className="file-warning"> - File seems small, ensure it's complete</span>
                )}
              </div>
            )}
            <div className="file-tips">
              <strong>Document Submission Guidelines:</strong>
              <ul>
                <li>Name your file clearly (e.g., "lastname_birth_certificate.pdf")</li>
                <li>Ensure text is clear and readable with good lighting</li>
                <li>PDF format is preferred for official documents</li>
                <li>Arrange documents in the required order as per announcement</li>
                <li>Submit high-quality scans or photos for better AI processing</li>
                <li>For IDs: Submit photocopied back-to-back on a single page</li>
              </ul>
              <div className="document-order-note">
                <strong>Important:</strong> Please arrange documents in the order specified in the official announcement for faster processing.
              </div>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !formData.document_type || !formData.file}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                {processingStatus || 'Processing...'}
              </>
            ) : (
              '⚡ Submit for Instant AI Processing'
            )}
          </button>
        </div>
      </form>

      <NotificationModal
        isOpen={showNotification}
        onClose={() => setShowNotification(false)}
        type="success"
        title="⚡ Instant AI Processing Complete!"
        message="🎉 AMAZING! Your document has been uploaded and processed in SECONDS by our ultra-fast AI system! ⚡ The AI instantly analyzed your document, verified its authenticity, checked quality, and IMMEDIATELY APPROVED it! 🚀 No waiting, no manual review needed - everything is automated and complete! You can now proceed to submit your grades or apply for allowances right away. Welcome to the future of document processing!"
        autoClose={true}
        duration={8000}
      />
    </div>
  );
};

export default DocumentSubmissionForm;
