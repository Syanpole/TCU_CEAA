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
    setFormData(prev => ({
      ...prev,
      file
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.document_type || !formData.file) {
      setError('Please select a document type and file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const submitFormData = new FormData();
      submitFormData.append('document_type', formData.document_type);
      submitFormData.append('description', formData.description);
      submitFormData.append('file', formData.file);

      await apiClient.post('/documents/', submitFormData, {
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
      setError(error.response?.data?.detail || 'Failed to submit document');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="document-submission-form">
      <div className="form-header">
        <h3>Submit Document</h3>
        <p>Upload required documents for your TCU CEAA application</p>
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
              </div>
            )}
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
        message="Your document has been uploaded and is now under review. The admin will review your submission within 3-5 business days. You'll receive a notification once it's approved or if any revisions are needed."
        autoClose={true}
        duration={6000}
      />
    </div>
  );
};

export default DocumentSubmissionForm;
