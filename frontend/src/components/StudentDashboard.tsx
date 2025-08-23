import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
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
        
        // Simplified - just use mock data for demo
        setAssignments([
          {
            id: 1,
            title: 'Submit Required Documents',
            description: 'Upload all required documents for TCU CEAA verification',
            due_date: '2025-08-25',
            submitted: false
          },
          {
            id: 2,
            title: 'Submit Grade Records',
            description: 'Upload your latest semester grades for allowance evaluation',
            due_date: '2025-08-30',
            submitted: false
          }
        ]);
        
        setDocuments([]);
        setGrades([]);
        setApplications([]);
        setStats({
          total_documents: 0,
          approved_documents: 0,
          total_applications: 0,
          approved_applications: 0
        });
        
        setError('');
      } catch (error: any) {
        console.error('Error fetching student data:', error);
        setError('Failed to load your information. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudentData();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getDaysUntilDue = (dueDate: string) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
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
    
    // Refresh data
    setTimeout(() => {
      // In real app, refetch documents data here
      setLoading(true);
      setTimeout(() => setLoading(false), 1000);
    }, 1000);
  };

  const handleGradeSubmissionSuccess = () => {
    setShowGradeForm(false);
    // Show dashboard notification  
    setNotificationType('success');
    setNotificationTitle('Grades Submitted Successfully!');
    setNotificationMessage('Your grades have been submitted for review. The allowance calculation will be processed within 3-5 business days.');
    setShowNotification(true);
    
    // Refresh data
    setTimeout(() => {
      // In real app, refetch grades data here
      setLoading(true);
      setTimeout(() => setLoading(false), 1000);
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

  const pendingAssignments = assignments.filter(a => !a.submitted);
  const completedAssignments = assignments.filter(a => a.submitted);

  return (
    <div className="student-dashboard-container">
      <div className="student-dashboard-content">
        {/* Welcome Section */}
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
                    size={80}
                    className="student-avatar-default"
                  />
                )}
              </div>
              <div className="welcome-text">
                <h2>{getGreeting()}, {user?.first_name}!</h2>
                <p>Welcome to your TCU CEAA student portal</p>
                <div className="student-info">
                  <span className="student-id">Student ID: {user?.student_id || 'Not assigned'}</span>
                  <span className="student-email">{user?.email}</span>
                </div>
              </div>
            </div>
            <div className="real-time-indicator">
              <div className="live-dot"></div>
              <span>Current Time</span>
              <div className="last-update">
                {currentDateTime.toLocaleDateString()} {currentDateTime.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
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
            {/* Quick Stats */}
            <div className="stats-grid">
              <div className="stat-card documents">
                <div className="stat-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="stat-content">
                  <div className="stat-number">{stats.total_documents}</div>
                  <div className="stat-label">Documents Submitted</div>
                  <div className="stat-sub">{stats.approved_documents} approved</div>
                </div>
              </div>
              <div className="stat-card grades">
                <div className="stat-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="stat-content">
                  <div className="stat-number">{grades.length}</div>
                  <div className="stat-label">Grade Submissions</div>
                </div>
              </div>
              <div className="stat-card applications">
                <div className="stat-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div className="stat-content">
                  <div className="stat-number">{stats.total_applications}</div>
                  <div className="stat-label">Allowance Applications</div>
                  <div className="stat-sub">{stats.approved_applications} approved</div>
                </div>
              </div>
              <div className="stat-card allowance">
                <div className="stat-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="stat-content">
                  <div className="stat-number">₱{applications.filter(a => a.status === 'approved').reduce((sum, app) => sum + app.amount, 0).toLocaleString()}</div>
                  <div className="stat-label">Total Allowance</div>
                </div>
              </div>
            </div>

            {/* Action Cards */}
            <div className="action-cards">
              <div className="action-card">
                <div className="action-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3>Submit Documents</h3>
                <p>Upload required documents for verification</p>
                <button 
                  className="action-button"
                  onClick={() => setShowDocumentForm(true)}
                >
                  Upload Documents
                </button>
              </div>
              <div className="action-card">
                <div className="action-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                    <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3>Submit Grades</h3>
                <p>Submit your semester grades for allowance evaluation</p>
                <button 
                  className="action-button"
                  onClick={() => setShowGradeForm(true)}
                >
                  Submit Grades
                </button>
              </div>
              <div className="action-card">
                <div className="action-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                    <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3>Apply for Allowance</h3>
                <p>Apply for Educational Assistance or Merit Incentive</p>
                <button className="action-button">Apply Now</button>
              </div>
            </div>
          </>
        )}

        {activeTab === 'documents' && (
          <div className="content-card">
            <div className="card-header">
              <h3>Document Submissions</h3>
              <button 
                className="add-button"
                onClick={() => setShowDocumentForm(true)}
              >
                + Upload Document
              </button>
            </div>
            <div className="card-content">
              {documents.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                      <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p>No documents submitted yet.</p>
                  <button className="action-button">Upload First Document</button>
                </div>
              ) : (
                <div className="submissions-list">
                  {documents.map((doc) => (
                    <div key={doc.id} className="submission-item">
                      <div className="submission-header">
                        <h4>{doc.document_type_display}</h4>
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(doc.status) }}
                        >
                          {doc.status_display}
                        </span>
                      </div>
                      <div className="submission-date">
                        Submitted: {new Date(doc.submitted_at).toLocaleDateString()}
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
              <h3>Grade Submissions</h3>
              <button 
                className="add-button"
                onClick={() => setShowGradeForm(true)}
              >
                + Submit Grades
              </button>
            </div>
            <div className="card-content">
              {grades.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                      <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <p>No grade submissions yet.</p>
                  <button className="action-button">Submit First Grades</button>
                </div>
              ) : (
                <div className="submissions-list">
                  {grades.map((grade) => (
                    <div key={grade.id} className="submission-item">
                      <div className="submission-header">
                        <h4>{grade.academic_year} - {grade.semester_display}</h4>
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(grade.status) }}
                        >
                          {grade.status_display}
                        </span>
                      </div>
                      <div className="grade-details">
                        <div className="grade-row">
                          <span>GWA: {grade.general_weighted_average}%</span>
                          <span>SWA: {grade.semestral_weighted_average}%</span>
                        </div>
                        <div className="eligibility-indicators">
                          <span className={`eligibility ${grade.qualifies_for_basic_allowance ? 'eligible' : 'not-eligible'}`}>
                            {grade.qualifies_for_basic_allowance ? '✅' : '❌'} Basic Allowance
                          </span>
                          <span className={`eligibility ${grade.qualifies_for_merit_incentive ? 'eligible' : 'not-eligible'}`}>
                            {grade.qualifies_for_merit_incentive ? '✅' : '❌'} Merit Incentive
                          </span>
                        </div>
                      </div>
                      <div className="submission-date">
                        Submitted: {new Date(grade.submitted_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'applications' && (
          <div className="content-card">
            <div className="card-header">
              <h3>Allowance Applications</h3>
              <button className="add-button">+ New Application</button>
            </div>
            <div className="card-content">
              {applications.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48">
                      <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p>No allowance applications yet.</p>
                  <button className="action-button">Apply for Allowance</button>
                </div>
              ) : (
                <div className="submissions-list">
                  {applications.map((app) => (
                    <div key={app.id} className="submission-item">
                      <div className="submission-header">
                        <h4>{app.application_type_display}</h4>
                        <span 
                          className="status-badge"
                          style={{ backgroundColor: getStatusColor(app.status) }}
                        >
                          {app.status_display}
                        </span>
                      </div>
                      <div className="application-amount">
                        Amount: ₱{app.amount.toLocaleString()}
                      </div>
                      <div className="submission-date">
                        Applied: {new Date(app.applied_at).toLocaleDateString()}
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
