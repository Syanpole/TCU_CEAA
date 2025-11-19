import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import GradeDetailsModal from './GradeDetailsModal';
import './GradesManagement.css';

interface Subject {
  id: number;
  subject_code: string;
  subject_name: string;
  units: number;
  grade_received: number | null;
  status: string;
  ai_confidence_score: number;
  ai_merit_level: string;
  submitted_at: string;
  reviewed_at: string;
  admin_notes: string;
}

interface SemesterGroup {
  academic_year: string;
  semester: string;
  semester_label: string;
  subjects: Subject[];
  gwa: number | null;
  subject_count: number;
  total_units: number;
  status_breakdown: { [key: string]: number };
  all_approved: boolean;
  merit_level: string;
  qualifies_basic: boolean;
  qualifies_merit: boolean;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
}

interface StudentGrades {
  student_id: number;
  student_name: string;
  semester_groups: SemesterGroup[];
}

interface GradeDetailsModal {
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
  const [studentGrades, setStudentGrades] = useState<StudentGrades[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [semesterFilter, setSemesterFilter] = useState('');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [selectedGrade, setSelectedGrade] = useState<GradeDetailsModal | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    const fetchGroupedGrades = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get<StudentGrades[] | StudentGrades>('/grades/grouped_by_semester/');
        
        // Handle both single object and array responses
        let data: StudentGrades[] = Array.isArray(response.data) 
          ? response.data 
          : [response.data as StudentGrades];
        
        setStudentGrades(data);
      } catch (err) {
        console.error('Error fetching grouped grades:', err);
        setError('Failed to load grades. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchGroupedGrades();
  }, []);

  const toggleGroupExpansion = (key: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedGroups(newExpanded);
  };

  const getMeritColor = (merit_level: string): string => {
    switch (merit_level) {
      case 'HIGH_HONORS': return '#d4af37';
      case 'HONORS': return '#007bff';
      case 'MERIT': return '#28a745';
      case 'REGULAR': return '#6c757d';
      case 'BELOW_PASSING': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getMeritEmoji = (merit_level: string): string => {
    switch (merit_level) {
      case 'HIGH_HONORS': return '🥇';
      case 'HONORS': return '🥈';
      case 'MERIT': return '🥉';
      case 'REGULAR': return '📋';
      case 'BELOW_PASSING': return '⚠️';
      default: return '📊';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      case 'processing': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleViewDetails = async (subject: Subject, studentName: string, academicYear: string, semester: string) => {
    // For now, we'll create a minimal detail object from subject data
    // In a real app, you'd fetch full details from the API
    const detailGrade: GradeDetailsModal = {
      id: subject.id,
      student_name: studentName,
      student_id: '',
      academic_year: academicYear,
      semester: semester,
      semester_display: semester,
      total_units: subject.units,
      general_weighted_average: subject.grade_received || 0,
      semestral_weighted_average: subject.grade_received || 0,
      grade_sheet: '',
      has_failing_grades: (subject.grade_received || 0) > 3,
      has_incomplete_grades: subject.status !== 'approved',
      has_dropped_subjects: false,
      ai_evaluation_completed: false,
      ai_evaluation_notes: '',
      ai_confidence_score: subject.ai_confidence_score,
      ai_extracted_grades: {},
      ai_grade_validation: {},
      ai_recommendations: [],
      qualifies_for_basic_allowance: false,
      qualifies_for_merit_incentive: false,
      status: subject.status,
      status_display: subject.status,
      admin_notes: subject.admin_notes,
      submitted_at: subject.submitted_at,
      reviewed_at: subject.reviewed_at,
      reviewed_by_name: ''
    };
    setSelectedGrade(detailGrade);
  };

  const handleApproveSemesterGroup = async (studentId: number, academicYear: string, semester: string) => {
    const confirmApprove = window.confirm(
      `Are you sure you want to approve all subjects in this semester group? This will update eligibility and allowance amounts.`
    );
    
    if (!confirmApprove) return;

    try {
      const response = await apiClient.post('/grades/approve_semester_group/', {
        student_id: studentId,
        academic_year: academicYear,
        semester: semester
      });

      // Refresh the grouped grades
      const updatedResponse = await apiClient.get<StudentGrades[]>('/grades/grouped_by_semester/');
      setStudentGrades(updatedResponse.data);
      
      alert(`✅ Successfully approved all grades in this semester group!`);
    } catch (err) {
      console.error('Error approving semester group:', err);
      alert('Failed to approve semester group. Please try again.');
    }
  };

  const handleRecalculateSemesterGWA = async (studentId: number, academicYear: string, semester: string) => {
    try {
      const response = await apiClient.post('/grades/grouped_by_semester/', {
        student_id: studentId,
        academic_year: academicYear,
        semester: semester,
        action: 'recalculate_gwa'
      });

      // Refresh the grouped grades
      const updatedResponse = await apiClient.get<StudentGrades[]>('/grades/grouped_by_semester/');
      setStudentGrades(updatedResponse.data);
      
      alert(`✅ GWA recalculated for this semester group!`);
    } catch (err) {
      console.error('Error recalculating GWA:', err);
      alert('Failed to recalculate GWA. Please try again.');
    }
  };

  const filteredStudents = searchTerm.trim() === '' 
    ? studentGrades  // Show all students when search is empty
    : studentGrades.filter(student => {
        const matchesSearch = student.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             student.student_id.toString().includes(searchTerm);
        return matchesSearch;
      });

  const getTotalStats = (): { total: number; approved: number; pending: number; merit: number } => {
    let totals = { total: 0, approved: 0, pending: 0, merit: 0 };
    
    // Use filtered students for stats
    const statsSource = searchTerm.trim() === '' ? studentGrades : filteredStudents;
    
    statsSource.forEach(student => {
      student.semester_groups.forEach(group => {
        totals.total += group.subject_count || 0;
        totals.approved += group.approved_count || 0;
        totals.pending += group.pending_count || 0;
        if (group.qualifies_merit) totals.merit += 1;
      });
    });
    
    return totals;
  };

  const stats = getTotalStats();

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2 className="loading-title">Loading Grades</h2>
          <p className="loading-text">Grouping by semester and calculating GWA...</p>
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
            <h1>📚 Grades Management Dashboard</h1>
            <p>Review and manage grade submissions grouped by semester with automatic GWA calculation</p>
          </div>
          
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-number">{stats.total}</div>
              <div className="stat-label">Total Subjects</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.approved}</div>
              <div className="stat-label">Approved</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.pending}</div>
              <div className="stat-label">Pending</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{stats.merit}</div>
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
                placeholder="Search by student name or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>

        {/* Semester Groups */}
        <div className="semester-groups-container">
          {filteredStudents.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>No Students Found</h3>
              <p>
                {searchTerm
                  ? `No students match your search`
                  : 'No grade submissions have been made yet.'
                }
              </p>
              {searchTerm && (
                <button 
                  className="clear-filters-btn"
                  onClick={() => setSearchTerm('')}
                >
                  Clear Search
                </button>
              )}
            </div>
          ) : (
            filteredStudents.map((student) => (
              <div key={student.student_id} className="student-section">
                <div className="student-header">
                  <h2 className="student-name">{student.student_name}</h2>
                  <span className="student-id">ID: {student.student_id}</span>
                  <span className="semester-count">{student.semester_groups.length} semester{student.semester_groups.length !== 1 ? 's' : ''}</span>
                </div>

                <div className="semester-cards">
                  {student.semester_groups.map((group, groupIndex) => {
                    const groupKey = `${student.student_id}-${group.academic_year}-${group.semester}`;
                    const isExpanded = expandedGroups.has(groupKey);
                    const merritColor = getMeritColor(group.merit_level);
                    const merritEmoji = getMeritEmoji(group.merit_level);
                    const allowanceAmount = group.qualifies_merit ? '₱10,000' : group.qualifies_basic ? '₱5,000' : '₱0';

                    return (
                      <div key={groupIndex} className="semester-card" data-merit={group.merit_level} data-border-color={merritColor}>
                        {/* Card Header - Click to Expand */}
                        <div 
                          className="card-header"
                          onClick={() => toggleGroupExpansion(groupKey)}
                          data-merit-bg={group.merit_level}
                        >
                          <div className="header-left">
                            <div className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                              ▼
                            </div>
                            <div className="semester-info">
                              <div className="semester-title">{group.semester_label}</div>
                              <div className="semester-meta">{group.subject_count} subjects • {group.total_units} units</div>
                            </div>
                          </div>

                          <div className="header-right">
                            <div className="gwa-display" data-merit={group.merit_level}>
                              <div className="gwa-value">{group.gwa?.toFixed(2) || 'N/A'}</div>
                              <div className="gwa-label">GWA</div>
                            </div>
                            <div className="merit-display" data-merit={group.merit_level}>
                              <div className="merit-emoji">{merritEmoji}</div>
                              <div className="merit-label">{group.merit_level.replace(/_/g, ' ')}</div>
                            </div>
                            <div className="allowance-display" data-merit={group.merit_level}>
                              <div className="allowance-amount">
                                {allowanceAmount}
                              </div>
                              <div className="allowance-label">Allowance</div>
                            </div>
                            <div className="status-indicator">
                              {group.all_approved ? (
                                <span className="approved-badge">✅ Complete</span>
                              ) : (
                                <span className="pending-badge">⏳ {group.pending_count} Pending</span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Card Content - Subjects Table (Collapsible) */}
                        {isExpanded && (
                          <div className="card-content">
                            <table className="subjects-table">
                              <thead>
                                <tr>
                                  <th>Subject Code</th>
                                  <th>Subject Name</th>
                                  <th className="text-center">Units</th>
                                  <th className="text-center">Grade</th>
                                  <th className="text-center">Status</th>
                                  <th className="text-center">AI Confidence</th>
                                </tr>
                              </thead>
                              <tbody>
                                {group.subjects.map((subject, subIndex) => (
                                  <tr key={subIndex} className={`subject-row status-${subject.status}`} data-status={subject.status}>
                                    <td className="subject-code">{subject.subject_code}</td>
                                    <td className="subject-name">{subject.subject_name}</td>
                                    <td className="text-center">{subject.units}</td>
                                    <td className="text-center grade-cell">
                                      <span className="grade-badge" data-merit={subject.ai_merit_level}>
                                        {subject.grade_received?.toFixed(2) || '—'}
                                      </span>
                                    </td>
                                    <td className="text-center">
                                      <span className="status-badge" data-status={subject.status}>
                                        {subject.status}
                                      </span>
                                    </td>
                                    <td className="text-center">
                                      <div className="confidence-meter">
                                        <div className="confidence-bar" style={{ width: `${subject.ai_confidence_score * 100}%` }}></div>
                                        <span className="confidence-text">{(subject.ai_confidence_score * 100).toFixed(0)}%</span>
                                      </div>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>

                            {/* Summary Footer */}
                            <div className="card-footer">
                              <div className="footer-left">
                                <div className="summary-item">
                                  <span className="summary-label">Completion:</span>
                                  <span className="summary-value">{group.approved_count}/{group.subject_count} approved</span>
                                </div>
                              </div>
                              <div className="footer-right">
                                <button 
                                  className="action-btn approve-all-btn"
                                  onClick={() => handleApproveSemesterGroup(student.student_id, group.academic_year, group.semester)}
                                  disabled={group.all_approved}
                                >
                                  ✅ Approve All
                                </button>
                                <button 
                                  className="action-btn recalculate-btn"
                                  onClick={() => handleRecalculateSemesterGWA(student.student_id, group.academic_year, group.semester)}
                                >
                                  🔄 Recalculate
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Grade Details Modal */}
      {selectedGrade && (
        <GradeDetailsModal 
          grade={selectedGrade as any}
          onClose={() => setSelectedGrade(null)}
        />
      )}
    </div>
  );
};

export default GradesManagement;
