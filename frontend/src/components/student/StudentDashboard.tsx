import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiClient } from '../../services/authService';
import { formatCurrency } from '../../utils/numberUtils';
import DocumentSubmissionForm from '../DocumentSubmissionForm';
import GradeSubmissionForm from '../GradeSubmissionForm';
import AllowanceApplicationForm from '../AllowanceApplicationForm';
import DefaultAvatar from '../DefaultAvatar';
import NotificationModal from '../NotificationModal';
import FastDocumentUploadSimple from '../FastDocumentUploadSimple';
import './StudentDashboard.css';
import './StudentDashboard.modern.css';

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

interface UploadResult {
  success: boolean;
  message?: string;
  data?: any;
}

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
  const [showAllowanceForm, setShowAllowanceForm] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationType, setNotificationType] = useState<'success' | 'warning' | 'error' | 'info'>('info');
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationMessage, setNotificationMessage] = useState('');
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('studentDashboardTheme');
    return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });
  
  // Enhanced smooth theme toggle function with modern transitions
  const toggleTheme = () => {
    // Add transition classes for smooth animations
    const container = document.querySelector('.student-dashboard-container');
    if (container) {
      container.classList.add('theme-transitioning');
      
      // Remove the transitioning class after animation completes
      setTimeout(() => {
        container.classList.remove('theme-transitioning');
      }, 300); // Faster transition for better UX
    }
    
    setDarkMode(prevMode => {
      const newMode = !prevMode;
      localStorage.setItem('studentDashboardTheme', newMode ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
      return newMode;
    });
  };

  // Initialize theme on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('studentDashboardTheme')) {
        setDarkMode(e.matches);
        document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [darkMode]);

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
        
        // Initialize default empty arrays
        let fetchedDocuments: DocumentSubmission[] = [];
        let fetchedGrades: GradeSubmission[] = [];
        let fetchedApplications: AllowanceApplication[] = [];
        
        // Try to fetch real data first
        try {
          const [documentsRes, gradesRes, applicationsRes, dashboardRes] = await Promise.all([
            apiClient.get<DocumentSubmission[]>('/documents/').catch(() => ({ data: [] as DocumentSubmission[] })),
            apiClient.get<GradeSubmission[]>('/grades/').catch(() => ({ data: [] as GradeSubmission[] })),
            apiClient.get<AllowanceApplication[]>('/applications/').catch(() => ({ data: [] as AllowanceApplication[] })),
            apiClient.get<StudentDashboardData>('/dashboard/student/').catch(() => ({ data: {} as StudentDashboardData }))
          ]);

          fetchedDocuments = Array.isArray(documentsRes.data) ? documentsRes.data : [];
          fetchedGrades = Array.isArray(gradesRes.data) ? gradesRes.data : [];
          fetchedApplications = Array.isArray(applicationsRes.data) ? applicationsRes.data : [];

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
              approved_applications: fetchedApplications.filter(a => a.status === 'approved' || a.status === 'disbursed').length
            });
          }
        } catch (apiError) {
          // Use demo/sample data for development
        }

        // Calculate approved documents count for assignments
        const currentApprovedDocuments = fetchedDocuments.filter(d => d.status === 'approved').length;

        // Always show these sample assignments for students to know what to do
        setAssignments([
          {
            id: 1,
            title: 'Submit Required Documents',
            description: 'Upload all required documents for TCU-CEAA verification (Birth Certificate, Report Card, etc.)',
            due_date: '',
            submitted: fetchedDocuments.length > 0
          },
          {
            id: 2,
            title: 'Submit Grade Records',
            description: `Upload your latest semester grades for allowance evaluation and eligibility check. Requires 2+ approved documents (Currently: ${currentApprovedDocuments}/2 approved)`,
            due_date: '',
            submitted: fetchedGrades.length > 0
          },
          {
            id: 3,
            title: 'Complete Allowance Application',
            description: 'Apply for your educational assistance allowance once requirements are met',
            due_date: '',
            submitted: fetchedApplications.length > 0
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
      if (!showDocumentForm && !showGradeForm && !showAllowanceForm && !showNotification) {
        fetchStudentData();
      }
    }, 300000); // 5 minutes instead of 30 seconds

    return () => clearInterval(interval);
  }, []);

  // Function to refresh documents after upload
  const refreshDocuments = async () => {
    try {
      const documentsRes = await apiClient.get<DocumentSubmission[]>('/documents/').catch(() => ({ data: [] as DocumentSubmission[] }));
      const fetchedDocuments = Array.isArray(documentsRes.data) ? documentsRes.data : [];
      setDocuments(fetchedDocuments);
    } catch (error) {
      console.error('Error refreshing documents:', error);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };



  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#22c55e';
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
    setNotificationMessage('Your document has been submitted and analyzed by our AI system. It has been instantly approved and processed automatically!');
    setShowNotification(true);
    
    // Refresh documents data to update the count
    setTimeout(async () => {
      try {
        const documentsRes = await apiClient.get<DocumentSubmission[]>('/documents/');
        const fetchedDocuments = Array.isArray(documentsRes.data) ? documentsRes.data : [];
        setDocuments(fetchedDocuments);
        
        // Update stats
        setStats(prevStats => ({
          ...prevStats,
          total_documents: fetchedDocuments.length,
          approved_documents: fetchedDocuments.filter((d: DocumentSubmission) => d.status === 'approved').length
        }));

        // Update assignments with new document count
        const currentApprovedDocuments = fetchedDocuments.filter((d: DocumentSubmission) => d.status === 'approved').length;
        setAssignments(prevAssignments => 
          prevAssignments.map((assignment, index) => {
            if (index === 0) {
              return { ...assignment, submitted: fetchedDocuments.length > 0 };
            } else if (index === 1) {
              return { 
                ...assignment, 
                description: `Upload your latest semester grades for allowance evaluation and eligibility check. Requires 2+ approved documents (Currently: ${currentApprovedDocuments}/2 approved)`
              };
            }
            return assignment;
          })
        );
      } catch (error) {
        console.log('Could not refresh documents:', error);
      }
    }, 1000);
  };

  const handleGradeSubmissionSuccess = () => {
    setShowGradeForm(false);
    // Show dashboard notification  
    setNotificationType('success');
    setNotificationTitle('Grades Submitted Successfully!');
    setNotificationMessage('Your grades have been submitted and analyzed by AI. They have been instantly approved and you can now apply for allowances!');
    setShowNotification(true);
    
    // Refresh data to update counts
    setTimeout(async () => {
      try {
        const [gradesRes, applicationsRes] = await Promise.all([
          apiClient.get<GradeSubmission[]>('/grades/').catch(() => ({ data: [] as GradeSubmission[] })),
          apiClient.get<AllowanceApplication[]>('/applications/').catch(() => ({ data: [] as AllowanceApplication[] }))
        ]);

        const fetchedGrades = Array.isArray(gradesRes.data) ? gradesRes.data : [];
        const fetchedApplications = Array.isArray(applicationsRes.data) ? applicationsRes.data : [];
        
        setGrades(fetchedGrades);
        setApplications(fetchedApplications);
        
        // Update assignments to show grade submission is complete
        setAssignments(prevAssignments => 
          prevAssignments.map((assignment, index) => {
            if (index === 1) {
              return { ...assignment, submitted: fetchedGrades.length > 0 };
            }
            return assignment;
          })
        );
      } catch (error) {
        console.log('Could not refresh data:', error);
      }
    }, 1000);
  };

  const handleAllowanceApplicationSuccess = () => {
    setShowAllowanceForm(false);
    // Show dashboard notification  
    setNotificationType('success');
    setNotificationTitle('Allowance Application Submitted!');
    setNotificationMessage('Your allowance application has been submitted successfully. It will be reviewed by admin within 3-5 business days. You will receive email updates on the status.');
    setShowNotification(true);
    
    // Refresh applications data
    setTimeout(async () => {
      try {
        const applicationsRes = await apiClient.get<AllowanceApplication[]>('/applications/');
        const fetchedApplications = Array.isArray(applicationsRes.data) ? applicationsRes.data : [];
        setApplications(fetchedApplications);
        
        // Update stats
        setStats(prevStats => ({
          ...prevStats,
          total_applications: fetchedApplications.length,
          approved_applications: fetchedApplications.filter(a => a.status === 'approved' || a.status === 'disbursed').length
        }));

        // Update assignments to show application is complete
        setAssignments(prevAssignments => 
          prevAssignments.map((assignment, index) => {
            if (index === 2) {
              return { ...assignment, submitted: fetchedApplications.length > 0 };
            }
            return assignment;
          })
        );
      } catch (error) {
        console.log('Could not refresh applications:', error);
      }
    }, 1000);
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

  // Check if grade submission is available
  const approvedDocuments = documents.filter(d => d.status === 'approved').length;
  const canSubmitGrades = approvedDocuments >= 2;
  
  // Check if allowance application is available
  const hasApprovedGrades = grades.some(g => g.status === 'approved' && (g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive));
  const canApplyForAllowance = hasApprovedGrades;

  const pendingAssignments = assignments.filter(a => !a.submitted);
  const completedAssignments = assignments.filter(a => a.submitted);

  return (
    <div className={`student-dashboard-container modern-student-dashboard ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      
      
      <div className="student-dashboard-content">
        {/* Welcome Section with Enhanced Greeting */}
        <div className="welcome-section">
          <div className="welcome-header">
            <div className="student-info-group">
              <div className="student-avatar user-avatar">
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
                <div className="online-indicator" title="Online"></div>
              </div>
              <div className="welcome-text">
                <h2 className="gradient-text">{getGreeting()}, {user?.first_name}! 👋</h2>
                <p className="welcome-subtitle">Ready to continue your TCU-CEAA journey?</p>
                <div className="student-info">
                  <span className="student-id info-chip">👨‍🎓 ID: {user?.student_id || 'Not assigned'}</span>
                  <span className="student-email info-chip">📧 {user?.email}</span>
                </div>
              </div>
            </div>
            <div className="header-controls">
              <div className="real-time-indicator">
                <div className="live-dot pulse-animation"></div>
                <div className="indicator-content">
                  <span className="live-label">Live Dashboard</span>
                  <div className="last-update">
                    📅 {currentDateTime.toLocaleDateString()} • ⏰ {currentDateTime.toLocaleTimeString()}
                  </div>
                </div>
              </div>
              <button 
                className="theme-toggle-btn theme-toggle"
                onClick={toggleTheme}
                title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                aria-label={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                <span className="theme-icon">{darkMode ? '☀️' : '🌙'}</span>
                <span className="theme-label">{darkMode ? 'Light' : 'Dark'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Enhanced Quick Stats */}
        <div className="stats-grid">
          <div 
            className="stat-card documents clickable" 
            onClick={() => setActiveTab('documents')}
            title="Click to view all documents"
          >
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
          <div 
            className="stat-card grades clickable"
            onClick={() => setActiveTab('grades')}
            title="Click to view all grade reports"
          >
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
          <div 
            className="stat-card applications clickable"
            onClick={() => setActiveTab('applications')}
            title="Click to view all applications"
          >
            <div className="stat-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="40" height="40">
                <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.total_applications}</div>
              <div className="stat-label">Applications</div>
              <div className="stat-sub">✅ {stats.approved_applications} processed</div>
            </div>
          </div>
          <div 
            className="stat-card allowance clickable"
            onClick={() => setActiveTab('allowance')}
            title="Click to view allowance summary"
          >
            <div className="stat-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="40" height="40">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{formatCurrency(applications.filter(a => a.status === 'approved' || a.status === 'disbursed').reduce((sum, app) => sum + Number(app.amount), 0))}</div>
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
          <button 
            className={`tab-button ${activeTab === 'allowance' ? 'active' : ''}`}
            onClick={() => setActiveTab('allowance')}
          >
            Allowance
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <>
            {/* Enhanced Progress Section */}
            <div className="progress-section">
              <div className="student-dashboard-section-header">
                <h3>Your Educational Journey</h3>
                <p>Complete these steps to unlock your full TCU-CEAA benefits!</p>
              </div>
              <div className="progress-steps">
                {assignments.map((assignment, index) => {
                  return (
                    <div key={assignment.id} className={`progress-step ${assignment.submitted ? 'completed' : ''}`}>
                      <div className="student-dashboard step-number">
                        {assignment.submitted ? '✅' : index + 1}
                      </div>
                      <div className="student-dashboard-step-content">
                        <h4>{assignment.title}</h4>
                        <p>{assignment.description}</p>
                        <div className="student-dashboard-step-meta">
                          {assignment.submitted ? (
                            <span className="status-completed">🎉 Completed! Great job!</span>
                          ) : (
                            <span>⏳ Ready to complete</span>
                          )}
                        </div>
                      </div>
                      {!assignment.submitted && (
                        <div className="student-dashboard-step-action">
                          {index === 0 && (
                            <button 
                              className="quick-action-btn"
                              onClick={() => setShowDocumentForm(true)}
                            >
                              Upload Now
                            </button>
                          )}
                          {index === 1 && (
                            <div>
                              {canSubmitGrades ? (
                                <button 
                                  className="quick-action-btn"
                                  onClick={() => setShowGradeForm(true)}
                                >
                                  Submit Grades
                                </button>
                              ) : (
                                <div className="requirement-warning">
                                  <p className="requirement-text">
                                    📋 Need {2 - approvedDocuments} more approved document{2 - approvedDocuments > 1 ? 's' : ''}
                                  </p>
                                  <button 
                                    className="quick-action-btn disabled"
                                    disabled
                                    title={`You need ${2 - approvedDocuments} more approved documents to submit grades`}
                                  >
                                    Submit Grades (Locked)
                                  </button>
                                </div>
                              )}
                            </div>
                          )}
                          {index === 2 && (
                            <div>
                              {canApplyForAllowance ? (
                                <button 
                                  className="quick-action-btn"
                                  onClick={() => setShowAllowanceForm(true)}
                                >
                                  Apply Now
                                </button>
                              ) : (
                                <div className="requirement-warning">
                                  <p className="requirement-text">
                                    📊 Need approved grades that qualify for allowances
                                  </p>
                                  <button 
                                    className="quick-action-btn disabled"
                                    disabled
                                    title="You need approved grades that qualify for allowances to apply"
                                  >
                                    Apply Now (Requirements not met)
                                  </button>
                                </div>
                              )}
                            </div>
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
              <div className="header-with-breadcrumb">
                <div className="breadcrumb">
                  <span 
                    className="breadcrumb-link" 
                    onClick={() => setActiveTab('overview')}
                  >
                    Overview
                  </span>
                  <span className="breadcrumb-separator">›</span>
                  <span className="breadcrumb-current">Documents</span>
                </div>
                <h3>📋 Document Submissions ({stats.total_documents} total)</h3>
              </div>
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
                          className={`status-badge status-${doc.status}`}
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
              <div className="header-with-breadcrumb">
                <div className="breadcrumb">
                  <span 
                    className="breadcrumb-link" 
                    onClick={() => setActiveTab('overview')}
                  >
                    Overview
                  </span>
                  <span className="breadcrumb-separator">›</span>
                  <span className="breadcrumb-current">Grades</span>
                </div>
                <h3>📈 Grade Submissions ({grades.length} total)</h3>
              </div>
              {canSubmitGrades ? (
                <button 
                  className="add-button"
                  onClick={() => setShowGradeForm(true)}
                >
                  📊 Submit Grades
                </button>
              ) : (
                <button 
                  className="add-button disabled"
                  disabled
                  title={`You need ${2 - approvedDocuments} more approved documents to submit grades`}
                >
                  📊 Submit Grades (Requires {2 - approvedDocuments} more approved docs)
                </button>
              )}
            </div>
            <div className="card-content">
              {!canSubmitGrades && (
                <div className="requirement-notice">
                  <div className="notice-icon">🔒</div>
                  <div className="notice-content">
                    <h4>Grade Submission Requirements</h4>
                    <p>
                      You need at least <strong>2 approved documents</strong> before you can submit your grades.
                    </p>
                    <div className="requirement-status">
                      <span className="status-item">
                        📄 Documents: {documents.length} submitted, {approvedDocuments} approved
                      </span>
                      <span className="status-item">
                        {approvedDocuments >= 2 ? '✅' : '❌'} Requirements: {approvedDocuments}/2 approved documents
                      </span>
                    </div>
                    <p className="help-text">
                      Submit more documents or wait for admin approval to unlock grade submission.
                    </p>
                  </div>
                </div>
              )}
              {grades.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="60" height="60">
                      <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <p>🎓 Time to show off your academic achievements! Submit your grades to unlock allowance opportunities.</p>
                  {canSubmitGrades ? (
                    <button 
                      className="action-button"
                      onClick={() => setShowGradeForm(true)}
                    >
                      📊 Submit First Grades
                    </button>
                  ) : (
                    <button 
                      className="action-button disabled"
                      disabled
                      title="Complete document requirements first"
                    >
                      📊 Submit First Grades (Requirements not met)
                    </button>
                  )}
                </div>
              ) : (
                <div className="grades-scroll-container">
                  <div className="submissions-list">
                    {grades.map((grade) => (
                      <div key={grade.id} className="submission-item">
                        <div className="submission-header">
                          <h4>🎓 {grade.academic_year} - {grade.semester_display}</h4>
                          <span 
                            className={`status-badge status-${grade.status}`}
                          >
                            {grade.status_display}
                          </span>
                        </div>
                        <div className="grade-details">
                          <div className="grade-row">
                            <span>📈 GWA: {Number(grade.general_weighted_average).toFixed(2)}%</span>
                            <span>📊 SWA: {Number(grade.semestral_weighted_average).toFixed(2)}%</span>
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
              {canApplyForAllowance ? (
                <button 
                  className="add-button"
                  onClick={() => setShowAllowanceForm(true)}
                >
                  💰 New Application
                </button>
              ) : (
                <button 
                  className="add-button disabled"
                  disabled
                  title="You need approved grades that qualify for allowances to apply"
                >
                  💰 New Application (Requirements not met)
                </button>
              )}
            </div>
            <div className="card-content">
              {!canApplyForAllowance && (
                <div className="requirement-notice">
                  <div className="notice-icon">🔒</div>
                  <div className="notice-content">
                    <h4>Allowance Application Requirements</h4>
                    <p>
                      You need <strong>approved grades that qualify for allowances</strong> before you can apply.
                    </p>
                    <div className="requirement-status">
                      <span className="status-item">
                        📊 Grades: {grades.length} submitted, {grades.filter(g => g.status === 'approved').length} approved
                      </span>
                      <span className="status-item">
                        {hasApprovedGrades ? '✅' : '❌'} Qualification: {hasApprovedGrades ? 'Eligible for allowances' : 'Need qualifying grades'}
                      </span>
                    </div>
                    <p className="help-text">
                      Submit grades with good academic performance to unlock allowance applications.
                    </p>
                  </div>
                </div>
              )}
              {applications.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="60" height="60">
                      <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p>🚀 Ready to apply for your allowance? Once your documents and grades are approved, you can submit your application!</p>
                  {canApplyForAllowance ? (
                    <button 
                      className="action-button"
                      onClick={() => setShowAllowanceForm(true)}
                    >
                      💰 Apply for Allowance
                    </button>
                  ) : (
                    <button 
                      className="action-button disabled"
                      disabled
                      title="Complete requirements first"
                    >
                      💰 Apply for Allowance (Requirements not met)
                    </button>
                  )}
                </div>
              ) : (
                <div className="submissions-list">
                  {applications.map((app) => (
                    <div key={app.id} className="submission-item">
                      <div className="submission-header">
                        <h4>💰 {app.application_type_display}</h4>
                        <span 
                          className={`status-badge status-${app.status}`}
                        >
                          {app.status_display}
                        </span>
                      </div>
                      <div className="application-amount">
                        💵 Amount: {formatCurrency(app.amount)}
                      </div>
                      <div className="submission-date">
                        📅 Applied: {new Date(app.applied_at).toLocaleDateString()}
                      </div>
                      {app.status === 'pending' && (
                        <div className="application-timeline">
                          ⏰ Expected processing: 3-5 business days
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'allowance' && (
          <div className="content-card">
            <div className="card-header">
              <div className="header-with-breadcrumb">
                <div className="breadcrumb">
                  <span 
                    className="breadcrumb-link" 
                    onClick={() => setActiveTab('overview')}
                  >
                    Overview
                  </span>
                  <span className="breadcrumb-separator">›</span>
                  <span className="breadcrumb-current">Allowance</span>
                </div>
                <h3>💰 Allowance Summary</h3>
              </div>
              <div className="count-badge">
                ₱{applications.filter(a => a.status === 'approved').reduce((sum, app) => sum + app.amount, 0).toLocaleString()} Total
              </div>
            </div>
            <div className="card-content">
              <div className="allowance-overview">
                <div className="allowance-stats-grid">
                  <div className="allowance-stat-item">
                    <div className="allowance-stat-icon">💰</div>
                    <div className="allowance-stat-content">
                      <div className="allowance-stat-value">
                        ₱{applications.filter(a => a.status === 'approved').reduce((sum, app) => sum + app.amount, 0).toLocaleString()}
                      </div>
                      <div className="allowance-stat-label">Total Received</div>
                    </div>
                  </div>
                  <div className="allowance-stat-item">
                    <div className="allowance-stat-icon">⏳</div>
                    <div className="allowance-stat-content">
                      <div className="allowance-stat-value">
                        ₱{applications.filter(a => a.status === 'pending').reduce((sum, app) => sum + app.amount, 0).toLocaleString()}
                      </div>
                      <div className="allowance-stat-label">Pending Amount</div>
                    </div>
                  </div>
                  <div className="allowance-stat-item">
                    <div className="allowance-stat-icon">📈</div>
                    <div className="allowance-stat-content">
                      <div className="allowance-stat-value">{applications.filter(a => a.status === 'approved').length}</div>
                      <div className="allowance-stat-label">Approved Applications</div>
                    </div>
                  </div>
                  <div className="allowance-stat-item">
                    <div className="allowance-stat-icon">⏰</div>
                    <div className="allowance-stat-content">
                      <div className="allowance-stat-value">{applications.filter(a => a.status === 'pending').length}</div>
                      <div className="allowance-stat-label">Pending Applications</div>
                    </div>
                  </div>
                </div>

                <div className="allowance-breakdown">
                  <h4>💵 Allowance Breakdown by Type</h4>
                  {applications.length === 0 ? (
                    <div className="empty-state">
                      <div className="empty-icon">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="60" height="60">
                          <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <p>🚀 No allowance applications yet! Complete your requirements and start earning your benefits.</p>
                      <button 
                        className="action-button"
                        onClick={() => setActiveTab('applications')}
                      >
                        💰 Go to Applications
                      </button>
                    </div>
                  ) : (
                    <div className="allowance-type-summary">
                      {Object.entries(
                        applications.reduce((acc, app) => {
                          if (!acc[app.application_type_display]) {
                            acc[app.application_type_display] = {
                              approved: 0,
                              pending: 0,
                              total_approved_amount: 0,
                              total_pending_amount: 0,
                              count: 0
                            };
                          }
                          acc[app.application_type_display].count++;
                          if (app.status === 'approved') {
                            acc[app.application_type_display].approved++;
                            acc[app.application_type_display].total_approved_amount += app.amount;
                          } else if (app.status === 'pending') {
                            acc[app.application_type_display].pending++;
                            acc[app.application_type_display].total_pending_amount += app.amount;
                          }
                          return acc;
                        }, {} as Record<string, any>)
                      ).map(([type, data]) => (
                        <div key={type} className="allowance-type-card">
                          <div className="allowance-type-header">
                            <h5>💼 {type}</h5>
                            <span className="allowance-type-count">{data.count} applications</span>
                          </div>
                          <div className="allowance-type-details">
                            <div className="allowance-detail-row">
                              <span className="allowance-detail-label">✅ Approved:</span>
                              <span className="allowance-detail-value">
                                {data.approved} apps (₱{data.total_approved_amount.toLocaleString()})
                              </span>
                            </div>
                            <div className="allowance-detail-row">
                              <span className="allowance-detail-label">⏳ Pending:</span>
                              <span className="allowance-detail-value">
                                {data.pending} apps (₱{data.total_pending_amount.toLocaleString()})
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="allowance-actions">
                  <button 
                    className="action-button"
                    onClick={() => setActiveTab('applications')}
                  >
                    📄 View All Applications
                  </button>
                  <button 
                    className="action-button"
                    onClick={() => setActiveTab('grades')}
                  >
                    📊 Check Grade Requirements
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Document Submission Form Modal */}
      {showDocumentForm && (
        <div className="compact-modal-overlay">
          <div className="compact-modal-content">
            <button 
              className="modal-close-btn"
              onClick={() => setShowDocumentForm(false)}
              aria-label="Close modal"
            >
              ×
            </button>
            <DocumentSubmissionForm
              onSubmissionSuccess={handleDocumentSubmissionSuccess}
              onCancel={() => setShowDocumentForm(false)}
            />
          </div>
        </div>
      )}

      {/* Grade Submission Form Modal */}
      {showGradeForm && (
        <div className="compact-modal-overlay">
          <div className="compact-modal-content">
            <button 
              className="modal-close-btn"
              onClick={() => setShowGradeForm(false)}
              aria-label="Close modal"
            >
              ×
            </button>
            <GradeSubmissionForm
              onSubmissionSuccess={handleGradeSubmissionSuccess}
              onCancel={() => setShowGradeForm(false)}
            />
          </div>
        </div>
      )}

      {/* Allowance Application Form Modal */}
      {showAllowanceForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <AllowanceApplicationForm
              onSubmissionSuccess={handleAllowanceApplicationSuccess}
              onCancel={() => setShowAllowanceForm(false)}
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