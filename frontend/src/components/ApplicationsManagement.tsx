import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import { formatCurrency } from '../utils/numberUtils';
import NotificationDialog from './NotificationDialog';
import { useNotification } from '../hooks/useNotification';
import './ApplicationsManagement.css';

interface Application {
  id: number;
  student_name: string;
  student_id: string;
  application_type: string;
  application_type_display: string;
  amount: number;
  status: string;
  status_display: string;
  applied_at: string;
  reason?: string;
}

interface ApplicationsManagementProps {
  onViewChange?: (view: string) => void;
}

const ApplicationsManagement: React.FC<ApplicationsManagementProps> = ({ onViewChange }) => {
  const { notification, confirm: showConfirm, alert: showAlert } = useNotification();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get<Application[]>('/applications/');
        setApplications(response.data);
      } catch (err) {
        console.error('Error fetching applications:', err);
        setError('Failed to load applications. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  // Function to refresh applications data
  const refreshApplications = async () => {
    try {
      const response = await apiClient.get<Application[]>('/applications/');
      setApplications(response.data);
    } catch (error) {
      console.error('Error refreshing applications:', error);
    }
  };

  // Handle view application details
  const handleViewApplication = (application: Application) => {
    setSelectedApplication(application);
    setShowApplicationModal(true);
  };

  // Close application modal
  const closeApplicationModal = () => {
    setShowApplicationModal(false);
    setSelectedApplication(null);
  };

  // Handle application actions (approve, reject, disburse)
  const handleApplicationAction = async (applicationId: number, action: string) => {
    const actionKey = `${action}_${applicationId}`;
    
    try {
      setActionLoading(prev => ({ ...prev, [actionKey]: true }));
      
      const endpoint = `/applications/${applicationId}/process/`;
      const payload = { 
        status: action, 
        admin_notes: `Application ${action} by admin` 
      };
      
      await apiClient.post(endpoint, payload);
      
      // Refresh applications data
      await refreshApplications();
      
      // Close modal if it's open
      if (showApplicationModal) {
        closeApplicationModal();
      }
      
    } catch (error) {
      console.error(`Error ${action}ing application:`, error);
      await showAlert({
        message: `Failed to ${action} application. Please try again.`,
        type: 'error',
        confirmText: 'OK'
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  // Handle delete application
  const handleDeleteApplication = async (applicationId: number, applicationName: string) => {
    // Confirm deletion
    const confirmed = await showConfirm({
      message: `Are you sure you want to delete this application?\n\nApplication: ${applicationName}\nID: #${applicationId}\n\nThis action cannot be undone!`,
      type: 'warning',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    });
    
    if (!confirmed) return;

    const actionKey = `delete_${applicationId}`;
    
    try {
      setActionLoading(prev => ({ ...prev, [actionKey]: true }));
      
      await apiClient.delete(`/applications/${applicationId}/`);
      
      // Refresh applications data
      await refreshApplications();
      
      // Close modal if it's open
      if (showApplicationModal) {
        closeApplicationModal();
      }
      
      await showAlert({
        message: 'Application deleted successfully!',
        type: 'success',
        confirmText: 'OK'
      });
      
    } catch (error: any) {
      console.error('Error deleting application:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Failed to delete application. Please try again.';
      await showAlert({
        message: `Error: ${errorMessage}`,
        type: 'error',
        confirmText: 'OK'
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: false }));
    }
  };

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.application_type_display.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === '' || app.status === statusFilter;
    const matchesType = typeFilter === '' || app.application_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      case 'disbursed': return '#3b82f6';
      default: return '#6b7280';
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

  const totalAmount = filteredApplications.reduce((sum, app) => sum + app.amount, 0);
  const approvedAmount = filteredApplications.filter(app => app.status === 'approved').reduce((sum, app) => sum + app.amount, 0);
  const pendingAmount = filteredApplications.filter(app => app.status === 'pending').reduce((sum, app) => sum + app.amount, 0);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2 className="loading-title">Loading Applications</h2>
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
          <h2 className="error-title">Error Loading Applications</h2>
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
    <div className="applications-management-container">
      <div className="applications-management-content">
        {/* Header */}
        <div className="management-header">
          <div className="header-content">
            <h1>Applications Management</h1>
            <p>Review and manage all allowance applications in the TCU-CEAA system</p>
          </div>
          
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-number">{applications.length}</div>
              <div className="stat-label">Total Applications</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{formatCurrency(approvedAmount)}</div>
              <div className="stat-label">Approved Amount</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{formatCurrency(pendingAmount)}</div>
              <div className="stat-label">Pending Amount</div>
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
                placeholder="Search by student name, ID, or application type..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="disbursed">Disbursed</option>
            </select>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Types</option>
              <option value="basic_allowance">Basic Allowance</option>
              <option value="merit_incentive">Merit Incentive</option>
              <option value="special_allowance">Special Allowance</option>
            </select>
          </div>
        </div>

        {/* Applications List */}
        <div className="applications-grid">
          {filteredApplications.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">💸</div>
              <h3>No Applications Found</h3>
              <p>
                {searchTerm || statusFilter || typeFilter
                  ? `No applications match your filters`
                  : 'No allowance applications have been submitted yet.'
                }
              </p>
              {(searchTerm || statusFilter || typeFilter) && (
                <button 
                  className="clear-filters-btn"
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('');
                    setTypeFilter('');
                  }}
                >
                  Clear Filters
                </button>
              )}
            </div>
          ) : (
            filteredApplications.map((app) => (
              <div key={app.id} className="application-card">
                <div className="application-header">
                  <div className="application-type">
                    <h3 className="type-title">{app.application_type_display}</h3>
                    <div className="application-id">App ID: #{app.id}</div>
                  </div>
                  <div className="application-status">
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(app.status) }}
                    >
                      {app.status_display}
                    </span>
                  </div>
                </div>

                <div className="student-section">
                  <div className="student-avatar">
                    {app.student_name.split(' ').map(name => name[0]).join('')}
                  </div>
                  <div className="student-details">
                    <div className="student-name">{app.student_name}</div>
                    <div className="student-id">ID: {app.student_id}</div>
                  </div>
                </div>

                <div className="amount-section">
                  <div className="amount-label">Requested Amount</div>
                  <div className="amount-value">{formatCurrency(app.amount)}</div>
                </div>

                <div className="application-details">
                  <div className="detail-row">
                    <span className="detail-label">Applied:</span>
                    <span className="detail-value">{formatDate(app.applied_at)}</span>
                  </div>
                  {app.reason && (
                    <div className="detail-row">
                      <span className="detail-label">Reason:</span>
                      <span className="detail-value">{app.reason}</span>
                    </div>
                  )}
                </div>

                <div className="application-actions">
                  <button 
                    className="action-btn view-btn"
                    onClick={() => handleViewApplication(app)}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                    </svg>
                    View Details
                  </button>
                  {app.status === 'pending' && (
                    <>
                      <button 
                        className="action-btn approve-btn"
                        onClick={() => handleApplicationAction(app.id, 'approved')}
                        disabled={actionLoading[`approved_${app.id}`]}
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {actionLoading[`approved_${app.id}`] ? 'Processing...' : 'Approve'}
                      </button>
                      <button 
                        className="action-btn reject-btn"
                        onClick={() => handleApplicationAction(app.id, 'rejected')}
                        disabled={actionLoading[`rejected_${app.id}`]}
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {actionLoading[`rejected_${app.id}`] ? 'Processing...' : 'Reject'}
                      </button>
                    </>
                  )}
                  {app.status === 'approved' && (
                    <button 
                      className="action-btn disburse-btn"
                      onClick={() => handleApplicationAction(app.id, 'disbursed')}
                      disabled={actionLoading[`disbursed_${app.id}`]}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {actionLoading[`disbursed_${app.id}`] ? 'Processing...' : 'Disburse'}
                    </button>
                  )}
                  <button 
                    className="action-btn delete-btn"
                    onClick={() => handleDeleteApplication(app.id, app.application_type_display)}
                    disabled={actionLoading[`delete_${app.id}`]}
                    title="Delete Application"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path fillRule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clipRule="evenodd" />
                    </svg>
                    {actionLoading[`delete_${app.id}`] ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Application Details Modal */}
        {showApplicationModal && selectedApplication && (
          <div className="modal-overlay" onClick={closeApplicationModal}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Application Details</h2>
                <button className="modal-close" onClick={closeApplicationModal}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="modal-body">
                <div className="application-info-grid">
                  <div className="info-section">
                    <h3>Student Information</h3>
                    <div className="info-row">
                      <label>Student Name:</label>
                      <span>{selectedApplication.student_name}</span>
                    </div>
                    <div className="info-row">
                      <label>Student ID:</label>
                      <span>{selectedApplication.student_id}</span>
                    </div>
                  </div>

                  <div className="info-section">
                    <h3>Application Information</h3>
                    <div className="info-row">
                      <label>Application ID:</label>
                      <span>#{selectedApplication.id}</span>
                    </div>
                    <div className="info-row">
                      <label>Application Type:</label>
                      <span>{selectedApplication.application_type_display}</span>
                    </div>
                    <div className="info-row">
                      <label>Requested Amount:</label>
                      <span className="amount-highlight">{formatCurrency(selectedApplication.amount)}</span>
                    </div>
                    <div className="info-row">
                      <label>Status:</label>
                      <span 
                        className="status-badge-modal"
                        style={{ backgroundColor: getStatusColor(selectedApplication.status) }}
                      >
                        {selectedApplication.status_display}
                      </span>
                    </div>
                    <div className="info-row">
                      <label>Applied Date:</label>
                      <span>{formatDate(selectedApplication.applied_at)}</span>
                    </div>
                    {selectedApplication.reason && (
                      <div className="info-row">
                        <label>Reason/Comments:</label>
                        <span className="reason-text">{selectedApplication.reason}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Buttons in Modal */}
                <div className="modal-actions">
                  {selectedApplication.status === 'pending' && (
                    <>
                      <button 
                        className="modal-action-btn approve"
                        onClick={() => handleApplicationAction(selectedApplication.id, 'approved')}
                        disabled={actionLoading[`approved_${selectedApplication.id}`]}
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {actionLoading[`approved_${selectedApplication.id}`] ? 'Processing...' : 'Approve Application'}
                      </button>
                      <button 
                        className="modal-action-btn reject"
                        onClick={() => handleApplicationAction(selectedApplication.id, 'rejected')}
                        disabled={actionLoading[`rejected_${selectedApplication.id}`]}
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {actionLoading[`rejected_${selectedApplication.id}`] ? 'Processing...' : 'Reject Application'}
                      </button>
                    </>
                  )}
                  {selectedApplication.status === 'approved' && (
                    <button 
                      className="modal-action-btn disburse"
                      onClick={() => handleApplicationAction(selectedApplication.id, 'disbursed')}
                      disabled={actionLoading[`disbursed_${selectedApplication.id}`]}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {actionLoading[`disbursed_${selectedApplication.id}`] ? 'Processing...' : 'Disburse Funds'}
                    </button>
                  )}
                  <button 
                    className="modal-action-btn delete"
                    onClick={() => handleDeleteApplication(selectedApplication.id, selectedApplication.application_type_display)}
                    disabled={actionLoading[`delete_${selectedApplication.id}`]}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path fillRule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clipRule="evenodd" />
                    </svg>
                    {actionLoading[`delete_${selectedApplication.id}`] ? 'Deleting...' : 'Delete Application'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <NotificationDialog {...notification} />
    </div>
  );
};

export default ApplicationsManagement;
