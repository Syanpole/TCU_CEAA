import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import documentService, { DocumentStatus, GradeSubmissionEligibility } from '../services/documentService';
import NotificationModal from './NotificationModal';
import './GradeSubmissionForm.css';

interface GradeSubmissionFormProps {
  onSubmissionSuccess?: () => void;
  onCancel?: () => void;
}

interface FormData {
  semester: string;
  academic_year: string;
  grade_sheet: File | null;
}

const GradeSubmissionForm: React.FC<GradeSubmissionFormProps> = ({
  onSubmissionSuccess,
  onCancel
}) => {
  const [formData, setFormData] = useState<FormData>({
    semester: '',
    academic_year: '',
    grade_sheet: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationType, setNotificationType] = useState<'success' | 'warning' | 'error'>('success');
  const [notificationMessage, setNotificationMessage] = useState('');
  const [eligibility, setEligibility] = useState<GradeSubmissionEligibility | null>(null);
  const [documentsLoading, setDocumentsLoading] = useState(true);

  const semesters = [
    { value: '1st', label: '1st Semester' },
    { value: '2nd', label: '2nd Semester' },
    { value: 'summer', label: 'Summer' }
  ];

  // Check document status on component mount
  useEffect(() => {
    const checkEligibility = async () => {
      try {
        setDocumentsLoading(true);
        const eligibilityData = await documentService.checkGradeSubmissionEligibility();
        setEligibility(eligibilityData);
      } catch (error) {
        console.error('Error checking eligibility:', error);
        setEligibility({
          canSubmit: false,
          requiredDocuments: ['enrollment_certificate', 'id_copy'],
          missingDocuments: ['enrollment_certificate', 'id_copy'],
          pendingDocuments: [],
          approvedDocuments: []
        });
      } finally {
        setDocumentsLoading(false);
      }
    };

    checkEligibility();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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
      grade_sheet: file
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if user can submit grades
    if (!eligibility?.canSubmit) {
      setNotificationType('warning');
      if (eligibility?.missingDocuments.length) {
        setNotificationMessage(`Please upload the following required documents first: ${eligibility.missingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}`);
      } else if (eligibility?.pendingDocuments.length) {
        setNotificationMessage(`Your documents are still under review. Please wait for admin approval of: ${eligibility.pendingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}`);
      } else {
        setNotificationMessage('You need to have your required documents approved before submitting grades. Please upload your Certificate of Enrollment and Valid ID Copy.');
      }
      setShowNotification(true);
      return;
    }
    
    if (!formData.semester || !formData.academic_year || !formData.grade_sheet) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const submitFormData = new FormData();
      submitFormData.append('semester', formData.semester);
      submitFormData.append('academic_year', formData.academic_year);
      submitFormData.append('grade_sheet', formData.grade_sheet);

      await apiClient.post('/grades/', submitFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Reset form
      setFormData({
        semester: '',
        academic_year: '',
        grade_sheet: null
      });

      // Show success notification
      setNotificationType('success');
      setNotificationMessage('Your grades have been submitted successfully! The admin will review your submission within 3-5 business days. You will be notified once your allowance application is processed.');
      setShowNotification(true);

      // Close form after notification
      setTimeout(() => {
        if (onSubmissionSuccess) {
          onSubmissionSuccess();
        }
      }, 3000);

    } catch (error: any) {
      console.error('Error submitting grades:', error);
      setError(error.response?.data?.detail || 'Failed to submit grades');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grade-submission-form">
      <div className="form-header">
        <h3>Submit Grades</h3>
        <p>Upload your grade sheet for TCU-CEAA allowance evaluation</p>
      </div>

      {/* Document Status Check */}
      <div className="document-status-section">
        <h4>📋 Document Verification Status</h4>
        {documentsLoading ? (
          <div className="loading-documents">
            <div className="loading-spinner"></div>
            <span>Checking your document status...</span>
          </div>
        ) : eligibility ? (
          <>
            <div className="document-requirements">
              {eligibility.requiredDocuments.map(docType => {
                const isApproved = eligibility.approvedDocuments.includes(docType);
                const isPending = eligibility.pendingDocuments.includes(docType);
                const isMissing = eligibility.missingDocuments.includes(docType);
                
                return (
                  <div key={docType} className={`requirement-item ${isApproved ? 'approved' : isPending ? 'pending' : 'missing'}`}>
                    <div className="requirement-icon">
                      {isApproved ? '✅' : isPending ? '⏳' : '❌'}
                    </div>
                    <div className="requirement-info">
                      <span className="requirement-name">
                        {documentService.getDocumentTypeLabel(docType)}
                      </span>
                      <span className="requirement-status">
                        {isApproved ? 'Approved' : isPending ? 'Under Review' : 'Not Submitted'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            {!eligibility.canSubmit && (
              <div className="document-warning">
                <div className="warning-icon">⚠️</div>
                <div className="warning-text">
                  <strong>Document Approval Required</strong>
                  {eligibility.missingDocuments.length > 0 && (
                    <p>
                      Missing documents: {eligibility.missingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}. 
                      Please upload these documents first.
                    </p>
                  )}
                  {eligibility.pendingDocuments.length > 0 && (
                    <p>
                      Pending approval: {eligibility.pendingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}. 
                      Please wait for admin approval (usually 3-5 business days).
                    </p>
                  )}
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>

      {error && (
        <div className="error-alert">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="submission-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="semester">Semester *</label>
            <select
              id="semester"
              name="semester"
              value={formData.semester}
              onChange={handleInputChange}
              required
              className="form-select"
            >
              <option value="">Select semester...</option>
              {semesters.map(sem => (
                <option key={sem.value} value={sem.value}>
                  {sem.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="academic_year">Academic Year *</label>
            <input
              type="text"
              id="academic_year"
              name="academic_year"
              value={formData.academic_year}
              onChange={handleInputChange}
              placeholder="e.g., 2024-2025"
              required
              className="form-input"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="grade_sheet">Upload Grade Sheet *</label>
          <input
            type="file"
            id="grade_sheet"
            name="grade_sheet"
            onChange={handleFileChange}
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            required
            className="form-file"
          />
          <div className="file-info">
            <small>
              📊 Upload your official grade sheet. AI will automatically evaluate your grades for allowance qualification.
            </small>
            {formData.grade_sheet && (
              <div className="selected-file">
                📊 {formData.grade_sheet.name} ({Math.round(formData.grade_sheet.size / 1024)} KB)
              </div>
            )}
          </div>
        </div>

        <div className="ai-processing-info">
          <h4>🤖 AI-Powered Grade Analysis</h4>
          <div className="ai-features">
            <div className="ai-feature-item">
              <span className="ai-icon">✨</span>
              <span>Automatic grade extraction and analysis</span>
            </div>
            <div className="ai-feature-item">
              <span className="ai-icon">📊</span>
              <span>Intelligent allowance qualification assessment</span>
            </div>
            <div className="ai-feature-item">
              <span className="ai-icon">⚡</span>
              <span>Instant base and merit allowance evaluation</span>
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
            disabled={loading || !eligibility?.canSubmit || !formData.semester || !formData.academic_year || !formData.grade_sheet}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Processing...
              </>
            ) : !eligibility?.canSubmit ? (
              'Documents Required'
            ) : (
              'Submit for AI Analysis'
            )}
          </button>
        </div>
      </form>

      <NotificationModal
        isOpen={showNotification}
        onClose={() => setShowNotification(false)}
        type={notificationType}
        title={
          notificationType === 'success' 
            ? 'Grades Submitted Successfully!' 
            : notificationType === 'warning'
            ? 'Document Approval Required'
            : 'Submission Error'
        }
        message={notificationMessage}
        autoClose={notificationType === 'success'}
        duration={6000}
      />
    </div>
  );
};

export default GradeSubmissionForm;
