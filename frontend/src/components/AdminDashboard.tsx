
import './AdminDashboard.css';

interface DocumentSubmission {
  id: number;
  student_name: string;
  student_id: string;
  document_type_display: string;
  status: string;
  status_display: string;
  submitted_at: string;
}

interface GradeSubmission {
  id: number;
  student_name: string;
  student_id: string;
  academic_year: string;
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
  student_name: string;
  student_id: string;
  application_type_display: string;
  amount: number;
  status: string;
  status_display: string;
  applied_at: string;
}

interface BasicQualificationRecord {
  id: number;
  student: {
    id: number;
    username: string;
    student_id: string;
    first_name: string;
    last_name: string;
  };
  student_name: string;
  student_id: string;
  applicant_type: string;
  is_qualified: boolean;
  is_enrolled: boolean;
  is_resident: boolean;
  is_eighteen_or_older: boolean;
  is_registered_voter: boolean;
  parent_is_voter: boolean;
  has_good_moral_character: boolean;
  is_committed: boolean;
  completed_at: string;
}

interface FullApplicationRecord {
  id: number;
  user: {
    id: number;
    username: string;
    student_id: string;
    first_name: string;
    last_name: string;
  };
  student_name?: string;
  student_id?: string;
  
  // Application Details
  facebook_link: string;
  application_type: string;
  scholarship_type: string;
  school_year: string;
  semester: string;
  applying_for_merit: string;
  
  // Personal Information
  first_name: string;
  middle_name: string;
  last_name: string;
  house_no: string;
  street: string;
  zip_code: string;
  barangay: string;
  district: string;
  mobile_no: string;
  other_contact: string;
  email: string;
  date_of_birth: string;
  age: number | string;
  citizenship: string;
  sex: string;
  marital_status: string;
  religion: string;
  place_of_birth: string;
  years_of_residency: string;
  
  // School Information
  course_name: string;
  ladderized: string;
  year_level: string;
  swa_input: string;
  units_enrolled: string;
  course_duration: string;
  school_name: string;
  school_address: string;
  graduating_this_term: string;
  semesters_to_graduate: string;
  with_honors: string;
  transferee: string;
  shiftee: string;
  status: string;
  
  // Educational Background - Senior High School
  shs_attended: string;
  shs_type: string;
  shs_address: string;
  shs_years: string;
  shs_honors: string;
  
  // Educational Background - Junior High School
  jhs_attended: string;
  jhs_type: string;
  jhs_address: string;
  jhs_years: string;
  jhs_honors: string;
  
  // Educational Background - Elementary
  elem_attended: string;
  elem_type: string;
  elem_address: string;
  elem_years: string;
  elem_honors: string;
  
  // Parents Information - Father
  father_name: string;
  father_address: string;
  father_contact: string;
  father_occupation: string;
  father_place_of_work: string;
  father_education: string;
  father_deceased: boolean;
  
  // Parents Information - Mother
  mother_name: string;
  mother_address: string;
  mother_contact: string;
  mother_occupation: string;
  mother_place_of_work: string;
  mother_education: string;
  mother_deceased: boolean;
  
  // Status
  is_submitted: boolean;
  is_locked: boolean;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
}

interface AdminStats {
  total_students: number;
  total_documents: number;
  total_grades: number;
  total_applications: number;
  total_qualifications?: number;
  total_full_applications?: number;
}

interface AdminDashboardData {
  pending_documents: DocumentSubmission[];
  pending_grades: GradeSubmission[];
  pending_applications: AllowanceApplication[];
  stats: AdminStats;
}

interface AuditLog {
  id: number;
  user: {
    id: number | null;
    username: string;
    full_name: string;
  };
  action_type: string;
  action_type_display: string;
  action_description: string;
  severity: string;
  severity_display: string;
  target_model: string | null;
  target_object_id: number | null;
  target_user: {
    id: number;
    username: string;
    full_name: string;
  } | null;
  metadata: any;
  ip_address: string | null;
  timestamp: string;
}

interface AIStats {
  total_processed: number;
  auto_approved: number;
  auto_rejected: number;
  manual_review: number;
  average_confidence: number;
  recent_activities: {
    timestamp: string;
    action: string;
    confidence: number;
    decision: string;
  }[];
}

interface AnalyticsData {
  today_snapshot: {
    total_users: number;
    total_students: number;
    total_documents: number;
    total_grades: number;
    total_applications: number;
    documents_pending: number;
    grades_pending: number;
    applications_pending: number;
  };
  trends: {
    documents: { date: string; count: number }[];
    grades: { date: string; count: number }[];
    applications: { date: string; count: number }[];
  };
  status_distribution: {
    documents: { status: string; count: number }[];
    grades: { status: string; count: number }[];
    applications: { status: string; count: number }[];
  };
  top_students: {
    student_name: string;
    student_id: string;
    gwa: number;
    swa: number;
    academic_year: string;
    semester: string;
  }[];
  financial_summary: {
    total_disbursed: number;
    total_pending: number;
    total_committed: number;
  };
}

interface AdminDashboardProps {
  onViewChange?: (view: string) => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onViewChange }) => {
  const { user } = useAuth();
  const { notification, confirm: showConfirm, alert: showAlert } = useNotification();
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'audit' | 'ai-dashboard' | 'face-verification' | 'qualifications' | 'applications'>('overview');
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [aiStats, setAiStats] = useState<AIStats | null>(null);
  const [basicQualifications, setBasicQualifications] = useState<BasicQualificationRecord[]>([]);
  const [fullApplications, setFullApplications] = useState<FullApplicationRecord[]>([]);
  const [selectedQualification, setSelectedQualification] = useState<BasicQualificationRecord | null>(null);
  const [selectedApplication, setSelectedApplication] = useState<FullApplicationRecord | null>(null);
  const [showQualificationModal, setShowQualificationModal] = useState(false);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<{ [key: string]: boolean }>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [auditFilter, setAuditFilter] = useState<string>('all'); // 'all', 'ai', 'admin', 'user'
  const [showReasonModal, setShowReasonModal] = useState(false);
  const [deletionReason, setDeletionReason] = useState('');
  const [pendingDeleteGrade, setPendingDeleteGrade] = useState<{id: number, name: string} | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        try {
          const response = await apiClient.get<AdminDashboardData>('/dashboard/admin/');
          setDashboardData(response.data);
        } catch (apiError) {
          // If API fails, try to get individual data
          
          try {
            const [documentsRes, gradesRes, applicationsRes, usersRes] = await Promise.all([
              apiClient.get('/documents/').catch(() => ({ data: [] })),
              apiClient.get('/grades/').catch(() => ({ data: [] })),
              apiClient.get('/applications/').catch(() => ({ data: [] })),
              apiClient.get('/students/').catch(() => ({ data: [] }))
            ]);

            // Process the data if available
            const documents = Array.isArray(documentsRes.data) ? documentsRes.data : [];
            const grades = Array.isArray(gradesRes.data) ? gradesRes.data : [];
            const applications = Array.isArray(applicationsRes.data) ? applicationsRes.data : [];
            const users = Array.isArray(usersRes.data) ? usersRes.data : [];

            setDashboardData({
              pending_documents: documents.filter((doc: any) => doc.status === 'pending') || [],
              pending_grades: grades.filter((grade: any) => grade.status === 'pending') || [],
              pending_applications: applications.filter((app: any) => app.status === 'pending') || [],
              stats: {
                total_students: users.length,
                total_documents: documents.length,
                total_grades: grades.length,
                total_applications: applications.length
              }
            });
          } catch (individualError) {
            // Use demo data structure
            setDashboardData({
              pending_documents: [],
              pending_grades: [],
              pending_applications: [],
              stats: {
                total_students: 0,
                total_documents: 0,
                total_grades: 0,
                total_applications: 0
              }
            });
          }
        }
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please check your connection and try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    
    // Removed automatic refresh to prevent data loss when filling forms
    // Admins can use manual refresh buttons if needed
  }, []);

  // Function to manually refresh data
  const refreshDashboardData = async () => {
    try {
      const response = await apiClient.get<AdminDashboardData>('/dashboard/admin/');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error refreshing dashboard data:', error);
    }
  };

  // Fetch Analytics Data
  const fetchAnalyticsData = async () => {
    try {
      const response = await apiClient.get<AnalyticsData>('/analytics/');
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  // Fetch Audit Logs
  const fetchAuditLogs = async (limit: number = 50) => {
    try {
      const response = await apiClient.get<{logs: AuditLog[]; count: number}>(`/audit-logs/?limit=${limit}`);
      setAuditLogs(response.data.logs);
    } catch (error) {
      console.error('Error fetching audit logs:', error);
    }
  };

  // Fetch AI Statistics
  const fetchAIStats = async () => {
    try {
      const response = await apiClient.get<AIStats>('/ai-stats/');
      setAiStats(response.data);
    } catch (error) {
      console.error('Error fetching AI stats:', error);
    }
  };

  // Fetch Basic Qualifications
  const fetchBasicQualifications = async () => {
    try {
      const response = await apiClient.get<BasicQualificationRecord[]>('/basic-qualification/');
      setBasicQualifications(response.data || []);
    } catch (error) {
      console.error('Error fetching basic qualifications:', error);
      setBasicQualifications([]);
    }
  };

  // Fetch Full Applications
  const fetchFullApplications = async () => {
    try {
      const response = await apiClient.get<FullApplicationRecord[]>('/full-application/');
      setFullApplications(response.data || []);
    } catch (error) {
      console.error('Error fetching full applications:', error);
      setFullApplications([]);
    }
  };

  // Fetch data based on active tab
  useEffect(() => {
    if (activeTab === 'analytics' && !analyticsData) {
      fetchAnalyticsData();
    } else if (activeTab === 'audit' && auditLogs.length === 0) {
      fetchAuditLogs();
      fetchAIStats();
    }
  }, [activeTab]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Safe function to format numbers with 2 decimal places
  const safeToFixed = (value: number | string | null | undefined): string => {
    if (value === null || value === undefined || value === '') {
      return '0.00';
    }
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    return isNaN(numValue) ? '0.00' : numValue.toFixed(2);
  };

  const handleQuickAction = async (actionType: string, itemId: number, newStatus: string) => {
    const actionKey = `${actionType}_${itemId}`;
    
    try {
      // Set loading state for this specific action
      setActionLoading(prev => ({ ...prev, [actionKey]: true }));
      
      let endpoint = '';
      let payload = {};
      
      if (actionType === 'document') {
        endpoint = `/documents/${itemId}/review/`;
        payload = { status: newStatus, admin_notes: `Quick action: ${newStatus} by admin` };
      } else if (actionType === 'grade') {
        endpoint = `/grades/${itemId}/review/`;
        payload = { status: newStatus, admin_notes: `Quick action: ${newStatus} by admin` };
      } else if (actionType === 'application') {
        endpoint = `/applications/${itemId}/process/`;
        payload = { status: newStatus, admin_notes: `Quick action: ${newStatus} by admin` };
      }
      
      await apiClient.post(endpoint, payload);
      
      // Refresh dashboard data immediately
      await refreshDashboardData();
      
      // Show success message
      const actionNames = {
        'document': 'Document',
        'grade': 'Grade submission',
        'application': 'Application'
      };
      setSuccessMessage(`${actionNames[actionType as keyof typeof actionNames]} ${newStatus} successfully!`);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
      
    } catch (error) {
      console.error(`Error updating ${actionType}:`, error);
      // Show error message to user
      alert(`Failed to ${newStatus} ${actionType}. Please try again.`);
    } finally {
      // Clear loading state
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  const handleReviewAction = (actionType: string, itemId: number) => {
    // Navigate to detailed review page
    if (onViewChange) {
      switch (actionType) {
        case 'document':
          onViewChange('documents');
          break;
        case 'grade':
          onViewChange('grades');
          break;
        case 'application':
          onViewChange('applications');
          break;
        default:
          console.log(`Review ${actionType} with ID: ${itemId}`);
      }
    } else {
      console.log(`Review ${actionType} with ID: ${itemId}`);
    }
  };

  const handleDeleteGrade = async (gradeId: number, studentName: string) => {
    const confirmed = window.confirm(
      `⚠️ Are you sure you want to delete this grade submission for ${studentName}?\n\n` +
      `This action cannot be undone and will permanently remove the grade record from the system.`
    );
    
    if (!confirmed) return;
    
    // Show custom reason modal
    setPendingDeleteGrade({ id: gradeId, name: studentName });
    setDeletionReason('');
    setShowReasonModal(true);
  };

  const confirmDeleteWithReason = async () => {
    if (!pendingDeleteGrade || !deletionReason.trim()) {
      alert('Please provide a reason for deletion.');
      return;
    }

    const actionKey = `delete_grade_${pendingDeleteGrade.id}`;
    
    try {
      setActionLoading(prev => ({ ...prev, [actionKey]: true }));
      
      await apiClient.delete(`/grades/${pendingDeleteGrade.id}/`, {
        params: { reason: deletionReason }
      });
      
      // Close modal and reset state
      setShowReasonModal(false);
      setPendingDeleteGrade(null);
      setDeletionReason('');
      
      // Refresh dashboard data
      await refreshDashboardData();
      
      setSuccessMessage(`Grade submission deleted successfully!`);
      setTimeout(() => setSuccessMessage(null), 3000);
      
    } catch (error) {
      console.error('Error deleting grade:', error);
      alert('Failed to delete grade submission. Please try again.');
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  const getPriorityLevel = (item: any) => {
    const submitDate = new Date(item.submitted_at || item.applied_at);
    const now = new Date();
    const daysOld = Math.floor((now.getTime() - submitDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysOld >= 7) return 'high';
    if (daysOld >= 3) return 'medium';
    return 'low';
  };

  if (loading) {
    return <ModernLoadingSpinner text="Loading Admin Dashboard..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-content">
          <div className="error-icon">⚠</div>
          <h2 className="error-title">Error Loading Dashboard</h2>
          <p className="error-message">{error}</p>
          <button 
            className="retry-btn"
            onClick={() => window.location.reload()}
          >
            RETRY CONNECTION
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-container">
      <div className="admin-dashboard-content">
        {/* Success Message */}
        {successMessage && (
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: '#10b981',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: 1000,
            animation: 'slideIn 0.3s ease-out'
          }}>
            ✅ {successMessage}
          </div>
        )}

        {/* Header Section */}
        <div className="command-center-header">
          <div className="header-grid">
            <div className="command-title">
              <div className="status-indicator">
                <div className="pulse-dot"></div>
                <span>Online</span>
              </div>
              <h1>Admin Dashboard</h1>
              <p>TCU-CEAA Management System</p>
            </div>
            <div className="admin-profile" onClick={() => onViewChange && onViewChange('profile')}>
              <div className="profile-avatar">
                <span>{user?.first_name?.[0]}{user?.last_name?.[0]}</span>
              </div>
              <div className="profile-info">
                <div className="profile-name">{user?.first_name} {user?.last_name}</div>
                <div className="profile-role">Administrator</div>
                <div className="profile-status">Active</div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="dashboard-tabs">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
            </svg>
            Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M16 11V3H8v6H2v12h20V11h-6zm-6-6h4v14h-4V5zm-6 6h4v8H4v-8zm16 8h-4v-6h4v6z" />
            </svg>
            Analytics
          </button>
          <button 
            className={`tab-btn ${activeTab === 'ai-dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai-dashboard')}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            AI System
          </button>
          <button 
            className={`tab-btn ${activeTab === 'face-verification' ? 'active' : ''}`}
            onClick={() => setActiveTab('face-verification')}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
            Face Verification
          </button>
          <button 
            className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" />
            </svg>
            Audit Logs
          </button>
          <button 
            className={`tab-btn ${activeTab === 'qualifications' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('qualifications');
              fetchBasicQualifications();
            }}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Qualifications
          </button>
          <button 
            className={`tab-btn ${activeTab === 'applications' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('applications');
              fetchFullApplications();
            }}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M9 2a1 1 0 000 2h6a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
            Full Applications
          </button>
        </div>

        {/* Conditional Content Based on Active Tab */}
        {activeTab === 'overview' && (
          <>
        {/* Stats Section */}
        <div className="metrics-grid">
          <div className="metric-card personnel" onClick={() => onViewChange && onViewChange('students')}>
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div className="metric-data">
              <div className="metric-number">{dashboardData?.stats.total_students || 0}</div>
              <div className="metric-label">Total Students</div>
              <div className="metric-status">Active</div>
            </div>
          </div>

          <div className="metric-card documents" onClick={() => onViewChange && onViewChange('documents')}>
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 2a1 1 0 000 2h6a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2h1a1 1 0 000 2H6a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 100 2H6a2 2 0 01-2-2V5zM14 5a1 1 0 011-1h3a2 2 0 012 2v6a2 2 0 01-2 2h-3a1 1 0 110-2h3a1 1 0 001-1V6a1 1 0 00-1-1h-3a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="metric-data">
              <div className="metric-number">{dashboardData?.stats.total_documents || 0}</div>
              <div className="metric-label">Documents</div>
              <div className="metric-status">Processed</div>
            </div>
          </div>

          <div className="metric-card grades" onClick={() => onViewChange && onViewChange('grades')}>
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="metric-data">
              <div className="metric-number">{dashboardData?.stats.total_grades || 0}</div>
              <div className="metric-label">Grade Submissions</div>
              <div className="metric-status">Reviewed</div>
            </div>
          </div>

          <div className="metric-card applications" onClick={() => onViewChange && onViewChange('applications')}>
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="metric-data">
              <div className="metric-number">{dashboardData?.stats.total_applications || 0}</div>
              <div className="metric-label">Applications</div>
              <div className="metric-status">Submitted</div>
            </div>
          </div>
        </div>

        {/* Action Commands */}
        <div className="command-grid">
          <button className="command-btn documents" onClick={() => onViewChange && onViewChange('documents')}>
            <div className="command-header">
              <div className="command-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="command-count">{String(dashboardData?.pending_documents.length || 0).padStart(2, '0')}</div>
            </div>
            <div className="command-label">Document Review</div>
            <div className="command-status">Pending Review</div>
            {dashboardData?.pending_documents && dashboardData.pending_documents.filter(doc => getPriorityLevel(doc) === 'high').length > 0 && (
              <div className="priority-indicator high">
                {dashboardData.pending_documents.filter(doc => getPriorityLevel(doc) === 'high').length} urgent
              </div>
            )}
          </button>

          <button className="command-btn grades" onClick={() => onViewChange && onViewChange('grades')}>
            <div className="command-header">
              <div className="command-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="command-count">{String(dashboardData?.pending_grades.length || 0).padStart(2, '0')}</div>
            </div>
            <div className="command-label">Grade Analysis</div>
            <div className="command-status">Awaiting Review</div>
            {dashboardData?.pending_grades && dashboardData.pending_grades.filter(grade => Number(grade.general_weighted_average) >= 85).length > 0 && (
              <div className="priority-indicator medium">
                {dashboardData.pending_grades.filter(grade => Number(grade.general_weighted_average) >= 85).length} high GPA
              </div>
            )}
          </button> 

          <button className="command-btn applications" onClick={() => onViewChange && onViewChange('applications')}>
            <div className="command-header">
              <div className="command-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="command-count">{String(dashboardData?.pending_applications.length || 0).padStart(2, '0')}</div>
            </div>
            <div className="command-label">Fund Applications</div>
            <div className="command-status">Requires Approval</div>
            {dashboardData?.pending_applications && dashboardData.pending_applications.length > 0 && (
              <div className="priority-indicator low">
                {formatCurrency(dashboardData.pending_applications.reduce((sum, app) => sum + app.amount, 0))} pending
              </div>
            )}
          </button>
        </div>

        {/* Operations Dashboard */}
        <div className="operations-layout">
          <div className="operations-panel">
            <div className="panel-header">
              <h3>Document Operations</h3>
              <div className="panel-count">{String(dashboardData?.pending_documents.length || 0).padStart(2, '0')} Pending</div>
            </div>
            <div className="operations-list">
              {dashboardData?.pending_documents && dashboardData.pending_documents.length > 0 ? (
                dashboardData.pending_documents.map((doc) => {
                  const priority = getPriorityLevel(doc);
                  return (
                    <div key={doc.id} className={`operation-item priority-${priority}`}>
                      <div className="operation-header">
                        <div className="operation-id">ID-{doc.student_id}</div>
                        <div className="operation-status pending">Pending</div>
                        {priority === 'high' && <div className="urgent-badge">URGENT</div>}
                      </div>
                      <div className="operation-title">{doc.student_name}</div>
                      <div className="operation-detail">{doc.document_type_display}</div>
                      <div className="operation-timestamp">
                        SUBMITTED: {new Date(doc.submitted_at).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: '2-digit', 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        }).toUpperCase()}
                      </div>
                      <div className="operation-actions">
                        <button 
                          className="action-btn approve"
                          onClick={() => handleQuickAction('document', doc.id, 'approved')}
                          disabled={actionLoading[`document_${doc.id}`]}
                        >
                          {actionLoading[`document_${doc.id}`] ? '⏳' : '✅'} Approve
                        </button>
                        <button 
                          className="action-btn reject"
                          onClick={() => handleQuickAction('document', doc.id, 'rejected')}
                          disabled={actionLoading[`document_${doc.id}`]}
                        >
                          {actionLoading[`document_${doc.id}`] ? '⏳' : '❌'} Reject
                        </button>
                        <button 
                          className="action-btn review"
                          onClick={() => handleReviewAction('document', doc.id)}
                        >
                          👁️ Review
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="empty-state-admin">
                  <div className="empty-icon">📄</div>
                  <h4>No pending documents</h4>
                  <p>All documents have been reviewed</p>
                </div>
              )}
            </div>
          </div>

          {/* Pending Grades */}
          <div style={{
            background: '#f8fafc',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}>
            <h3 style={{
              color: '#1e293b',
              fontSize: '18px',
              fontWeight: '600',
              margin: '0 0 15px 0'
            }}>
              Pending Grades ({dashboardData?.pending_grades.length || 0})
            </h3>
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {dashboardData?.pending_grades && dashboardData.pending_grades.length > 0 ? (
                dashboardData.pending_grades.map((grade) => (
                  <div key={grade.id} style={{
                    background: 'white',
                    padding: '15px',
                    borderRadius: '8px',
                    marginBottom: '10px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                      <strong style={{ color: '#1e293b', fontSize: '14px' }}>{grade.student_name}</strong>
                      <span style={{
                        background: '#3b82f6',
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px'
                      }}>
                        {grade.status_display}
                      </span>
                    </div>
                    <div style={{ color: '#64748b', fontSize: '13px', marginBottom: '5px' }}>
                      ID: {grade.student_id} • {grade.academic_year} {grade.semester_display}
                    </div>
                    <div style={{ color: '#64748b', fontSize: '12px', marginBottom: '5px' }}>
                      GWA: {safeToFixed(grade.general_weighted_average)} | SWA: {safeToFixed(grade.semestral_weighted_average)}
                    </div>
                    <div style={{ color: '#64748b', fontSize: '12px' }}>
                      Submitted: {formatDate(grade.submitted_at)}
                    </div>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                      <button 
                        style={{
                          background: '#10b981',
                          color: 'white',
                          border: 'none',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                        onClick={() => handleQuickAction('grade', grade.id, 'approved')}
                        disabled={actionLoading[`grade_${grade.id}`]}
                      >
                        {actionLoading[`grade_${grade.id}`] ? '⏳' : '✅'} Approve
                      </button>
                      <button 
                        style={{
                          background: '#ef4444',
                          color: 'white',
                          border: 'none',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                        onClick={() => handleQuickAction('grade', grade.id, 'rejected')}
                        disabled={actionLoading[`grade_${grade.id}`]}
                      >
                        {actionLoading[`grade_${grade.id}`] ? '⏳' : '❌'} Reject
                      </button>
                      <button 
                        style={{
                          background: '#dc2626',
                          color: 'white',
                          border: 'none',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer',
                          fontWeight: '600'
                        }}
                        onClick={() => handleDeleteGrade(grade.id, grade.student_name)}
                        disabled={actionLoading[`delete_grade_${grade.id}`]}
                        title="Permanently delete this grade submission"
                      >
                        {actionLoading[`delete_grade_${grade.id}`] ? '⏳' : '🗑️'} Delete
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div style={{
                  background: 'white',
                  padding: '20px',
                  borderRadius: '8px',
                  textAlign: 'center',
                  color: '#64748b'
                }}>
                  <div style={{ fontSize: '32px', opacity: '0.5', marginBottom: '10px' }}>📄</div>
                  <p style={{ margin: '0' }}>No pending grades</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Pending Applications */}
        <div style={{
          background: '#f8fafc',
          padding: '20px',
          borderRadius: '12px',
          border: '1px solid #e2e8f0'
        }}>
          <h3 style={{
            color: '#1e293b',
            fontSize: '18px',
            fontWeight: '600',
            margin: '0 0 15px 0'
          }}>
            Pending Applications ({dashboardData?.pending_applications.length || 0})
          </h3>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {dashboardData?.pending_applications && dashboardData.pending_applications.length > 0 ? (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '15px'
              }}>
                {dashboardData.pending_applications.map((app) => (
                  <div key={app.id} style={{
                    background: 'white',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                      <strong style={{ color: '#1e293b', fontSize: '14px' }}>{app.student_name}</strong>
                      <span style={{
                        background: '#f59e0b',
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px'
                      }}>
                        {app.status_display}
                      </span>
                    </div>
                    <div style={{ color: '#64748b', fontSize: '13px', marginBottom: '5px' }}>
                      ID: {app.student_id} • {app.application_type_display}
                    </div>
                    <div style={{ color: '#10b981', fontSize: '14px', fontWeight: '600', marginBottom: '5px' }}>
                      {formatCurrency(app.amount)}
                    </div>
                    <div style={{ color: '#64748b', fontSize: '12px' }}>
                      Applied: {formatDate(app.applied_at)}
                    </div>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                      <button 
                        style={{
                          background: '#10b981',
                          color: 'white',
                          border: 'none',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                        onClick={() => handleQuickAction('application', app.id, 'approved')}
                        disabled={actionLoading[`application_${app.id}`]}
                      >
                        {actionLoading[`application_${app.id}`] ? '⏳' : '✅'} Approve
                      </button>
                      <button 
                        style={{
                          background: '#ef4444',
                          color: 'white',
                          border: 'none',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                        onClick={() => handleQuickAction('application', app.id, 'rejected')}
                        disabled={actionLoading[`application_${app.id}`]}
                      >
                        {actionLoading[`application_${app.id}`] ? '⏳' : '❌'} Reject
                      </button>
                      <button 
                        style={{
                          background: '#3b82f6',
                          color: 'white',
                          border: 'none',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                        onClick={() => handleQuickAction('application', app.id, 'disbursed')}
                        disabled={actionLoading[`application_${app.id}`]}
                      >
                        {actionLoading[`application_${app.id}`] ? '⏳' : '💰'} Disburse
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{
                background: 'white',
                padding: '20px',
                borderRadius: '8px',
                textAlign: 'center',
                color: '#64748b'
              }}>
                <div style={{ fontSize: '48px', opacity: '0.5', marginBottom: '10px' }}>💸</div>
                <p style={{ margin: '0 0 10px 0' }}>No pending applications</p>
                <p style={{ fontSize: '14px', marginTop: '10px', margin: '0' }}>
                  New allowance applications will appear here
                </p>
              </div>
            )}
          </div>
        </div>
          </>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="analytics-section">
            {analyticsData ? (
              <>
                {/* Quick Stats */}
                <div className="analytics-stats-grid">
                  <div className="analytics-stat-card">
                    <div className="stat-icon" style={{background: '#dbeafe'}}>
                      <svg viewBox="0 0 24 24" fill="#3b82f6" style={{width: '24px', height: '24px'}}>
                        <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div className="stat-details">
                      <div className="stat-value">{analyticsData.today_snapshot.total_students}</div>
                      <div className="stat-label">Total Students</div>
                    </div>
                  </div>
                  
                  <div className="analytics-stat-card">
                    <div className="stat-icon" style={{background: '#fef3c7'}}>
                      <svg viewBox="0 0 24 24" fill="#f59e0b" style={{width: '24px', height: '24px'}}>
                        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div className="stat-details">
                      <div className="stat-value">{analyticsData.today_snapshot.documents_pending}</div>
                      <div className="stat-label">Pending Documents</div>
                    </div>
                  </div>

                  <div className="analytics-stat-card">
                    <div className="stat-icon" style={{background: '#dcfce7'}}>
                      <svg viewBox="0 0 24 24" fill="#10b981" style={{width: '24px', height: '24px'}}>
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="stat-details">
                      <div className="stat-value">{analyticsData.today_snapshot.grades_pending}</div>
                      <div className="stat-label">Pending Grades</div>
                    </div>
                  </div>

                  <div className="analytics-stat-card">
                    <div className="stat-icon" style={{background: '#fce7f3'}}>
                      <svg viewBox="0 0 24 24" fill="#ec4899" style={{width: '24px', height: '24px'}}>
                        <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="stat-details">
                      <div className="stat-value">{formatCurrency(analyticsData.financial_summary.total_disbursed)}</div>
                      <div className="stat-label">Total Disbursed</div>
                    </div>
                  </div>
                </div>

                {/* Top Students */}
                <div className="analytics-section-card">
                  <h3>🏆 Top Performing Students</h3>
                  <div className="top-students-list">
                    {analyticsData.top_students.map((student, idx) => (
                      <div key={idx} className="top-student-item">
                        <div className="student-rank">#{idx + 1}</div>
                        <div className="student-info">
                          <div className="student-name">{student.student_name}</div>
                          <div className="student-id">ID: {student.student_id} • {student.academic_year} {student.semester}</div>
                        </div>
                        <div className="student-grades">
                          <span className="grade-badge gwa">GWA: {student.gwa.toFixed(2)}</span>
                          <span className="grade-badge swa">SWA: {student.swa.toFixed(2)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Financial Summary */}
                <div className="analytics-section-card">
                  <h3>💰 Financial Summary</h3>
                  <div className="financial-grid">
                    <div className="financial-item">
                      <div className="financial-label">Total Disbursed</div>
                      <div className="financial-value disbursed">{formatCurrency(analyticsData.financial_summary.total_disbursed)}</div>
                    </div>
                    <div className="financial-item">
                      <div className="financial-label">Pending Approval</div>
                      <div className="financial-value pending">{formatCurrency(analyticsData.financial_summary.total_pending)}</div>
                    </div>
                    <div className="financial-item">
                      <div className="financial-label">Total Committed</div>
                      <div className="financial-value committed">{formatCurrency(analyticsData.financial_summary.total_committed)}</div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="loading-content">
                <div className="loading-spinner"></div>
                <p>Loading analytics data...</p>
              </div>
            )}
          </div>
        )}

        {/* Audit Logs Tab */}
        {activeTab === 'audit' && (
          <div className="audit-logs-section">
            <div className="audit-logs-header">
              <h2>📋 System Audit Logs</h2>
              <button className="refresh-btn" onClick={() => { fetchAuditLogs(); fetchAIStats(); }}>
                <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '16px', height: '16px'}}>
                  <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>

            {/* AI Performance Monitoring Section */}
            {aiStats && (
              <div className="ai-monitoring-section" style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                padding: '24px',
                borderRadius: '12px',
                marginBottom: '24px',
                color: 'white',
                boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  marginBottom: '20px',
                  gap: '12px'
                }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    padding: '12px',
                    borderRadius: '12px',
                    backdropFilter: 'blur(10px)'
                  }}>
                    <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '32px', height: '32px'}}>
                      <path d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 style={{margin: '0 0 4px 0', fontSize: '24px', fontWeight: '700'}}>
                      🤖 AI Processing Monitor
                    </h3>
                    <p style={{margin: 0, fontSize: '14px', opacity: 0.9}}>
                      Real-time AI document verification performance
                    </p>
                  </div>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '16px',
                  marginTop: '20px'
                }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.15)',
                    padding: '16px',
                    borderRadius: '10px',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.2)'
                  }}>
                    <div style={{fontSize: '12px', opacity: 0.9, marginBottom: '8px', fontWeight: '600'}}>
                      📊 Total AI Processed
                    </div>
                    <div style={{fontSize: '32px', fontWeight: '700', marginBottom: '4px'}}>
                      {aiStats.total_processed}
                    </div>
                    <div style={{fontSize: '11px', opacity: 0.8}}>
                      Documents analyzed
                    </div>
                  </div>

                  <div style={{
                    background: 'rgba(16, 185, 129, 0.2)',
                    padding: '16px',
                    borderRadius: '10px',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(16, 185, 129, 0.3)'
                  }}>
                    <div style={{fontSize: '12px', opacity: 0.9, marginBottom: '8px', fontWeight: '600'}}>
                      ✅ Auto-Approved
                    </div>
                    <div style={{fontSize: '32px', fontWeight: '700', marginBottom: '4px'}}>
                      {aiStats.auto_approved}
                    </div>
                    <div style={{fontSize: '11px', opacity: 0.8}}>
                      {aiStats.total_processed > 0 
                        ? `${((aiStats.auto_approved / aiStats.total_processed) * 100).toFixed(1)}% success rate`
                        : 'No data yet'
                      }
                    </div>
                  </div>

                  <div style={{
                    background: 'rgba(239, 68, 68, 0.2)',
                    padding: '16px',
                    borderRadius: '10px',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(239, 68, 68, 0.3)'
                  }}>
                    <div style={{fontSize: '12px', opacity: 0.9, marginBottom: '8px', fontWeight: '600'}}>
                      ❌ Auto-Rejected
                    </div>
                    <div style={{fontSize: '32px', fontWeight: '700', marginBottom: '4px'}}>
                      {aiStats.auto_rejected}
                    </div>
                    <div style={{fontSize: '11px', opacity: 0.8}}>
                      Fraud/quality issues
                    </div>
                  </div>

                  <div style={{
                    background: 'rgba(245, 158, 11, 0.2)',
                    padding: '16px',
                    borderRadius: '10px',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(245, 158, 11, 0.3)'
                  }}>
                    <div style={{fontSize: '12px', opacity: 0.9, marginBottom: '8px', fontWeight: '600'}}>
                      👁️ Manual Review
                    </div>
                    <div style={{fontSize: '32px', fontWeight: '700', marginBottom: '4px'}}>
                      {aiStats.manual_review}
                    </div>
                    <div style={{fontSize: '11px', opacity: 0.8}}>
                      Pending admin review
                    </div>
                  </div>

                  <div style={{
                    background: 'rgba(59, 130, 246, 0.2)',
                    padding: '16px',
                    borderRadius: '10px',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(59, 130, 246, 0.3)'
                  }}>
                    <div style={{fontSize: '12px', opacity: 0.9, marginBottom: '8px', fontWeight: '600'}}>
                      🎯 AI Confidence
                    </div>
                    <div style={{fontSize: '32px', fontWeight: '700', marginBottom: '4px'}}>
                      {(aiStats.average_confidence * 100).toFixed(1)}%
                    </div>
                    <div style={{fontSize: '11px', opacity: 0.8}}>
                      Average accuracy score
                    </div>
                  </div>
                </div>

                {/* Recent AI Activities */}
                {aiStats.recent_activities && aiStats.recent_activities.length > 0 && (
                  <div style={{marginTop: '20px'}}>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      marginBottom: '12px',
                      opacity: 0.95
                    }}>
                      🕒 Recent AI Activities
                    </div>
                    <div style={{
                      display: 'grid',
                      gap: '8px'
                    }}>
                      {aiStats.recent_activities.slice(0, 3).map((activity, idx) => (
                        <div key={idx} style={{
                          background: 'rgba(255, 255, 255, 0.1)',
                          padding: '12px',
                          borderRadius: '8px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          fontSize: '13px'
                        }}>
                          <div>
                            <span style={{marginRight: '8px'}}>
                              {activity.decision === 'approved' ? '✅' : activity.decision === 'rejected' ? '❌' : '⏳'}
                            </span>
                            {activity.action}
                          </div>
                          <div style={{
                            display: 'flex',
                            gap: '12px',
                            alignItems: 'center',
                            fontSize: '12px'
                          }}>
                            <span style={{
                              background: 'rgba(255, 255, 255, 0.2)',
                              padding: '4px 8px',
                              borderRadius: '4px'
                            }}>
                              {(activity.confidence * 100).toFixed(0)}% confidence
                            </span>
                            <span style={{opacity: 0.8}}>
                              {new Date(activity.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Filter Buttons */}
            <div style={{
              display: 'flex',
              gap: '12px',
              marginBottom: '20px',
              flexWrap: 'wrap'
            }}>
              <button
                className={`filter-btn ${auditFilter === 'all' ? 'active' : ''}`}
                onClick={() => setAuditFilter('all')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: auditFilter === 'all' ? '2px solid #3b82f6' : '1px solid #e2e8f0',
                  background: auditFilter === 'all' ? '#3b82f6' : 'white',
                  color: auditFilter === 'all' ? 'white' : '#64748b',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s'
                }}
              >
                All Activities
              </button>
              <button
                className={`filter-btn ${auditFilter === 'ai' ? 'active' : ''}`}
                onClick={() => setAuditFilter('ai')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: auditFilter === 'ai' ? '2px solid #8b5cf6' : '1px solid #e2e8f0',
                  background: auditFilter === 'ai' ? '#8b5cf6' : 'white',
                  color: auditFilter === 'ai' ? 'white' : '#64748b',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s'
                }}
              >
                AI Actions
              </button>
              <button
                className={`filter-btn ${auditFilter === 'admin' ? 'active' : ''}`}
                onClick={() => setAuditFilter('admin')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: auditFilter === 'admin' ? '2px solid #10b981' : '1px solid #e2e8f0',
                  background: auditFilter === 'admin' ? '#10b981' : 'white',
                  color: auditFilter === 'admin' ? 'white' : '#64748b',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s'
                }}
              >
                Admin Actions
              </button>
              <button
                className={`filter-btn ${auditFilter === 'user' ? 'active' : ''}`}
                onClick={() => setAuditFilter('user')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: auditFilter === 'user' ? '2px solid #f59e0b' : '1px solid #e2e8f0',
                  background: auditFilter === 'user' ? '#f59e0b' : 'white',
                  color: auditFilter === 'user' ? 'white' : '#64748b',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s'
                }}
              >
                User Actions
              </button>
            </div>

            <div className="audit-logs-list">
              {auditLogs
                .filter(log => {
                  if (auditFilter === 'all') return true;
                  if (auditFilter === 'ai') return log.action_type === 'ai_analysis' || log.action_type === 'ai_auto_approve';
                  if (auditFilter === 'admin') return log.action_type.startsWith('admin_') || log.action_type.includes('approved') || log.action_type.includes('rejected');
                  if (auditFilter === 'user') return log.action_type.startsWith('user_') || log.action_type.includes('submitted');
                  return true;
                })
                .map((log) => (
                <div key={log.id} className={`audit-log-item severity-${log.severity}`}>
                  <div className="audit-log-header">
                    <div className="audit-log-user">
                      <div className="user-avatar">
                        {log.action_type.startsWith('ai_') ? '🤖' : log.user.username[0].toUpperCase()}
                      </div>
                      <div>
                        <div className="user-name">
                          {log.action_type.startsWith('ai_') ? '🤖 AI System' : log.user.full_name}
                        </div>
                        <div className="user-action">{log.action_type_display}</div>
                      </div>
                    </div>
                    <div className="audit-log-meta">
                      <span className={`severity-badge ${log.severity}`}>{log.severity_display}</span>
                      <span className="audit-time">{formatDate(log.timestamp)}</span>
                    </div>
                  </div>
                  <div className="audit-log-description">{log.action_description}</div>
                  {log.metadata && log.metadata.confidence_score && (
                    <div style={{
                      marginTop: '8px',
                      padding: '8px 12px',
                      background: '#f0f9ff',
                      borderRadius: '6px',
                      fontSize: '13px',
                      color: '#0369a1'
                    }}>
                      🎯 AI Confidence Score: <strong>{(log.metadata.confidence_score * 100).toFixed(1)}%</strong>
                      {log.metadata.auto_decision && (
                        <span style={{marginLeft: '12px'}}>
                          • Decision: <strong>{log.metadata.decision || 'Auto-processed'}</strong>
                        </span>
                      )}
                    </div>
                  )}
                  {log.target_user && (
                    <div className="audit-log-target">
                      Target: {log.target_user.full_name} ({log.target_user.username})
                    </div>
                  )}
                  {log.ip_address && (
                    <div className="audit-log-ip">IP: {log.ip_address}</div>
                  )}
                </div>
              ))}
              
              {auditLogs.length === 0 && (
                <div className="empty-state-admin">
                  <div className="empty-icon">📋</div>
                  <h4>No audit logs found</h4>
                  <p>System activities will be logged here</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Dashboard Tab */}
        {activeTab === 'ai-dashboard' && (
          <div className="ai-dashboard-section">
            <AdminAIDashboard />
          </div>
        )}

        {/* Face Verification Tab */}
        {activeTab === 'face-verification' && (
          <div className="face-verification-section">
            <FaceAdjudicationDashboard />
          </div>
        )}

        {/* Basic Qualifications Tab */}
        {activeTab === 'qualifications' && (
          <div className="qualifications-section">
            <div className="section-header">
              <h2>Basic Qualifications</h2>
              <button 
                className="refresh-btn"
                onClick={fetchBasicQualifications}
                style={{
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                🔄 Refresh
              </button>
            </div>

            <div className="qualifications-stats" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px',
              marginBottom: '24px'
            }}>
              <div className="stat-card" style={{background: '#f0fdf4', padding: '20px', borderRadius: '8px'}}>
                <div style={{fontSize: '32px', fontWeight: 'bold', color: '#16a34a'}}>
                  {basicQualifications.length}
                </div>
                <div style={{color: '#15803d', marginTop: '8px'}}>Total Submissions</div>
              </div>
              <div className="stat-card" style={{background: '#ecfdf5', padding: '20px', borderRadius: '8px'}}>
                <div style={{fontSize: '32px', fontWeight: 'bold', color: '#059669'}}>
                  {basicQualifications.filter(q => q.is_qualified).length}
                </div>
                <div style={{color: '#047857', marginTop: '8px'}}>Qualified Students</div>
              </div>
              <div className="stat-card" style={{background: '#fef2f2', padding: '20px', borderRadius: '8px'}}>
                <div style={{fontSize: '32px', fontWeight: 'bold', color: '#dc2626'}}>
                  {basicQualifications.filter(q => !q.is_qualified).length}
                </div>
                <div style={{color: '#b91c1c', marginTop: '8px'}}>Not Qualified</div>
              </div>
            </div>

            <div className="qualifications-table" style={{
              background: 'white',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <table style={{width: '100%', borderCollapse: 'collapse'}}>
                <thead>
                  <tr style={{background: '#f9fafb', borderBottom: '1px solid #e5e7eb'}}>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Student</th>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Student ID</th>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Type</th>
                    <th style={{padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151'}}>Status</th>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Completed</th>
                    <th style={{padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151'}}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {basicQualifications.length === 0 ? (
                    <tr>
                      <td colSpan={6} style={{padding: '40px', textAlign: 'center', color: '#6b7280'}}>
                        No basic qualifications found
                      </td>
                    </tr>
                  ) : (
                    basicQualifications.map(qual => (
                      <tr key={qual.id} style={{borderBottom: '1px solid #f3f4f6'}}>
                        <td style={{padding: '12px'}}>
                          <div style={{fontWeight: '500', color: '#1f2937'}}>
                            {qual.student_name || `${qual.student.first_name} ${qual.student.last_name}`}
                          </div>
                        </td>
                        <td style={{padding: '12px', color: '#6b7280'}}>
                          {qual.student_id || qual.student.student_id}
                        </td>
                        <td style={{padding: '12px'}}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: '500',
                            background: qual.applicant_type === 'new' ? '#dbeafe' : '#fef3c7',
                            color: qual.applicant_type === 'new' ? '#1e40af' : '#92400e'
                          }}>
                            {qual.applicant_type === 'new' ? '🆕 New' : '🔄 Renewing'}
                          </span>
                        </td>
                        <td style={{padding: '12px', textAlign: 'center'}}>
                          <span style={{
                            padding: '6px 12px',
                            borderRadius: '12px',
                            fontSize: '13px',
                            fontWeight: '600',
                            background: qual.is_qualified ? '#d1fae5' : '#fee2e2',
                            color: qual.is_qualified ? '#065f46' : '#991b1b'
                          }}>
                            {qual.is_qualified ? '✅ Qualified' : '❌ Not Qualified'}
                          </span>
                        </td>
                        <td style={{padding: '12px', fontSize: '14px', color: '#6b7280'}}>
                          {new Date(qual.completed_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </td>
                        <td style={{padding: '12px', textAlign: 'center'}}>
                          <button 
                            style={{
                              background: '#eff6ff',
                              color: '#1d4ed8',
                              border: '1px solid #3b82f6',
                              padding: '6px 12px',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              fontSize: '13px',
                              fontWeight: '500'
                            }}
                            onClick={() => {
                              setSelectedQualification(qual);
                              setShowQualificationModal(true);
                            }}
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Full Applications Tab */}
        {activeTab === 'applications' && (
          <div className="applications-section">
            <div className="section-header">
              <h2>📝 Full Application Forms</h2>
              <button 
                className="refresh-btn"
                onClick={fetchFullApplications}
                style={{
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                🔄 Refresh
              </button>
            </div>

            <div className="applications-stats" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px',
              marginBottom: '24px'
            }}>
              <div className="stat-card" style={{background: '#f0f9ff', padding: '20px', borderRadius: '8px'}}>
                <div style={{fontSize: '32px', fontWeight: 'bold', color: '#0284c7'}}>
                  {fullApplications.length}
                </div>
                <div style={{color: '#0369a1', marginTop: '8px'}}>Total Applications</div>
              </div>
              <div className="stat-card" style={{background: '#f0fdf4', padding: '20px', borderRadius: '8px'}}>
                <div style={{fontSize: '32px', fontWeight: 'bold', color: '#16a34a'}}>
                  {fullApplications.filter(app => app.is_submitted).length}
                </div>
                <div style={{color: '#15803d', marginTop: '8px'}}>Submitted</div>
              </div>
              <div className="stat-card" style={{background: '#fef3c7', padding: '20px', borderRadius: '8px'}}>
                <div style={{fontSize: '32px', fontWeight: 'bold', color: '#d97706'}}>
                  {fullApplications.filter(app => !app.is_submitted).length}
                </div>
                <div style={{color: '#b45309', marginTop: '8px'}}>Drafts</div>
              </div>
            </div>

            <div className="applications-table" style={{
              background: 'white',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <table style={{width: '100%', borderCollapse: 'collapse'}}>
                <thead>
                  <tr style={{background: '#f9fafb', borderBottom: '1px solid #e5e7eb'}}>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Student</th>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Student ID</th>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>School Year</th>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Semester</th>
                    <th style={{padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151'}}>Status</th>
                    <th style={{padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151'}}>Date</th>
                    <th style={{padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151'}}>Details</th>
                    <th style={{padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151'}}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {fullApplications.length === 0 ? (
                    <tr>
                      <td colSpan={8} style={{padding: '40px', textAlign: 'center', color: '#6b7280'}}>
                        No full applications found
                      </td>
                    </tr>
                  ) : (
                    fullApplications.map(app => (
                      <tr key={app.id} style={{borderBottom: '1px solid #f3f4f6'}}>
                        <td style={{padding: '12px'}}>
                          <div style={{fontWeight: '500', color: '#1f2937'}}>
                            {app.user.first_name} {app.user.last_name}
                          </div>
                          <div style={{fontSize: '12px', color: '#6b7280'}}>
                            {app.email}
                          </div>
                        </td>
                        <td style={{padding: '12px', color: '#6b7280'}}>
                          {app.user.student_id}
                        </td>
                        <td style={{padding: '12px', fontSize: '14px', color: '#374151'}}>
                          {app.school_year}
                        </td>
                        <td style={{padding: '12px', fontSize: '14px', color: '#374151'}}>
                          {app.semester}
                        </td>
                        <td style={{padding: '12px', textAlign: 'center'}}>
                          {app.is_submitted ? (
                            <span style={{
                              padding: '6px 12px',
                              borderRadius: '12px',
                              fontSize: '13px',
                              fontWeight: '600',
                              background: '#d1fae5',
                              color: '#065f46'
                            }}>
                              ✅ Submitted
                            </span>
                          ) : (
                            <span style={{
                              padding: '6px 12px',
                              borderRadius: '12px',
                              fontSize: '13px',
                              fontWeight: '600',
                              background: '#fef3c7',
                              color: '#92400e'
                            }}>
                              ⚠️ Draft
                            </span>
                          )}
                        </td>
                        <td style={{padding: '12px', fontSize: '14px', color: '#6b7280'}}>
                          {app.created_at ? new Date(app.created_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          }) : 'N/A'}
                        </td>
                        <td style={{padding: '12px', textAlign: 'center'}}>
                          <button 
                            onClick={() => {
                              setSelectedApplication(app);
                              setShowApplicationModal(true);
                            }}
                            style={{
                              padding: '6px 16px',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: '500',
                              color: '#2563eb',
                              background: 'transparent',
                              border: '1px solid #2563eb',
                              cursor: 'pointer'
                            }}
                          >
                            View
                          </button>
                        </td>
                        <td style={{padding: '12px', textAlign: 'center'}}>
                          <button 
                            onClick={async () => {
                              const confirmed = await showConfirm({
                                message: `Are you sure you want to delete the application for ${app.user.first_name} ${app.user.last_name}?`,
                                type: 'warning',
                                confirmText: 'Delete',
                                cancelText: 'Cancel'
                              });
                              
                              if (confirmed) {
                                try {
                                  await apiClient.delete(`/full-application/${app.id}/`);
                                  await showAlert({
                                    message: 'Application deleted successfully',
                                    type: 'success',
                                    confirmText: 'OK'
                                  });
                                  fetchFullApplications();
                                } catch (error) {
                                  console.error('Error deleting application:', error);
                                  await showAlert({
                                    message: 'Failed to delete application',
                                    type: 'error',
                                    confirmText: 'OK'
                                  });
                                }
                              }
                            }}
                            style={{
                              padding: '6px 16px',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: '500',
                              color: '#dc2626',
                              background: 'transparent',
                              border: '1px solid #dc2626',
                              cursor: 'pointer'
                            }}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>

      {/* Qualification Detail Modal */}
      {showQualificationModal && selectedQualification && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setShowQualificationModal(false)}
        >
          <div 
            style={{
              background: '#ffffff',
              borderRadius: '16px',
              maxWidth: '600px',
              width: '90%',
              maxHeight: '85vh',
              overflow: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{
              padding: '24px',
              borderBottom: '1px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <h2 style={{
                  fontSize: '22px',
                  fontWeight: '600',
                  color: '#111827',
                  margin: '0 0 8px 0'
                }}>
                  Basic Qualification Details
                </h2>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                  <span style={{ fontWeight: '500', color: '#374151' }}>
                    {selectedQualification.student_name || `${selectedQualification.student.first_name} ${selectedQualification.student.last_name}`}
                  </span>
                  {' • '}
                  <span>ID: {selectedQualification.student_id || selectedQualification.student.student_id}</span>
                </div>
              </div>
              <button
                onClick={() => setShowQualificationModal(false)}
                style={{
                  background: '#f3f4f6',
                  border: 'none',
                  borderRadius: '8px',
                  width: '36px',
                  height: '36px',
                  fontSize: '20px',
                  cursor: 'pointer',
                  color: '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                ✕
              </button>
            </div>

            {/* Content */}
            <div style={{ padding: '24px' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr',
                gap: '12px'
              }}>
                {[
                  { label: 'Currently Enrolled', value: selectedQualification.is_enrolled, icon: '🎓' },
                  { label: 'Taguig City Resident', value: selectedQualification.is_resident, icon: '🏠' },
                  { label: '18 Years or Older', value: selectedQualification.is_eighteen_or_older, icon: '👤' },
                  { label: 'Registered Voter', value: selectedQualification.is_registered_voter, icon: '🗳️' },
                  { label: 'Parent is Voter', value: selectedQualification.parent_is_voter, icon: '👨‍👩‍👧' },
                  { label: 'Good Moral Character', value: selectedQualification.has_good_moral_character, icon: '⭐' },
                  { label: 'Committed to Requirements', value: selectedQualification.is_committed, icon: '✍️' }
                ].map((item, index) => (
                  <div 
                    key={index}
                    style={{
                      padding: '16px',
                      background: item.value ? '#d1fae5' : '#fee2e2',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      border: `1px solid ${item.value ? '#a7f3d0' : '#fecaca'}`
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '24px' }}>{item.icon}</span>
                      <span style={{
                        fontSize: '15px',
                        fontWeight: '500',
                        color: item.value ? '#065f46' : '#991b1b'
                      }}>
                        {item.label}
                      </span>
                    </div>
                    <span style={{
                      fontSize: '20px',
                      fontWeight: '600'
                    }}>
                      {item.value ? '✓' : '✗'}
                    </span>
                  </div>
                ))}
              </div>

              {/* Completed Date */}
              <div style={{
                marginTop: '24px',
                padding: '16px',
                background: '#f9fafb',
                borderRadius: '10px',
                fontSize: '14px',
                color: '#6b7280'
              }}>
                <strong style={{ color: '#374151' }}>Completed:</strong>{' '}
                {new Date(selectedQualification.completed_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Application Detail Modal */}
      {showApplicationModal && selectedApplication && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setShowApplicationModal(false)}
        >
          <div 
            style={{
              background: '#ffffff',
              borderRadius: '16px',
              maxWidth: '800px',
              width: '90%',
              maxHeight: '85vh',
              overflow: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{
              padding: '24px',
              borderBottom: '1px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <h2 style={{
                  fontSize: '22px',
                  fontWeight: '600',
                  color: '#111827',
                  margin: '0 0 8px 0'
                }}>
                  Full Application Details
                </h2>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                  <span style={{ fontWeight: '500', color: '#374151' }}>
                    {selectedApplication.user.first_name} {selectedApplication.user.last_name}
                  </span>
                  {' • '}
                  <span>ID: {selectedApplication.user.student_id}</span>
                </div>
              </div>
              <button
                onClick={() => setShowApplicationModal(false)}
                style={{
                  background: '#f3f4f6',
                  border: 'none',
                  borderRadius: '8px',
                  width: '36px',
                  height: '36px',
                  fontSize: '20px',
                  cursor: 'pointer',
                  color: '#6b7280',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                ✕
              </button>
            </div>

            {/* Content */}
            <div style={{ padding: '24px' }}>
              
              {/* Application Details */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>📋</span> Application Details
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>School Year</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.school_year}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Semester</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.semester}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Application Type</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.application_type}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Scholarship Type</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.scholarship_type}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Facebook Link</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827', wordBreak: 'break-all' }}>{selectedApplication.facebook_link || 'N/A'}</div>
                  </div>
                </div>
              </div>

              {/* Personal Information */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>👤</span> Personal Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>First Name</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.first_name}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Middle Name</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.middle_name || 'N/A'}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Last Name</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.last_name}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Date of Birth</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.date_of_birth}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Age</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.age}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Sex</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.sex}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Citizenship</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.citizenship}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Marital Status</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.marital_status}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Religion</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.religion}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Place of Birth</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.place_of_birth}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Years of Residency</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.years_of_residency}</div>
                  </div>
                </div>
              </div>

              {/* Address Information */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>🏠</span> Address Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>House No.</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.house_no}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Street</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.street}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Barangay</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.barangay}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>District</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.district}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Zip Code</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.zip_code}</div>
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>📱</span> Contact Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Email</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.email}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Mobile No.</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.mobile_no}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Other Contact</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.other_contact}</div>
                  </div>
                </div>
              </div>

              {/* School Information */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>🎓</span> School Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>School Name</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.school_name}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>School Address</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.school_address}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Course Name</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.course_name}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Year Level</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.year_level}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Units Enrolled</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.units_enrolled}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Course Duration</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.course_duration}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Ladderized</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.ladderized}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Status</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.status}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Transferee</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.transferee}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Shiftee</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.shiftee}</div>
                  </div>
                </div>
              </div>

              {/* Educational Background - SHS */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>📚</span> Senior High School
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>School Attended</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.shs_attended}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Type</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.shs_type}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Address</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.shs_address}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Years</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.shs_years}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Honors</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.shs_honors || 'N/A'}</div>
                  </div>
                </div>
              </div>

              {/* Educational Background - JHS */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>📚</span> Junior High School
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>School Attended</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.jhs_attended}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Type</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.jhs_type}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Address</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.jhs_address}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Years</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.jhs_years}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Honors</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.jhs_honors || 'N/A'}</div>
                  </div>
                </div>
              </div>

              {/* Educational Background - Elementary */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>📚</span> Elementary School
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>School Attended</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.elem_attended}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Type</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.elem_type}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Address</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.elem_address}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Years</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.elem_years}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Honors</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.elem_honors || 'N/A'}</div>
                  </div>
                </div>
              </div>

              {/* Father's Information */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>👨</span> Father's Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Full Name</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.father_name}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Contact</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.father_contact}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Address</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.father_address}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Occupation</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.father_occupation}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Place of Work</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.father_place_of_work}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Education</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.father_education}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Status</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>
                      {selectedApplication.father_deceased ? '❌ Deceased' : '✅ Living'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Mother's Information */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>👩</span> Mother's Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Full Name</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.mother_name}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Contact</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.mother_contact}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Address</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.mother_address}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Occupation</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.mother_occupation}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Place of Work</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.mother_place_of_work}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Education</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>{selectedApplication.mother_education}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Status</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>
                      {selectedApplication.mother_deceased ? '❌ Deceased' : '✅ Living'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Status Information */}
              <div>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#111827',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>📋</span> Status Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  padding: '16px',
                  background: '#f9fafb',
                  borderRadius: '10px'
                }}>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Submitted</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>
                      {selectedApplication.is_submitted ? '✅ Yes' : '❌ No'}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Locked</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>
                      {selectedApplication.is_locked ? '🔒 Locked' : '🔓 Unlocked'}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Created At</div>
                    <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>
                      {new Date(selectedApplication.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                  {selectedApplication.submitted_at && (
                    <div>
                      <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>Submitted At</div>
                      <div style={{ fontSize: '15px', fontWeight: '500', color: '#111827' }}>
                        {new Date(selectedApplication.submitted_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Deletion Reason Modal */}
      {showReasonModal && pendingDeleteGrade && (
        <div className="reason-modal-overlay" onClick={() => setShowReasonModal(false)}>
          <div className="reason-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="reason-modal-header">
              <h3>🗑️ Delete Grade Submission</h3>
              <button className="reason-modal-close" onClick={() => setShowReasonModal(false)}>✕</button>
            </div>
            <div className="reason-modal-body">
              <p className="reason-modal-message">
                Please provide a reason for deleting the grade submission for <strong>{pendingDeleteGrade.name}</strong>:
              </p>
              <textarea
                className="reason-modal-input"
                placeholder="Enter deletion reason (e.g., re-upload, correction needed, duplicate entry...)"
                value={deletionReason}
                onChange={(e) => setDeletionReason(e.target.value)}
                autoFocus
                rows={4}
              />
            </div>
            <div className="reason-modal-footer">
              <button 
                className="reason-modal-btn cancel-btn" 
                onClick={() => {
                  setShowReasonModal(false);
                  setPendingDeleteGrade(null);
                  setDeletionReason('');
                }}
              >
                Cancel
              </button>
              <button 
                className="reason-modal-btn confirm-btn" 
                onClick={confirmDeleteWithReason}
                disabled={!deletionReason.trim()}
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}
      
      <NotificationDialog {...notification} />
    </div>
  );
};

export default AdminDashboard;

