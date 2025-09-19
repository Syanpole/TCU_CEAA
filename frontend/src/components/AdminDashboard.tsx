import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';
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
  application_type: string;
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

interface AdminDashboardProps {
  onViewChange?: (view: string) => void;
}

// Utility functions
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
    minimumFractionDigits: 2
  }).format(amount);
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const safeToFixed = (value: number | string, decimals: number = 2): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return isNaN(num) ? '0.00' : num.toFixed(decimals);
};

const getPriorityLevel = (doc: DocumentSubmission): 'high' | 'medium' | 'low' => {
  const submittedDate = new Date(doc.submitted_at);
  const daysSinceSubmitted = (Date.now() - submittedDate.getTime()) / (1000 * 60 * 60 * 24);
  
  if (daysSinceSubmitted > 7) return 'high';
  if (daysSinceSubmitted > 3) return 'medium';
  return 'low';
};

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onViewChange }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<{ [key: string]: boolean }>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [showStatsModal, setShowStatsModal] = useState(false);
  const [allApplications, setAllApplications] = useState<AllowanceApplication[]>([]);

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
          console.log('Main dashboard API failed, trying individual endpoints...');
          
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

            // Store all applications for stats modal
            setAllApplications(applications);

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
            console.log('Individual APIs also failed, using demo data for development');
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

  // Calculate financial statistics for the stats modal
  const calculateFinancialStats = () => {
    if (!allApplications || allApplications.length === 0) {
      return {
        total: { amount: 0, count: 0 },
        approved: { amount: 0, count: 0 },
        disbursed: { amount: 0, count: 0 },
        pending: { amount: 0, count: 0 },
        rejected: { amount: 0, count: 0 }
      };
    }

    const stats = {
      total: { amount: 0, count: allApplications.length },
      approved: { amount: 0, count: 0 },
      disbursed: { amount: 0, count: 0 },
      pending: { amount: 0, count: 0 },
      rejected: { amount: 0, count: 0 }
    };

    allApplications.forEach(app => {
      stats.total.amount += app.amount;
      
      switch (app.status) {
        case 'approved':
          stats.approved.amount += app.amount;
          stats.approved.count++;
          break;
        case 'disbursed':
          stats.disbursed.amount += app.amount;
          stats.disbursed.count++;
          break;
        case 'pending':
          stats.pending.amount += app.amount;
          stats.pending.count++;
          break;
        case 'rejected':
          stats.rejected.amount += app.amount;
          stats.rejected.count++;
          break;
      }
    });

    return stats;
  };

  // Stats Modal Component
  const StatsModal = () => {
    const stats = calculateFinancialStats();
    
    return (
      <div className="modal-overlay" onClick={() => setShowStatsModal(false)}>
        <div className="stats-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Financial Statistics Overview</h2>
            <button className="modal-close" onClick={() => setShowStatsModal(false)}>×</button>
          </div>
          
          <div className="stats-grid">
            <div className="stat-card total">
              <div className="stat-icon">💰</div>
              <div className="stat-content">
                <div className="stat-title">Total Applications</div>
                <div className="stat-amount">{formatCurrency(stats.total.amount)}</div>
                <div className="stat-count">{stats.total.count} applications</div>
              </div>
            </div>

            <div className="stat-card approved">
              <div className="stat-icon">✅</div>
              <div className="stat-content">
                <div className="stat-title">Approved Amount</div>
                <div className="stat-amount">{formatCurrency(stats.approved.amount)}</div>
                <div className="stat-count">{stats.approved.count} applications</div>
              </div>
            </div>

            <div className="stat-card disbursed">
              <div className="stat-icon">💸</div>
              <div className="stat-content">
                <div className="stat-title">Disbursed Amount</div>
                <div className="stat-amount">{formatCurrency(stats.disbursed.amount)}</div>
                <div className="stat-count">{stats.disbursed.count} applications</div>
              </div>
            </div>

            <div className="stat-card pending">
              <div className="stat-icon">⏳</div>
              <div className="stat-content">
                <div className="stat-title">Pending Amount</div>
                <div className="stat-amount">{formatCurrency(stats.pending.amount)}</div>
                <div className="stat-count">{stats.pending.count} applications</div>
              </div>
            </div>

            <div className="stat-card rejected">
              <div className="stat-icon">❌</div>
              <div className="stat-content">
                <div className="stat-title">Rejected Amount</div>
                <div className="stat-amount">{formatCurrency(stats.rejected.amount)}</div>
                <div className="stat-count">{stats.rejected.count} applications</div>
              </div>
            </div>

            <div className="stat-card efficiency">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <div className="stat-title">Approval Rate</div>
                <div className="stat-amount">
                  {stats.total.count > 0 
                    ? `${Math.round((stats.approved.count / stats.total.count) * 100)}%`
                    : '0%'
                  }
                </div>
                <div className="stat-count">
                  {stats.approved.count} of {stats.total.count} approved
                </div>
              </div>
            </div>
          </div>

          <div className="detailed-breakdown">
            <h3>Application Type Breakdown</h3>
            <div className="breakdown-grid">
              {['basic', 'merit', 'both'].map(type => {
                const typeApps = allApplications.filter(app => app.application_type === type);
                const typeAmount = typeApps.reduce((sum, app) => sum + app.amount, 0);
                const typeName = type === 'basic' ? 'Basic Educational Assistance' :
                                type === 'merit' ? 'Merit Incentive' : 'Both Allowances';
                
                return (
                  <div key={type} className="breakdown-item">
                    <div className="breakdown-title">{typeName}</div>
                    <div className="breakdown-amount">{formatCurrency(typeAmount)}</div>
                    <div className="breakdown-count">{typeApps.length} applications</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="modal-actions">
            <button className="btn-secondary" onClick={() => setShowStatsModal(false)}>
              Close
            </button>
            <button className="btn-primary" onClick={() => onViewChange && onViewChange('applications')}>
              View Applications
            </button>
          </div>
        </div>
      </div>
    );
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
                ₱{dashboardData.pending_applications.reduce((sum, app) => sum + app.amount, 0).toLocaleString()} pending
              </div>
            )}
          </button>

          <button className="command-btn analytics" onClick={() => onViewChange && onViewChange('analytics')}>
            <div className="command-header">
              <div className="command-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div className="command-label">Analytics Dashboard</div>
            <div className="command-status">View Insights</div>
            <div className="priority-indicator medium">
              Data Insights
            </div>
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
            background: 'var(--secondary-bg)',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid var(--border-color)'
          }}>
            <h3 style={{
              color: 'var(--text-primary)',
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
                    background: 'var(--card-bg)',
                    padding: '15px',
                    borderRadius: '8px',
                    marginBottom: '10px',
                    border: '1px solid var(--border-color)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                      <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>{grade.student_name}</strong>
                      <span style={{
                        background: 'var(--accent-blue)',
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px'
                      }}>
                        {grade.status_display}
                      </span>
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '5px' }}>
                      ID: {grade.student_id} • {grade.academic_year} {grade.semester_display}
                    </div>
                    <div style={{ color: '#64748b', fontSize: '12px', marginBottom: '5px' }}>
                      GWA: {safeToFixed(grade.general_weighted_average)} | SWA: {safeToFixed(grade.semestral_weighted_average)}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
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
                  background: 'var(--card-bg)',
                  padding: '20px',
                  borderRadius: '8px',
                  textAlign: 'center',
                  color: 'var(--text-muted)'
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
          background: 'var(--secondary-bg)',
          padding: '20px',
          borderRadius: '12px',
          border: '1px solid var(--border-color)'
        }}>
          <h3 style={{
            color: 'var(--text-primary)',
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
                    background: 'var(--card-bg)',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                      <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>{app.student_name}</strong>
                      <span style={{
                        background: 'var(--accent-orange)',
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '12px'
                      }}>
                        {app.status_display}
                      </span>
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '5px' }}>
                      ID: {app.student_id} • {app.application_type_display}
                    </div>
                    <div style={{ color: '#10b981', fontSize: '14px', fontWeight: '600', marginBottom: '5px' }}>
                      ₱{app.amount.toLocaleString()}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                      Applied: {new Date(app.applied_at).toLocaleDateString()}
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
                background: 'var(--card-bg)',
                padding: '20px',
                borderRadius: '8px',
                textAlign: 'center',
                color: 'var(--text-muted)'
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
      </div>

      {/* Stats Modal */}
      {showStatsModal && <StatsModal />}
    </div>
  );
};

export default AdminDashboard;
