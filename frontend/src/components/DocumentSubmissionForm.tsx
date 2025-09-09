import React, { useState } from 'react';
import { apiClient } from '../services/authService';
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

  const documentTypes = [
    'birth_certificate',
    'school_id', 
    'report_card',
    'enrollment_certificate',
    'barangay_clearance',
    'parents_id',
    'voter_certification',
    'other'
  ];

  const documentTypeLabels: { [key: string]: string } = {
    birth_certificate: 'Birth Certificate',
    school_id: 'School ID',
    report_card: 'Report Card/Grades', 
    enrollment_certificate: 'Certificate of Enrollment',
    barangay_clearance: 'Barangay Clearance',
    parents_id: 'Parent\'s Valid ID',
    voter_certification: 'Voter\'s Certification',
    other: 'Other Document'
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

    try {
      const submitFormData = new FormData();
      submitFormData.append('document_type', formData.document_type);
      submitFormData.append('description', formData.description);
      submitFormData.append('file', formData.file);

      const response = await apiClient.post('/documents/', submitFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

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
      }, 2000);
    } catch (error: any) {
      console.error('Error submitting document:', error);
      
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
        <h3>Submit Document</h3>
        <p>Upload required documents for your TCU-CEAA application</p>
      </div>

      {error && (
        <div className="error-alert">
          <span className="error-icon">⚠️</span>
          {error}
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
              <strong>💡 Tips for better AI analysis:</strong>
              <ul>
                <li>📝 Name your file clearly (e.g., "john_birth_certificate.pdf")</li>
                <li>📷 Ensure text is clear and readable</li>
                <li>🖼️ For images, use good lighting and avoid shadows</li>
                <li>📄 PDF format is preferred for official documents</li>
              </ul>
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
                Uploading...
              </>
            ) : (
              'Submit Document'
            )}
          </button>
        </div>
      </form>

      <NotificationModal
        isOpen={showNotification}
        onClose={() => setShowNotification(false)}
        type="success"
        title="Document Submitted Successfully!"
        message="Your document has been uploaded and analyzed by our AI system. The document has been processed and is now under admin review. You'll receive a notification once it's approved or if any revisions are needed. The AI analysis will help speed up the review process!"
        autoClose={true}
        duration={8000}
      />
    </div>
  );
};

export default DocumentSubmissionForm;
