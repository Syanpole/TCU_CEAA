import React, { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/authService';
import documentService, { GradeSubmissionEligibility } from '../services/documentService';
import gradeService, { COESubject, GradeSubmissionStatus } from '../services/gradeService';
import NotificationModal from './NotificationModal';
import LiveCameraCapture from './LiveCameraCapture';
import './GradeSubmissionForm.css';

interface GradeSubmissionFormProps {
  onSubmissionSuccess?: () => void;
  onCancel?: () => void;
}

interface SubjectSubmissionState {
  subject: COESubject;
  file: File | null;
  units: number;
  grade: number;
  status: 'not-submitted' | 'uploading' | 'submitted' | 'approved' | 'rejected';
  submissionId?: number;
  error?: string;
  adminNotes?: string;
}

const GradeSubmissionForm: React.FC<GradeSubmissionFormProps> = ({
  onSubmissionSuccess,
  onCancel
}) => {
  // COE and subject state
  const [coeSubjects, setCoeSubjects] = useState<COESubject[]>([]);
  const [subjectStates, setSubjectStates] = useState<SubjectSubmissionState[]>([]);
  const [semester, setSemester] = useState('');
  const [academicYear, setAcademicYear] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [coeLoading, setCoeLoading] = useState(true);
  const [error, setError] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationType, setNotificationType] = useState<'success' | 'warning' | 'error'>('success');
  const [notificationMessage, setNotificationMessage] = useState('');
  
  // Eligibility and status
  const [eligibility, setEligibility] = useState<GradeSubmissionEligibility | null>(null);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [gradeStatus, setGradeStatus] = useState<GradeSubmissionStatus | null>(null);
  


  const semesters = [
    { value: '1st', label: '1st Semester' },
    { value: '2nd', label: '2nd Semester' },
    { value: 'summer', label: 'Summer' }
  ];

  // Fetch submission status
  const fetchSubmissionStatus = useCallback(async () => {
    if (!semester || !academicYear) return;
    
    try {
      const status = await gradeService.getGradeSubmissionStatus(academicYear, semester);
      setGradeStatus(status);

      // Update subject states with existing submissions
      if (status.submissions && status.submissions.length > 0) {
        setSubjectStates(prevStates => 
          prevStates.map(state => {
            const existingSubmission = status.submissions.find(
              sub => sub.subject_code === state.subject.subject_code
            );
            if (existingSubmission) {
              return {
                ...state,
                status: existingSubmission.status as any,
                submissionId: existingSubmission.id,
                units: existingSubmission.units,
                grade: existingSubmission.grade_received,
                adminNotes: existingSubmission.admin_notes,
              };
            }
            return state;
          })
        );
      }
    } catch (error) {
      console.error('Error fetching submission status:', error);
    }
  }, [semester, academicYear]);

  // Function to reload COE subjects
  const reloadCOESubjects = async () => {
    try {
      setCoeLoading(true);
      setError('');
      
      const coeData = await gradeService.getCOESubjects();
      setCoeSubjects(coeData.subjects);
      
      // Initialize subject states
      const initialStates: SubjectSubmissionState[] = coeData.subjects.map(subject => ({
        subject,
        file: null,
        units: 3,
        grade: 1.0,
        status: 'not-submitted' as const,
      }));
      setSubjectStates(initialStates);
      
      // Set default semester and academic year from COE if available
      if (coeData.semester) setSemester(coeData.semester);
      if (coeData.academic_year) setAcademicYear(coeData.academic_year);
      
      // Show success message
      setNotificationMessage(`Successfully loaded ${coeData.subjects.length} subjects from your COE`);
      setNotificationType('success');
      setShowNotification(true);
      
    } catch (error: any) {
      setError(error.message || 'Failed to reload COE subjects');
      setNotificationMessage(error.message || 'Failed to reload COE subjects');
      setNotificationType('error');
      setShowNotification(true);
    } finally {
      setCoeLoading(false);
    }
  };

  // Check document eligibility and load COE subjects on mount
  useEffect(() => {
    const initializeForm = async () => {
      try {
        setDocumentsLoading(true);
        setCoeLoading(true);

        // Check eligibility
        const eligibilityData = await documentService.checkGradeSubmissionEligibility();
        setEligibility(eligibilityData);

        if (eligibilityData.canSubmit) {
          // Fetch COE subjects
          const coeData = await gradeService.getCOESubjects();
          setCoeSubjects(coeData.subjects);
          
          // Initialize subject states
          const initialStates: SubjectSubmissionState[] = coeData.subjects.map(subject => ({
            subject,
            file: null,
            units: 3, // Default units
            grade: 1.0, // Default grade
            status: 'not-submitted' as const,
          }));
          setSubjectStates(initialStates);

          // Set default semester and academic year from COE if available
          if (coeData.semester) setSemester(coeData.semester);
          if (coeData.academic_year) setAcademicYear(coeData.academic_year);

          // Fetch existing submissions status
          await fetchSubmissionStatus();
        }
      } catch (error: any) {
        console.error('Error initializing form:', error);
        setError(error.message || 'Failed to load COE subjects');
        setEligibility({
          canSubmit: false,
          requiredDocuments: ['enrollment_certificate', 'id_copy'],
          missingDocuments: ['enrollment_certificate', 'id_copy'],
          pendingDocuments: [],
          approvedDocuments: []
        });
      } finally {
        setDocumentsLoading(false);
        setCoeLoading(false);
      }
    };

    initializeForm();
  }, []); // Run only once on mount

  // Handle file selection for a subject
  const handleFileChange = (index: number, file: File | null) => {
    setSubjectStates(prev => {
      const newStates = [...prev];
      newStates[index] = { ...newStates[index], file, error: undefined };
      return newStates;
    });
  };

  // Handle units change for a subject
  const handleUnitsChange = (index: number, units: number) => {
    setSubjectStates(prev => {
      const newStates = [...prev];
      newStates[index] = { ...newStates[index], units };
      return newStates;
    });
  };

  // Handle grade change for a subject
  const handleGradeChange = (index: number, grade: number) => {
    setSubjectStates(prev => {
      const newStates = [...prev];
      newStates[index] = { ...newStates[index], grade };
      return newStates;
    });
  };

  // Submit grade for a single subject
  const handleSubmitSubject = async (index: number) => {
    const state = subjectStates[index];
    
    if (!state.file) {
      setSubjectStates(prev => {
        const newStates = [...prev];
        newStates[index] = { ...newStates[index], error: 'Please select a grade sheet file' };
        return newStates;
      });
      return;
    }

    if (!semester || !academicYear) {
      setError('Please select semester and academic year');
      return;
    }

    // Update status to uploading
    setSubjectStates(prev => {
      const newStates = [...prev];
      newStates[index] = { ...newStates[index], status: 'uploading', error: undefined };
      return newStates;
    });

    try {
      const submission = await gradeService.submitSubjectGrade({
        subject_code: state.subject.subject_code,
        subject_name: state.subject.subject_name,
        academic_year: academicYear,
        semester: semester,
        units: state.units,
        grade_received: state.grade,
        grade_sheet: state.file,
      });

      // Update state with submission result
      setSubjectStates(prev => {
        const newStates = [...prev];
        newStates[index] = {
          ...newStates[index],
          status: 'submitted',
          submissionId: submission.id,
          error: undefined,
        };
        return newStates;
      });

      // Refresh status
      await fetchSubmissionStatus();

      setNotificationType('success');
      setNotificationMessage(`✅ Grade submitted for ${state.subject.subject_code} - ${state.subject.subject_name}`);
      setShowNotification(true);
    } catch (error: any) {
      setSubjectStates(prev => {
        const newStates = [...prev];
        newStates[index] = {
          ...newStates[index],
          status: 'not-submitted',
          error: error.message || 'Failed to submit grade',
        };
        return newStates;
      });
    }
  };

  // Validate all submissions
  const handleValidateAll = async () => {
    if (!semester || !academicYear) {
      setError('Please select semester and academic year');
      return;
    }

    setLoading(true);
    try {
      const validation = await gradeService.validateGradeSubmissions(academicYear, semester);
      
      if (validation.is_valid) {
        setNotificationType('success');
        setNotificationMessage('✅ All grades validated successfully! Your submissions match your COE subjects.');
      } else {
        const errorMsg = [
          '⚠️ Grade validation issues found:',
          '',
          ...validation.errors,
          '',
          ...(validation.warnings.length > 0 ? ['Warnings:', ...validation.warnings] : [])
        ].join('\n');
        
        setNotificationType('warning');
        setNotificationMessage(errorMsg);
      }
      setShowNotification(true);
    } catch (error: any) {
      setNotificationType('error');
      setNotificationMessage(error.message || 'Failed to validate submissions');
      setShowNotification(true);
    } finally {
      setLoading(false);
    }
  };

  // Calculate progress
  const submittedCount = subjectStates.filter(s => s.status !== 'not-submitted').length;
  const totalSubjects = subjectStates.length;
  const allSubmitted = submittedCount === totalSubjects && totalSubjects > 0;

  return (
    <div className="grade-submission-form-compact">
      {/* Header */}
      <div className="compact-header">
        <h2>Submit Grades by Subject</h2>
        <p className="header-subtitle">Upload grade sheet for each subject from your COE</p>
      </div>

      {/* Loading states */}
      {(documentsLoading || coeLoading) && (
        <div className="compact-loading">
          <div className="loading-spinner-small"></div>
          <span>{documentsLoading ? 'Verifying eligibility...' : 'Loading COE subjects...'}</span>
        </div>
      )}

      {/* Main Form - Only show if eligible */}
      {!documentsLoading && !coeLoading && eligibility?.canSubmit && (
        <div className="compact-form">
          {error && (
            <div className="compact-error">
              ⚠️ {error}
            </div>
          )}

          {/* Semester and Academic Year Selection */}
          <div className="compact-grid compact-grid-spacing">
            <div className="compact-field">
              <label>Semester</label>
              <select
                value={semester}
                onChange={(e) => {
                  setSemester(e.target.value);
                  fetchSubmissionStatus();
                }}
                required
                className="compact-input"
                title="Select semester"
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
                value={academicYear}
                onChange={(e) => {
                  setAcademicYear(e.target.value);
                  fetchSubmissionStatus();
                }}
                placeholder="2024-2025"
                required
                className="compact-input"
              />
            </div>
          </div>

          {/* Progress Indicator */}
          {totalSubjects > 0 && (
            <div className="progress-section">
              <h4>📊 Submission Progress</h4>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: (submittedCount / totalSubjects) * 100 + '%' }}
                ></div>
              </div>
              <p className="progress-text">
                {submittedCount} of {totalSubjects} subjects submitted
              </p>
            </div>
          )}

          {/* Subject List */}
          {coeSubjects.length === 0 ? (
            <div className="no-subjects-message">
              <p>📋 No subjects found in your COE. Please ensure your Certificate of Enrollment has been approved and contains subject information.</p>
              <p>If you just uploaded a new COE, please wait for admin approval. Once approved, subjects will be extracted automatically.</p>
              <button 
                onClick={reloadCOESubjects} 
                disabled={coeLoading}
                className="refresh-button"
                style={{ marginTop: '10px', padding: '8px 16px', cursor: 'pointer' }}
              >
                {coeLoading ? '⏳ Loading...' : '🔄 Reload Subjects'}
              </button>
            </div>
          ) : (
            <div className="subject-list">
              <h4>📚 Subjects from COE ({coeSubjects.length})</h4>
              
              {/* Pending Submission Notice */}
              {gradeStatus && gradeStatus.pending_count > 0 && (
                <div className="info-message" style={{ 
                  backgroundColor: '#fff3cd', 
                  border: '1px solid #ffc107', 
                  borderRadius: '4px', 
                  padding: '12px', 
                  marginBottom: '15px',
                  color: '#856404'
                }}>
                  <strong>⏳ Pending Review:</strong> You have {gradeStatus.pending_count} grade submission(s) pending admin review. 
                  New submissions are disabled until pending grades are reviewed.
                </div>
              )}
              
              {subjectStates.map((state, index) => (
                <div key={state.subject.subject_code} className="subject-card">
                  <div className="subject-header">
                    <div className="subject-info">
                      <span className="subject-code">{state.subject.subject_code}</span>
                      <span className="subject-name">{state.subject.subject_name}</span>
                    </div>
                    <div className="subject-status">
                      {state.status === 'not-submitted' && <span className="status-badge status-pending">Not Submitted</span>}
                      {state.status === 'uploading' && <span className="status-badge status-uploading">Uploading...</span>}
                      {state.status === 'submitted' && <span className="status-badge status-submitted">Submitted</span>}
                      {state.status === 'approved' && <span className="status-badge status-approved">✅ Approved</span>}
                      {state.status === 'rejected' && <span className="status-badge status-rejected">❌ Rejected</span>}
                    </div>
                  </div>

                  {(state.status === 'not-submitted' || state.status === 'uploading') && (
                    <div className="subject-inputs">
                      <div className="input-row">
                        <div className="input-group">
                          <label>Units</label>
                          <input
                            type="number"
                            min="1"
                            max="6"
                            value={state.units}
                            onChange={(e) => handleUnitsChange(index, parseInt(e.target.value) || 3)}
                            className="compact-input"
                            title="Credit units for this subject"
                            placeholder="3"
                          />
                        </div>
                        <div className="input-group">
                          <label>Grade</label>
                          <input
                            type="number"
                            min="1.0"
                            max="5.0"
                            step="0.25"
                            value={state.grade}
                            onChange={(e) => handleGradeChange(index, parseFloat(e.target.value) || 1.0)}
                            className="compact-input"
                            title="Grade received (1.0-5.0)"
                            placeholder="1.0"
                          />
                        </div>
                      </div>
                      
                      <div className="file-upload-section">
                        <label className="upload-label-inline">
                          📄 Grade Sheet
                          <input
                            type="file"
                            onChange={(e) => handleFileChange(index, e.target.files?.[0] || null)}
                            accept=".pdf,.jpg,.jpeg,.png"
                            className="file-input-hidden"
                          />
                        </label>
                        {state.file && (
                          <span className="file-name">✓ {state.file.name}</span>
                        )}
                      </div>

                      {state.error && (
                        <div className="subject-error">
                          ⚠️ {state.error}
                        </div>
                      )}

                      <button
                        type="button"
                        onClick={() => handleSubmitSubject(index)}
                        className="btn-submit-subject"
                        disabled={
                          !state.file || 
                          state.status === 'uploading' || 
                          state.status === 'submitted' || 
                          state.status === 'approved' ||
                          (gradeStatus && gradeStatus.pending_count > 0)
                        }
                        title={
                          state.status === 'submitted' ? 'Grade already submitted and pending review' :
                          state.status === 'approved' ? 'Grade already approved' :
                          (gradeStatus && gradeStatus.pending_count > 0) ? 'Cannot submit - you have pending grade submissions' :
                          !state.file ? 'Please select a grade sheet file' : 
                          'Submit grade for review'
                        }
                      >
                        {state.status === 'uploading' ? 'Uploading...' : 
                         state.status === 'submitted' ? 'Submitted (Pending Review)' :
                         state.status === 'approved' ? 'Already Approved' :
                         'Submit Grade'}
                      </button>
                    </div>
                  )}

                  {(state.status === 'submitted' || state.status === 'approved' || state.status === 'rejected') && (
                    <div className="subject-details">
                      <p><strong>Units:</strong> {state.units} | <strong>Grade:</strong> {state.grade}</p>
                      {state.adminNotes && (
                        <p className="admin-notes"><strong>Admin Notes:</strong> {state.adminNotes}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="compact-actions compact-actions-spacing">
            <button
              type="button"
              onClick={onCancel}
              className="btn-compact btn-cancel"
              disabled={loading}
            >
              Cancel
            </button>

            {allSubmitted && (
              <button
                type="button"
                onClick={handleValidateAll}
                className="btn-compact btn-validate"
                disabled={loading}
              >
                Validate All
              </button>
            )}
          </div>

          {/* Info Section */}
          {gradeStatus?.gpa_calculated && (
            <div className="compact-ai-info compact-ai-info-spacing">
              <div className="ai-badge">🎓 GPA CALCULATED</div>
              <p>Your GPA: {gradeStatus.general_weighted_average?.toFixed(2)}</p>
            </div>
          )}
        </div>
      )}

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
