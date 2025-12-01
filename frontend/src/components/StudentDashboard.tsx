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
import BasicQualification, { QualificationData } from './BasicQualification';
import FullApplicationForm from './FullApplicationForm';
import ModernLoadingSpinner from './ModernLoadingSpinner';
import { StudentIcon, EmailIcon, MoneyIcon, DocumentIcon, ChartIcon, WarningIcon, CheckIcon, GradeIcon, ApplicationIcon } from './Icons';
import TutorialModal, { HelpTooltip, InfoNote, PageGuideBanner } from './TutorialSystem';
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
}

interface AllowanceApplication {
  id: number;
  application_type_display: string;
  amount: number;
  status: string;
  status_display: string;
  applied_at: string;
}

interface FullApplicationData {
  id: number;
  school_year: string;
  semester: string;
  status: string;
  is_submitted: boolean;
  is_locked: boolean;
  submitted_at: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  [key: string]: any; // Allow other fields
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

interface QualificationCheckResponse {
  completed: boolean;
  qualified: boolean;
  data: any;
}

interface QualificationSubmitResponse {
  success: boolean;
  qualified: boolean;
  message: string;
  data: any;
}

interface FullApplicationRecord {
  id: number;
  school_year: string;
  semester: string;
  semester_display?: string;
  application_type?: string;
  application_type_display?: string;
  first_name: string;
  last_name: string;
  is_submitted: boolean;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
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
  const [showBasicQualification, setShowBasicQualification] = useState(false);
  const [hasCompletedQualification, setHasCompletedQualification] = useState(false);
  const [isQualified, setIsQualified] = useState(false);
  const [showFullApplication, setShowFullApplication] = useState(false);
  const [hasCompletedApplication, setHasCompletedApplication] = useState(false);
  const [applicationData, setApplicationData] = useState<{
    school_year: string;
    semester: string;
  } | null>(null);
  const [applicantType, setApplicantType] = useState<'new' | 'renewing' | null>(null);
  const [showTutorial, setShowTutorial] = useState(false);

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
          dashboardResponse,
          qualificationResponse,
          fullApplicationResponse
        ] = await Promise.all([
          apiClient.get('/tasks/'),
          apiClient.get('/documents/'),
          apiClient.get('/grades/'),
        apiClient.get('/applications/'),
        apiClient.get('/dashboard/student/'),
        apiClient.get('/basic-qualification/check_status/'),
        apiClient.get('/full-application/').catch(() => ({ data: [] })) // Gracefully handle if no applications exist
      ]);        setAssignments((assignmentsResponse.data as Assignment[]) || []);
        setDocuments((documentsResponse.data as DocumentSubmission[]) || []);
        setGrades((gradesResponse.data as GradeSubmission[]) || []);
        setApplications((applicationsResponse.data as AllowanceApplication[]) || []);
        
        const dashboardData = dashboardResponse.data as StudentDashboardData;
        if (dashboardData?.stats) {
          setStats(dashboardData.stats);
        }

        // Check basic qualification status
        const qualificationData = qualificationResponse.data as QualificationCheckResponse;
        setHasCompletedQualification(qualificationData.completed || false);
        setIsQualified(qualificationData.qualified || false);

        const qualificationApplicantType = qualificationData.data?.applicant_type as 'new' | 'renewing' | undefined;
        if (qualificationApplicantType) {
          setApplicantType(qualificationApplicantType);
        }

      // Check if user has already submitted a full application
      const fullApplications = Array.isArray(fullApplicationResponse.data)
        ? (fullApplicationResponse.data as FullApplicationRecord[])
        : [];
      if (fullApplications.length > 0) {
        // User has submitted application(s)
        setHasCompletedApplication(true);
        const latestApp = fullApplications[0]; // Most recent application
        setApplicationData({
          school_year: latestApp.school_year || '',
          semester: latestApp.semester_display || latestApp.semester || ''
        });
        const rawApplicationType = latestApp.application_type || latestApp.application_type_display;
        if (typeof rawApplicationType === 'string') {
          const lowerValue = rawApplicationType.toLowerCase();
          if (lowerValue.includes('renew')) {
            setApplicantType('renewing');
          } else if (lowerValue.includes('new')) {
            setApplicantType('new');
          }
        }
        console.log('✅ Found existing full application:', latestApp);
      } else {
        setHasCompletedApplication(false);
        console.log('ℹ️ No existing full application found');
      }      } catch (err: any) {
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
    
    // Removed automatic refresh interval to prevent form data loss
    // Users can manually refresh if needed
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

  const handleGradesRefresh = async () => {
    try {
      const response = await apiClient.get('/grades/');
      setGrades((response.data as GradeSubmission[]) || []);
    } catch (err) {
      console.error('Error refreshing grades:', err);
    }
  };

  const handleAllowanceApplicationSuccess = () => {
    setShowAllowanceForm(false);
    
    setNotificationType('success');
    setNotificationTitle('Application Submitted Successfully');
    setNotificationMessage('Your allowance application has been submitted and is under review. You will receive an email notification at your registered email address once your application is approved by the admin.');
    setShowNotification(true);
  };

  const handleApplicationsRefresh = async () => {
    try {
      const response = await apiClient.get('/applications/');
      setApplications((response.data as AllowanceApplication[]) || []);
    } catch (err) {
      console.error('Error refreshing applications:', err);
    }
  };

  const handleQualificationComplete = async (data: QualificationData) => {
    try {
      const response = await apiClient.post('/basic-qualification/submit/', data);
      const responseData = response.data as QualificationSubmitResponse;
      
      if (responseData.success) {
        setHasCompletedQualification(true);
        setIsQualified(responseData.qualified);
        setShowBasicQualification(false);
        if (data.applicant_type) {
          setApplicantType(data.applicant_type);
        }
        
        if (responseData.qualified) {
          // Show full application form immediately for qualified users
          setShowFullApplication(true);
          setNotificationType('success');
          setNotificationTitle('Qualification Completed!');
          setNotificationMessage('Congratulations! You have met all the basic qualification criteria. Please complete the full application form.');
        } else {
          setNotificationType('warning');
          setNotificationTitle('Qualification Not Met');
          setNotificationMessage('Unfortunately, you do not meet all the basic qualification criteria at this time. Please review the requirements.');
        }
        setShowNotification(true);
      }
    } catch (err: any) {
      console.error('Error submitting qualification:', err);
      setNotificationType('error');
      setNotificationTitle('Submission Failed');
      setNotificationMessage(err.response?.data?.error || 'Failed to submit qualification. Please try again.');
      setShowNotification(true);
    }
  };

  const handleQualificationCancel = () => {
    setShowBasicQualification(false);
  };

  const handleApplicationComplete = (data: { school_year: string; semester: string }) => {
    setHasCompletedApplication(true);
    setApplicationData(data);
    setShowFullApplication(false);
    setNotificationType('success');
    setNotificationTitle('Application Completed & Locked!');
    setNotificationMessage(`Your application for ${data.semester} ${data.school_year} has been successfully submitted and locked. You can now proceed to submit your requirements.`);
    setShowNotification(true);
    setActiveSection('requirements'); // Navigate to submission of requirements
  };

  const handleApplicationCancel = () => {
    setShowFullApplication(false);
  };

  if (loading) {
    return <ModernLoadingSpinner text="Loading your dashboard..." />;
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
  const hasPendingGrades = grades.some(g => g.status === 'pending');
  const hasAnyApprovedGrades = grades.some(g => g.status === 'approved');
  // Hide button if: not enough documents, has pending grades, or already has approved grades
  const canSubmitGrades = approvedDocuments >= 2 && !hasPendingGrades && !hasAnyApprovedGrades;
  
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
      case 'application':
        return (
          <div className="application-section">
            {!hasCompletedQualification ? (
              <div className="qualification-prompt">
                <div className="prompt-card">
                  <h2>Complete Basic Qualification</h2>
                  <p>Before you can access documents and grades, you need to complete the basic qualification criteria.</p>
                  <button 
                    className="start-qualification-btn"
                    onClick={() => setShowBasicQualification(true)}
                  >
                    Start Application Process
                  </button>
                </div>
              </div>
            ) : (
              <div className="qualification-completed">
                <div className="completion-card">
                  <div style={{ color: '#10b981' }}>
                    <CheckIcon size={48} />
                  </div>
                  <h2>Application Process {hasCompletedApplication ? 'Completed' : 'In Progress'}</h2>
                  {isQualified ? (
                    <>
                      {!hasCompletedApplication ? (
                        <>
                          <p>✓ Basic qualification completed successfully.</p>
                          <p>Next step: Complete the full application form with your personal, school, and family information.</p>
                          <button 
                            className="start-qualification-btn"
                            onClick={() => setShowFullApplication(true)}
                          >
                            Complete Application Form
                          </button>
                        </>
                      ) : (
                        <>
                          <div style={{ color: '#10b981', fontSize: '64px', marginBottom: '20px' }}>✓</div>
                          <p style={{ fontSize: '18px', fontWeight: 'bold', color: '#10b981' }}>Application Completed & Locked</p>
                          <p>Your application has been successfully submitted and locked.</p>
                          <p>You can now proceed to submit your documents and grades in the "Submission of Requirements" section.</p>
                          {applicationData && (
                            <div className="application-info-box">
                              <p style={{ margin: '5px 0' }}><strong>School Year:</strong> {applicationData.school_year}</p>
                              <p style={{ margin: '5px 0' }}><strong>Semester:</strong> {applicationData.semester}</p>
                            </div>
                          )}
                          <button 
                            className="start-qualification-btn"
                            onClick={() => handleSectionChange('requirements')}
                            style={{ marginTop: '20px' }}
                          >
                            Go to Submission of Requirements
                          </button>
                        </>
                      )}
                    </>
                  ) : (
                    <>
                      <p>You have completed the qualification form, but you do not meet all the criteria at this time.</p>
                      <button 
                        className="retake-qualification-btn"
                        onClick={() => setShowBasicQualification(true)}
                        style={{ marginTop: '10px' }}
                      >
                        Review/Update Qualification
                      </button>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      case 'requirements':
        if (!hasCompletedQualification || !isQualified) {
          return (
            <div className="locked-section">
              <div className="lock-message">
                <div style={{ color: '#f59e0b' }}>
                  <WarningIcon size={48} />
                </div>
                <h2>Submission of Requirements Locked</h2>
                <p>Please complete the basic qualification criteria in the Application section first.</p>
                <button onClick={() => handleSectionChange('application')}>
                  Go to Application
                </button>
              </div>
            </div>
          );
        }
        if (!hasCompletedApplication) {
          return (
            <div className="locked-section">
              <div className="lock-message">
                <div style={{ color: '#f59e0b' }}>
                  <WarningIcon size={48} />
                </div>
                <h2>Submission of Requirements Locked</h2>
                <p>Please complete the full application form in the Application section first.</p>
                <button onClick={() => handleSectionChange('application')}>
                  Go to Application
                </button>
              </div>
            </div>
          );
        }
        return (
          <DocumentRequirements 
            darkMode={darkMode}
            schoolYear={applicationData?.school_year}
            semester={applicationData?.semester}
            isRenewing={applicantType === 'renewing'}
          />
        );
      case 'documents':
        if (!hasCompletedQualification || !isQualified) {
          return (
            <div className="locked-section">
              <div className="lock-message">
                <div style={{ color: '#f59e0b' }}>
                  <WarningIcon size={48} />
                </div>
                <h2>Documents Locked</h2>
                <p>Please complete the basic qualification criteria in the Application section first.</p>
                <button onClick={() => handleSectionChange('application')}>
                  Go to Application
                </button>
              </div>
            </div>
          );
        }
        if (!hasCompletedApplication) {
          return (
            <div className="locked-section">
              <div className="lock-message">
                <div style={{ color: '#f59e0b' }}>
                  <WarningIcon size={48} />
                </div>
                <h2>Documents Locked</h2>
                <p>Please complete the full application form in the Application section first.</p>
                <button onClick={() => handleSectionChange('application')}>
                  Go to Application
                </button>
              </div>
            </div>
          );
        }
        return (
          <DocumentsPage
            documents={documents}
            darkMode={darkMode}
            onDocumentSubmissionSuccess={handleDocumentSubmissionSuccess}
          />
        );
      case 'grades':
        if (!hasCompletedQualification || !isQualified) {
          return (
            <div className="locked-section">
              <div className="lock-message">
                <div style={{ color: '#f59e0b' }}>
                  <WarningIcon size={48} />
                </div>
                <h2>Grades Locked</h2>
                <p>Please complete the basic qualification criteria in the Application section first.</p>
                <button onClick={() => handleSectionChange('application')}>
                  Go to Application
                </button>
              </div>
            </div>
          );
        }
        if (!hasCompletedApplication) {
          return (
            <div className="locked-section">
              <div className="lock-message">
                <div style={{ color: '#f59e0b' }}>
                  <WarningIcon size={48} />
                </div>
                <h2>Grades Locked</h2>
                <p>Please complete the full application form in the Application section first.</p>
                <button onClick={() => handleSectionChange('application')}>
                  Go to Application
                </button>
              </div>
            </div>
          );
        }
        return (
          <GradesPage
            grades={grades}
            darkMode={darkMode}
            canSubmitGrades={canSubmitGrades}
            onGradeSubmissionSuccess={handleGradeSubmissionSuccess}
            onRefresh={handleGradesRefresh}
          />
        );
      case 'application-details':
        return (
          <ApplicationDetailsPage
            applications={applications}
            darkMode={darkMode}
            canApplyForAllowance={canApplyForAllowance}
            onAllowanceApplicationSuccess={handleAllowanceApplicationSuccess}
            onRefresh={handleApplicationsRefresh}
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
              <p>Track your scholarship application progress</p>
            </div>

            {/* Page Guide Banner */}
            <PageGuideBanner 
              icon="👋"
              title="Welcome to Your Dashboard!"
              text="Complete all three steps below to submit your scholarship application: upload documents, submit grades, and fill out the application form. Click the ? button for detailed guidance."
            />

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
                    <p>{user?.email}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Application Progress */}
            <div className="progress-section">
              <div className="progress-header">
                <h3>
                  Application Progress
                  <HelpTooltip text="Complete all three steps in order. Each step must be approved before moving to the next." />
                </h3>
                <div className="overall-completion">
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
              </div>
            </div>

            {/* Helpful Information */}
            {!isDocumentsComplete && (
              <InfoNote 
                title="Next Step: Submit Documents"
                text="Start by uploading all required documents. Go to the Documents section using the sidebar or click on the Documents card below."
              />
            )}
            {isDocumentsComplete && !isGradesComplete && (
              <InfoNote 
                title="Next Step: Submit Grades"
                text="Great job on documents! Now submit your academic grades. Your GWA will determine your eligibility for allowances."
              />
            )}
            {isDocumentsComplete && isGradesComplete && !isApplicationComplete && (
              <InfoNote 
                title="Final Step: Complete Application"
                text="Almost there! Complete the Basic Qualification and Full Application forms to finish your submission."
              />
            )}
            {isApplicationComplete && (
              <InfoNote 
                title="Application Submitted Successfully!"
                text="Your application is complete and under review. You'll receive email notifications about your application status."
              />
            )}

            {/* Quick Stats */}
            <div className="stats-grid">
              <div className="stat-card documents">
                <div className="stat-icon">
                  <DocumentIcon size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{stats.total_documents}</div>
                  <div className="stat-label">Documents</div>
                </div>
              </div>
              <div className="stat-card grades">
                <div className="stat-icon">
                  <ChartIcon size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{grades.length}</div>
                  <div className="stat-label">Grade Reports</div>
                </div>
              </div>
              <div className="stat-card applications">
                <div className="stat-icon">
                  <MoneyIcon size={24} />
                </div>
                <div className="stat-content">
                  <div className="stat-number">{stats.total_applications}</div>
                  <div className="stat-label">Applications</div>
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
              </div>
              
              <div className="action-card" onClick={() => setActiveSection('grades')}>
                <div className="card-icon">
                  <GradeIcon size={48} />
                </div>
                <h3>Submit Grades</h3>
                <p>Submit your grades</p>
              </div>
              
              <div className="action-card" onClick={() => setActiveSection('application-details')}>
                <div className="card-icon">
                  <ApplicationIcon size={48} />
                </div>
                <h3>Application</h3>
                <p>View application status</p>
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

      {/* Tutorial Button - Fixed Bottom Right */}
      <button 
        className="tutorial-button" 
        onClick={() => setShowTutorial(true)}
        title="Help & Tutorial"
        aria-label="Open Tutorial"
      >
        ?
      </button>

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

      {/* Tutorial Modal */}
      <TutorialModal 
        isOpen={showTutorial}
        onClose={() => setShowTutorial(false)}
        page={activeSection}
      />

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

      {/* Basic Qualification Modal */}
      {showBasicQualification && (
        <BasicQualification
          onComplete={handleQualificationComplete}
          onCancel={handleQualificationCancel}
        />
      )}

      {/* Full Application Form Modal */}
      {showFullApplication && (
        <FullApplicationForm
          applicantType="renewing"
          onComplete={handleApplicationComplete}
          onCancel={handleApplicationCancel}
        />
      )}
    </div>
  );
};

export default StudentDashboard;