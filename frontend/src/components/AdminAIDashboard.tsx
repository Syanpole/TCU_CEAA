/**
 * 🤖 Admin AI Dashboard
 * Comprehensive AI system management and monitoring for administrators
 * Real-time statistics, system controls, and performance analytics
 */

import React, { useState, useEffect } from 'react';
import { aiService, AIDashboardStats } from '../services/aiService';
import AIVerificationDashboard from './AIVerificationDashboard';
import ModernLoadingSpinner from './ModernLoadingSpinner';
import './AdminAIDashboard.css';

interface AdminAIDashboardProps {
  refreshInterval?: number; // Auto-refresh interval in milliseconds
}

const AdminAIDashboard: React.FC<AdminAIDashboardProps> = ({
  refreshInterval = 30000 // 30 seconds default
}) => {
  const [dashboardStats, setDashboardStats] = useState<AIDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(() => {
        loadDashboardData(false); // Silent refresh
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const loadDashboardData = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      setError('');
      
      const stats = await aiService.getDashboardStats();
      setDashboardStats(stats);
      setLastUpdated(new Date());
    } catch (error: any) {
      setError(`Failed to load AI dashboard: ${error.message}`);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const calculateSystemHealth = (): { score: number; status: string; color: string } => {
    if (!dashboardStats) return { score: 0, status: 'Unknown', color: '#999' };

    const {
      auto_approval_rate,
      average_confidence,
      processing_efficiency
    } = dashboardStats.ai_statistics;

    const healthScore = (auto_approval_rate + average_confidence + processing_efficiency) / 3;
    
    if (healthScore >= 0.8) {
      return { score: healthScore, status: 'Excellent', color: '#52c41a' };
    } else if (healthScore >= 0.6) {
      return { score: healthScore, status: 'Good', color: '#faad14' };
    } else if (healthScore >= 0.4) {
      return { score: healthScore, status: 'Fair', color: '#ff7a45' };
    } else {
      return { score: healthScore, status: 'Poor', color: '#ff4d4f' };
    }
  };

  const getRecentActivitySummary = () => {
    if (!dashboardStats?.recent_activities) return null;

    const activities = dashboardStats.recent_activities.slice(0, 5);
    return activities.map((activity, index) => ({
      ...activity,
      timeAgo: getTimeAgo(new Date(activity.timestamp))
    }));
  };

  const getTimeAgo = (date: Date): string => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  if (loading && !dashboardStats) {
    return <ModernLoadingSpinner text="Loading AI System Dashboard..." />;
  }

  if (error && !dashboardStats) {
    return (
      <div className="admin-ai-dashboard error">
        <div className="error-container">
          <div className="error-icon">❌</div>
          <h2>Dashboard Error</h2>
          <p>{error}</p>
          <button className="retry-btn" onClick={handleRefresh}>
            🔄 Retry Loading
          </button>
        </div>
      </div>
    );
  }

  const systemHealth = calculateSystemHealth();
  const recentActivities = getRecentActivitySummary();
  const performanceMetrics = dashboardStats ? aiService.calculatePerformanceMetrics(dashboardStats) : null;

  return (
    <div className="admin-ai-dashboard">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1>AI System Administration Dashboard</h1>
          <p>Comprehensive monitoring and management of the AI verification system</p>
        </div>
        <div className="header-controls">
          <div className="last-updated">
            Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}
          </div>
          <button 
            className={`auto-refresh-btn ${autoRefresh ? 'active' : ''}`}
            onClick={toggleAutoRefresh}
            title={`Auto refresh is ${autoRefresh ? 'ON' : 'OFF'}`}
          >
            {autoRefresh ? '🔄' : '⏸️'} Auto Refresh
          </button>
          <button className="refresh-btn" onClick={handleRefresh} disabled={loading}>
            🔄 Refresh Now
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      {dashboardStats && (
        <>
          {/* System Health Overview */}
          <div className="health-overview">
            <div className="health-card">
              <div className={`health-icon ${systemHealth.status.toLowerCase()}`}>
                {systemHealth.status === 'Excellent' ? '🟢' : 
                 systemHealth.status === 'Good' ? '🟡' : 
                 systemHealth.status === 'Fair' ? '🟠' : '🔴'}
              </div>
              <div className="health-content">
                <h3>System Health</h3>
                <div className={`health-score ${systemHealth.status.toLowerCase()}`}>
                  {(systemHealth.score * 100).toFixed(1)}% - {systemHealth.status}
                </div>
                <div className="health-description">
                  Overall AI system performance based on approval rate, confidence, and efficiency
                </div>
              </div>
            </div>

            <div className="quick-stats">
              <div className="quick-stat">
                <div className="stat-content">
                  <div className="stat-value">{dashboardStats.ai_statistics.total_processed}</div>
                  <div className="stat-label">Documents Processed</div>
                </div>
              </div>
              <div className="quick-stat">
                <div className="stat-content">
                  <div className="stat-value">{(dashboardStats.ai_statistics.auto_approval_rate * 100).toFixed(1)}%</div>
                  <div className="stat-label">Auto Approval Rate</div>
                </div>
              </div>
              <div className="quick-stat">
                <div className="stat-content">
                  <div className="stat-value">{(dashboardStats.ai_statistics.average_confidence * 100).toFixed(1)}%</div>
                  <div className="stat-label">Avg Confidence</div>
                </div>
              </div>
              <div className="quick-stat">
                <div className="stat-content">
                  <div className="stat-value">{(dashboardStats.ai_statistics.processing_efficiency * 100).toFixed(1)}%</div>
                  <div className="stat-label">Efficiency</div>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          {performanceMetrics && (
            <div className="performance-metrics">
              <h3>📈 Performance Analytics</h3>
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-title">Accuracy Rate</span>
                  </div>
                  <div className="metric-value">{performanceMetrics.accuracy_rate.toFixed(1)}%</div>
                  <div className="metric-description">Documents correctly processed</div>
                </div>
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-title">Processing Rate</span>
                  </div>
                  <div className="metric-value">{performanceMetrics.processing_rate.toFixed(1)}%</div>
                  <div className="metric-description">System processing efficiency</div>
                </div>
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-title">High Confidence</span>
                  </div>
                  <div className="metric-value">{performanceMetrics.high_confidence_ratio.toFixed(1)}%</div>
                  <div className="metric-description">Documents with 85%+ confidence</div>
                </div>
                <div className="metric-card">
                  <div className="metric-header">
                    <span className="metric-title">System Efficiency</span>
                  </div>
                  <div className="metric-value">{performanceMetrics.system_efficiency.toFixed(1)}%</div>
                  <div className="metric-description">Overall system performance</div>
                </div>
              </div>
            </div>
          )}

          {/* Recent Activities */}
          {recentActivities && recentActivities.length > 0 && (
            <div className="recent-activities">
              <h3>📋 Recent AI Activities</h3>
              <div className="activities-list">
                {recentActivities.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">
                      {activity.action === 'document_processed' ? '📄' :
                       activity.action === 'ai_analysis_completed' ? '🤖' :
                       activity.action === 'auto_approved' ? '✅' :
                       activity.action === 'manual_review' ? '👁️' : '📊'}
                    </div>
                    <div className="activity-content">
                      <div className="activity-description">{activity.description}</div>
                      <div className="activity-meta">
                        <span className="activity-user">👤 {activity.user}</span>
                        <span className="activity-time">🕐 {activity.timeAgo}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* System Status */}
          <div className="system-status">
            <h3>⚙️ System Status</h3>
            <div className="status-grid">
              <div className="status-item">
                <div className="status-indicator">
                  <div className={`status-light ${dashboardStats.system_status.ai_enabled ? 'green' : 'red'}`}></div>
                  <span className="status-label">AI System</span>
                </div>
                <div className="status-value">
                  {dashboardStats.system_status.ai_enabled ? 'Online' : 'Offline'}
                </div>
              </div>
              <div className="status-item">
                <div className="status-indicator">
                  <span className="status-label">Algorithms</span>
                </div>
                <div className="status-value">
                  {dashboardStats.system_status.algorithms_available}/6 Available
                </div>
              </div>
              <div className="status-item">
                <div className="status-indicator">
                  <span className="status-label">Queue</span>
                </div>
                <div className="status-value">
                  {dashboardStats.system_status.processing_queue} documents
                </div>
              </div>
            </div>
          </div>

          {/* Full AI Verification Dashboard */}
          <div className="full-dashboard-section">
            <AIVerificationDashboard showFullDashboard={true} />
          </div>
        </>
      )}
    </div>
  );
};

export default AdminAIDashboard;