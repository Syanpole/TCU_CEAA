import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './StudentDashboard.css';

interface Assignment {
  id: number;
  title: string;
  description: string;
  due_date: string;
  submitted: boolean;
}

const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStudentData = async () => {
      try {
        setLoading(true);
        
        // Simple mock assignment for demo
        setAssignments([
          {
            id: 1,
            title: 'Welcome to TCU CEAA',
            description: 'Complete your student profile setup and explore the platform',
            due_date: '2025-08-25',
            submitted: false
          }
        ]);
        
        setError('');
      } catch (error: any) {
        console.error('Error fetching student data:', error);
        setError('Failed to load your information. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudentData();
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getDaysUntilDue = (dueDate: string) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="student-dashboard-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading your dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-dashboard-container">
        <div className="error-container">
          <div className="error-message">
            <h3>⚠️ Error</h3>
            <p>{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="retry-button"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const pendingAssignments = assignments.filter(a => !a.submitted);
  const completedAssignments = assignments.filter(a => a.submitted);

  return (
    <div className="student-dashboard-container">
      <div className="student-dashboard-content">
        {/* Welcome Section */}
        <div className="welcome-section">
          <div className="welcome-header">
            <div className="student-avatar">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <div className="welcome-text">
              <h2>{getGreeting()}, {user?.first_name}!</h2>
              <p>Welcome to your TCU CEAA student portal</p>
              <div className="student-info">
                <span className="student-id">Student ID: {user?.student_id || 'Not assigned'}</span>
                <span className="student-email">📧 {user?.email}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="stats-grid">
          <div className="stat-card pending">
            <div className="stat-icon">📋</div>
            <div className="stat-content">
              <div className="stat-number">{pendingAssignments.length}</div>
              <div className="stat-label">Pending Tasks</div>
            </div>
          </div>
          <div className="stat-card completed">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-number">{completedAssignments.length}</div>
              <div className="stat-label">Completed</div>
            </div>
          </div>
          <div className="stat-card total">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-number">{assignments.length}</div>
              <div className="stat-label">Total Assignments</div>
            </div>
          </div>
          <div className="stat-card progress">
            <div className="stat-icon">🎯</div>
            <div className="stat-content">
              <div className="stat-number">
                {assignments.length > 0 ? Math.round((completedAssignments.length / assignments.length) * 100) : 0}%
              </div>
              <div className="stat-label">Progress</div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="content-grid">
          {/* Pending Assignments */}
          <div className="content-card">
            <div className="card-header">
              <h3>📝 Pending Assignments</h3>
              <span className="count-badge">{pendingAssignments.length}</span>
            </div>
            <div className="card-content">
              {pendingAssignments.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">🎉</div>
                  <p>Great job! No pending assignments.</p>
                </div>
              ) : (
                <div className="assignments-list">
                  {pendingAssignments.map((assignment) => {
                    const daysUntil = getDaysUntilDue(assignment.due_date);
                    return (
                      <div key={assignment.id} className={`assignment-item ${daysUntil <= 3 ? 'urgent' : ''}`}>
                        <div className="assignment-header">
                          <h4>{assignment.title}</h4>
                          <span className={`due-badge ${daysUntil <= 3 ? 'urgent' : ''}`}>
                            {daysUntil === 0 ? 'Due Today' : 
                             daysUntil === 1 ? 'Due Tomorrow' :
                             daysUntil < 0 ? 'Overdue' :
                             `${daysUntil} days left`}
                          </span>
                        </div>
                        <p className="assignment-description">{assignment.description}</p>
                        <div className="assignment-footer">
                          <span className="due-date">Due: {new Date(assignment.due_date).toLocaleDateString()}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="content-card">
            <div className="card-header">
              <h3>📈 Recent Activity</h3>
            </div>
            <div className="card-content">
              <div className="activity-list">
                <div className="activity-item">
                  <div className="activity-icon completed">✅</div>
                  <div className="activity-content">
                    <p>Completed English Essay</p>
                    <span className="activity-time">2 hours ago</span>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon new">📋</div>
                  <div className="activity-content">
                    <p>New assignment: Math Assignment 1</p>
                    <span className="activity-time">1 day ago</span>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon login">🔐</div>
                  <div className="activity-content">
                    <p>Logged in to TCU CEAA</p>
                    <span className="activity-time">Today</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Upcoming Deadlines */}
        <div className="deadlines-section">
          <div className="content-card">
            <div className="card-header">
              <h3>⏰ Upcoming Deadlines</h3>
            </div>
            <div className="card-content">
              <div className="deadlines-calendar">
                {pendingAssignments
                  .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
                  .slice(0, 5)
                  .map((assignment) => (
                    <div key={assignment.id} className="deadline-item">
                      <div className="deadline-date">
                        <div className="date-day">{new Date(assignment.due_date).getDate()}</div>
                        <div className="date-month">
                          {new Date(assignment.due_date).toLocaleDateString('en-US', { month: 'short' })}
                        </div>
                      </div>
                      <div className="deadline-content">
                        <h4>{assignment.title}</h4>
                        <p>{assignment.description}</p>
                      </div>
                    </div>
                  ))}
                {pendingAssignments.length === 0 && (
                  <div className="empty-state">
                    <p>No upcoming deadlines 📅</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
