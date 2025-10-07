import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';
import { safeToFixed, formatCurrency } from '../utils/numberUtils';
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

interface AdminStats {
  total_students: number;
  total_documents: number;
  total_grades: number;
  total_applications: number;
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
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'audit'>('overview');
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<{ [key: string]: boolean }>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

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
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000);

    return () => clearInterval(interval);
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

  // Fetch data based on active tab
  useEffect(() => {
    if (activeTab === 'analytics' && !analyticsData) {
      fetchAnalyticsData();
    } else if (activeTab === 'audit' && auditLogs.length === 0) {
      fetchAuditLogs();
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

  const getPriorityLevel = (item: any) => {
    const submitDate = new Date(item.submitted_at || item.applied_at);
    const now = new Date();
    const daysOld = Math.floor((now.getTime() - submitDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysOld >= 7) return 'high';
    if (daysOld >= 3) return 'medium';
    return 'low';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2 className="loading-title">Loading Dashboard</h2>
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
            className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '20px', height: '20px', marginRight: '8px'}}>
              <path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" />
            </svg>
            Audit Logs
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
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
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
              <button className="refresh-btn" onClick={() => fetchAuditLogs()}>
                <svg viewBox="0 0 24 24" fill="currentColor" style={{width: '16px', height: '16px'}}>
                  <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>

            <div className="audit-logs-list">
              {auditLogs.map((log) => (
                <div key={log.id} className={`audit-log-item severity-${log.severity}`}>
                  <div className="audit-log-header">
                    <div className="audit-log-user">
                      <div className="user-avatar">{log.user.username[0].toUpperCase()}</div>
                      <div>
                        <div className="user-name">{log.user.full_name}</div>
                        <div className="user-action">{log.action_type_display}</div>
                      </div>
                    </div>
                    <div className="audit-log-meta">
                      <span className={`severity-badge ${log.severity}`}>{log.severity_display}</span>
                      <span className="audit-time">{formatDate(log.timestamp)}</span>
                    </div>
                  </div>
                  <div className="audit-log-description">{log.action_description}</div>
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

      </div>
    </div>
  );
};

export default AdminDashboard;

