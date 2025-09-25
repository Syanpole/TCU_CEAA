import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import { safeToFixed } from '../utils/numberUtils';
import './Analytics.css';

interface AnalyticsData {
  students: any[];
  documents: any[];
  grades: any[];
  applications: any[];
}

interface StudentProcessMetrics {
  totalStudents: number;
  activeStudents: number;
  documentsPerStudent: number;
  averageGPA: number;
  applicationSuccessRate: number;
}

interface DocumentMetrics {
  totalDocuments: number;
  approvedDocuments: number;
  rejectedDocuments: number;
  pendingDocuments: number;
  averageProcessingTime: number;
  documentTypes: Record<string, number>;
}

interface GradeMetrics {
  totalGradeSubmissions: number;
  averageGWA: number;
  averageSWA: number;
  qualifyingStudents: number;
  gradeDistribution: Record<string, number>;
  semesterBreakdown: Record<string, number>;
}

interface ApplicationMetrics {
  totalApplications: number;
  totalAmount: number;
  approvedApplications: number;
  approvedAmount: number;
  rejectedApplications: number;
  rejectedAmount: number;
  pendingApplications: number;
  pendingAmount: number;
  disbursedApplications: number;
  disbursedAmount: number;
  applicationTypes: Record<string, { count: number; amount: number }>;
  monthlyTrends: Record<string, { count: number; amount: number }>;
}

interface AnalyticsProps {
  onViewChange?: (view: string) => void;
}

const Analytics: React.FC<AnalyticsProps> = ({ onViewChange }) => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('all');
  const [selectedMetric, setSelectedMetric] = useState('overview');

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [studentsRes, documentsRes, gradesRes, applicationsRes] = await Promise.all([
          apiClient.get('/students/').catch(() => ({ data: [] })),
          apiClient.get('/documents/').catch(() => ({ data: [] })),
          apiClient.get('/grades/').catch(() => ({ data: [] })),
          apiClient.get('/applications/').catch(() => ({ data: [] }))
        ]);

        setAnalyticsData({
          students: studentsRes.data || [],
          documents: documentsRes.data || [],
          grades: gradesRes.data || [],
          applications: applicationsRes.data || []
        });
      } catch (err) {
        console.error('Error fetching analytics data:', err);
        setError('Failed to load analytics data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, []);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount).replace('$', '₱');
  };

  const formatPercentage = (value: number): string => {
    return `${Math.round(value * 100)}%`;
  };

  const getStudentMetrics = (): StudentProcessMetrics => {
    if (!analyticsData) return { 
      totalStudents: 0, 
      activeStudents: 0, 
      documentsPerStudent: 0, 
      averageGPA: 0, 
      applicationSuccessRate: 0 
    };

    const { students, documents, grades, applications } = analyticsData;
    
    // Students with any activity (documents, grades, or applications)
    const studentsWithActivity = new Set([
      ...documents.map(d => d.student_id || d.user_id || d.student?.id).filter(Boolean),
      ...grades.map(g => g.student_id || g.user_id || g.student?.id).filter(Boolean),
      ...applications.map(a => a.student_id || a.user_id || a.student?.id).filter(Boolean)
    ]);

    // Calculate average GPA from valid grades
    const validGrades = grades.filter(g => 
      g.general_weighted_average && 
      g.general_weighted_average > 0 && 
      g.general_weighted_average <= 100
    );
    const averageGPA = validGrades.length > 0 
      ? validGrades.reduce((sum, g) => sum + parseFloat(g.general_weighted_average), 0) / validGrades.length 
      : 0;

    // Calculate application success rate
    const completedApps = applications.filter(a => 
      a.status === 'approved' || 
      a.status === 'disbursed' || 
      a.status === 'rejected'
    );
    const successfulApps = applications.filter(a => 
      a.status === 'approved' || 
      a.status === 'disbursed'
    );
    const applicationSuccessRate = completedApps.length > 0 
      ? successfulApps.length / completedApps.length 
      : 0;

    return {
      totalStudents: students.length,
      activeStudents: studentsWithActivity.size,
      documentsPerStudent: students.length > 0 ? documents.length / students.length : 0,
      averageGPA,
      applicationSuccessRate
    };
  };

  const getDocumentMetrics = (): DocumentMetrics => {
    if (!analyticsData) return {
      totalDocuments: 0, approvedDocuments: 0, rejectedDocuments: 0, 
      pendingDocuments: 0, averageProcessingTime: 0, documentTypes: {}
    };

    const { documents } = analyticsData;
    
    const approved = documents.filter(d => d.status === 'approved').length;
    const rejected = documents.filter(d => d.status === 'rejected').length;
    const pending = documents.filter(d => d.status === 'pending').length;

    // Calculate average processing time for completed documents
    const completedDocs = documents.filter(d => d.status === 'approved' || d.status === 'rejected');
    const avgProcessingTime = completedDocs.length > 0 
      ? completedDocs.reduce((sum, doc) => {
          const submitted = new Date(doc.submitted_at);
          const updated = new Date(doc.updated_at || doc.submitted_at);
          return sum + (updated.getTime() - submitted.getTime()) / (1000 * 60 * 60 * 24);
        }, 0) / completedDocs.length
      : 0;

    // Document type breakdown
    const documentTypes: Record<string, number> = {};
    documents.forEach(doc => {
      const type = doc.document_type_display || doc.document_type || 'Unknown';
      documentTypes[type] = (documentTypes[type] || 0) + 1;
    });

    return {
      totalDocuments: documents.length,
      approvedDocuments: approved,
      rejectedDocuments: rejected,
      pendingDocuments: pending,
      averageProcessingTime: avgProcessingTime,
      documentTypes
    };
  };

  const getGradeMetrics = (): GradeMetrics => {
    if (!analyticsData) return {
      totalGradeSubmissions: 0, averageGWA: 0, averageSWA: 0, 
      qualifyingStudents: 0, gradeDistribution: {}, semesterBreakdown: {}
    };

    const { grades } = analyticsData;
    
    const validGrades = grades.filter(g => g.general_weighted_average && g.general_weighted_average > 0);
    const avgGWA = validGrades.length > 0 
      ? validGrades.reduce((sum, g) => sum + g.general_weighted_average, 0) / validGrades.length 
      : 0;

    const validSWA = grades.filter(g => g.semestral_weighted_average && g.semestral_weighted_average > 0);
    const avgSWA = validSWA.length > 0 
      ? validSWA.reduce((sum, g) => sum + g.semestral_weighted_average, 0) / validSWA.length 
      : 0;

    const qualifyingStudents = grades.filter(g => 
      g.qualifies_for_basic_allowance || g.qualifies_for_merit_incentive
    ).length;

    // Grade distribution
    const gradeDistribution: Record<string, number> = {
      'Excellent (90-100)': 0,
      'Very Good (85-89)': 0,
      'Good (80-84)': 0,
      'Fair (75-79)': 0,
      'Below 75': 0
    };

    validGrades.forEach(grade => {
      const gwa = grade.general_weighted_average;
      if (gwa >= 90) gradeDistribution['Excellent (90-100)']++;
      else if (gwa >= 85) gradeDistribution['Very Good (85-89)']++;
      else if (gwa >= 80) gradeDistribution['Good (80-84)']++;
      else if (gwa >= 75) gradeDistribution['Fair (75-79)']++;
      else gradeDistribution['Below 75']++;
    });

    // Semester breakdown
    const semesterBreakdown: Record<string, number> = {};
    grades.forEach(grade => {
      const semester = `${grade.academic_year} ${grade.semester_display}`;
      semesterBreakdown[semester] = (semesterBreakdown[semester] || 0) + 1;
    });

    return {
      totalGradeSubmissions: grades.length,
      averageGWA: avgGWA,
      averageSWA: avgSWA,
      qualifyingStudents,
      gradeDistribution,
      semesterBreakdown
    };
  };

  const getApplicationMetrics = (): ApplicationMetrics => {
    if (!analyticsData) return {
      totalApplications: 0, totalAmount: 0, approvedApplications: 0, approvedAmount: 0,
      rejectedApplications: 0, rejectedAmount: 0, pendingApplications: 0, pendingAmount: 0,
      disbursedApplications: 0, disbursedAmount: 0, applicationTypes: {}, monthlyTrends: {}
    };

    const { applications } = analyticsData;
    
    // Filter applications by status
    const approved = applications.filter(a => a.status === 'approved');
    const rejected = applications.filter(a => a.status === 'rejected');
    const pending = applications.filter(a => a.status === 'pending');
    const disbursed = applications.filter(a => a.status === 'disbursed');

    // Calculate amounts with proper number handling
    const parseAmount = (amount: any): number => {
      const num = parseFloat(amount);
      return isNaN(num) ? 0 : num;
    };

    const totalAmount = applications.reduce((sum, a) => sum + parseAmount(a.amount), 0);
    const approvedAmount = approved.reduce((sum, a) => sum + parseAmount(a.amount), 0);
    const rejectedAmount = rejected.reduce((sum, a) => sum + parseAmount(a.amount), 0);
    const pendingAmount = pending.reduce((sum, a) => sum + parseAmount(a.amount), 0);
    const disbursedAmount = disbursed.reduce((sum, a) => sum + parseAmount(a.amount), 0);

    // Application type breakdown with fallback
    const applicationTypes: Record<string, { count: number; amount: number }> = {};
    applications.forEach(app => {
      let type = app.application_type_display || app.application_type || 'Other';
      
      // Standardize type names
      if (type.toLowerCase().includes('basic')) type = 'Basic Educational Assistance';
      else if (type.toLowerCase().includes('merit')) type = 'Merit Incentive';
      else if (type.toLowerCase().includes('both')) type = 'Both Allowances';
      else if (type === 'basic') type = 'Basic Educational Assistance';
      else if (type === 'merit') type = 'Merit Incentive';
      else if (type === 'both') type = 'Both Allowances';
      
      if (!applicationTypes[type]) {
        applicationTypes[type] = { count: 0, amount: 0 };
      }
      applicationTypes[type].count++;
      applicationTypes[type].amount += parseAmount(app.amount);
    });

    // Add default types if no data exists
    if (Object.keys(applicationTypes).length === 0) {
      applicationTypes['Basic Educational Assistance'] = { count: 0, amount: 0 };
      applicationTypes['Merit Incentive'] = { count: 0, amount: 0 };
      applicationTypes['Both Allowances'] = { count: 0, amount: 0 };
    }

    // Monthly trends with better date handling
    const monthlyTrends: Record<string, { count: number; amount: number }> = {};
    applications.forEach(app => {
      try {
        const dateStr = app.applied_at || app.created_at || app.submitted_at;
        if (dateStr) {
          const date = new Date(dateStr);
          if (!isNaN(date.getTime())) {
            const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            if (!monthlyTrends[monthYear]) {
              monthlyTrends[monthYear] = { count: 0, amount: 0 };
            }
            monthlyTrends[monthYear].count++;
            monthlyTrends[monthYear].amount += parseAmount(app.amount);
          }
        }
      } catch (error) {
        console.warn('Error parsing application date:', error);
      }
    });

    return {
      totalApplications: applications.length,
      totalAmount,
      approvedApplications: approved.length,
      approvedAmount,
      rejectedApplications: rejected.length,
      rejectedAmount,
      pendingApplications: pending.length,
      pendingAmount,
      disbursedApplications: disbursed.length,
      disbursedAmount,
      applicationTypes,
      monthlyTrends
    };
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2 className="loading-title">Loading Analytics</h2>
          <p className="loading-text">Analyzing data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-content">
          <div className="error-icon">⚠</div>
          <h2 className="error-title">Error Loading Analytics</h2>
          <p className="error-message">{error}</p>
          <button className="retry-btn" onClick={() => window.location.reload()}>
            RETRY
          </button>
        </div>
      </div>
    );
  }

  const studentMetrics = getStudentMetrics();
  const documentMetrics = getDocumentMetrics();
  const gradeMetrics = getGradeMetrics();
  const applicationMetrics = getApplicationMetrics();

  return (
    <div className="analytics-container">
      <div className="analytics-content">
        {/* Header */}
        <div className="analytics-header">
          <div className="header-content">
            <h1>Analytics Dashboard</h1>
            <p>Comprehensive analysis of TCU-CEAA system performance and student progress</p>
          </div>
          
          <div className="header-controls">
            <select 
              value={selectedTimeframe} 
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="timeframe-select"
            >
              <option value="all">All Time</option>
              <option value="year">This Year</option>
              <option value="semester">This Semester</option>
              <option value="month">This Month</option>
            </select>
            
            <button className="export-btn">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 16l-6-6h4V4h4v6h4l-6 6zm6 4H6v2h12v-2z"/>
              </svg>
              Export Report
            </button>
          </div>
        </div>

        {/* Key Metrics Overview */}
        <div className="metrics-overview">
          <div className="metric-card primary">
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">{studentMetrics.totalStudents}</div>
              <div className="metric-label">Total Students</div>
              <div className="metric-sublabel">{studentMetrics.activeStudents} active</div>
            </div>
          </div>

          <div className="metric-card success">
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">{formatPercentage(documentMetrics.totalDocuments > 0 ? documentMetrics.approvedDocuments / documentMetrics.totalDocuments : 0)}</div>
              <div className="metric-label">Document Approval Rate</div>
              <div className="metric-sublabel">{documentMetrics.approvedDocuments} of {documentMetrics.totalDocuments}</div>
            </div>
          </div>

          <div className="metric-card info">
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">{safeToFixed(gradeMetrics.averageGWA, 2)}</div>
              <div className="metric-label">Average GWA</div>
              <div className="metric-sublabel">{gradeMetrics.qualifyingStudents} qualifying students</div>
            </div>
          </div>

          <div className="metric-card warning">
            <div className="metric-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">{formatCurrency(applicationMetrics.totalAmount)}</div>
              <div className="metric-label">Total Application Value</div>
              <div className="metric-sublabel">{applicationMetrics.totalApplications} applications</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="analytics-nav">
          <button 
            className={`nav-btn ${selectedMetric === 'overview' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('overview')}
          >
            Overview
          </button>
          <button 
            className={`nav-btn ${selectedMetric === 'students' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('students')}
          >
            Students
          </button>
          <button 
            className={`nav-btn ${selectedMetric === 'documents' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('documents')}
          >
            Documents
          </button>
          <button 
            className={`nav-btn ${selectedMetric === 'grades' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('grades')}
          >
            Grades
          </button>
          <button 
            className={`nav-btn ${selectedMetric === 'applications' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('applications')}
          >
            Applications
          </button>
        </div>

        {/* Content based on selected metric */}
        {selectedMetric === 'overview' && (
          <div className="analytics-grid">
            {/* System Performance */}
            <div className="analytics-panel">
              <h3>System Performance</h3>
              {analyticsData && (
                analyticsData.students.length > 0 || 
                analyticsData.documents.length > 0 || 
                analyticsData.grades.length > 0 || 
                analyticsData.applications.length > 0
              ) ? (
                <div className="performance-grid">
                  <div className="performance-item">
                    <div className="performance-label">Active Students</div>
                    <div className="performance-value">
                      {studentMetrics.activeStudents} / {studentMetrics.totalStudents}
                    </div>
                    <div className="performance-bar">
                      <div 
                        className="performance-fill" 
                        style={{ 
                          width: `${studentMetrics.totalStudents > 0 ? (studentMetrics.activeStudents / studentMetrics.totalStudents) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>

                  <div className="performance-item">
                    <div className="performance-label">Document Processing</div>
                    <div className="performance-value">
                      {safeToFixed(documentMetrics.averageProcessingTime, 1)} days avg
                    </div>
                    <div className="performance-bar">
                      <div 
                        className="performance-fill" 
                        style={{ 
                          width: `${Math.min((10 - documentMetrics.averageProcessingTime) / 10 * 100, 100)}%` 
                        }}
                      ></div>
                    </div>
                  </div>

                  <div className="performance-item">
                    <div className="performance-label">Application Success Rate</div>
                    <div className="performance-value">
                      {formatPercentage(applicationMetrics.totalApplications > 0 ? applicationMetrics.approvedApplications / applicationMetrics.totalApplications : 0)}
                    </div>
                    <div className="performance-bar">
                      <div 
                        className="performance-fill" 
                        style={{ 
                          width: `${applicationMetrics.totalApplications > 0 ? (applicationMetrics.approvedApplications / applicationMetrics.totalApplications) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>

                  <div className="performance-item">
                    <div className="performance-label">Total Application Value</div>
                    <div className="performance-value">
                      {formatCurrency(applicationMetrics.totalAmount)}
                    </div>
                    <div className="performance-bar">
                      <div 
                        className="performance-fill" 
                        style={{ 
                          width: `${applicationMetrics.totalAmount > 0 ? Math.min((applicationMetrics.totalAmount / 1000000) * 100, 100) : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="no-data-state">
                  <div className="no-data-icon">📊</div>
                  <h4>No System Data Available</h4>
                  <p>Performance metrics will appear here once students begin using the system.</p>
                </div>
              )}
            </div>

            {/* Recent Activity */}
            <div className="analytics-panel">
              <h3>Recent Activity Summary</h3>
              <div className="activity-list">
                <div className="activity-item">
                  <div className="activity-icon documents">📄</div>
                  <div className="activity-content">
                    <div className="activity-title">Document Submissions</div>
                    <div className="activity-value">
                      {documentMetrics.pendingDocuments} pending review
                      {documentMetrics.totalDocuments === 0 && " (No submissions yet)"}
                    </div>
                  </div>
                </div>

                <div className="activity-item">
                  <div className="activity-icon grades">📊</div>
                  <div className="activity-content">
                    <div className="activity-title">Grade Submissions</div>
                    <div className="activity-value">
                      {gradeMetrics.totalGradeSubmissions} total submissions
                      {gradeMetrics.totalGradeSubmissions === 0 && " (No grades submitted)"}
                    </div>
                  </div>
                </div>

                <div className="activity-item">
                  <div className="activity-icon applications">💰</div>
                  <div className="activity-content">
                    <div className="activity-title">Financial Applications</div>
                    <div className="activity-value">
                      {formatCurrency(applicationMetrics.pendingAmount)} pending
                      {applicationMetrics.totalApplications === 0 && " (No applications yet)"}
                    </div>
                  </div>
                </div>

                <div className="activity-item">
                  <div className="activity-icon total">💎</div>
                  <div className="activity-content">
                    <div className="activity-title">Total Application Value</div>
                    <div className="activity-value">
                      {formatCurrency(applicationMetrics.totalAmount)} 
                      {applicationMetrics.totalApplications === 0 ? " (System ready for applications)" : ` across ${applicationMetrics.totalApplications} applications`}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedMetric === 'students' && (
          <div className="analytics-grid">
            <div className="analytics-panel full-width">
              <h3>Student Analytics</h3>
              <div className="student-stats-grid">
                <div className="stat-box">
                  <div className="stat-number">{studentMetrics.totalStudents}</div>
                  <div className="stat-label">Total Registered</div>
                </div>
                <div className="stat-box">
                  <div className="stat-number">{studentMetrics.activeStudents}</div>
                  <div className="stat-label">Active Students</div>
                </div>
                <div className="stat-box">
                  <div className="stat-number">{safeToFixed(studentMetrics.documentsPerStudent, 1)}</div>
                  <div className="stat-label">Docs per Student</div>
                </div>
                <div className="stat-box">
                  <div className="stat-number">{safeToFixed(studentMetrics.averageGPA, 2)}</div>
                  <div className="stat-label">Average GPA</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedMetric === 'documents' && (
          <div className="analytics-grid">
            <div className="analytics-panel">
              <h3>Document Processing Status</h3>
              <div className="status-breakdown">
                <div className="status-item approved">
                  <div className="status-count">{documentMetrics.approvedDocuments}</div>
                  <div className="status-label">Approved</div>
                </div>
                <div className="status-item pending">
                  <div className="status-count">{documentMetrics.pendingDocuments}</div>
                  <div className="status-label">Pending</div>
                </div>
                <div className="status-item rejected">
                  <div className="status-count">{documentMetrics.rejectedDocuments}</div>
                  <div className="status-label">Rejected</div>
                </div>
              </div>
            </div>

            <div className="analytics-panel">
              <h3>Document Types</h3>
              <div className="document-types">
                {Object.entries(documentMetrics.documentTypes).map(([type, count]) => (
                  <div key={type} className="type-item">
                    <div className="type-label">{type}</div>
                    <div className="type-count">{count}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedMetric === 'grades' && (
          <div className="analytics-grid">
            <div className="analytics-panel">
              <h3>Grade Distribution</h3>
              <div className="grade-distribution">
                {Object.entries(gradeMetrics.gradeDistribution).map(([range, count]) => (
                  <div key={range} className="grade-item">
                    <div className="grade-range">{range}</div>
                    <div className="grade-bar">
                      <div 
                        className="grade-fill" 
                        style={{ 
                          width: `${gradeMetrics.totalGradeSubmissions > 0 ? (count / gradeMetrics.totalGradeSubmissions) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                    <div className="grade-count">{count}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="analytics-panel">
              <h3>Academic Performance</h3>
              <div className="performance-stats">
                <div className="perf-stat">
                  <div className="perf-value">{safeToFixed(gradeMetrics.averageGWA, 2)}</div>
                  <div className="perf-label">Average GWA</div>
                </div>
                <div className="perf-stat">
                  <div className="perf-value">{safeToFixed(gradeMetrics.averageSWA, 2)}</div>
                  <div className="perf-label">Average SWA</div>
                </div>
                <div className="perf-stat">
                  <div className="perf-value">{gradeMetrics.qualifyingStudents}</div>
                  <div className="perf-label">Qualifying Students</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedMetric === 'applications' && (
          <div className="analytics-grid">
            <div className="analytics-panel">
              <h3>Financial Overview</h3>
              <div className="financial-grid">
                <div className="financial-item total">
                  <div className="financial-amount">{formatCurrency(applicationMetrics.totalAmount)}</div>
                  <div className="financial-label">Total Applied</div>
                  <div className="financial-count">{applicationMetrics.totalApplications} applications</div>
                  <div className="financial-note">
                    {applicationMetrics.totalApplications === 0 ? "No applications submitted yet" : "All-time total value"}
                  </div>
                </div>
                <div className="financial-item approved">
                  <div className="financial-amount">{formatCurrency(applicationMetrics.approvedAmount)}</div>
                  <div className="financial-label">Approved</div>
                  <div className="financial-count">{applicationMetrics.approvedApplications} applications</div>
                  <div className="financial-note">
                    {applicationMetrics.totalApplications > 0 
                      ? `${Math.round((applicationMetrics.approvedApplications / applicationMetrics.totalApplications) * 100)}% approval rate`
                      : "Ready for approvals"
                    }
                  </div>
                </div>
                <div className="financial-item disbursed">
                  <div className="financial-amount">{formatCurrency(applicationMetrics.disbursedAmount)}</div>
                  <div className="financial-label">Disbursed</div>
                  <div className="financial-count">{applicationMetrics.disbursedApplications} applications</div>
                  <div className="financial-note">
                    {applicationMetrics.disbursedApplications === 0 ? "No disbursements yet" : "Funds distributed"}
                  </div>
                </div>
                <div className="financial-item pending">
                  <div className="financial-amount">{formatCurrency(applicationMetrics.pendingAmount)}</div>
                  <div className="financial-label">Pending</div>
                  <div className="financial-count">{applicationMetrics.pendingApplications} applications</div>
                  <div className="financial-note">
                    {applicationMetrics.pendingApplications === 0 ? "No pending reviews" : "Awaiting decision"}
                  </div>
                </div>
                <div className="financial-item rejected">
                  <div className="financial-amount">{formatCurrency(applicationMetrics.rejectedAmount)}</div>
                  <div className="financial-label">Rejected</div>
                  <div className="financial-count">{applicationMetrics.rejectedApplications} applications</div>
                  <div className="financial-note">
                    {applicationMetrics.rejectedApplications === 0 ? "No rejections" : "Not approved"}
                  </div>
                </div>
                <div className="financial-item efficiency">
                  <div className="financial-amount">
                    {applicationMetrics.totalApplications > 0 
                      ? `${Math.round(((applicationMetrics.approvedApplications + applicationMetrics.disbursedApplications) / applicationMetrics.totalApplications) * 100)}%`
                      : '0%'
                    }
                  </div>
                  <div className="financial-label">Success Rate</div>
                  <div className="financial-count">
                    {applicationMetrics.approvedApplications + applicationMetrics.disbursedApplications} successful
                  </div>
                  <div className="financial-note">
                    {applicationMetrics.totalApplications === 0 ? "No data available" : "Approved + Disbursed"}
                  </div>
                </div>
              </div>
            </div>

            <div className="analytics-panel">
              <h3>Application Types</h3>
              {Object.keys(applicationMetrics.applicationTypes).length > 0 ? (
                <div className="application-types">
                  {Object.entries(applicationMetrics.applicationTypes).map(([type, data]) => (
                    <div key={type} className="app-type-item">
                      <div className="app-type-header">
                        <div className="app-type-name">{type}</div>
                        <div className="app-type-count">{data.count}</div>
                      </div>
                      <div className="app-type-amount">{formatCurrency(data.amount)}</div>
                      <div className="app-type-note">
                        {data.count === 0 ? "No applications yet" : `Average: ${formatCurrency(data.amount / data.count)}`}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-data-state">
                  <div className="no-data-icon">📋</div>
                  <h4>No Application Types Data</h4>
                  <p>Application breakdowns will appear here once students submit applications.</p>
                  <div className="placeholder-types">
                    <div className="placeholder-type">Basic Educational Assistance - ₱0.00</div>
                    <div className="placeholder-type">Merit Incentive - ₱0.00</div>
                    <div className="placeholder-type">Both Allowances - ₱0.00</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;