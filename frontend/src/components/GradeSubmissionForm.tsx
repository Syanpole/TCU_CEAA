import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import documentService, { GradeSubmissionEligibility } from '../services/documentService';
import NotificationModal from './NotificationModal';
import LiveCameraCapture from './LiveCameraCapture';
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
  const [showLivenessVerification, setShowLivenessVerification] = useState(false);
  const [pendingGradeSubmissionId, setPendingGradeSubmissionId] = useState<number | null>(null);
  const [livenessImage, setLivenessImage] = useState<string | null>(null);

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

  const handleLivenessCapture = async (imageBlob: Blob, imageUrl: string, livenessData?: any) => {
    try {
      setLivenessImage(imageUrl);
      setLoading(true);

      // Use the provided blob directly
      const file = new File([imageBlob], 'face_verification.jpg', { type: 'image/jpeg' });

      // Submit face verification
      const faceFormData = new FormData();
      faceFormData.append('photo', file);
      faceFormData.append('liveness_data', JSON.stringify(livenessData));
      if (pendingGradeSubmissionId) {
        faceFormData.append('grade_submission_id', pendingGradeSubmissionId.toString());
      }

      await apiClient.post('/face-verification/grade-submission/', faceFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Success! Reset form and show final success message
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
      setShowLivenessVerification(false);
      setPendingGradeSubmissionId(null);
      
      setNotificationType('success');
      setNotificationMessage('🎉 SUCCESS! Your grades have been submitted and your identity has been VERIFIED! The AI system has:\n\n✅ Analyzed your grade sheet\n✅ Validated liveness detection\n✅ Verified your facial identity\n✅ Approved your submission\n\nYour application is now complete and ready for final admin approval!');
      setShowNotification(true);

      setTimeout(() => {
        if (onSubmissionSuccess) {
          onSubmissionSuccess();
        }
      }, 5000);
    } catch (error: any) {
      console.error('Face verification error:', error);
      setShowLivenessVerification(false);
      
      let errorMessage = 'Face verification failed. ';
      if (error.response?.data) {
        if (error.response.data.detail) {
          errorMessage += error.response.data.detail;
        } else if (error.response.data.error) {
          errorMessage += error.response.data.error;
        } else {
          errorMessage += 'Please ensure your face is clearly visible and try again.';
        }
      } else {
        errorMessage += 'Please try again.';
      }
      
      setNotificationType('error');
      setNotificationMessage(errorMessage);
      setShowNotification(true);
    } finally {
      setLoading(false);
    }
  };

  const handleLivenessCancel = () => {
    setShowLivenessVerification(false);
    setPendingGradeSubmissionId(null);
    setNotificationType('warning');
    setNotificationMessage('Identity verification cancelled. Your grades were submitted but require identity verification to complete.');
    setShowNotification(true);
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

      const response = await apiClient.post('/grades/', submitFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Store the grade submission ID for face verification
      const gradeSubmissionId = (response.data as any).id;
      console.log('✅ Grade submitted successfully! ID:', gradeSubmissionId);
      
      // Don't show notification during liveness flow to avoid UI conflicts
      // Show liveness verification immediately
      console.log('🎬 Triggering liveness verification screen...');
      setLoading(false); // Stop loading state
      setPendingGradeSubmissionId(gradeSubmissionId);
      setShowLivenessVerification(true);

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

  // Show liveness verification screen if triggered
  if (showLivenessVerification) {
    return (
      <div className="grade-submission-form-compact">
        <div className="liveness-verification-container">
          <div className="liveness-header">
            <h2>🔒 Final Identity Verification</h2>
            <p className="liveness-subtitle">
              Your grades have been processed! Complete this quick identity verification to proceed.
            </p>
          </div>
          
          <div className="liveness-instructions">
            <h3>📋 What to Expect:</h3>
            <ul>
              <li>🎨 <strong>Color Flash:</strong> Look at the screen as colors flash</li>
              <li>👁️ <strong>Blink Detection:</strong> Blink naturally</li>
              <li>📱 <strong>Movement Check:</strong> Move your face slightly</li>
            </ul>
            <p className="liveness-note">⚡ This takes only 10-15 seconds!</p>
          </div>

          <LiveCameraCapture
            documentType="Face Verification"
            onCapture={handleLivenessCapture}
            onCancel={handleLivenessCancel}
            requireLiveness={true}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="grade-submission-form-compact">
      {/* Header with Icon */}
      <div className="compact-header">
        <h2>Submit Grades</h2>
        <p className="header-subtitle">Academic Performance Submission</p>
      </div>

      {/* Quick Status Check */}
      {!documentsLoading && eligibility && !eligibility.canSubmit && (
        <div className="quick-warning">
          ⚠️ Document approval required
        </div>
      )}

      {/* Document Status Check - Minimized */}
      {documentsLoading ? (
        <div className="compact-loading">
          <div className="loading-spinner-small"></div>
          <span>Verifying eligibility...</span>
        </div>
      ) : eligibility && !eligibility.canSubmit ? (
        <div className="compact-status-section">
          <h4>📋 Document Status</h4>
          {eligibility.requiredDocuments.map(docType => {
            const isApproved = eligibility.approvedDocuments.includes(docType);
            const isPending = eligibility.pendingDocuments.includes(docType);
            
            return (
              <div key={docType} className="compact-doc-item">
                <span className="doc-icon">{isApproved ? '✅' : isPending ? '⏳' : '❌'}</span>
                <span className="doc-name">{documentService.getDocumentTypeLabel(docType)}</span>
              </div>
            );
          })}
        </div>
      ) : null}

      {/* Compact Form */}
      <form onSubmit={handleSubmit} className="compact-form">
        {error && (
          <div className="compact-error">
            ⚠️ {error}
          </div>
        )}

        {/* Form Grid */}
        <div className="compact-grid">
          <div className="compact-field">
            <label>Semester</label>
            <select
              name="semester"
              value={formData.semester}
              onChange={handleInputChange}
              required
              className="compact-input"
            >
              <option value="">Select...</option>
              {semesters.map(sem => (
                <option key={sem.value} value={sem.value}>{sem.label}</option>
              ))}
            </select>
          </div>

          <div className="compact-field">
            <label>Academic Year</label>
            <input
              type="text"
              name="academic_year"
              value={formData.academic_year}
              onChange={handleInputChange}
              placeholder="2024-2025"
              required
              className="compact-input"
            />
          </div>

          <div className="compact-field">
            <label>GWA</label>
            <input
              type="number"
              name="general_weighted_average"
              value={formData.general_weighted_average}
              onChange={handleInputChange}
              min="1"
              max="5"
              step="any"
              placeholder="1.75"
              required
              className="compact-input"
            />
          </div>

          <div className="compact-field">
            <label>Total Units</label>
            <input
              type="number"
              name="total_units"
              value={formData.total_units}
              onChange={handleInputChange}
              min="1"
              max="30"
              placeholder="21"
              required
              className="compact-input"
            />
          </div>
        </div>

        {/* File Upload */}
        <div className="compact-upload">
          <label className="upload-label">
            📄 Grade Sheet
            <input
              type="file"
              name="grade_sheet"
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png"
              required
              className="file-input-hidden"
            />
          </label>
          {formData.grade_sheet && (
            <div className="file-selected">
              ✓ {formData.grade_sheet.name}
            </div>
          )}
        </div>

        {/* AI Info - Compact */}
        <div className="compact-ai-info">
          <div className="ai-badge">🤖 AI AUTO-APPROVAL</div>
          <p>Instant verification & processing</p>
        </div>

        {/* Action Buttons */}
        <div className="compact-actions">
          <button
            type="button"
            onClick={onCancel}
            className="btn-compact btn-cancel"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-compact btn-submit"
            disabled={loading || !eligibility?.canSubmit || !formData.semester || !formData.academic_year || 
                     !formData.total_units || !formData.general_weighted_average || !formData.grade_sheet}
          >
            {loading ? (
              <>
                <span className="spinner-compact"></span>
                Processing...
              </>
            ) : (
              'Submit Grade'
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
