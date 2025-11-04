import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import GradeDetailsModal from './GradeDetailsModal';
import './GradesManagement.css';

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

interface GradesManagementProps {
  onViewChange?: (view: string) => void;
}

const GradesManagement: React.FC<GradesManagementProps> = ({ onViewChange }) => {
  const [grades, setGrades] = useState<Grade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [semesterFilter, setSemesterFilter] = useState('');
  const [selectedGrade, setSelectedGrade] = useState<Grade | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [deletingGradeId, setDeletingGradeId] = useState<number | null>(null);

  // Helper function to safely format percentage values
  const safePercentage = (value: number | string): string => {
    const numValue = Number(value);
    if (isNaN(numValue)) return '0.00%';
    return `${numValue.toFixed(2)}%`;
  };

  useEffect(() => {
    const fetchGrades = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get<Grade[]>('/grades/');
        setGrades(response.data);
      } catch (err) {
        console.error('Error fetching grades:', err);
        setError('Failed to load grades. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchGrades();
  }, []);

  const filteredGrades = grades.filter(grade => {
    const matchesSearch = grade.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         grade.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         grade.academic_year.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === '' || grade.status === statusFilter;
    const matchesSemester = semesterFilter === '' || grade.semester === semesterFilter;
    return matchesSearch && matchesStatus && matchesSemester;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleViewDetails = async (gradeId: number) => {
    try {
      setLoadingDetails(true);
      const response = await apiClient.get<Grade>(`/grades/${gradeId}/`);
      setSelectedGrade(response.data);
    } catch (err) {
      console.error('Error fetching grade details:', err);
      alert('Failed to load grade details. Please try again.');
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleCloseDetails = () => {
    setSelectedGrade(null);
  };

  const handleDeleteGrade = async (gradeId: number, studentName: string) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete the grade submission for ${studentName}? This action cannot be undone.`
    );
    
    if (!confirmDelete) return;

    try {
      setDeletingGradeId(gradeId);
      await apiClient.delete(`/grades/${gradeId}/`);
      
      // Remove the grade from the local state
      setGrades(grades.filter(g => g.id !== gradeId));
      
      alert('Grade submission deleted successfully!');
    } catch (err) {
      console.error('Error deleting grade:', err);
      alert('Failed to delete grade submission. Please try again.');
    } finally {
      setDeletingGradeId(null);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2 className="loading-title">Loading Grades</h2>
          <p className="loading-text">Please wait...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-content">
          <div className="error-icon">⚠</div>
          <h2 className="error-title">Error Loading Grades</h2>
          <p className="error-message">{error}</p>
          <button 
            className="retry-btn"
            onClick={() => window.location.reload()}
          >
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="grades-management-container">
      <div className="grades-management-content">
        {/* Header */}
        <div className="management-header">
          <div className="header-content">
            <h1>Grades Management</h1>
            <p>Review and analyze all grade submissions in the TCU-CEAA system</p>
          </div>
          
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-number">{grades.length}</div>
              <div className="stat-label">Total Submissions</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{grades.filter(g => g.qualifies_for_basic_allowance).length}</div>
              <div className="stat-label">Basic Eligible</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{grades.filter(g => g.qualifies_for_merit_incentive).length}</div>
              <div className="stat-label">Merit Eligible</div>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="management-controls">
          <div className="search-section">
            <div className="search-input-container">
              <svg viewBox="0 0 24 24" fill="currentColor" className="search-icon">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search by student name, ID, or academic year..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
            <select
              value={semesterFilter}
              onChange={(e) => setSemesterFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Semesters</option>
              <option value="first">First Semester</option>
              <option value="second">Second Semester</option>
              <option value="summer">Summer</option>
            </select>
          </div>
        </div>

        {/* Grades List */}
        <div className="grades-list">
          {filteredGrades.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>No Grades Found</h3>
              <p>
                {searchTerm || statusFilter || semesterFilter
                  ? `No grades match your filters`
                  : 'No grade submissions have been made yet.'
                }
              </p>
              {(searchTerm || statusFilter || semesterFilter) && (
                <button 
                  className="clear-filters-btn"
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('');
                    setSemesterFilter('');
                  }}
                >
                  Clear Filters
                </button>
              )}
            </div>
          ) : (
            filteredGrades.map((grade) => (
              <div key={grade.id} className="grade-card">
                <div className="grade-header">
                  <div className="student-info">
                    <h3 className="student-name">{grade.student_name}</h3>
                    <p className="student-details">
                      ID: {grade.student_id} • {grade.academic_year} {grade.semester_display}
                    </p>
                  </div>
                  <div className="grade-status">
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(grade.status) }}
                    >
                      {grade.status_display}
                    </span>
                  </div>
                </div>

                <div className="grade-metrics">
                  <div className="metric-item">
                    <div className="metric-label">General Weighted Average</div>
                    <div className="metric-value">{safePercentage(grade.general_weighted_average)}</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-label">Semestral Weighted Average</div>
                    <div className="metric-value">{safePercentage(grade.semestral_weighted_average)}</div>
                  </div>
                </div>

                <div className="eligibility-section">
                  <div className="eligibility-title">Allowance Eligibility</div>
                  <div className="eligibility-indicators">
                    <div className={`eligibility-item ${grade.qualifies_for_basic_allowance ? 'eligible' : 'not-eligible'}`}>
                      <span className="eligibility-icon">
                        {grade.qualifies_for_basic_allowance ? '✅' : '❌'}
                      </span>
                      <span className="eligibility-label">Basic Allowance</span>
                    </div>
                    <div className={`eligibility-item ${grade.qualifies_for_merit_incentive ? 'eligible' : 'not-eligible'}`}>
                      <span className="eligibility-icon">
                        {grade.qualifies_for_merit_incentive ? '✅' : '❌'}
                      </span>
                      <span className="eligibility-label">Merit Incentive</span>
                    </div>
                  </div>
                </div>

                <div className="grade-footer">
                  <div className="submission-date">
                    Submitted: {formatDate(grade.submitted_at)}
                  </div>
                  <div className="grade-actions">
                    <button 
                      className="action-btn view-btn"
                      onClick={() => handleViewDetails(grade.id)}
                      disabled={loadingDetails || deletingGradeId === grade.id}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                      </svg>
                      {loadingDetails ? 'Loading...' : 'View Details'}
                    </button>
                    {grade.status === 'pending' && (
                      <>
                        <button 
                          className="action-btn approve-btn"
                          disabled={deletingGradeId === grade.id}
                        >
                          <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Approve
                        </button>
                        <button 
                          className="action-btn reject-btn"
                          disabled={deletingGradeId === grade.id}
                        >
                          <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Reject
                        </button>
                      </>
                    )}
                    <button 
                      className="action-btn delete-btn"
                      onClick={() => handleDeleteGrade(grade.id, grade.student_name)}
                      disabled={deletingGradeId === grade.id}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path fillRule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clipRule="evenodd" />
                      </svg>
                      {deletingGradeId === grade.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Grade Details Modal */}
      {selectedGrade && (
        <GradeDetailsModal 
          grade={selectedGrade} 
          onClose={handleCloseDetails}
        />
      )}
    </div>
  );
};

export default GradesManagement;
