import React, { useState, useEffect } from 'react';
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
  onRefresh: () => void;
}

const GradesPage: React.FC<GradesPageProps> = ({ 
  grades, 
  darkMode, 
  canSubmitGrades,
  onGradeSubmissionSuccess,
  onRefresh 
}) => {
  const [showGradeForm, setShowGradeForm] = useState(false);
  const [selectedGrade, setSelectedGrade] = useState<GradeSubmission | null>(null);
  const [showGradeModal, setShowGradeModal] = useState(false);

  // Handle Escape key to close modals
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (showGradeForm) setShowGradeForm(false);
        if (showGradeModal) setShowGradeModal(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [showGradeForm, showGradeModal]);

  // Prevent body scroll when modals are open
  useEffect(() => {
    if (showGradeForm || showGradeModal) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [showGradeForm, showGradeModal]);

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

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleFormSuccess = () => {
    setShowGradeForm(false);
    onGradeSubmissionSuccess();
  };

  const handleRefreshClick = async () => {
    setIsRefreshing(true);
    await onRefresh();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const handleViewGrade = (grade: GradeSubmission) => {
    setSelectedGrade(grade);
    setShowGradeModal(true);
  };

  const handleCloseGradeModal = () => {
    setShowGradeModal(false);
    setSelectedGrade(null);
  };

  return (
    <div className={`grades-page ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Modern Header with Refresh Button */}
      <div className="grades-page-header">
        <div className="header-left">
          <h1>Grade Submissions</h1>
          <p className="header-subtitle">Track your academic performance and allowance eligibility</p>
        </div>
        <div className="header-right">
          <button 
            className="refresh-btn-grades" 
            onClick={handleRefreshClick} 
            disabled={isRefreshing}
            title="Refresh grades"
          >
            <span className={`refresh-icon ${isRefreshing ? 'spinning' : ''}`}>🔄</span>
            Refresh
          </button>
          {canSubmitGrades && (
            <button 
              className="add-grades-btn"
              onClick={() => setShowGradeForm(true)}
            >
              <span className="btn-plus">+</span>
              Submit Grades
            </button>
          )}
        </div>
      </div>

      {/* Stats Overview Cards */}
      <div className="stats-overview">
        <div className="stat-card-modern">
          <div className="stat-icon-wrapper progress-icon">
            <span className="stat-emoji">🎓</span>
          </div>
          <div className="stat-details">
            <span className="stat-label">Submission Progress</span>
            <span className="stat-number">{completionPercentage}%</span>
            <span className="stat-description">{approvedGrades} of {completedSemesters} semesters</span>
          </div>
        </div>

        <div className="stat-card-modern">
          <div className="stat-icon-wrapper gpa-icon">
            <span className="stat-emoji">📊</span>
          </div>
          <div className="stat-details">
            <span className="stat-label">Average GWA</span>
            <span className="stat-number">{averageGPA}</span>
            <span className="stat-description">Overall performance</span>
          </div>
        </div>

        <div className="stat-card-modern">
          <div className="stat-icon-wrapper eligibility-icon">
            <span className="stat-emoji">
              {grades.some(g => g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive) ? '✅' : '⏳'}
            </span>
          </div>
          <div className="stat-details">
            <span className="stat-label">Allowance Status</span>
            <span className="stat-number">
              {grades.some(g => g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive) 
                ? 'Eligible' 
                : 'Pending'}
            </span>
            <span className="stat-description">
              {grades.some(g => g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive)
                ? 'Qualified for benefits'
                : 'Submit grades to qualify'}
            </span>
          </div>
        </div>
      </div>

      {/* Notice for Document Requirements */}
      {!canSubmitGrades && (
        <div className="info-banner warning">
          <div className="banner-icon">⚠️</div>
          <div className="banner-content">
            <h3>Documents Required First</h3>
            <p>You need to submit at least 2 approved documents before submitting grades.</p>
          </div>
        </div>
      )}

      {/* Grades List Section */}
      <div className="grades-section">
        {grades.length > 0 ? (
          <>
            <div className="section-header">
              <h2>📚 Submitted Grades</h2>
              <span className="grade-count">{grades.length} semester{grades.length !== 1 ? 's' : ''}</span>
            </div>
            <div className="grades-grid-modern">
              {grades.map((grade) => (
                <div key={grade.id} className="grade-card-modern">
                  <div className="card-top">
                    <div className="semester-info">
                      <h3 className="semester-title">{grade.semester_display}</h3>
                      <span className="academic-year">{grade.academic_year}</span>
                    </div>
                    <span 
                      className={`status-badge-modern status-${grade.status}`}
                      style={{ backgroundColor: getStatusColor(grade.status) }}
                    >
                      {getStatusIcon(grade.status)} {grade.status_display}
                    </span>
                  </div>

                  <div className="card-divider"></div>

                  <div className="card-body-grade">
                    <div className="gwa-display">
                      <span className="gwa-label">General Weighted Average</span>
                      <span className="gwa-value">{grade.general_weighted_average}</span>
                    </div>

                    <div className="eligibility-grid">
                      <div className={`eligibility-badge ${grade.qualifies_for_basic_allowance ? 'qualified' : 'not-qualified'}`}>
                        <span className="badge-icon">
                          {grade.qualifies_for_basic_allowance ? '✅' : '❌'}
                        </span>
                        <div className="badge-text">
                          <span className="badge-title">Basic Allowance</span>
                          <span className="badge-status">
                            {grade.qualifies_for_basic_allowance ? 'Qualified' : 'Not Qualified'}
                          </span>
                        </div>
                      </div>

                      <div className={`eligibility-badge ${grade.qualifies_for_merit_incentive ? 'qualified' : 'not-qualified'}`}>
                        <span className="badge-icon">
                          {grade.qualifies_for_merit_incentive ? '✅' : '❌'}
                        </span>
                        <div className="badge-text">
                          <span className="badge-title">Merit Incentive</span>
                          <span className="badge-status">
                            {grade.qualifies_for_merit_incentive ? 'Qualified' : 'Not Qualified'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="card-footer-grade">
                    <button 
                      className="btn-view-details"
                      onClick={() => handleViewGrade(grade)}
                    >
                      View Details
                    </button>
                    <span className="submission-timestamp">
                      📅 {new Date(grade.submitted_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="empty-state-modern">
            <div className="empty-icon-large">📚</div>
            <h3>No Grades Submitted Yet</h3>
            <p>Start tracking your academic performance by submitting your semester grades.</p>
            {canSubmitGrades && (
              <button 
                className="btn-empty-action"
                onClick={() => setShowGradeForm(true)}
              >
                <span className="btn-icon">+</span>
                Submit Your First Grade
              </button>
            )}
          </div>
        )}
      </div>

      {/* Grade Submission Form Modal */}
      {showGradeForm && (
        <div className="grade-form-modal-overlay" onClick={() => setShowGradeForm(false)}>
          <div className="modal-hint">Click outside or press ESC to close</div>
          <div className="grade-form-modal-container" onClick={(e) => e.stopPropagation()}>
            <button 
              className="grade-form-close-btn"
              onClick={() => setShowGradeForm(false)}
              aria-label="Close form"
              title="Close (Esc)"
            >
              ×
            </button>
            <GradeSubmissionForm
              onCancel={() => setShowGradeForm(false)}
              onSubmissionSuccess={handleFormSuccess}
            />
          </div>
        </div>
      )}

      {/* Grade Details Modal */}
      {showGradeModal && selectedGrade && (
        <div className="grade-modal-overlay" onClick={handleCloseGradeModal}>
          <div className="grade-modal" onClick={(e) => e.stopPropagation()}>
            {/* Close Button */}
            <button 
              className="grade-modal-close"
              onClick={handleCloseGradeModal}
              aria-label="Close"
            >
              ×
            </button>

            {/* Modal Header */}
            <div className="grade-modal-header">
              <div className="modal-header-icon">📊</div>
              <h2>Grade Details</h2>
              <p className="modal-subtitle">{selectedGrade.semester_display} • {selectedGrade.academic_year}</p>
            </div>

            {/* Status Badge */}
            <div className="modal-status-container">
              <span 
                className={`modal-status-badge status-${selectedGrade.status}`}
                style={{ backgroundColor: getStatusColor(selectedGrade.status) }}
              >
                {getStatusIcon(selectedGrade.status)} {selectedGrade.status_display}
              </span>
            </div>

            {/* GWA Display */}
            <div className="modal-gwa-section">
              <div className="modal-gwa-card">
                <span className="modal-gwa-label">General Weighted Average</span>
                <span className="modal-gwa-number">{selectedGrade.general_weighted_average}</span>
                <div className="modal-gwa-bar">
                  <div 
                    className="modal-gwa-fill"
                    style={{ 
                      width: `${Math.max(0, Math.min(100, (5 - Number(selectedGrade.general_weighted_average)) * 25))}%`,
                      backgroundColor: Number(selectedGrade.general_weighted_average) <= 1.75 ? '#10b981' : 
                                     Number(selectedGrade.general_weighted_average) <= 2.25 ? '#3b82f6' : '#64748b'
                    }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Eligibility Section */}
            <div className="modal-eligibility-section">
              <h3 className="modal-section-title">Allowance Eligibility</h3>
              <div className="modal-eligibility-cards">
                <div className={`modal-eligibility-card ${selectedGrade.qualifies_for_basic_allowance ? 'qualified' : 'not-qualified'}`}>
                  <div className="eligibility-card-icon">
                    {selectedGrade.qualifies_for_basic_allowance ? '✅' : '❌'}
                  </div>
                  <div className="eligibility-card-content">
                    <h4>Basic Allowance</h4>
                    <p className="eligibility-requirement">Requires GWA ≤ 2.25 (≥80%)</p>
                    <span className={`eligibility-result ${selectedGrade.qualifies_for_basic_allowance ? 'qualified' : 'not-qualified'}`}>
                      {selectedGrade.qualifies_for_basic_allowance ? 'Qualified ✓' : 'Not Qualified'}
                    </span>
                  </div>
                </div>

                <div className={`modal-eligibility-card ${selectedGrade.qualifies_for_merit_incentive ? 'qualified' : 'not-qualified'}`}>
                  <div className="eligibility-card-icon">
                    {selectedGrade.qualifies_for_merit_incentive ? '✅' : '❌'}
                  </div>
                  <div className="eligibility-card-content">
                    <h4>Merit Incentive</h4>
                    <p className="eligibility-requirement">Requires GWA ≤ 1.75 (≥87%)</p>
                    <span className={`eligibility-result ${selectedGrade.qualifies_for_merit_incentive ? 'qualified' : 'not-qualified'}`}>
                      {selectedGrade.qualifies_for_merit_incentive ? 'Qualified ✓' : 'Not Qualified'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Submission Info */}
            <div className="modal-info-section">
              <div className="modal-info-item">
                <span className="modal-info-label">Submitted On</span>
                <span className="modal-info-value">
                  {new Date(selectedGrade.submitted_at).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
            </div>

            {/* Action Button */}
            <div className="modal-actions">
              <button className="btn-modal-close" onClick={handleCloseGradeModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GradesPage;