import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import { safePercentage } from '../utils/numberUtils';
import './GradesManagement.css';

interface Grade {
  id: number;
  student_name: string;
  student_id: string;
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
                    <button className="action-btn view-btn">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                      </svg>
                      View Details
                    </button>
                    {grade.status === 'pending' && (
                      <>
                        <button className="action-btn approve-btn">
                          <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Approve
                        </button>
                        <button className="action-btn reject-btn">
                          <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Reject
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default GradesManagement;
