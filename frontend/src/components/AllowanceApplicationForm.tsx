import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import { sendApplicationConfirmationEmail } from '../services/email/emailService';
import { useAuth } from '../contexts/AuthContext';
import './AllowanceApplicationForm.css';

interface GradeSubmission {
  id: number;
  academic_year: string;
  semester: string;
  semester_display: string;
  general_weighted_average: number;
  semestral_weighted_average: number;
  qualifies_for_basic_allowance: boolean;
  qualifies_for_merit_incentive: boolean;
  status: string;
  submitted_at: string;
}

interface AllowanceApplication {
  id: number;
  grade_submission: number;
  application_type: string;
  status: string;
}

interface AllowanceApplicationFormProps {
  onSubmissionSuccess: () => void;
  onCancel: () => void;
}

const AllowanceApplicationForm: React.FC<AllowanceApplicationFormProps> = ({
  onSubmissionSuccess,
  onCancel
}) => {
  const { user } = useAuth();
  const [gradeSubmissions, setGradeSubmissions] = useState<GradeSubmission[]>([]);
  const [existingApplications, setExistingApplications] = useState<AllowanceApplication[]>([]);
  const [selectedGradeSubmission, setSelectedGradeSubmission] = useState<number | null>(null);
  const [applicationType, setApplicationType] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [loadingGrades, setLoadingGrades] = useState(true);
  const [emailStatus, setEmailStatus] = useState<string>('');

  useEffect(() => {
    fetchApprovedGrades();
    fetchExistingApplications();
  }, []);

  const fetchApprovedGrades = async () => {
    try {
      setLoadingGrades(true);
      const response = await apiClient.get<GradeSubmission[]>('/grades/');
      // Filter only approved grades that qualify for allowances
      const approvedGrades = response.data.filter(grade => 
        grade.status === 'approved' && 
        (grade.qualifies_for_basic_allowance || grade.qualifies_for_merit_incentive)
      );
      setGradeSubmissions(approvedGrades);
      setError('');
    } catch (error: any) {
      console.error('Error fetching grades:', error);
      setError('Failed to load eligible grade submissions. Please try again.');
    } finally {
      setLoadingGrades(false);
    }
  };

  const fetchExistingApplications = async () => {
    try {
      const response = await apiClient.get<AllowanceApplication[]>('/applications/');
      setExistingApplications(response.data);
    } catch (error: any) {
      console.error('Error fetching existing applications:', error);
      // Don't show error to user, just log it
    }
  };

  const hasExistingApplication = (gradeId: number): boolean => {
    return existingApplications.some(app => app.grade_submission === gradeId);
  };

  const getAvailableGradeSubmissions = (): GradeSubmission[] => {
    return gradeSubmissions.filter(grade => !hasExistingApplication(grade.id));
  };

  const getSelectedGrade = (): GradeSubmission | null => {
    if (!selectedGradeSubmission) return null;
    return gradeSubmissions.find(grade => grade.id === selectedGradeSubmission) || null;
  };

  const getAvailableApplicationTypes = (): Array<{value: string, label: string, amount: string}> => {
    const selectedGrade = getSelectedGrade();
    if (!selectedGrade) return [];

    const types = [];
    
    if (selectedGrade.qualifies_for_basic_allowance) {
      types.push({
        value: 'basic',
        label: 'Basic Educational Assistance',
        amount: '₱5,000'
      });
    }
    
    if (selectedGrade.qualifies_for_merit_incentive) {
      types.push({
        value: 'merit',
        label: 'Merit Incentive',
        amount: '₱5,000'
      });
    }
    
    if (selectedGrade.qualifies_for_basic_allowance && selectedGrade.qualifies_for_merit_incentive) {
      types.push({
        value: 'both',
        label: 'Both Allowances (Basic + Merit)',
        amount: '₱10,000'
      });
    }
    
    return types;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedGradeSubmission || !applicationType) {
      setError('Please select a grade submission and application type.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setEmailStatus('');

      const applicationData = {
        grade_submission: selectedGradeSubmission,
        application_type: applicationType
      };

      // Submit the application
      const response = await apiClient.post('/applications/', applicationData);
      const submittedApplication: any = response.data;
      
      // Send confirmation email to student
      if (user?.email && user?.first_name && user?.last_name) {
        setEmailStatus('📧 Sending confirmation email...');
        
        const studentFullName = `${user.last_name}, ${user.first_name}`;
        const applicationId = submittedApplication?.id ? `APP-${submittedApplication.id}` : 'Pending Assignment';
        const selectedType = getAvailableApplicationTypes().find(t => t.value === applicationType);
        const typeDisplay = selectedType?.label || 'Educational Assistance';
        const amountDisplay = calculateAmount();
        
        const emailResult = await sendApplicationConfirmationEmail(
          studentFullName,
          user.email,
          applicationId,
          typeDisplay,
          amountDisplay
        );
        
        if (emailResult.success) {
          setEmailStatus('✅ Application submitted successfully! A confirmation email has been sent to ' + user.email);
        } else {
          console.warn('Email sending failed:', emailResult.message);
          setEmailStatus('✅ Application submitted successfully! (Email notification failed - please check your email settings)');
        }
      } else {
        setEmailStatus('✅ Application submitted successfully!');
      }
      
      // Small delay to show message before closing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      onSubmissionSuccess();
    } catch (error: any) {
      console.error('Error submitting application:', error);
      
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          // Handle field-specific errors
          const errorMessages: string[] = [];
          
          // Check for non_field_errors (like unique_together constraint)
          if (error.response.data.non_field_errors) {
            errorMessages.push(...error.response.data.non_field_errors);
          }
          
          // Check for other field errors
          Object.entries(error.response.data).forEach(([key, value]) => {
            if (key !== 'non_field_errors' && Array.isArray(value)) {
              errorMessages.push(...value);
            } else if (key !== 'non_field_errors' && typeof value === 'string') {
              errorMessages.push(value);
            }
          });
          
          if (errorMessages.length > 0) {
            // Check if it's a duplicate application error
            const isDuplicateError = errorMessages.some(msg => 
              msg.toLowerCase().includes('already exists') || 
              msg.toLowerCase().includes('unique') ||
              msg.toLowerCase().includes('duplicate')
            );
            
            if (isDuplicateError) {
              setError('You have already submitted an allowance application for this grade submission. Please check your application history.');
            } else {
              setError(errorMessages.join(' '));
            }
          } else {
            setError('Failed to submit application. Please try again.');
          }
        } else if (typeof error.response.data === 'string') {
          setError(error.response.data);
        } else {
          setError(error.response.data.detail || 'Failed to submit application. Please try again.');
        }
      } else {
        setError('Failed to submit application. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const calculateAmount = (): string => {
    const selectedType = getAvailableApplicationTypes().find(type => type.value === applicationType);
    return selectedType ? selectedType.amount : '₱0';
  };

  return (
    <div className="allowance-form-container">
      <div className="allowance-form-header">
        <h3>Allowance Application</h3>
        <p>Apply for your educational assistance allowance based on your approved grades</p>
      </div>

      {loadingGrades ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading your eligible grade submissions...</p>
        </div>
      ) : gradeSubmissions.length === 0 ? (
        <div className="no-grades-state">
          <h4>No Eligible Grades Found</h4>
          <p>You need approved grade submissions that qualify for allowances before you can apply.</p>
          <div className="requirements-list">
            <h5>Requirements:</h5>
            <ul>
              <li>Submit and get approval for your grade reports</li>
              <li>Meet the academic performance criteria</li>
              <li>Ensure grades qualify for basic allowance or merit incentive</li>
            </ul>
          </div>
          <button type="button" onClick={onCancel} className="cancel-button">
            Close
          </button>
        </div>
      ) : getAvailableGradeSubmissions().length === 0 ? (
        <div className="no-grades-state">
          <h4>All Eligible Grades Already Applied</h4>
          <p>You have already submitted allowance applications for all your eligible grade submissions.</p>
          <div className="requirements-list">
            <h5>What you can do:</h5>
            <ul>
              <li>Check your application status in the dashboard</li>
              <li>Wait for your current applications to be processed</li>
              <li>Submit new grade reports to apply for additional allowances</li>
            </ul>
          </div>
          <button type="button" onClick={onCancel} className="cancel-button">
            Close
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="allowance-form">
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {emailStatus && (
            <div className="email-status-message">
              <span className="email-icon">📧</span>
              {emailStatus}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="gradeSubmission">Select Grade Submission *</label>
            <select
              id="gradeSubmission"
              value={selectedGradeSubmission || ''}
              onChange={(e) => {
                const gradeId = parseInt(e.target.value);
                setSelectedGradeSubmission(gradeId);
                
                // Automatically set application type based on grade eligibility
                const selectedGrade = gradeSubmissions.find(g => g.id === gradeId);
                if (selectedGrade) {
                  if (selectedGrade.qualifies_for_basic_allowance && selectedGrade.qualifies_for_merit_incentive) {
                    setApplicationType('both');
                  } else if (selectedGrade.qualifies_for_merit_incentive) {
                    setApplicationType('merit');
                  } else if (selectedGrade.qualifies_for_basic_allowance) {
                    setApplicationType('basic');
                  }
                }
              }}
              required
              className="grade-select"
            >
              <option value="">Choose a grade submission...</option>
              {getAvailableGradeSubmissions().map((grade) => (
                <option key={grade.id} value={grade.id}>
                  {grade.academic_year} - {grade.semester_display} 
                  (GWA: {Number(grade.general_weighted_average).toFixed(2)}%, 
                   SWA: {Number(grade.semestral_weighted_average).toFixed(2)}%)
                </option>
              ))}
            </select>
          </div>

          {selectedGradeSubmission && (
            <div className="grade-summary">
              <h4>Selected Grade Summary</h4>
              <div className="grade-details">
                {(() => {
                  const selectedGrade = getSelectedGrade();
                  return selectedGrade ? (
                    <>
                      <div className="grade-info-row">
                        <div className="info-item">
                          <span className="info-label">Academic Year</span>
                          <span className="info-value">{selectedGrade.academic_year}</span>
                        </div>
                        <div className="info-item">
                          <span className="info-label">Semester</span>
                          <span className="info-value">{selectedGrade.semester_display}</span>
                        </div>
                      </div>
                      <div className="grade-scores-row">
                        <div className="score-item">
                          <span className="score-label">General Weighted Average</span>
                          <span className="score-value">{Number(selectedGrade.general_weighted_average).toFixed(2)}%</span>
                        </div>
                        <div className="score-item">
                          <span className="score-label">Semestral Weighted Average</span>
                          <span className="score-value">{Number(selectedGrade.semestral_weighted_average).toFixed(2)}%</span>
                        </div>
                      </div>
                      <div className="eligibility-status">
                        <span className={`eligibility ${selectedGrade.qualifies_for_basic_allowance ? 'eligible' : 'not-eligible'}`}>
                          {selectedGrade.qualifies_for_basic_allowance ? '✓' : '✗'} Basic Allowance
                        </span>
                        <span className={`eligibility ${selectedGrade.qualifies_for_merit_incentive ? 'eligible' : 'not-eligible'}`}>
                          {selectedGrade.qualifies_for_merit_incentive ? '✓' : '✗'} Merit Incentive
                        </span>
                      </div>
                    </>
                  ) : null;
                })()}
              </div>
            </div>
          )}

          {selectedGradeSubmission && applicationType && (
            <div className="application-summary">
              <h4>Application Summary</h4>
              <div className="summary-details">
                <div className="summary-row">
                  <span className="summary-label">Application Type</span>
                  <span className="summary-value">{getAvailableApplicationTypes().find(t => t.value === applicationType)?.label}</span>
                </div>
                <div className="summary-row total">
                  <span className="summary-label">Total Amount</span>
                  <span className="amount">{calculateAmount()}</span>
                </div>
              </div>
              <div className="processing-info">
                <div className="info-note">
                  <strong>Processing Time:</strong> 3-5 business days
                </div>
                <div className="info-note">
                  <strong>Approval:</strong> Requires admin approval
                </div>
                <div className="info-note">
                  <strong>Updates:</strong> You'll receive email notifications on status changes
                </div>
              </div>
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              onClick={onCancel}
              className="cancel-button"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={loading || !selectedGradeSubmission || !applicationType}
            >
              {loading ? (
                <>
                  <span className="loading-spinner-small"></span>
                  Submitting Application...
                </>
              ) : (
                `Submit Application for ${calculateAmount()}`
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default AllowanceApplicationForm;
