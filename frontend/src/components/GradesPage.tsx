import React, { useState, useEffect } from 'react';
import GradeSubmissionForm from './GradeSubmissionForm';
import { PageGuideBanner, HelpTooltip, InfoNote } from './TutorialSystem';
import './GradesPage.css';

interface SubjectGrade {
  id: number;
  subject_code: string;
  subject_name: string;
  units: number;
  grade_received: number;
  status: string;
  ai_gwa_calculated?: number;
  ai_merit_level?: string;
}

interface GroupedSemester {
  academic_year: string;
  semester: string;
  semester_display: string;
  subjects: SubjectGrade[];
  general_weighted_average: number;
  total_units: number;
  qualifies_for_basic_allowance: boolean;
  qualifies_for_merit_incentive: boolean;
  status: string;
  status_display: string;
  submitted_at: string;
  all_approved: boolean;
  ai_gwa_calculated?: number;
  ai_merit_level?: string;
}

interface GradeSubmission {
  id: number;
  academic_year: string;
  semester: string;
  semester_display: string;
  subject_code: string;
  subject_name: string;
  units: number;
  grade_received: number;
  general_weighted_average: number | string;
  semestral_weighted_average: number | string;
  qualifies_for_basic_allowance: boolean;
  qualifies_for_merit_incentive: boolean;
  status: string;
  status_display: string;
  submitted_at: string;
  ai_gwa_calculated?: number;
  ai_merit_level?: string;
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
  const [selectedGrade, setSelectedGrade] = useState<GroupedSemester | null>(null);
  const [showGradeModal, setShowGradeModal] = useState(false);
  const [groupedGrades, setGroupedGrades] = useState<GroupedSemester[]>([]);

  // Group grades by semester
  useEffect(() => {
    const groupBySemester = () => {
      const grouped = new Map<string, GroupedSemester>();
      
      grades.forEach(grade => {
        const key = `${grade.academic_year}-${grade.semester}`;
        
        if (!grouped.has(key)) {
          grouped.set(key, {
            academic_year: grade.academic_year,
            semester: grade.semester,
            semester_display: grade.semester_display,
            subjects: [],
            general_weighted_average: 0,
            total_units: 0,
            qualifies_for_basic_allowance: false,
            qualifies_for_merit_incentive: false,
            status: grade.status,
            status_display: grade.status_display,
            submitted_at: grade.submitted_at,
            all_approved: true
          });
        }
        
        const group = grouped.get(key)!;
        
        // Add subject to group
        group.subjects.push({
          id: grade.id,
          subject_code: grade.subject_code,
          subject_name: grade.subject_name,
          units: grade.units,
          grade_received: grade.grade_received,
          status: grade.status
        });
        
        // Track if all are approved
        if (grade.status !== 'approved') {
          group.all_approved = false;
        }
        
        // Update status to show pending if any subject is pending
        if (grade.status === 'pending' && group.status === 'approved') {
          group.status = 'pending';
          group.status_display = 'Pending Review';
        }
      });
      
      // Calculate GWA for each semester group
      const result = Array.from(grouped.values()).map(group => {
        const totalGradePoints = group.subjects.reduce((sum, subject) => {
          return sum + (Number(subject.grade_received) * subject.units);
        }, 0);
        
        group.total_units = group.subjects.reduce((sum, subject) => sum + subject.units, 0);
        group.general_weighted_average = group.total_units > 0 ? totalGradePoints / group.total_units : 0;
        
        // Determine merit eligibility
        const gwa = group.general_weighted_average;
        group.qualifies_for_merit_incentive = gwa <= 2.50 && group.all_approved;
        group.qualifies_for_basic_allowance = gwa <= 3.00 && group.all_approved;
        
        // Update status display based on all subjects
        if (group.all_approved) {
          group.status = 'approved';
          group.status_display = 'Approved';
        }
        
        // Include AI-calculated fields from any subject entry
        const anySubject = group.subjects.find(item => item.ai_gwa_calculated !== undefined);
        if (anySubject) {
          group.ai_gwa_calculated = anySubject.ai_gwa_calculated;
          group.ai_merit_level = anySubject.ai_merit_level;
        }
        
        return group;
      });
      
      setGroupedGrades(result);
    };
    
    groupBySemester();
  }, [grades]);

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

  const completedSemesters = groupedGrades.length;
  const approvedSemesters = groupedGrades.filter(g => g.all_approved).length;
  const completionPercentage = groupedGrades.length > 0 ? Math.round((approvedSemesters / completedSemesters) * 100) : 0;

  const averageGPA = groupedGrades.length > 0 
    ? (groupedGrades.reduce((sum, semester) => {
        return sum + semester.general_weighted_average;
      }, 0) / groupedGrades.length).toFixed(2)
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

  const handleViewGrade = (semester: GroupedSemester) => {
    setSelectedGrade(semester);
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

      {/* Page Guide Banner */}
      <PageGuideBanner 
        icon="📊"
        title="Submit Your Academic Grades"
        text="Submit your grades for each semester. Your GWA determines your eligibility: 2.5 or better for Basic Allowance, 1.75 or better for Merit Incentive. The system calculates your GWA automatically."
      />

      {groupedGrades.length === 0 && (
        <InfoNote 
          title="No Grades Submitted Yet"
          text="Click 'Submit Grades' to add your academic records. Include all subjects with their codes, units, and grades for accurate GWA calculation."
        />
      )}

      {/* Stats Overview Cards */}
      <div className="stats-overview">
        <div className="stat-card-modern">
          <div className="stat-icon-wrapper progress-icon">
            <span className="stat-emoji">🎓</span>
          </div>
          <div className="stat-details">
            <span className="stat-label">Submission Progress</span>
            <span className="stat-number">{completionPercentage}%</span>
            <span className="stat-description">{approvedSemesters} of {completedSemesters} semesters</span>
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
              {groupedGrades.some(g => g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive) ? '✅' : '⏳'}
            </span>
          </div>
          <div className="stat-details">
            <span className="stat-label">Allowance Status</span>
            <span className="stat-number">
              {groupedGrades.some(g => g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive) 
                ? 'Eligible' 
                : 'Pending'}
            </span>
            <span className="stat-description">
              {groupedGrades.some(g => g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive)
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
        {groupedGrades.length > 0 ? (
          <>
            <div className="section-header">
              <h2>📚 Submitted Grades</h2>
              <span className="grade-count">{groupedGrades.length} semester{groupedGrades.length !== 1 ? 's' : ''}</span>
            </div>
            <div className="grades-grid-modern">
              {groupedGrades.map((semester, index) => (
                <div key={`${semester.academic_year}-${semester.semester}`} className="grade-card-modern">
                  <div className="card-top">
                    <div className="semester-info">
                      <h3 className="semester-title">{semester.semester_display}</h3>
                      <span className="academic-year">{semester.academic_year}</span>
                    </div>
                    <span 
                      className={`status-badge-modern status-${semester.status}`}
                      style={{ backgroundColor: getStatusColor(semester.status) }}
                    >
                      {getStatusIcon(semester.status)} {semester.status_display}
                    </span>
                  </div>

                  <div className="card-divider"></div>

                  <div className="card-body-grade">
                    <div className="gwa-display">
                      <span className="gwa-label">General Weighted Average</span>
                      <span className="gwa-value">
                        {semester.ai_gwa_calculated ? 
                          Number(semester.ai_gwa_calculated).toFixed(2) : 
                          semester.general_weighted_average.toFixed(2)
                        }
                      </span>
                      <span className="gwa-subjects">{semester.subjects.length} subjects • {semester.total_units} units</span>
                      {semester.ai_merit_level && (
                        <div className="merit-level-badge">
                          <span className="merit-label">Merit Level:</span>
                          <span className={`merit-value ${semester.ai_merit_level.toLowerCase().replace(' ', '-')}`}>
                            {semester.ai_merit_level}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="eligibility-grid">
                      <div className={`eligibility-badge ${semester.qualifies_for_basic_allowance ? 'qualified' : 'not-qualified'}`}>
                        <span className="badge-icon">
                          {semester.qualifies_for_basic_allowance ? '✅' : '❌'}
                        </span>
                        <div className="badge-text">
                          <span className="badge-title">Basic Allowance</span>
                          <span className="badge-status">
                            {semester.qualifies_for_basic_allowance ? 'Qualified' : 'Not Qualified'}
                          </span>
                        </div>
                      </div>

                      <div className={`eligibility-badge ${semester.qualifies_for_merit_incentive ? 'qualified' : 'not-qualified'}`}>
                        <span className="badge-icon">
                          {semester.qualifies_for_merit_incentive ? '✅' : '❌'}
                        </span>
                        <div className="badge-text">
                          <span className="badge-title">Merit Incentive</span>
                          <span className="badge-status">
                            {semester.qualifies_for_merit_incentive ? 'Qualified' : 'Not Qualified'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="card-footer-grade">
                    <button 
                      className="btn-view-details"
                      onClick={() => handleViewGrade(semester)}
                    >
                      View Details
                    </button>
                    <span className="submission-timestamp">
                      📅 {new Date(semester.submitted_at).toLocaleDateString('en-US', {
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
                <span className="modal-gwa-number">
                  {selectedGrade.ai_gwa_calculated ? 
                    Number(selectedGrade.ai_gwa_calculated).toFixed(2) : 
                    selectedGrade.general_weighted_average.toFixed(2)
                  }
                </span>
                <div className="modal-gwa-bar">
                  <div 
                    className="modal-gwa-fill"
                    style={{ 
                      width: `${Math.max(0, Math.min(100, (5 - (selectedGrade.ai_gwa_calculated || selectedGrade.general_weighted_average)) * 25))}%`,
                      backgroundColor: (selectedGrade.ai_gwa_calculated || selectedGrade.general_weighted_average) <= 1.75 ? '#10b981' : 
                                     (selectedGrade.ai_gwa_calculated || selectedGrade.general_weighted_average) <= 2.25 ? '#3b82f6' : '#64748b'
                    }}
                  ></div>
                </div>
                {selectedGrade.ai_merit_level && (
                  <div className="modal-merit-display">
                    <span className="modal-merit-label">AI-Calculated Merit Level:</span>
                    <span className={`modal-merit-value ${selectedGrade.ai_merit_level.toLowerCase().replace(' ', '-')}`}>
                      {selectedGrade.ai_merit_level}
                    </span>
                  </div>
                )}
              </div>
              
              {/* Subjects List */}
              <div className="modal-subjects-list">
                <h4>📚 Subjects ({selectedGrade.subjects.length})</h4>
                <div className="modal-subjects-container">
                  {selectedGrade.subjects.map((subject) => (
                    <div key={subject.id} className="modal-subject-item">
                      <div className="modal-subject-left">
                        <div className="subject-code">{subject.subject_code}</div>
                        <div className="subject-name">{subject.subject_name}</div>
                      </div>
                      <div className="modal-subject-right">
                        <div className="subject-grade">{Number(subject.grade_received).toFixed(2)}</div>
                        <div className="subject-units">{subject.units} {subject.units === 1 ? 'unit' : 'units'}</div>
                      </div>
                    </div>
                  ))}
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