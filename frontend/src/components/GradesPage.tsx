import React, { useState } from 'react';
import GradeSubmissionForm from './GradeSubmissionForm';
import './GradesPage.css';

interface GradeSubmission {
  id: number;
  academic_year: string;
  semester: string;
  semester_display: string;
  general_weighted_average: number | string;
  semestral_weighted_average: number | string;
  qualifies_for_basic_allowance: boolean;
  qualifies_for_merit_incentive: boolean;
  status: string;
  status_display: string;
  submitted_at: string;
}

interface GradesPageProps {
  grades: GradeSubmission[];
  darkMode: boolean;
  canSubmitGrades: boolean;
  onGradeSubmissionSuccess: () => void;
}

const GradesPage: React.FC<GradesPageProps> = ({ 
  grades, 
  darkMode, 
  canSubmitGrades,
  onGradeSubmissionSuccess 
}) => {
  const [showGradeForm, setShowGradeForm] = useState(false);

  const completedSemesters = grades.length;
  const approvedGrades = grades.filter(g => g.status === 'approved').length;
  const completionPercentage = grades.length > 0 ? Math.round((approvedGrades / completedSemesters) * 100) : 0;

  const averageGPA = grades.length > 0 
    ? (grades.reduce((sum, grade) => {
        const gwa = typeof grade.general_weighted_average === 'string' 
          ? parseFloat(grade.general_weighted_average) 
          : grade.general_weighted_average;
        return sum + (isNaN(gwa) ? 0 : gwa);
      }, 0) / grades.length).toFixed(2)
    : '0.00';

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return '#10b981';
      case 'pending':
        return '#f59e0b';
      case 'rejected':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return '✅';
      case 'pending':
        return '⏳';
      case 'rejected':
        return '❌';
      default:
        return '📊';
    }
  };

  const handleFormSuccess = () => {
    setShowGradeForm(false);
    onGradeSubmissionSuccess();
  };

  return (
    <div className={`grades-page ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      <div className="page-header">
        <h1>Submit Grades</h1>
        <p>Submit your grades for each semester to qualify for allowances</p>
      </div>

      {/* Stats Overview */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🎓</div>
          <div className="stat-content">
            <h3>Submission Progress</h3>
            <div className="stat-value">{completionPercentage}% Complete</div>
            <p>{approvedGrades} of {completedSemesters} semesters completed</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>Average GPA</h3>
            <div className="stat-value">{averageGPA}</div>
            <p>Overall weighted average</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3>Eligibility Status</h3>
            <div className="stat-value">
              {grades.some(g => g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive) 
                ? 'Eligible' 
                : 'Not Eligible'}
            </div>
            <p>For allowance programs</p>
          </div>
        </div>
      </div>

      {/* Add New Grades Button */}
      {canSubmitGrades && (
        <div className="add-grades-section">
          <button 
            className="add-grades-button"
            onClick={() => setShowGradeForm(true)}
          >
            Submit Grades
          </button>
          <p>Submit grades for a new semester to update your eligibility status</p>
        </div>
      )}

      {!canSubmitGrades && (
        <div className="requirement-notice">
          <div className="notice-icon">⚠️</div>
          <div className="notice-content">
            <h3>Documents Required</h3>
            <p>You need to submit at least 2 approved documents before you can add your grades.</p>
          </div>
        </div>
      )}

      {/* Grades List */}
      {grades.length > 0 ? (
        <div className="grades-list">
          <h2>Submitted Grades</h2>
          <div className="grades-grid">
            {grades.map((grade) => (
              <div key={grade.id} className="grade-card">
                <div className="grade-header">
                  <div className="grade-info">
                    <h3>{grade.semester_display} {grade.academic_year}</h3>
                    <div className="grade-status">
                      <span className="status-icon">
                        {getStatusIcon(grade.status)}
                      </span>
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(grade.status) }}
                      >
                        {grade.status_display}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grade-details">
                  <div className="grade-row">
                    <span className="grade-label">General Weighted Average:</span>
                    <span className="grade-value">{grade.general_weighted_average}</span>
                  </div>
                  <div className="grade-row">
                    <span className="grade-label">Semestral Weighted Average:</span>
                    <span className="grade-value">{grade.semestral_weighted_average}</span>
                  </div>
                </div>

                <div className="eligibility-section">
                  <h4>Allowance Eligibility</h4>
                  <div className="eligibility-items">
                    <div className={`eligibility-item ${grade.qualifies_for_basic_allowance ? 'eligible' : 'not-eligible'}`}>
                      <span className="eligibility-icon">
                        {grade.qualifies_for_basic_allowance ? '✅' : '❌'}
                      </span>
                      <span>Basic Allowance</span>
                    </div>
                    <div className={`eligibility-item ${grade.qualifies_for_merit_incentive ? 'eligible' : 'not-eligible'}`}>
                      <span className="eligibility-icon">
                        {grade.qualifies_for_merit_incentive ? '✅' : '❌'}
                      </span>
                      <span>Merit Incentive</span>
                    </div>
                  </div>
                </div>

                <div className="submission-info">
                  <span className="submission-date">
                    Submitted: {new Date(grade.submitted_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📚</div>
          <h3>No Grades Submitted</h3>
          <p>Submit your semester grades to track your academic progress and eligibility for allowances.</p>
        </div>
      )}

      {/* Grade Submission Form Modal */}
      {showGradeForm && (
        <GradeSubmissionForm
          onCancel={() => setShowGradeForm(false)}
          onSubmissionSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
};

export default GradesPage;