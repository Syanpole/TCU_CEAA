import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
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

interface AllowanceApplicationFormProps {
  onSubmissionSuccess: () => void;
  onCancel: () => void;
}

const AllowanceApplicationForm: React.FC<AllowanceApplicationFormProps> = ({
  onSubmissionSuccess,
  onCancel
}) => {
  const [gradeSubmissions, setGradeSubmissions] = useState<GradeSubmission[]>([]);
  const [selectedGradeSubmission, setSelectedGradeSubmission] = useState<number | null>(null);
  const [applicationType, setApplicationType] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [loadingGrades, setLoadingGrades] = useState(true);

  useEffect(() => {
    fetchApprovedGrades();
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

      const applicationData = {
        grade_submission: selectedGradeSubmission,
        application_type: applicationType
      };

      await apiClient.post('/applications/', applicationData);
      onSubmissionSuccess();
    } catch (error: any) {
      console.error('Error submitting application:', error);
      
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          const errorMessages = Object.values(error.response.data).flat();
          setError(errorMessages.join(' '));
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
        <h3>💰 Allowance Application</h3>
        <p>Apply for your educational assistance allowance based on your approved grades</p>
      </div>

      {loadingGrades ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading your eligible grade submissions...</p>
        </div>
      ) : gradeSubmissions.length === 0 ? (
        <div className="no-grades-state">
          <div className="no-grades-icon">📊</div>
          <h4>No Eligible Grades Found</h4>
          <p>You need approved grade submissions that qualify for allowances before you can apply.</p>
          <div className="requirements-list">
            <h5>Requirements:</h5>
            <ul>
              <li>✅ Submit and get approval for your grade reports</li>
              <li>✅ Meet the academic performance criteria</li>
              <li>✅ Ensure grades qualify for basic allowance or merit incentive</li>
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

          <div className="form-group">
            <label htmlFor="gradeSubmission">
              <span className="label-icon">📈</span>
              Select Grade Submission
            </label>
            <select
              id="gradeSubmission"
              value={selectedGradeSubmission || ''}
              onChange={(e) => {
                setSelectedGradeSubmission(parseInt(e.target.value));
                setApplicationType(''); // Reset application type when grade changes
              }}
              required
              className="grade-select"
            >
              <option value="">Choose a grade submission...</option>
              {gradeSubmissions.map((grade) => (
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
              <h4>📊 Selected Grade Summary</h4>
              <div className="grade-details">
                {(() => {
                  const selectedGrade = getSelectedGrade();
                  return selectedGrade ? (
                    <>
                      <div className="grade-info">
                        <span>📅 Academic Year: {selectedGrade.academic_year}</span>
                        <span>📚 Semester: {selectedGrade.semester_display}</span>
                      </div>
                      <div className="grade-scores">
                        <span>📈 General Weighted Average: {Number(selectedGrade.general_weighted_average).toFixed(2)}%</span>
                        <span>📊 Semestral Weighted Average: {Number(selectedGrade.semestral_weighted_average).toFixed(2)}%</span>
                      </div>
                      <div className="eligibility-status">
                        <span className={`eligibility ${selectedGrade.qualifies_for_basic_allowance ? 'eligible' : 'not-eligible'}`}>
                          {selectedGrade.qualifies_for_basic_allowance ? '✅' : '❌'} Basic Allowance Eligible
                        </span>
                        <span className={`eligibility ${selectedGrade.qualifies_for_merit_incentive ? 'eligible' : 'not-eligible'}`}>
                          {selectedGrade.qualifies_for_merit_incentive ? '🌟' : '❌'} Merit Incentive Eligible
                        </span>
                      </div>
                    </>
                  ) : null;
                })()}
              </div>
            </div>
          )}

          {selectedGradeSubmission && getAvailableApplicationTypes().length > 0 && (
            <div className="form-group">
              <label htmlFor="applicationType">
                <span className="label-icon">💰</span>
                Application Type
              </label>
              <div className="application-types">
                {getAvailableApplicationTypes().map((type) => (
                  <label key={type.value} className="radio-option">
                    <input
                      type="radio"
                      name="applicationType"
                      value={type.value}
                      checked={applicationType === type.value}
                      onChange={(e) => setApplicationType(e.target.value)}
                      required
                    />
                    <div className="radio-content">
                      <div className="radio-header">
                        <span className="radio-title">{type.label}</span>
                        <span className="radio-amount">{type.amount}</span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {applicationType && (
            <div className="application-summary">
              <h4>💸 Application Summary</h4>
              <div className="summary-details">
                <div className="summary-row">
                  <span>📋 Application Type:</span>
                  <span>{getAvailableApplicationTypes().find(t => t.value === applicationType)?.label}</span>
                </div>
                <div className="summary-row total">
                  <span>💰 Total Amount:</span>
                  <span className="amount">{calculateAmount()}</span>
                </div>
              </div>
              <div className="processing-info">
                <div className="info-item">
                  <span className="info-icon">⏰</span>
                  <span>Processing Time: 3-5 business days</span>
                </div>
                <div className="info-item">
                  <span className="info-icon">👩‍💼</span>
                  <span>Requires admin approval</span>
                </div>
                <div className="info-item">
                  <span className="info-icon">📧</span>
                  <span>You'll receive email updates on status changes</span>
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
                <>
                  💰 Submit Application for {calculateAmount()}
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default AllowanceApplicationForm;
