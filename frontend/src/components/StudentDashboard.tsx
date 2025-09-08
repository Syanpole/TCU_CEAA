import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';
import DocumentSubmissionForm from './DocumentSubmissionForm';
import GradeSubmissionForm from './GradeSubmissionForm';
import DefaultAvatar from './DefaultAvatar';
import NotificationModal from './NotificationModal';
import './StudentDashboard.css';

interface Assignment {
  id: number;
  title: string;
  description: string;
  due_date: string;
  submitted: boolean;
}

interface DocumentSubmission {
  id: number;
  document_type: string;
  document_type_display: string;
  status: string;
  status_display: string;
  submitted_at: string;
}

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
  status_display: string;
  submitted_at: string;
}

interface AllowanceApplication {
  id: number;
  application_type_display: string;
  amount: number;
  status: string;
  status_display: string;
  applied_at: string;
}

interface DashboardStats {
  total_documents: number;
  approved_documents: number;
  total_applications: number;
  approved_applications: number;
}

interface StudentDashboardData {
  stats?: DashboardStats;
}

const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [documents, setDocuments] = useState<DocumentSubmission[]>([]);
  const [grades, setGrades] = useState<GradeSubmission[]>([]);
  const [applications, setApplications] = useState<AllowanceApplication[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    total_documents: 0,
    approved_documents: 0,
    total_applications: 0,
    approved_applications: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [currentDateTime, setCurrentDateTime] = useState<Date>(new Date());
  const [showDocumentForm, setShowDocumentForm] = useState(false);
  const [showGradeForm, setShowGradeForm] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationType, setNotificationType] = useState<'success' | 'warning' | 'error' | 'info'>('info');
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationMessage, setNotificationMessage] = useState('');
  const [darkMode, setDarkMode] = useState(false);

  // Theme toggle function
  const toggleTheme = () => {
    setDarkMode(!darkMode);
    // Save preference to localStorage
    localStorage.setItem('studentDashboardTheme', !darkMode ? 'dark' : 'light');
  };

  // Load saved theme preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('studentDashboardTheme');
    if (savedTheme === 'dark') {
      setDarkMode(true);
    } else {
      setDarkMode(false); // Explicitly set to false for light mode
    }
  }, []);

  // Simple date/time update
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDateTime(new Date());
    }, 1000); // Update every second

    return () => clearInterval(timer);
  }, []);

  // Real-time update handler (removed complex logic)
  const handleRealTimeUpdate = () => {
    // Simplified - just update timestamp
    setCurrentDateTime(new Date());
  };

  useEffect(() => {
    const fetchStudentData = async () => {
      try {
        setLoading(true);
        
        // Try to fetch real data first
        try {
          const [documentsRes, gradesRes, applicationsRes, dashboardRes] = await Promise.all([
            apiClient.get<DocumentSubmission[]>('/documents/').catch(() => ({ data: [] as DocumentSubmission[] })),
            apiClient.get<GradeSubmission[]>('/grades/').catch(() => ({ data: [] as GradeSubmission[] })),
            apiClient.get<AllowanceApplication[]>('/applications/').catch(() => ({ data: [] as AllowanceApplication[] })),
            apiClient.get<StudentDashboardData>('/dashboard/student/').catch(() => ({ data: {} as StudentDashboardData }))
          ]);

          const fetchedDocuments = Array.isArray(documentsRes.data) ? documentsRes.data : [];
          const fetchedGrades = Array.isArray(gradesRes.data) ? gradesRes.data : [];
          const fetchedApplications = Array.isArray(applicationsRes.data) ? applicationsRes.data : [];

          setDocuments(fetchedDocuments);
          setGrades(fetchedGrades);
          setApplications(fetchedApplications);

          if (dashboardRes.data && dashboardRes.data.stats) {
            setStats(dashboardRes.data.stats);
          } else {
            // Calculate stats from fetched data
            setStats({
              total_documents: fetchedDocuments.length,
              approved_documents: fetchedDocuments.filter(d => d.status === 'approved').length,
              total_applications: fetchedApplications.length,
              approved_applications: fetchedApplications.filter(a => a.status === 'approved').length
            });
          }
        } catch (apiError) {
          // Use demo/sample data for development
        }

        // Always show these sample assignments for students to know what to do
        setAssignments([
          {
            id: 1,
            title: 'Submit Required Documents',
            description: 'Upload all required documents for TCU-CEAA verification (Birth Certificate, Report Card, etc.)',
            due_date: '',
            submitted: documents.length > 0
          },
          {
            id: 2,
            title: 'Submit Grade Records',
            description: 'Upload your latest semester grades for allowance evaluation and eligibility check',
            due_date: '',
            submitted: grades.length > 0
          },
          {
            id: 3,
            title: 'Complete Allowance Application',
            description: 'Apply for your educational assistance allowance once requirements are met',
            due_date: '',
            submitted: applications.length > 0
          }
        ]);
        
        setError('');
      } catch (error: any) {
        console.error('Error fetching student data:', error);
        setError('Unable to load some information. Please check your connection and try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudentData();
    
    // Set up interval to refresh data every 5 minutes (less frequent and less disruptive)
    const interval = setInterval(() => {
      // Only refresh if user is not currently interacting with modals
      if (!showDocumentForm && !showGradeForm && !showNotification) {
        fetchStudentData();
      }
    }, 300000); // 5 minutes instead of 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };



  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      case 'revision_needed': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const handleDocumentSubmissionSuccess = () => {
    setShowDocumentForm(false);
    // Show dashboard notification
    setNotificationType('success');
    setNotificationTitle('Document Uploaded Successfully!');
    setNotificationMessage('Your document has been submitted and is under review. You will be notified once it is approved by the admin.');
    setShowNotification(true);
    
    // Optionally refresh data without loading state
    setTimeout(() => {
      // In real app, refetch documents data here silently
      // No loading state to avoid visual disruption
    }, 2000);
  };

  const handleGradeSubmissionSuccess = () => {
    setShowGradeForm(false);
    // Show dashboard notification  
    setNotificationType('success');
    setNotificationTitle('Grades Submitted Successfully!');
    setNotificationMessage('Your grades have been submitted for review. The allowance calculation will be processed within 3-5 business days.');
    setShowNotification(true);
    
    // Optionally refresh data without loading state
    setTimeout(() => {
      // In real app, refetch grades data here silently
      // No loading state to avoid visual disruption
    }, 2000);
  };

  if (loading) {
    return (
      <div className="student-dashboard-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading your dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-dashboard-container">
        <div className="error-container">
          <div className="error-message">
            <h3>Error Loading Dashboard</h3>
            <p>{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="retry-button"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const pendingAssignments = assignments.filter(a => !a.submitted);
  const completedAssignments = assignments.filter(a => a.submitted);

  return (
    <div className={`student-dashboard-container ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      <div className="student-dashboard-content">
        {/* Welcome Section with Enhanced Greeting */}
        <div className="welcome-section">
          <div className="welcome-header">
            <div className="student-info-group">
              <div className="student-avatar">
                {user?.profile_image_url ? (
                  <img 
                    src={user.profile_image_url} 
                    alt="Profile" 
                    className="student-avatar-image"
                  />
                ) : (
                  <DefaultAvatar 
                    firstName={user?.first_name}
                    lastName={user?.last_name}
                    size={100}
                    className="student-avatar-default"
                  />
                )}
              </div>
              <div className="welcome-text">
                <h2>{getGreeting()}, {user?.first_name}!</h2>
                <p>Ready to continue your TCU-CEAA journey?</p>
                <div className="student-info">
                  <span className="student-id">👨‍🎓 ID: {user?.student_id || 'Not assigned'}</span>
                  <span className="student-email">📧 {user?.email}</span>
                </div>
              </div>
            </div>
            <div className="header-controls">
              <div className="real-time-indicator">
                <div className="live-dot"></div>
                <span>Live Dashboard</span>
                <div className="last-update">
                  {currentDateTime.toLocaleDateString()} • {currentDateTime.toLocaleTimeString()}
                </div>
              </div>
              <button 
                className="theme-toggle-btn"
                onClick={toggleTheme}
                title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
            </div>
          </div>
        </div>

        {/* Enhanced Quick Stats */}
        <div className="stats-grid">
          <div className="stat-card documents">
            <div className="stat-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="40" height="40">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.total_documents}</div>
              <div className="stat-label">Documents</div>
              <div className="stat-sub">✅ {stats.approved_documents} approved</div>
            </div>
          </div>
          <div className="stat-card grades">
            <div className="stat-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="40" height="40">
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{grades.length}</div>
              <div className="stat-label">Grade Reports</div>
              <div className="stat-sub">
                {grades.filter(g => g.qualifies_for_basic_allowance).length} qualify
              </div>
            </div>
          </div>
          <div className="stat-card applications">
            <div className="stat-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="40" height="40">
                <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.total_applications}</div>
              <div className="stat-label">Applications</div>
              <div className="stat-sub">✅ {stats.approved_applications} approved</div>
            </div>
          </div>
          <div className="stat-card allowance">
            <div className="stat-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="40" height="40">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">₱{applications.filter(a => a.status === 'approved').reduce((sum, app) => sum + app.amount, 0).toLocaleString()}</div>
              <div className="stat-label">Total Received</div>
              <div className="stat-sub">
                {applications.filter(a => a.status === 'pending').length} pending
              </div>
            </div>
          </div>
        </div>        {/* Enhanced Navigation Tabs */}
        <div className="dashboard-tabs">
          <button 
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab-button ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            Documents
          </button>
          <button 
            className={`tab-button ${activeTab === 'grades' ? 'active' : ''}`}
            onClick={() => setActiveTab('grades')}
          >
            Grades
          </button>
          <button 
            className={`tab-button ${activeTab === 'applications' ? 'active' : ''}`}
            onClick={() => setActiveTab('applications')}
          >
            Applications
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <>
            {/* Enhanced Progress Section */}
            <div className="progress-section">
              <div className="section-header">
                <h3>Your Educational Journey</h3>
                <p>Complete these steps to unlock your full TCU-CEAA benefits!</p>
              </div>
              <div className="progress-steps">
                {assignments.map((assignment, index) => {
                  return (
                    <div key={assignment.id} className={`progress-step ${assignment.submitted ? 'completed' : ''}`}>
                      <div className="step-number">
                        {assignment.submitted ? '✅' : index + 1}
                      </div>
                      <div className="step-content">
                        <h4>{assignment.title}</h4>
                        <p>{assignment.description}</p>
                        <div className="step-meta">
                          {assignment.submitted ? (
                            <span className="status-completed">🎉 Completed! Great job!</span>
                          ) : (
                            <span>⏳ Ready to complete</span>
                          )}
                        </div>
                      </div>
                      {!assignment.submitted && (
                        <div className="step-action">
                          {index === 0 && (
                            <button 
                              className="quick-action-btn"
                              onClick={() => setShowDocumentForm(true)}
                            >
                              Upload Now
                            </button>
                          )}
                          {index === 1 && (
                            <button 
                              className="quick-action-btn"
                              onClick={() => setShowGradeForm(true)}
                            >
                              Submit Grades
                            </button>
                          )}
                          {index === 2 && (
                            <button className="quick-action-btn">
                              Apply Now
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}        {activeTab === 'documents' && (
          <div className="content-card">
            <div className="card-header">
              <h3>📋 Document Submissions</h3>
              <button 
                className="add-button"
                onClick={() => setShowDocumentForm(true)}
              >
                📤 Upload Document
              </button>
            </div>
            <div className="card-content">
              {documents.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="60" height="60">
                      <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p>🎯 Ready to start? Upload your first document to begin your TCU-CEAA journey!</p>
                  <button 
                    className="action-button"
                    onClick={() => setShowDocumentForm(true)}
                  >
                    📤 Upload First Document
                  </button>
                </div>
              ) : (
                <div className="submissions-list">
                  {documents.map((doc) => (
                    <div key={doc.id} className="submission-item">
                      <div className="submission-header">
                        <h4>📄 {doc.document_type_display}</h4>
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(doc.status) }}
                        >
                          {doc.status_display}
                        </span>
                      </div>
                      <div className="submission-date">
                        📅 Submitted: {new Date(doc.submitted_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'grades' && (
          <div className="content-card">
            <div className="card-header">
              <h3>📈 Grade Submissions</h3>
              <button 
                className="add-button"
                onClick={() => setShowGradeForm(true)}
              >
                📊 Submit Grades
              </button>
            </div>
            <div className="card-content">
              {grades.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="60" height="60">
                      <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <p>🎓 Time to show off your academic achievements! Submit your grades to unlock allowance opportunities.</p>
                  <button 
                    className="action-button"
                    onClick={() => setShowGradeForm(true)}
                  >
                    📊 Submit First Grades
                  </button>
                </div>
              ) : (
                <div className="grades-scroll-container">
                  <div className="submissions-list">
                    {grades.map((grade) => (
                      <div key={grade.id} className="submission-item">
                        <div className="submission-header">
                          <h4>🎓 {grade.academic_year} - {grade.semester_display}</h4>
                          <span 
                            className="status-badge"
                            style={{ backgroundColor: getStatusColor(grade.status) }}
                          >
                            {grade.status_display}
                          </span>
                        </div>
                        <div className="grade-details">
                          <div className="grade-row">
                            <span>📈 GWA: {grade.general_weighted_average}%</span>
                            <span>📊 SWA: {grade.semestral_weighted_average}%</span>
                          </div>
                          <div className="eligibility-indicators">
                            <span className={`eligibility ${grade.qualifies_for_basic_allowance ? 'eligible' : 'not-eligible'}`}>
                              {grade.qualifies_for_basic_allowance ? '✅' : '❌'} Basic Allowance
                            </span>
                            <span className={`eligibility ${grade.qualifies_for_merit_incentive ? 'eligible' : 'not-eligible'}`}>
                              {grade.qualifies_for_merit_incentive ? '🌟' : '❌'} Merit Incentive
                            </span>
                          </div>
                        </div>
                        <div className="submission-date">
                          📅 Submitted: {new Date(grade.submitted_at).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'applications' && (
          <div className="content-card">
            <div className="card-header">
              <h3>💸 Allowance Applications</h3>
              <button className="add-button">💰 New Application</button>
            </div>
            <div className="card-content">
              {applications.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="60" height="60">
                      <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p>🚀 Ready to apply for your allowance? Once your documents and grades are approved, you can submit your application!</p>
                  <button className="action-button">💰 Apply for Allowance</button>
                </div>
              ) : (
                <div className="submissions-list">
                  {applications.map((app) => (
                    <div key={app.id} className="submission-item">
                      <div className="submission-header">
                        <h4>💰 {app.application_type_display}</h4>
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(app.status) }}
                        >
                          {app.status_display}
                        </span>
                      </div>
                      <div className="application-amount">
                        💵 Amount: ₱{app.amount.toLocaleString()}
                      </div>
                      <div className="submission-date">
                        📅 Applied: {new Date(app.applied_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Document Submission Form Modal */}
      {showDocumentForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <DocumentSubmissionForm
              onSubmissionSuccess={handleDocumentSubmissionSuccess}
              onCancel={() => setShowDocumentForm(false)}
            />
          </div>
        </div>
      )}

      {/* Grade Submission Form Modal */}
      {showGradeForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <GradeSubmissionForm
              onSubmissionSuccess={handleGradeSubmissionSuccess}
              onCancel={() => setShowGradeForm(false)}
            />
          </div>
        </div>
      )}

      {/* Dashboard Notification Modal */}
      <NotificationModal
        isOpen={showNotification}
        onClose={() => setShowNotification(false)}
        type={notificationType}
        title={notificationTitle}
        message={notificationMessage}
        autoClose={notificationType === 'success'}
        duration={5000}
      />
    </div>
  );
};

export default StudentDashboard;
