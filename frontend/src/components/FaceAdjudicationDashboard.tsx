import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import './FaceAdjudicationDashboard.css';

interface DashboardResponse {
  stats: DashboardStats;
  recent_pending: VerificationAdjudication[];
  low_confidence: VerificationAdjudication[];
}

interface DecisionResponse {
  success: boolean;
  message?: string;
  error?: string;
}

interface VerificationAdjudication {
  id: number;
  user_name: string;
  user_student_id: string;
  user: number;
  application_type: string;
  school_id_image_path: string;
  selfie_image_path: string;
  verification_backend: string;
  automated_liveness_score: number;
  automated_match_result: boolean;
  automated_similarity_score: number;
  automated_confidence_level: string;
  status: string;
  admin_decision: string;
  admin_notes?: string;
  admin_reviewer_name?: string;
  created_at: string;
  reviewed_at?: string;
  grade_submission_info?: {
    academic_year: string;
    semester: string;
    gwa: string;
  };
}

interface DashboardStats {
  total_pending: number;
  total_under_review: number;
  total_completed: number;
  total_errors: number;
  total_approved: number;
  total_rejected: number;
  total_escalated: number;
  low_confidence_count: number;
  high_confidence_count: number;
}

const FaceAdjudicationDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pendingVerifications, setPendingVerifications] = useState<VerificationAdjudication[]>([]);
  const [lowConfidenceVerifications, setLowConfidenceVerifications] = useState<VerificationAdjudication[]>([]);
  const [selectedVerification, setSelectedVerification] = useState<VerificationAdjudication | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'pending' | 'low-confidence' | 'detail'>('pending');
  const [decisionLoading, setDecisionLoading] = useState(false);
  const [decisionNotes, setDecisionNotes] = useState('');
  const [decisionError, setDecisionError] = useState('');
  const [decisionSuccess, setDecisionSuccess] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('pending_review');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/face-adjudications/dashboard/');
      const data = response.data as DashboardResponse;
      
      console.log('Face Adjudication Dashboard Data:', data);
      
      setStats(data.stats);
      setPendingVerifications(data.recent_pending || []);
      setLowConfidenceVerifications(data.low_confidence || []);
    } catch (error: any) {
      console.error('Error fetching face adjudication dashboard:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      // Set empty data on error
      setStats({
        total_pending: 0,
        total_under_review: 0,
        total_completed: 0,
        total_errors: 0,
        total_approved: 0,
        total_rejected: 0,
        total_escalated: 0,
        low_confidence_count: 0,
        high_confidence_count: 0
      });
      setPendingVerifications([]);
      setLowConfidenceVerifications([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectVerification = (verification: VerificationAdjudication) => {
    setSelectedVerification(verification);
    setActiveTab('detail');
    setDecisionNotes('');
    setDecisionError('');
    setDecisionSuccess('');
  };

  const handleApprove = async () => {
    if (!selectedVerification) return;
    await submitDecision('approved');
  };

  const handleReject = async () => {
    if (!selectedVerification) return;
    await submitDecision('rejected');
  };

  const handleEscalate = async () => {
    if (!selectedVerification) return;
    await submitDecision('escalated');
  };

  const submitDecision = async (decision: 'approved' | 'rejected' | 'escalated') => {
    if (!selectedVerification) return;

    try {
      setDecisionLoading(true);
      setDecisionError('');
      setDecisionSuccess('');

      const response = await apiClient.post(
        `/admin/face-adjudications/${selectedVerification.id}/decide/`,
        {
          decision: decision,
          notes: decisionNotes
        }
      );
      const data = response.data as DecisionResponse;

      if (data.success) {
        setDecisionSuccess(`Verification ${decision} successfully!`);
        // Refresh dashboard
        setTimeout(() => {
          fetchDashboardData();
          setSelectedVerification(null);
          setActiveTab('pending');
        }, 1500);
      }
    } catch (error: any) {
      console.error(`Error ${decision} verification:`, error);
      setDecisionError(error.response?.data?.error || `Failed to ${decision} verification`);
    } finally {
      setDecisionLoading(false);
    }
  };

  const getConfidenceBadgeColor = (level: string): string => {
    switch (level) {
      case 'very_high':
        return 'badge-success';
      case 'high':
        return 'badge-info';
      case 'medium':
        return 'badge-warning';
      case 'low':
        return 'badge-orange';
      case 'very_low':
        return 'badge-danger';
      default:
        return 'badge-secondary';
    }
  };

  const formatConfidenceLevel = (level: string): string => {
    const map: Record<string, string> = {
      'very_high': 'Very High (≥99%)',
      'high': 'High (≥95%)',
      'medium': 'Medium (≥90%)',
      'low': 'Low (≥85%)',
      'very_low': 'Very Low (<85%)'
    };
    return map[level] || level;
  };

  if (loading) {
    return (
      <div className="face-adjudication-dashboard">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading adjudication dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="face-adjudication-dashboard">
      <div className="dashboard-header">
        <h1>🔒 Face Verification Adjudication Dashboard</h1>
        <p>Review and approve/reject face verification attempts</p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="statistics-grid">
          <div className="stat-card pending">
            <div className="stat-value">{stats.total_pending}</div>
            <div className="stat-label">Pending Review</div>
          </div>
          <div className="stat-card approved">
            <div className="stat-value">{stats.total_approved}</div>
            <div className="stat-label">Approved</div>
          </div>
          <div className="stat-card rejected">
            <div className="stat-value">{stats.total_rejected}</div>
            <div className="stat-label">Rejected</div>
          </div>
          <div className="stat-card escalated">
            <div className="stat-value">{stats.total_escalated}</div>
            <div className="stat-label">Escalated</div>
          </div>
          <div className="stat-card low-confidence">
            <div className="stat-value">{stats.low_confidence_count}</div>
            <div className="stat-label">Low Confidence</div>
          </div>
          <div className="stat-card high-confidence">
            <div className="stat-value">{stats.high_confidence_count}</div>
            <div className="stat-label">High Confidence</div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveTab('pending')}
        >
          📋 Pending ({pendingVerifications.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'low-confidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('low-confidence')}
        >
          ⚠️ Low Confidence ({lowConfidenceVerifications.length})
        </button>
      </div>

      <div className="dashboard-content">
        {/* Pending Verifications List */}
        {activeTab === 'pending' && (
          <div className="verification-list">
            <div className="list-header">
              <h3>Pending Verifications</h3>
              <p>{pendingVerifications.length} awaiting admin review</p>
            </div>
            {pendingVerifications.length === 0 ? (
              <div className="empty-state">
                <p>✅ No pending verifications. All caught up!</p>
              </div>
            ) : (
              <div className="verification-items">
                {pendingVerifications.map((verification) => (
                  <div
                    key={verification.id}
                    className="verification-item"
                    onClick={() => handleSelectVerification(verification)}
                  >
                    <div className="item-header">
                      <div className="user-info">
                        <span className="user-name">{verification.user_name}</span>
                        <span className="student-id">{verification.user_student_id}</span>
                      </div>
                      <span className={`confidence-badge ${getConfidenceBadgeColor(verification.automated_confidence_level)}`}>
                        {formatConfidenceLevel(verification.automated_confidence_level)}
                      </span>
                    </div>
                    <div className="item-scores">
                      <div className="score">
                        <span className="score-label">Similarity:</span>
                        <span className="score-value">{(verification.automated_similarity_score * 100).toFixed(2)}%</span>
                      </div>
                      <div className="score">
                        <span className="score-label">Liveness:</span>
                        <span className="score-value">{(verification.automated_liveness_score * 100).toFixed(2)}%</span>
                      </div>
                    </div>
                    <div className="item-timestamp">
                      <small>{new Date(verification.created_at).toLocaleString()}</small>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Low Confidence List */}
        {activeTab === 'low-confidence' && (
          <div className="verification-list">
            <div className="list-header">
              <h3>Low Confidence Verifications</h3>
              <p>⚠️ {lowConfidenceVerifications.length} requiring closer review</p>
            </div>
            {lowConfidenceVerifications.length === 0 ? (
              <div className="empty-state">
                <p>✅ No low-confidence verifications found.</p>
              </div>
            ) : (
              <div className="verification-items">
                {lowConfidenceVerifications.map((verification) => (
                  <div
                    key={verification.id}
                    className="verification-item low-confidence-item"
                    onClick={() => handleSelectVerification(verification)}
                  >
                    <div className="item-header">
                      <div className="user-info">
                        <span className="user-name">{verification.user_name}</span>
                        <span className="student-id">{verification.user_student_id}</span>
                      </div>
                      <span className={`confidence-badge ${getConfidenceBadgeColor(verification.automated_confidence_level)}`}>
                        ⚠️ {formatConfidenceLevel(verification.automated_confidence_level)}
                      </span>
                    </div>
                    <div className="item-scores">
                      <div className="score">
                        <span className="score-label">Similarity:</span>
                        <span className="score-value">{(verification.automated_similarity_score * 100).toFixed(2)}%</span>
                      </div>
                      <div className="score">
                        <span className="score-label">Match:</span>
                        <span className={`score-value ${verification.automated_match_result ? 'pass' : 'fail'}`}>
                          {verification.automated_match_result ? '✓ PASS' : '✗ FAIL'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Detailed Review Panel */}
        {activeTab === 'detail' && selectedVerification && (
          <div className="verification-detail-panel">
            <div className="detail-header">
              <h2>Verification Details</h2>
              <button className="close-button" onClick={() => setActiveTab('pending')}>✕</button>
            </div>

            {decisionError && (
              <div className="alert alert-error">
                <span className="alert-icon">❌</span>
                {decisionError}
              </div>
            )}

            {decisionSuccess && (
              <div className="alert alert-success">
                <span className="alert-icon">✅</span>
                {decisionSuccess}
              </div>
            )}

            <div className="detail-content">
              {/* User Info Section */}
              <section className="detail-section">
                <h3>Student Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Name:</span>
                    <span className="info-value">{selectedVerification.user_name}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Student ID:</span>
                    <span className="info-value">{selectedVerification.user_student_id}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Application Type:</span>
                    <span className="info-value">{selectedVerification.application_type || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Submitted:</span>
                    <span className="info-value">{new Date(selectedVerification.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </section>

              {/* Grade Info Section */}
              {selectedVerification.grade_submission_info && (
                <section className="detail-section">
                  <h3>Grade Submission Information</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <span className="info-label">Academic Year:</span>
                      <span className="info-value">{selectedVerification.grade_submission_info.academic_year}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Semester:</span>
                      <span className="info-value">{selectedVerification.grade_submission_info.semester}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">GWA:</span>
                      <span className="info-value">{selectedVerification.grade_submission_info.gwa}%</span>
                    </div>
                  </div>
                </section>
              )}

              {/* Automated Results Section */}
              <section className="detail-section verification-results">
                <h3>Automated Verification Results</h3>
                <div className="results-grid">
                  <div className="result-box">
                    <span className="result-label">Verification Method:</span>
                    <span className="result-value">Automated Verification</span>
                  </div>
                  <div className="result-box">
                    <span className="result-label">Similarity Score:</span>
                    <span className="result-value">
                      {(selectedVerification.automated_similarity_score * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="result-box">
                    <span className="result-label">Liveness Score:</span>
                    <span className="result-value">
                      {(selectedVerification.automated_liveness_score * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="result-box">
                    <span className="result-label">Confidence:</span>
                    <span className={`result-value ${getConfidenceBadgeColor(selectedVerification.automated_confidence_level).replace('badge-', '')}`}>
                      {formatConfidenceLevel(selectedVerification.automated_confidence_level)}
                    </span>
                  </div>
                  <div className="result-box">
                    <span className="result-label">Face Match:</span>
                    <span className={`result-value ${selectedVerification.automated_match_result ? 'pass' : 'fail'}`}>
                      {selectedVerification.automated_match_result ? '✓ MATCHED' : '✗ NOT MATCHED'}
                    </span>
                  </div>
                </div>
              </section>

              {/* Image Comparison Section */}
              <section className="detail-section image-comparison">
                <h3>Image Comparison</h3>
                <div className="images-grid">
                  <div className="image-container">
                    <h4>School ID</h4>
                    <div className="image-placeholder">
                      <p>School ID Image</p>
                      <small>{selectedVerification.school_id_image_path}</small>
                    </div>
                  </div>
                  <div className="image-container">
                    <h4>Live Selfie</h4>
                    <div className="image-placeholder">
                      <p>Live Captured Selfie</p>
                      <small>{selectedVerification.selfie_image_path}</small>
                    </div>
                  </div>
                </div>
              </section>

              {/* Admin Decision Section */}
              <section className="detail-section admin-decision">
                <h3>Administrative Decision</h3>
                <div className="decision-form">
                  <div className="form-group">
                    <label htmlFor="adminNotes">Notes (Optional):</label>
                    <textarea
                      id="adminNotes"
                      value={decisionNotes}
                      onChange={(e) => setDecisionNotes(e.target.value)}
                      placeholder="Add admin notes or observations..."
                      rows={4}
                      disabled={decisionLoading}
                    />
                  </div>

                  <div className="decision-buttons">
                    <button
                      className="btn btn-reject"
                      onClick={handleReject}
                      disabled={decisionLoading}
                    >
                      ✗ Reject
                    </button>
                    <button
                      className="btn btn-escalate"
                      onClick={handleEscalate}
                      disabled={decisionLoading}
                    >
                      ⚠️ Escalate
                    </button>
                    <button
                      className="btn btn-approve"
                      onClick={handleApprove}
                      disabled={decisionLoading}
                    >
                      ✓ Approve
                    </button>
                  </div>
                </div>
              </section>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceAdjudicationDashboard;
