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

interface AdminDashboardProps {
  onViewChange?: (view: string) => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onViewChange }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get<AdminDashboardData>('/dashboard/admin/');
        setDashboardData(response.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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
        {/* Header Section */}
        <div className="command-center-header">
          <div className="header-grid">
            <div className="command-title">
              <div className="status-indicator">
                <div className="pulse-dot"></div>
                <span>Online</span>
              </div>
              <h1>Admin Dashboard</h1>
              <p>TCU CEAA Management System</p>
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
          <button className="command-btn documents" onClick={() => console.log('Navigate to documents')}>
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
          </button>

          <button className="command-btn grades" onClick={() => console.log('Navigate to grades')}>
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
          </button>

          <button className="command-btn applications" onClick={() => console.log('Navigate to applications')}>
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
                dashboardData.pending_documents.map((doc) => (
                  <div key={doc.id} className="operation-item">
                    <div className="operation-header">
                      <div className="operation-id">ID-{doc.student_id}</div>
                      <div className="operation-status pending">Pending</div>
                    </div>
                    <div className="operation-title">{doc.student_name}</div>
                    <div className="operation-detail">{doc.document_type_display}</div>
                    <div className="operation-timestamp">
                      SUBMITTED: {new Date(doc.submitted_at).toLocaleDateString('en-US', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' }).toUpperCase()}
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
                  <p style={{ margin: '0' }}>No pending documents</p>
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
              � Pending Grades ({dashboardData?.pending_grades.length || 0})
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
                      GWA: {grade.general_weighted_average.toFixed(2)} | SWA: {grade.semestral_weighted_average.toFixed(2)}
                    </div>
                    <div style={{ color: '#64748b', fontSize: '12px' }}>
                      Submitted: {formatDate(grade.submitted_at)}
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
                  <div style={{ fontSize: '32px', opacity: '0.5', marginBottom: '10px' }}>�</div>
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
                      ₱{app.amount.toLocaleString()}
                    </div>
                    <div style={{ color: '#64748b', fontSize: '12px' }}>
                      Applied: {formatDate(app.applied_at)}
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
      </div>
    </div>
  );
};

export default AdminDashboard;
