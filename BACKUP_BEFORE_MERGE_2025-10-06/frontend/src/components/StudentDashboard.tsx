import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';
import { formatCurrency } from '../utils/numberUtils';
import Sidebar from './Sidebar';
import DocumentsPage from './DocumentsPage';
import GradesPage from './GradesPage';
import ApplicationDetailsPage from './ApplicationDetailsPage';
import ProfileSettings from './ProfileSettings';
import DocumentSubmissionForm from './DocumentSubmissionForm';
import GradeSubmissionForm from './GradeSubmissionForm';
import AllowanceApplicationForm from './AllowanceApplicationForm';
import DefaultAvatar from './DefaultAvatar';
import NotificationModal from './NotificationModal';
import FastDocumentUploadSimple from './FastDocumentUploadSimple';
import DocumentRequirements from './DocumentRequirements';
import { StudentIcon, EmailIcon, MoneyIcon, DocumentIcon, ChartIcon, WarningIcon, CheckIcon, GradeIcon, ApplicationIcon } from './Icons';
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
  const [currentDateTime, setCurrentDateTime] = useState<Date>(new Date());
  const [showDocumentForm, setShowDocumentForm] = useState(false);
  const [showGradeForm, setShowGradeForm] = useState(false);
  const [showAllowanceForm, setShowAllowanceForm] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationType, setNotificationType] = useState<'success' | 'warning' | 'error' | 'info'>('info');
  const [notificationTitle, setNotificationTitle] = useState('');
  const [notificationMessage, setNotificationMessage] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [activeSection, setActiveSection] = useState('overview');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Theme toggle function
  const toggleTheme = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('studentDashboardTheme', newDarkMode ? 'dark' : 'light');
    
    window.dispatchEvent(new CustomEvent('themeChange', {
      detail: { darkMode: newDarkMode }
    }));
  };

  // Mobile menu toggle function
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Handle section change and close mobile menu
  const handleSectionChange = (section: string) => {
    setActiveSection(section);
    setIsMobileMenuOpen(false);
  };

  // Load saved theme preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('studentDashboardTheme');
    if (savedTheme === 'dark') {
      setDarkMode(true);
    } else {
      setDarkMode(false);
    }
  }, []);

  // Simple date/time update
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDateTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchStudentData = async () => {
      try {
        setLoading(true);
        setError('');
        
        console.log('Starting to fetch student data...');
        console.log('Current user:', user);
        console.log('Auth token:', localStorage.getItem('token'));

        const [
          assignmentsResponse,
          documentsResponse,
          gradesResponse,
          applicationsResponse,
          dashboardResponse
        ] = await Promise.all([
          apiClient.get('/tasks/'),
          apiClient.get('/documents/'),
          apiClient.get('/grades/'),
          apiClient.get('/applications/'),
          apiClient.get('/dashboard/student/')
        ]);

        setAssignments((assignmentsResponse.data as Assignment[]) || []);
        setDocuments((documentsResponse.data as DocumentSubmission[]) || []);
        setGrades((gradesResponse.data as GradeSubmission[]) || []);
        setApplications((applicationsResponse.data as AllowanceApplication[]) || []);
        
        const dashboardData = dashboardResponse.data as StudentDashboardData;
        if (dashboardData?.stats) {
          setStats(dashboardData.stats);
        }

      } catch (err: any) {
        console.error('Error fetching student data:', err);
        if (err.response) {
          console.error('Response status:', err.response.status);
          console.error('Response data:', err.response.data);
          setError(`API Error ${err.response.status}: ${err.response.data?.detail || 'Failed to load dashboard data'}`);
        } else if (err.request) {
          console.error('Request failed:', err.request);
          setError('Network error: Unable to connect to server. Please check if the backend is running.');
        } else {
          console.error('Error:', err.message);
          setError(`Error: ${err.message}`);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStudentData();
    
    const intervalId = setInterval(fetchStudentData, 300000);
    return () => clearInterval(intervalId);
  }, []);

  const refreshDocuments = async () => {
    try {
      const response = await apiClient.get('/documents/');
      setDocuments((response.data as DocumentSubmission[]) || []);
    } catch (err) {
      console.error('Error refreshing documents:', err);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'rejected': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const handleDocumentSubmissionSuccess = () => {
    setShowDocumentForm(false);
    refreshDocuments();
    
    setNotificationType('success');
    setNotificationTitle('Document Submitted Successfully');
    setNotificationMessage('Your document has been submitted and is now under review.');
    setShowNotification(true);
  };

  const handleGradeSubmissionSuccess = () => {
    setShowGradeForm(false);
    
    setNotificationType('success');
    setNotificationTitle('Grades Submitted Successfully');
    setNotificationMessage('Your academic records have been submitted and are being processed.');
    setShowNotification(true);
  };

  const handleAllowanceApplicationSuccess = () => {
    setShowAllowanceForm(false);
    
    setNotificationType('success');
    setNotificationTitle('Application Submitted Successfully');
    setNotificationMessage('Your allowance application has been submitted and is under review.');
    setShowNotification(true);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p className="loading-text">Loading your dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">
          <WarningIcon size={48} />
        </div>
        <h3>Unable to Load Dashboard</h3>
        <p>{error}</p>
        <button 
          className="retry-button"
          onClick={() => window.location.reload()}
        >
          Try Again
        </button>
      </div>
    );
  }

  // Check if grade submission is available
  const approvedDocuments = documents.filter(d => d.status === 'approved').length;
  const canSubmitGrades = approvedDocuments >= 2;
  
  // Check if allowance application is available
  const hasApprovedGrades = grades.some(g => g.status === 'approved' && (g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive));
  const canApplyForAllowance = hasApprovedGrades;

  // Calculate step completion status
  const isDocumentsComplete = approvedDocuments >= 2;
  const isGradesComplete = grades.some(g => g.status === 'approved');
  const isApplicationComplete = applications.some(a => a.status === 'pending' || a.status === 'approved' || a.status === 'disbursed');
  const isReviewComplete = applications.some(a => a.status === 'approved' || a.status === 'disbursed');

  // Calculate accurate application progress
  const calculateApplicationProgress = (): number => {
    let completedSteps = 0;
    const totalSteps = 4;

    if (isDocumentsComplete) completedSteps += 1;
    if (isGradesComplete) completedSteps += 1;
    if (isApplicationComplete) completedSteps += 1;
    if (isReviewComplete) completedSteps += 1;

    return Math.round((completedSteps / totalSteps) * 100);
  };

  const applicationProgress = calculateApplicationProgress();

  // Calculate individual card progress
  const documentsProgress = approvedDocuments >= 2 ? 100 : Math.round((approvedDocuments / 2) * 100);
  const gradesProgress = grades.length === 0 ? 0 : grades.some(g => g.status === 'approved') ? 100 : Math.round((grades.filter(g => g.status === 'pending' || g.status === 'approved').length / Math.max(grades.length, 1)) * 100);
  const applicationDetailsProgress = applications.length === 0 ? 0 : applications.some(a => a.status === 'approved' || a.status === 'disbursed') ? 100 : Math.round((applications.filter(a => a.status !== 'rejected').length / Math.max(applications.length, 1)) * 100);

  // Determine current step (the first incomplete step, or the last step if all complete)
  const getCurrentStep = (): number => {
    if (!isDocumentsComplete) return 1;
    if (!isGradesComplete) return 2;
    if (!isApplicationComplete) return 3;
    if (!isReviewComplete) return 4;
    return 4; // All complete
  };

  const currentStep = getCurrentStep();

  const renderContent = () => {
    switch (activeSection) {
      case 'requirements':
        return (
          <DocumentRequirements darkMode={darkMode} />
        );
      case 'documents':
        return (
          <DocumentsPage
            documents={documents}
            darkMode={darkMode}
            onDocumentSubmissionSuccess={handleDocumentSubmissionSuccess}
          />
        );
      case 'grades':
        return (
          <GradesPage
            grades={grades}
            darkMode={darkMode}
            canSubmitGrades={canSubmitGrades}
            onGradeSubmissionSuccess={handleGradeSubmissionSuccess}
          />
        );
      case 'application-details':
        return (
          <ApplicationDetailsPage
            applications={applications}
            darkMode={darkMode}
            canApplyForAllowance={canApplyForAllowance}
            onAllowanceApplicationSuccess={handleAllowanceApplicationSuccess}
          />
        );
      case 'profile':
        return <ProfileSettings />;
      case 'overview':
      default:
        return (
          <div className="overview-page">
            <div className="page-header">
              <h1>Student Dashboard</h1>
              <p>Track your application progress and complete required steps</p>
            </div>

            {/* Welcome Section */}
            <div className="welcome-card">
              <div className="welcome-content">
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
                    <p>Track your application progress and complete required steps</p>
                    <div className="student-info">
                      <span className="student-id">
                        <StudentIcon size={14} /> ID: {user?.student_id || 'Not assigned'}
                      </span>
                      <span className="student-email">
                        <EmailIcon size={14} /> {user?.email}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="real-time-indicator">
                  <div className="live-dot"></div>
                  <span>Live Dashboard</span>
                  <div className="last-update">
                    {currentDateTime.toLocaleDateString()} • {currentDateTime.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Application Progress */}
            <div className="progress-section">
              <div className="progress-header">
                <h3>Application Progress</h3>
                <div className="overall-completion">
                  <span className="completion-text">Overall Completion</span>
                  <span className="completion-percentage">{applicationProgress}%</span>
                </div>
              </div>
              
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${applicationProgress}%` }}></div>
              </div>

              <div className="progress-steps">
                <div className={`progress-step ${isDocumentsComplete ? 'completed' : currentStep === 1 ? 'current' : ''}`}>
                  <div className="step-circle">
                    {isDocumentsComplete ? <CheckIcon size={16} /> : <span className="step-number">1</span>}
                  </div>
                  <div className="step-info">
                    <h4>Documents</h4>
                  </div>
                </div>
                
                <div className={`step-connector ${isDocumentsComplete ? 'completed' : ''}`}></div>
                
                <div className={`progress-step ${isGradesComplete ? 'completed' : currentStep === 2 ? 'current' : ''}`}>
                  <div className="step-circle">
                    {isGradesComplete ? <CheckIcon size={16} /> : <span className="step-number">2</span>}
                  </div>
                  <div className="step-info">
                    <h4>Grades</h4>
                  </div>
                </div>
                
                <div className={`step-connector ${isGradesComplete ? 'completed' : ''}`}></div>
                
                <div className={`progress-step ${isApplicationComplete ? 'completed' : currentStep === 3 ? 'current' : ''}`}>
                  <div className="step-circle">
                    {isApplicationComplete ? <CheckIcon size={16} /> : <span className="step-number">3</span>}
                  </div>
                  <div className="step-info">
                    <h4>Application</h4>
                  </div>
                </div>
                
                <div className={`step-connector ${isApplicationComplete ? 'completed' : ''}`}></div>
                
                <div className={`progress-step ${isReviewComplete ? 'completed' : currentStep === 4 ? 'current' : ''}`}>
                  <div className="step-circle">
                    {isReviewComplete ? <CheckIcon size={16} /> : <span className="step-number">4</span>}
                  </div>
                  <div className="step-info">
                    <h4>Review</h4>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="stats-grid">
              <div className="stat-card documents">
                <div className="stat-icon">
                  <DocumentIcon size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{stats.total_documents}</div>
                  <div className="stat-label">Documents</div>
                  <div className="stat-sub">✅ {stats.approved_documents} approved</div>
                </div>
              </div>
              <div className="stat-card grades">
                <div className="stat-icon">
                  <ChartIcon size={24} />
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
                  <MoneyIcon size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{stats.total_applications}</div>
                  <div className="stat-label">Applications</div>
                  <div className="stat-sub">✅ {stats.approved_applications} processed</div>
                </div>
              </div>
            </div>

            {/* Quick Action Cards */}
            <div className="action-cards-grid">
              <div className="action-card" onClick={() => setActiveSection('documents')}>
                <div className="card-icon">
                  <DocumentIcon size={48} />
                </div>
                <h3>Documents</h3>
                <p>Upload required documents</p>
                <div className="card-progress">{documentsProgress}% Complete</div>
              </div>
              
              <div className="action-card" onClick={() => setActiveSection('grades')}>
                <div className="card-icon">
                  <GradeIcon size={48} />
                </div>
                <h3>Submit Grades</h3>
                <p>Submit your grades</p>
                <div className="card-progress">{gradesProgress}% Complete</div>
              </div>
              
              <div className="action-card" onClick={() => setActiveSection('application-details')}>
                <div className="card-icon">
                  <ApplicationIcon size={48} />
                </div>
                <h3>Application Details</h3>
                <p>Complete your application</p>
                <div className="card-progress">{applicationDetailsProgress}% Complete</div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className={`student-dashboard-container ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Sidebar */}
      <Sidebar 
        activeSection={activeSection}
        onSectionChange={handleSectionChange}
        darkMode={darkMode}
        isMobileMenuOpen={isMobileMenuOpen}
        onMobileMenuToggle={toggleMobileMenu}
      />
      
      {/* Mobile Header */}
      <div className="mobile-header">
        <button 
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label="Toggle Menu"
        >
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
        </button>
        <div className="mobile-logo">
          <span className="mobile-logo-text">TCU-CEAA</span>
        </div>
        <div className="mobile-user">
          <div className="mobile-user-avatar">
            {user?.first_name ? user.first_name.charAt(0) : 'U'}
          </div>
        </div>
      </div>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="mobile-overlay"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
      
      {/* Main Content */}
      <div className="main-content">
        {renderContent()}
      </div>

      {/* Theme Toggle - Fixed Bottom Right */}
      <div className="theme-toggle-container">
        <div className="theme-toggle-switch" onClick={toggleTheme}>
          <div className="theme-toggle-track">
            <div className={`theme-toggle-thumb ${darkMode ? 'dark' : 'light'}`}>
              <span className="theme-icon">
                {darkMode ? '🌙' : '☀️'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Notification Modal */}
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