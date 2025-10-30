import React, { useState } from 'react';
import AllowanceApplicationForm from './AllowanceApplicationForm';
import { DocumentIcon, RequirementsIcon, MoneyIcon, WarningIcon } from './Icons';
import './ApplicationDetailsPage.css';

interface AllowanceApplication {
  id: number;
  application_type_display: string;
  amount: number;
  status: string;
  status_display: string;
  applied_at: string;
}

interface ApplicationDetailsPageProps {
  applications: AllowanceApplication[];
  darkMode: boolean;
  canApplyForAllowance: boolean;
  onAllowanceApplicationSuccess: () => void;
  onRefresh: () => void;
}

const ApplicationDetailsPage: React.FC<ApplicationDetailsPageProps> = ({ 
  applications, 
  darkMode, 
  canApplyForAllowance,
  onAllowanceApplicationSuccess,
  onRefresh 
}) => {
  const [showAllowanceForm, setShowAllowanceForm] = useState(false);

  const totalApplications = applications.length;
  const approvedApplications = applications.filter(a => a.status === 'approved').length;
  const pendingApplications = applications.filter(a => a.status === 'pending').length;
  const totalAmount = applications
    .filter(a => a.status === 'approved')
    .reduce((sum, app) => sum + app.amount, 0);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP'
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return '#10b981';
      case 'pending':
        return '#f59e0b';
      case 'rejected':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return '✅';
      case 'pending':
        return '⏳';
      case 'rejected':
        return '❌';
      default:
        return <DocumentIcon size={16} />;
    }
  };

  const handleFormSuccess = () => {
    setShowAllowanceForm(false);
    onAllowanceApplicationSuccess();
  };

  const handleRefresh = () => {
    onRefresh();
  };

  return (
    <div className={`application-details-page ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Refresh Button - Always Visible */}
      <button 
          className="refresh-button-corner"
          onClick={handleRefresh}
          title="Refresh to see updated data"
        >
          🔄
        </button>
      
      <div className="page-header">
        <h1>Application Details</h1>
        <p>Track your allowance applications and their status</p>
      </div>

      {/* Stats Overview */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <RequirementsIcon size={24} />
          </div>
          <div className="stat-content">
            <h3>Total Applications</h3>
            <div className="stat-value">{totalApplications}</div>
            <p>Submitted applications</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>Approved</h3>
            <div className="stat-value">{approvedApplications}</div>
            <p>Successfully processed</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <h3>Pending</h3>
            <div className="stat-value">{pendingApplications}</div>
            <p>Under review</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <MoneyIcon size={24} />
          </div>
          <div className="stat-content">
            <h3>Total Amount</h3>
            <div className="stat-value">{formatCurrency(totalAmount)}</div>
            <p>Approved allowances</p>
          </div>
        </div>
      </div>

      {/* Apply for Allowance Section */}
      {canApplyForAllowance && (
        <div className="apply-section">
          <button 
            className="apply-button"
            onClick={() => setShowAllowanceForm(true)}
          >
            <MoneyIcon size={16} />
            Apply for Allowance
          </button>
          <p>Submit a new allowance application based on your approved grades</p>
        </div>
      )}

      {!canApplyForAllowance && (
        <div className="requirement-notice">
          <div className="notice-icon">
            <WarningIcon size={24} />
          </div>
          <div className="notice-content">
            <h3>Grades Required</h3>
            <p>You need approved grades that qualify for allowances before you can submit an application.</p>
          </div>
        </div>
      )}

      {/* Application Process Steps */}
      <div className="process-section">
        <h2>Application Process</h2>
        <div className="process-steps">
          <div className="process-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Submit Documents</h3>
              <p>Upload required documents (ID, transcript, etc.)</p>
            </div>
          </div>
          <div className="process-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Submit Grades</h3>
              <p>Add your semester grades for evaluation</p>
            </div>
          </div>
          <div className="process-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Apply for Allowance</h3>
              <p>Submit allowance application based on grades</p>
            </div>
          </div>
          <div className="process-step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>Review Process</h3>
              <p>Admin reviews and approves your application</p>
            </div>
          </div>
        </div>
      </div>

      {/* Applications List */}
      {applications.length > 0 ? (
        <div className="applications-list">
          <h2>Your Applications</h2>
          <div className="applications-grid">
            {applications.map((application) => (
              <div key={application.id} className="application-card">
                <div className="application-header">
                  <div className="application-info">
                    <h3>{application.application_type_display}</h3>
                    <div className="application-amount">
                      {formatCurrency(application.amount)}
                    </div>
                  </div>
                  <div className="application-status">
                    <span className="status-icon">
                      {getStatusIcon(application.status)}
                    </span>
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(application.status) }}
                    >
                      {application.status_display}
                    </span>
                  </div>
                </div>

                <div className="application-details">
                  <div className="detail-row">
                    <span className="detail-label">Application Type:</span>
                    <span className="detail-value">{application.application_type_display}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Amount Requested:</span>
                    <span className="detail-value">{formatCurrency(application.amount)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Status:</span>
                    <span className="detail-value">{application.status_display}</span>
                  </div>
                </div>

                <div className="application-footer">
                  <span className="application-date">
                    Applied: {new Date(application.applied_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <h3>No Applications Yet</h3>
          <p>Submit your documents and grades first, then you can apply for allowances based on your academic performance.</p>
        </div>
      )}

      {/* Allowance Application Form Modal */}
      {showAllowanceForm && (
        <AllowanceApplicationForm
          onCancel={() => setShowAllowanceForm(false)}
          onSubmissionSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
};

export default ApplicationDetailsPage;