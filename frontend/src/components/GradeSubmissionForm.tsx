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
  total_units: string;
  general_weighted_average: string;
  semestral_weighted_average: string;
  has_incomplete_grades: boolean;
  has_failing_grades: boolean;
  grade_sheet: File | null;
  notes: string;
}

const GradeSubmissionForm: React.FC<GradeSubmissionFormProps> = ({
  onSubmissionSuccess,
  onCancel
}) => {
  const [formData, setFormData] = useState<FormData>({
    semester: '',
    academic_year: '',
    total_units: '',
    general_weighted_average: '',
    semestral_weighted_average: '',
    has_incomplete_grades: false,
    has_failing_grades: false,
    grade_sheet: null,
    notes: ''
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({
        ...prev,
        [name]: checked
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
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
    
    if (!formData.semester || !formData.academic_year || !formData.total_units || !formData.general_weighted_average || !formData.semestral_weighted_average || !formData.grade_sheet) {
      setError('Please fill in all required fields');
      return;
    }

    // Validate GWA and SWA ranges
    const gwa = parseFloat(formData.general_weighted_average);
    const swa = parseFloat(formData.semestral_weighted_average);
    const units = parseInt(formData.total_units);
    
    if (isNaN(gwa) || gwa < 65 || gwa > 100) {
      setError('General Weighted Average must be between 65 and 100');
      return;
    }
    
    if (isNaN(swa) || swa < 65 || swa > 100) {
      setError('Semestral Weighted Average must be between 65 and 100');
      return;
    }

    if (isNaN(units) || units < 1 || units > 30) {
      setError('Total units must be between 1 and 30');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const submitFormData = new FormData();
      submitFormData.append('semester', formData.semester);
      submitFormData.append('academic_year', formData.academic_year);
      submitFormData.append('total_units', formData.total_units);
      submitFormData.append('general_weighted_average', formData.general_weighted_average);
      submitFormData.append('semestral_weighted_average', formData.semestral_weighted_average);
      submitFormData.append('has_incomplete_grades', formData.has_incomplete_grades.toString());
      submitFormData.append('has_failing_grades', formData.has_failing_grades.toString());
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
        total_units: '',
        general_weighted_average: '',
        semestral_weighted_average: '',
        has_incomplete_grades: false,
        has_failing_grades: false,
        grade_sheet: null,
        notes: ''
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
        <p>Upload your grade sheet for TCU CEAA allowance evaluation</p>
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

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="total_units">Total Units *</label>
            <input
              type="number"
              id="total_units"
              name="total_units"
              value={formData.total_units}
              onChange={handleInputChange}
              min="1"
              max="30"
              placeholder="e.g., 18"
              required
              className="form-input"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="general_weighted_average">
              General Weighted Average *
              <span className="grade-hint">65 - 100</span>
            </label>
            <input
              type="number"
              id="general_weighted_average"
              name="general_weighted_average"
              value={formData.general_weighted_average}
              onChange={handleInputChange}
              step="0.01"
              min="65"
              max="100"
              placeholder="e.g., 89.25"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="semestral_weighted_average">
              Semestral Weighted Average *
              <span className="grade-hint">65 - 100</span>
            </label>
            <input
              type="number"
              id="semestral_weighted_average"
              name="semestral_weighted_average"
              value={formData.semestral_weighted_average}
              onChange={handleInputChange}
              step="0.01"
              min="65"
              max="100"
              placeholder="e.g., 89.25"
              required
              className="form-input"
            />
          </div>
        </div>

        <div className="form-group checkbox-group">
          <div className="checkbox-item">
            <input
              type="checkbox"
              id="has_incomplete_grades"
              name="has_incomplete_grades"
              checked={formData.has_incomplete_grades}
              onChange={handleInputChange}
              className="form-checkbox"
            />
            <label htmlFor="has_incomplete_grades">I have incomplete grades (INC)</label>
          </div>

          <div className="checkbox-item">
            <input
              type="checkbox"
              id="has_failing_grades"
              name="has_failing_grades"
              checked={formData.has_failing_grades}
              onChange={handleInputChange}
              className="form-checkbox"
            />
            <label htmlFor="has_failing_grades">I have failing grades</label>
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
              Accepted formats: PDF, JPG, PNG, DOC, DOCX (Max 10MB)
            </small>
            {formData.grade_sheet && (
              <div className="selected-file">
                📊 {formData.grade_sheet.name} ({Math.round(formData.grade_sheet.size / 1024)} KB)
              </div>
            )}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="notes">Additional Notes</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleInputChange}
            placeholder="Any additional information about your grades..."
            className="form-textarea"
            rows={3}
          />
        </div>

        <div className="allowance-info">
          <h4>📊 TCU CEAA Allowance Information</h4>
          <div className="allowance-details">
            <div className="allowance-item">
              <span className="allowance-label">Base Allowance:</span>
              <span className="allowance-value">₱5,000 (if GWA ≥ 80% equivalent)</span>
            </div>
            <div className="allowance-item">
              <span className="allowance-label">Merit Incentive:</span>
              <span className="allowance-value">₱5,000 (if SWA ≥ 88.75%)</span>
            </div>
            <div className="allowance-note">
              <strong>Note:</strong> No allowance if you have incomplete or failed subjects
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
            disabled={loading || !eligibility?.canSubmit || !formData.semester || !formData.academic_year || !formData.total_units || !formData.general_weighted_average || !formData.semestral_weighted_average || !formData.grade_sheet}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Submitting...
              </>
            ) : !eligibility?.canSubmit ? (
              'Documents Required'
            ) : (
              'Submit Grades'
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
