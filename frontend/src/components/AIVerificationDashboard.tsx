/**
 * 🤖 AI Verification Dashboard
 * Real-time AI analysis monitoring and control center
 * Displays AI processing status, confidence scores, and algorithm results
 */

import React, { useState, useEffect } from 'react';
import { aiService, AIStatus, AIAnalysisResult, AIDashboardStats } from '../services/aiService';
import './AIVerificationDashboard.css';

interface AIVerificationDashboardProps {
  documentId?: number;
  showFullDashboard?: boolean;
}

const AIVerificationDashboard: React.FC<AIVerificationDashboardProps> = ({ 
  documentId, 
  showFullDashboard = true 
}) => {
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [dashboardStats, setDashboardStats] = useState<AIDashboardStats | null>(null);
  const [processingResults, setProcessingResults] = useState<AIAnalysisResult | null>(null);
  const [notification, setNotification] = useState<string>('');

  // Load AI status and dashboard data
  useEffect(() => {
    if (showFullDashboard) {
      loadDashboardStats();
    }
    if (documentId) {
      loadAIStatus();
    }
  }, [documentId, showFullDashboard]);

  const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setNotification(`${type.toUpperCase()}: ${message}`);
    setTimeout(() => setNotification(''), 5000);
  };

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      const stats = await aiService.getDashboardStats();
      setDashboardStats(stats);
    } catch (error: any) {
      showNotification(`Failed to load AI dashboard: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadAIStatus = async () => {
    if (!documentId) return;
    
    try {
      const status = await aiService.getAnalysisStatus(documentId);
      setAiStatus(status);
    } catch (error: any) {
      showNotification(`Failed to load AI status: ${error.message}`, 'error');
    }
  };

  const handleRunAIAnalysis = async () => {
    if (!documentId) return;

    try {
      setLoading(true);
      showNotification('AI Analysis Started - Running all 6 AI algorithms on the document...', 'info');

      const result = await aiService.analyzeDocument(documentId);
      setProcessingResults(result.results);
      
      showNotification(`AI Analysis Complete - Document processed with ${(result.results.overall_analysis.overall_confidence * 100).toFixed(1)}% confidence`, 'success');

      // Reload status
      await loadAIStatus();
    } catch (error: any) {
      showNotification(`AI Analysis Failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    const interpretation = aiService.interpretConfidence(confidence);
    return interpretation.color;
  };

  const getConfidenceLabel = (confidence: number): string => {
    const interpretation = aiService.interpretConfidence(confidence);
    return interpretation.label;
  };

  const getConfidenceLevel = (confidence: number): string => {
    const interpretation = aiService.interpretConfidence(confidence);
    return `${interpretation.level}-confidence`;
  };

  const getAlgorithmData = () => {
    if (!processingResults) return [];
    
    return Object.entries(processingResults.algorithms_results).map(([key, result]) => ({
      key,
      name: result?.name || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      confidence: result?.confidence || 0,
      status: result?.error ? 'error' : 'completed',
      error: result?.error,
      result: result,
    }));
  };

  if (loading && !dashboardStats && !aiStatus) {
    return (
      <div className="ai-dashboard-loading">
        <div className="loading-spinner">⏳</div>
        <p>Loading AI Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="ai-verification-dashboard">
      {/* Notification Bar */}
      {notification && (
        <div className="notification-bar">
          {notification}
        </div>
      )}

      {/* AI Status Card for Specific Document */}
      {documentId && (
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>🤖 AI Analysis Status - Document #{documentId}</h3>
            <button 
              className={`ai-btn ${loading ? 'loading' : ''} ${aiStatus?.ai_completed ? 'disabled' : 'primary'}`}
              onClick={handleRunAIAnalysis}
              disabled={loading || aiStatus?.ai_completed}
            >
              ⚡ {aiStatus?.ai_completed ? 'Analysis Complete' : 'Run AI Analysis'}
            </button>
          </div>
          
          <div className="ai-card-content">
            {aiStatus ? (
              <div className="ai-stats-grid">
                <div className="ai-stat">
                  <div className="ai-stat-title">Status</div>
                  <div className="ai-stat-value">
                    {aiStatus.ai_completed ? '✅' : '⏳'} {aiStatus.status.replace(/_/g, ' ').toUpperCase()}
                  </div>
                </div>
                <div className="ai-stat">
                  <div className="ai-stat-title">Confidence Score</div>
                  <div className={`ai-stat-value ${getConfidenceLevel(aiStatus.confidence_score)}`}>
                    {(aiStatus.confidence_score * 100).toFixed(1)}%
                  </div>
                  <div className="ai-confidence-label">
                    {getConfidenceLabel(aiStatus.confidence_score)}
                  </div>
                </div>
                <div className="ai-stat">
                  <div className="ai-stat-title">Auto Approved</div>
                  <div className={`ai-stat-value ${aiStatus.auto_approved ? 'approved' : 'pending'}`}>
                    {aiStatus.auto_approved ? 'YES' : 'NO'}
                  </div>
                </div>
                <div className="ai-stat">
                  <div className="ai-stat-title">Last Updated</div>
                  <div className="ai-stat-value">
                    {aiStatus.last_updated ? new Date(aiStatus.last_updated).toLocaleString() : 'N/A'}
                  </div>
                </div>
              </div>
            ) : (
              <div className="ai-alert info">
                <h4>No AI analysis data available</h4>
                <p>Click 'Run AI Analysis' to process this document through all AI algorithms.</p>
              </div>
            )}

            {/* Analysis Notes */}
            {aiStatus?.analysis_notes && (
              <div className="ai-alert info">
                <h4>📝 AI Analysis Notes</h4>
                <p>{aiStatus.analysis_notes}</p>
              </div>
            )}

            {/* Recommendations */}
            {aiStatus?.recommendations && aiStatus.recommendations.length > 0 && (
              <div className="ai-recommendations">
                <h4>🎯 AI Recommendations:</h4>
                <ul>
                  {aiStatus.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Algorithm Results */}
      {processingResults && (
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>📊 Algorithm Analysis Results</h3>
          </div>
          
          <div className="ai-card-content">
            <div className="ai-stats-grid">
              <div className="ai-stat">
                <div className="ai-stat-title">Overall Confidence</div>
                <div className={`ai-stat-value ${getConfidenceLevel(processingResults.overall_analysis.overall_confidence)}`}>
                  {(processingResults.overall_analysis.overall_confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="ai-stat">
                <div className="ai-stat-title">Algorithms Run</div>
                <div className="ai-stat-value">
                  {processingResults.overall_analysis.total_algorithms_run}
                </div>
              </div>
              <div className="ai-stat">
                <div className="ai-stat-title">Successful</div>
                <div className="ai-stat-value approved">
                  {processingResults.overall_analysis.successful_algorithms}
                </div>
              </div>
              <div className="ai-stat">
                <div className="ai-stat-title">Recommendation</div>
                <div className={`ai-stat-value ${
                  processingResults.overall_analysis.recommendation === 'approved' ? 'approved' : 
                  processingResults.overall_analysis.recommendation === 'manual_review' ? 'pending' : 'low-confidence'
                }`}>
                  {processingResults.overall_analysis.recommendation.toUpperCase()}
                </div>
              </div>
            </div>

            {/* Algorithm Results Table */}
            <div className="ai-algorithm-table">
              <h4>Algorithm Details</h4>
              <table>
                <thead>
                  <tr>
                    <th>Algorithm</th>
                    <th>Status</th>
                    <th>Confidence</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {getAlgorithmData().map((algo, index) => (
                    <tr key={index}>
                      <td>
                        <strong>🤖 {algo.name}</strong>
                      </td>
                      <td>
                        {algo.error ? (
                          <span className="ai-tag error">❌ ERROR</span>
                        ) : (
                          <span className="ai-tag success">✅ COMPLETED</span>
                        )}
                      </td>
                      <td>
                        {algo.error ? (
                          'N/A'
                        ) : (
                          <div className="ai-confidence-bar">
                            <div 
                              className={`ai-confidence-fill ${getConfidenceLevel(algo.confidence)}`}
                              data-confidence={Math.round(algo.confidence * 100)}
                            ></div>
                            <span className="ai-confidence-text">
                              {(algo.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                      </td>
                      <td>
                        <button 
                          className="ai-btn small"
                          onClick={() => {
                            const details = algo.error || JSON.stringify(algo.result, null, 2);
                            showNotification(`${algo.name} Details: ${details}`, 'info');
                          }}
                        >
                          👁️ View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Dashboard Statistics */}
      {showFullDashboard && dashboardStats && (
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>📊 AI System Performance Dashboard</h3>
            <button 
              className={`ai-btn ${loading ? 'loading' : ''}`}
              onClick={loadDashboardStats}
              disabled={loading}
            >
              🔄 Refresh
            </button>
          </div>
          
          <div className="ai-card-content">
            <div className="ai-stats-grid">
              <div className="ai-stat">
                <div className="ai-stat-title">Total Processed</div>
                <div className="ai-stat-value">
                  🤖 {dashboardStats.ai_statistics.total_processed}
                </div>
              </div>
              <div className="ai-stat">
                <div className="ai-stat-title">Auto Approval Rate</div>
                <div className="ai-stat-value approved">
                  {(dashboardStats.ai_statistics.auto_approval_rate * 100).toFixed(1)}%
                </div>
              </div>
              <div className="ai-stat">
                <div className="ai-stat-title">Average Confidence</div>
                <div className={`ai-stat-value ${getConfidenceLevel(dashboardStats.ai_statistics.average_confidence)}`}>
                  {(dashboardStats.ai_statistics.average_confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="ai-stat">
                <div className="ai-stat-title">Processing Efficiency</div>
                <div className="ai-stat-value primary">
                  {(dashboardStats.ai_statistics.processing_efficiency * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Confidence Distribution */}
            <div className="ai-section">
              <h4>📊 Confidence Distribution</h4>
              <div className="ai-distribution-grid">
                <div className="ai-distribution-item">
                  <div className="ai-distribution-title">High Confidence (85%+)</div>
                  <div className="ai-distribution-value high">
                    {dashboardStats.ai_statistics.confidence_distribution.high_confidence}
                  </div>
                </div>
                <div className="ai-distribution-item">
                  <div className="ai-distribution-title">Medium Confidence (65-84%)</div>
                  <div className="ai-distribution-value medium">
                    {dashboardStats.ai_statistics.confidence_distribution.medium_confidence}
                  </div>
                </div>
                <div className="ai-distribution-item">
                  <div className="ai-distribution-title">Low Confidence (&lt;65%)</div>
                  <div className="ai-distribution-value low">
                    {dashboardStats.ai_statistics.confidence_distribution.low_confidence}
                  </div>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="ai-section">
              <h4>⚙️ System Status</h4>
              <div className="ai-system-status">
                <div className="ai-status-item">
                  <span className={`ai-tag ${dashboardStats.system_status.ai_enabled ? 'success' : 'error'}`}>
                    {dashboardStats.system_status.ai_enabled ? '✅ AI Enabled' : '❌ AI Disabled'}
                  </span>
                </div>
                <div className="ai-status-item">
                  <span>🤖 Algorithms Available: <strong>{dashboardStats.system_status.algorithms_available}</strong></span>
                </div>
                <div className="ai-status-item">
                  <span>⏳ Processing Queue: <strong>{dashboardStats.system_status.processing_queue}</strong></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIVerificationDashboard;