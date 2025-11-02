import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import documentService, { GradeSubmissionEligibility } from '../services/documentService';
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
  has_failing_grades: boolean;
  has_incomplete_grades: boolean;
  has_dropped_subjects: boolean;
  grade_sheet: File | null;
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
    has_failing_grades: false,
    has_incomplete_grades: false,
    has_dropped_subjects: false,
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
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const { checked } = e.target as HTMLInputElement;
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
      if (eligibility?.missingDocuments.length && eligibility?.requiredDocuments.length === 0) {
        setNotificationMessage('Please upload at least one supporting document before submitting grades. Required documents include: Certificate of Enrollment, Birth Certificate, School ID, Report Card, or Transcript of Records.');
      } else if (eligibility?.missingDocuments.length) {
        setNotificationMessage(`Please upload the following required documents first: ${eligibility.missingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}`);
      } else if (eligibility?.pendingDocuments.length) {
        setNotificationMessage(`Your documents are still under review. Please wait for admin approval of: ${eligibility.pendingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}`);
      } else {
        setNotificationMessage('You need to have at least one approved supporting document before submitting grades. Please upload your Certificate of Enrollment, Birth Certificate, School ID, Report Card, or Transcript of Records.');
      }
      setShowNotification(true);
      return;
    }
    
    if (!formData.semester || !formData.academic_year || !formData.total_units || 
        !formData.general_weighted_average || !formData.grade_sheet) {
      setError('Please fill in all required fields');
      return;
    }

    // Validate numeric fields
    const totalUnits = parseInt(formData.total_units);
    const gwa = parseFloat(formData.general_weighted_average);

    if (isNaN(totalUnits) || totalUnits < 1 || totalUnits > 30) {
      setError('Total units must be between 1 and 30');
      return;
    }

    // Validate GWA is in point scale (1.00 - 5.00) - accepts any decimal format
    if (isNaN(gwa) || gwa < 1.0 || gwa > 5.0) {
      setError('General Weighted Average must be between 1.0 and 5.0 (point scale). Examples: 1, 1.5, 1.75, 2.0, 2.35');
      return;
    }

    // Validate file upload
    if (!formData.grade_sheet || !(formData.grade_sheet instanceof File)) {
      setError('Please upload your grade sheet file');
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (formData.grade_sheet.size > maxSize) {
      setError('File size must be less than 10MB');
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
      submitFormData.append('has_failing_grades', formData.has_failing_grades.toString());
      submitFormData.append('has_incomplete_grades', formData.has_incomplete_grades.toString());
      submitFormData.append('has_dropped_subjects', formData.has_dropped_subjects.toString());
      submitFormData.append('grade_sheet', formData.grade_sheet);

      // Debug logging
      console.log('Submitting grade with data:', {
        semester: formData.semester,
        academic_year: formData.academic_year,
        total_units: formData.total_units,
        general_weighted_average: formData.general_weighted_average,
        has_failing_grades: formData.has_failing_grades,
        has_incomplete_grades: formData.has_incomplete_grades,
        has_dropped_subjects: formData.has_dropped_subjects,
        grade_sheet: formData.grade_sheet?.name,
        grade_sheet_size: formData.grade_sheet?.size
      });

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
        has_failing_grades: false,
        has_incomplete_grades: false,
        has_dropped_subjects: false,
        grade_sheet: null
      });

      // Show success notification
      setNotificationType('success');
      setNotificationMessage('🎉 Excellent! Your grades have been submitted and AUTOMATICALLY APPROVED by our advanced AI system! The AI has comprehensively analyzed your grade sheet, validated all information, calculated your allowance eligibility, and completed the entire evaluation process autonomously. No waiting for manual review - your submission is immediately processed and approved! The only remaining step is the final allowance application approval by admin, which typically takes 3-5 business days. You can now proceed with confidence knowing your academic records are fully verified and approved by our intelligent system!');
      setShowNotification(true);

      // Close form after notification
      setTimeout(() => {
        if (onSubmissionSuccess) {
          onSubmissionSuccess();
        }
      }, 5000); // Longer delay for important message

    } catch (error: any) {
      console.error('Error submitting grades:', error);
      console.error('Error response:', error.response);
      
      // Extract detailed error message
      let errorMessage = 'Failed to submit grades';
      
      if (error.response?.data) {
        // Check for fraud rejection (admin_notes contains rejection reason)
        if (error.response.data.admin_notes && error.response.data.admin_notes.includes('FRAUD ALERT')) {
          // Fraud detected by AI - show detailed message
          errorMessage = error.response.data.admin_notes;
          setNotificationType('error');
          setNotificationMessage(errorMessage);
          setShowNotification(true);
          return; // Don't set error, use notification modal instead
        }
        
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data.grade_sheet) {
          // Handle grade_sheet field errors (this is where rejection message appears)
          const gradeSheetError = Array.isArray(error.response.data.grade_sheet) 
            ? error.response.data.grade_sheet[0] 
            : error.response.data.grade_sheet;
          
          // Check if it's a fraud rejection
          if (typeof gradeSheetError === 'string' && gradeSheetError.includes('SECURITY REJECTION')) {
            setNotificationType('error');
            setNotificationMessage(`🚨 Grade Sheet Rejected\n\n${gradeSheetError}`);
            setShowNotification(true);
            return;
          }
          
          errorMessage = `Grade Sheet Error: ${gradeSheetError}`;
        } else if (error.response.data.general_weighted_average) {
          errorMessage = `GWA Error: ${error.response.data.general_weighted_average[0]}`;
        } else if (error.response.data.non_field_errors) {
          errorMessage = error.response.data.non_field_errors[0];
        } else {
          // Try to extract first error from any field
          const firstError = Object.values(error.response.data).find(val => Array.isArray(val) || typeof val === 'string');
          if (firstError) {
            errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
          }
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
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
        <h4>Document Verification Status</h4>
        {documentsLoading ? (
          <div className="loading-documents">
            <div className="loading-spinner"></div>
            <span>Checking your document status...</span>
          </div>
        ) : eligibility ? (
          <>
            {eligibility.requiredDocuments.length > 0 ? (
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
            ) : (
              <div className="no-documents-message">
                <div className="info-icon">ℹ️</div>
                <div className="info-text">
                  <strong>No Documents Submitted Yet</strong>
                  <p>Please submit at least one of the following documents before submitting grades: Certificate of Enrollment, Birth Certificate, School ID, Report Card, or Transcript of Records.</p>
                </div>
              </div>
            )}
            {!eligibility.canSubmit && (
              <div className="document-warning">
                <div className="warning-icon">⚠️</div>
                <div className="warning-text">
                  <strong>Document Approval Required</strong>
                  {eligibility.missingDocuments.length > 0 && eligibility.requiredDocuments.length === 0 && (
                    <p>
                      No documents submitted yet. Please upload at least one supporting document (Certificate of Enrollment, Birth Certificate, School ID, Report Card, or Transcript of Records) before submitting grades.
                    </p>
                  )}
                  {eligibility.missingDocuments.length > 0 && eligibility.requiredDocuments.length > 0 && (
                    <p>
                      Missing documents: {eligibility.missingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}. 
                      Please upload these documents first.
                    </p>
                  )}
                  {eligibility.pendingDocuments.length > 0 && eligibility.approvedDocuments.length === 0 && (
                    <p>
                      Pending approval: {eligibility.pendingDocuments.map(doc => documentService.getDocumentTypeLabel(doc)).join(', ')}. 
                      Please wait for admin approval (usually 3-5 business days).
                    </p>
                  )}
                </div>
              </div>
            )}
            {eligibility.canSubmit && (
              <div className="document-success">
                <div className="success-icon">✅</div>
                <div className="success-text">
                  <strong>You're all set!</strong>
                  <p>Your documents have been approved. You can now submit your grades.</p>
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
              placeholder="e.g., 21"
              required
              className="form-input"
            />
            <small>Number of units enrolled this semester (1-30)</small>
          </div>

          <div className="form-group">
            <label htmlFor="general_weighted_average">General Weighted Average (GWA) *</label>
            <input
              type="number"
              id="general_weighted_average"
              name="general_weighted_average"
              value={formData.general_weighted_average}
              onChange={handleInputChange}
              min="1"
              max="5"
              step="any"
              placeholder="e.g., 1.75, 1.7, 2, 2.35"
              required
              className="form-input"
            />
            <small>Enter any GWA between 1.0 and 5.0 (Examples: 1, 1.5, 1.75, 2.0, 2.35, 3.5)</small>
            <div className="grading-scale-hint">
              <details>
                <summary>📊 Official University Grading Scale</summary>
                <div className="scale-table">
                  <div className="scale-header">
                    <span><strong>Grade</strong></span>
                    <span></span>
                    <span><strong>%</strong></span>
                    <span><strong>Remarks</strong></span>
                    <span><strong>Eligibility</strong></span>
                  </div>
                  <div className="scale-row merit"><span>1.0</span> <span>=</span> <span>96-100</span> <span>Excellent</span> <span>✅ Merit + Basic</span></div>
                  <div className="scale-row merit"><span>1.25</span> <span>=</span> <span>93-95</span> <span>Very Good</span> <span>✅ Merit + Basic</span></div>
                  <div className="scale-row merit"><span>1.5</span> <span>=</span> <span>90-92</span> <span>Good</span> <span>✅ Merit + Basic</span></div>
                  <div className="scale-row merit"><span>1.75</span> <span>=</span> <span>87-89</span> <span>Satisfactory</span> <span>✅ Merit + Basic</span></div>
                  <div className="scale-row basic"><span>2.0</span> <span>=</span> <span>84-86</span> <span>Fair</span> <span>✓ Basic Only</span></div>
                  <div className="scale-row basic"><span>2.25</span> <span>=</span> <span>81-83</span> <span>Average</span> <span>✓ Basic Only</span></div>
                  <div className="scale-row"><span>2.5</span> <span>=</span> <span>78-80</span> <span>Below Avg</span> <span>❌ None</span></div>
                  <div className="scale-row"><span>2.75</span> <span>=</span> <span>75-77</span> <span>Passing</span> <span>❌ None</span></div>
                  <div className="scale-row"><span>3.0</span> <span>=</span> <span>70-74</span> <span>Min. Pass</span> <span>❌ None</span></div>
                  <div className="scale-row"><span>5.0</span> <span>=</span> <span>&lt;70</span> <span>Failing</span> <span>❌ None</span></div>
                </div>
                <div className="eligibility-note">
                  <small>
                    <strong>Basic Allowance:</strong> Requires ≥80% (GWA ≤2.25) + ≥15 units + no fails/inc/drops<br/>
                    <strong>Merit Incentive:</strong> Requires ≥87% (GWA ≤1.75) + ≥15 units + no fails/inc/drops<br/>
                    <em>Note: System accepts any decimal format (1, 1.0, 1.75, 1.91, etc.)</em>
                  </small>
                </div>
              </details>
            </div>
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
              Upload your official grade sheet. AI will automatically evaluate your grades for allowance qualification.
            </small>
            {formData.grade_sheet && (
              <div className="selected-file">
                {formData.grade_sheet.name} ({Math.round(formData.grade_sheet.size / 1024)} KB)
              </div>
            )}
          </div>
        </div>

        <div className="ai-processing-info">
          <h4>Fully Autonomous AI Processing System</h4>
          <div className="ai-features">
            <div className="ai-feature-item">
              <span>INSTANT AUTO-APPROVAL - No waiting for manual review</span>
            </div>
            <div className="ai-feature-item">
              <span>Comprehensive document analysis with OCR text extraction</span>
            </div>
            <div className="ai-feature-item">
              <span>Intelligent cross-validation and grade verification</span>
            </div>
            <div className="ai-feature-item">
              <span>Advanced quality assessment and accuracy validation</span>
            </div>
            <div className="ai-feature-item">
              <span>Automatic allowance eligibility calculation and approval</span>
            </div>
            <div className="ai-feature-item">
              <span>Complete autonomous processing - Submit and get approved instantly!</span>
            </div>
          </div>
          <div className="ai-confidence-note">
            <strong>Revolutionary Processing:</strong> Our AI system has full authority to approve 
            documents and grades automatically. No more waiting days for manual review - get instant 
            approval and proceed immediately with your allowance application!
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
            disabled={loading || !eligibility?.canSubmit || !formData.semester || !formData.academic_year || 
                     !formData.total_units || !formData.general_weighted_average || !formData.grade_sheet}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Processing...
              </>
            ) : !eligibility?.canSubmit ? (
              'Documents Required'
            ) : (
              'Submit for Instant AI Approval'
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
            ? 'Grades Auto-Approved by AI System!' 
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
