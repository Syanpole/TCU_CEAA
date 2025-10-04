import React from 'react';
import { safePercentage } from '../utils/numberUtils';
import './GradeDetailsModal.css';

interface Grade {
  id: number;
  student_name: string;
  student_id: string;
  academic_year: string;
  semester: string;
  semester_display: string;
  total_units: number;
  general_weighted_average: number | string;
  semestral_weighted_average: number | string;
  grade_sheet: string;
  has_failing_grades: boolean;
  has_incomplete_grades: boolean;
  has_dropped_subjects: boolean;
  ai_evaluation_completed: boolean;
  ai_evaluation_notes: string;
  ai_confidence_score: number;
  ai_extracted_grades: any;
  ai_grade_validation: any;
  ai_recommendations: string[];
  qualifies_for_basic_allowance: boolean;
  qualifies_for_merit_incentive: boolean;
  status: string;
  status_display: string;
  admin_notes: string;
  submitted_at: string;
  reviewed_at: string;
  reviewed_by_name: string;
}

interface GradeDetailsModalProps {
  grade: Grade;
  onClose: () => void;
}

const GradeDetailsModal: React.FC<GradeDetailsModalProps> = ({ grade, onClose }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="grade-details-modal-backdrop" onClick={handleBackdropClick}>
      <div className="grade-details-modal">
        <div className="modal-header">
          <div className="header-left">
            <h2>Grade Submission Details</h2>
            <div className="grade-id">ID: {grade.id}</div>
          </div>
          <button className="close-btn" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 18L18 6M6 6l12 12" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <div className="modal-content">
          {/* Student Information */}
          <section className="details-section">
            <h3 className="section-title">
              <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Student Information
            </h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Student Name</label>
                <div className="info-value">{grade.student_name}</div>
              </div>
              <div className="info-item">
                <label>Student ID</label>
                <div className="info-value">{grade.student_id}</div>
              </div>
            </div>
          </section>

          {/* Academic Information */}
          <section className="details-section">
            <h3 className="section-title">
              <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                <path d="M12 14l9-5-9-5-9 5 9 5z" />
                <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
              </svg>
              Academic Information
            </h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Academic Year</label>
                <div className="info-value">{grade.academic_year}</div>
              </div>
              <div className="info-item">
                <label>Semester</label>
                <div className="info-value">{grade.semester_display}</div>
              </div>
              <div className="info-item">
                <label>Total Units</label>
                <div className="info-value">{grade.total_units}</div>
              </div>
            </div>
          </section>

          {/* Grade Averages */}
          <section className="details-section">
            <h3 className="section-title">
              <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Grade Averages
            </h3>
            <div className="grades-display">
              <div className="grade-box">
                <div className="grade-label">General Weighted Average</div>
                <div className="grade-percentage">{safePercentage(grade.general_weighted_average)}</div>
              </div>
              <div className="grade-box">
                <div className="grade-label">Semestral Weighted Average</div>
                <div className="grade-percentage">{safePercentage(grade.semestral_weighted_average)}</div>
              </div>
            </div>
          </section>

          {/* Grade Status Indicators */}
          <section className="details-section">
            <h3 className="section-title">
              <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Grade Status
            </h3>
            <div className="status-indicators">
              <div className={`status-indicator ${grade.has_failing_grades ? 'negative' : 'positive'}`}>
                <span className="indicator-icon">{grade.has_failing_grades ? '❌' : '✅'}</span>
                <span className="indicator-label">
                  {grade.has_failing_grades ? 'Has Failing Grades' : 'No Failing Grades'}
                </span>
              </div>
              <div className={`status-indicator ${grade.has_incomplete_grades ? 'negative' : 'positive'}`}>
                <span className="indicator-icon">{grade.has_incomplete_grades ? '❌' : '✅'}</span>
                <span className="indicator-label">
                  {grade.has_incomplete_grades ? 'Has Incomplete Grades' : 'No Incomplete Grades'}
                </span>
              </div>
              <div className={`status-indicator ${grade.has_dropped_subjects ? 'negative' : 'positive'}`}>
                <span className="indicator-icon">{grade.has_dropped_subjects ? '❌' : '✅'}</span>
                <span className="indicator-label">
                  {grade.has_dropped_subjects ? 'Has Dropped Subjects' : 'No Dropped Subjects'}
                </span>
              </div>
            </div>
          </section>

          {/* Allowance Eligibility */}
          <section className="details-section">
            <h3 className="section-title">
              <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Allowance Eligibility
            </h3>
            <div className="eligibility-display">
              <div className={`eligibility-card ${grade.qualifies_for_basic_allowance ? 'eligible' : 'not-eligible'}`}>
                <div className="eligibility-icon">
                  {grade.qualifies_for_basic_allowance ? '✅' : '❌'}
                </div>
                <div className="eligibility-text">
                  <div className="eligibility-name">Basic Educational Assistance</div>
                  <div className="eligibility-status">
                    {grade.qualifies_for_basic_allowance ? 'Qualified (₱5,000)' : 'Not Qualified'}
                  </div>
                </div>
              </div>
              <div className={`eligibility-card ${grade.qualifies_for_merit_incentive ? 'eligible' : 'not-eligible'}`}>
                <div className="eligibility-icon">
                  {grade.qualifies_for_merit_incentive ? '✅' : '❌'}
                </div>
                <div className="eligibility-text">
                  <div className="eligibility-name">Merit Incentive</div>
                  <div className="eligibility-status">
                    {grade.qualifies_for_merit_incentive ? 'Qualified (₱5,000)' : 'Not Qualified'}
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* AI Analysis */}
          {grade.ai_evaluation_completed && (
            <section className="details-section">
              <h3 className="section-title">
                <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                  <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                AI Analysis
              </h3>
              <div className="ai-analysis">
                <div className="ai-confidence">
                  <label>AI Confidence Score</label>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${(grade.ai_confidence_score * 100)}%` }}
                    ></div>
                  </div>
                  <div className="confidence-text">{(grade.ai_confidence_score * 100).toFixed(1)}%</div>
                </div>
                {grade.ai_evaluation_notes && (
                  <div className="ai-notes">
                    <label>AI Evaluation Notes</label>
                    <pre className="notes-content">{grade.ai_evaluation_notes}</pre>
                  </div>
                )}
                {grade.ai_recommendations && grade.ai_recommendations.length > 0 && (
                  <div className="ai-recommendations">
                    <label>AI Recommendations</label>
                    <ul>
                      {grade.ai_recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Submission Status */}
          <section className="details-section">
            <h3 className="section-title">
              <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Submission Status
            </h3>
            <div className="status-display">
              <div className="status-badge-large" style={{ backgroundColor: getStatusColor(grade.status) }}>
                {grade.status_display}
              </div>
              <div className="submission-timeline">
                <div className="timeline-item">
                  <label>Submitted At</label>
                  <div className="timeline-value">{formatDate(grade.submitted_at)}</div>
                </div>
                {grade.reviewed_at && (
                  <div className="timeline-item">
                    <label>Reviewed At</label>
                    <div className="timeline-value">{formatDate(grade.reviewed_at)}</div>
                  </div>
                )}
                {grade.reviewed_by_name && (
                  <div className="timeline-item">
                    <label>Reviewed By</label>
                    <div className="timeline-value">{grade.reviewed_by_name}</div>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Admin Notes */}
          {grade.admin_notes && (
            <section className="details-section">
              <h3 className="section-title">
                <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                  <path d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                Admin Notes
              </h3>
              <div className="admin-notes">
                <pre className="notes-content">{grade.admin_notes}</pre>
              </div>
            </section>
          )}

          {/* Grade Sheet */}
          {grade.grade_sheet && (
            <section className="details-section">
              <h3 className="section-title">
                <svg viewBox="0 0 24 24" fill="currentColor" className="section-icon">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Grade Sheet Document
              </h3>
              <div className="document-preview">
                <a 
                  href={grade.grade_sheet} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="document-link"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Open Grade Sheet Document
                </a>
              </div>
            </section>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default GradeDetailsModal;
