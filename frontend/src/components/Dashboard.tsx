import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import { useAuth } from '../contexts/AuthContext';
import './Dashboard.css';

interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
}

interface Student {
  id: number;
  student_id: string;
  first_name: string;
  last_name: string;
  email: string;
  enrollment_date: string;
}

const Dashboard: React.FC = () => {
  const { isAdmin, user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAdmin) {
      return; // Don't fetch data if not admin
    }
    
    const fetchData = async () => {
      try {
        setLoading(true);
        const [tasksResponse, studentsResponse] = await Promise.all([
          apiClient.get<Task[]>('/tasks/'),
          apiClient.get<Student[]>('/students/')
        ]);
        setTasks(tasksResponse.data);
        setStudents(studentsResponse.data);
        setError('');
      } catch (error: any) {
        console.error('Error fetching data:', error);
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAdmin]);

  // Redirect non-admin users
  if (!isAdmin) {
    return (
      <div className="dashboard-container">
        <div className="error-container">
          <div className="error-message">
            <h3>🔒 Access Denied</h3>
            <p>This dashboard is only available for administrators.</p>
            <p>Students should use the student portal instead.</p>
          </div>
        </div>
      </div>
    );
  }

  const handleTaskToggle = async (taskId: number) => {
    if (!isAdmin) return; // Only admins can modify tasks
    
    try {
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;

      const updatedTask = await apiClient.patch<Task>(`/tasks/${taskId}/`, {
        completed: !task.completed
      });

      setTasks(prev => prev.map(t => 
        t.id === taskId ? updatedTask.data : t
      ));
    } catch (error) {
      console.error('Error updating task:', error);
      setError('Failed to update task');
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
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

  return (
    <div className="dashboard-container">
      <div className="dashboard-content">
        <div className="dashboard-header">
          <h2>Welcome to your dashboard!</h2>
          <p>Here's an overview of your tasks and student information.</p>
          {isAdmin && (
            <div className="admin-notice">
              🔑 You have administrator privileges
            </div>
          )}
        </div>
        
        <div className="dashboard-grid">
          {/* Tasks Section */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>Tasks</h3>
              <span className="item-count">{tasks.length} items</span>
            </div>
            
            {tasks.length === 0 ? (
              <div className="no-items">
                <p>No tasks found.</p>
                {isAdmin && <p>Create some tasks to get started!</p>}
              </div>
            ) : (
              <div className="items-grid">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className={`task-card ${task.completed ? 'completed' : 'pending'}`}
                    onClick={() => handleTaskToggle(task.id)}
                    style={{ cursor: isAdmin ? 'pointer' : 'default' }}
                  >
                    <div className="task-header">
                      <h4>{task.title}</h4>
                      <span className={`status-badge ${task.completed ? 'completed' : 'pending'}`}>
                        {task.completed ? '✓ Done' : '⏳ Pending'}
                      </span>
                    </div>
                    <p className="task-description">{task.description}</p>
                    <div className="task-footer">
                      <span className="task-date">
                        Created: {new Date(task.created_at).toLocaleDateString()}
                      </span>
                      {isAdmin && (
                        <span className="admin-hint">Click to toggle</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Students Section */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>Students</h3>
              <span className="item-count">{students.length} enrolled</span>
            </div>
            
            {students.length === 0 ? (
              <div className="no-items">
                <p>No students found.</p>
                {isAdmin && <p>Add students to see them here!</p>}
              </div>
            ) : (
              <div className="items-grid">
                {students.map((student) => (
                  <div key={student.id} className="student-card">
                    <div className="student-header">
                      <h4>{student.first_name} {student.last_name}</h4>
                      <span className="student-id">#{student.student_id}</span>
                    </div>
                    <div className="student-details">
                      <p className="student-email">📧 {student.email}</p>
                      <p className="student-date">
                        Enrolled: {new Date(student.enrollment_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Statistics */}
        <div className="stats-section">
          <div className="stat-card">
            <div className="stat-number">{tasks.length}</div>
            <div className="stat-label">Total Tasks</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{tasks.filter(t => t.completed).length}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{students.length}</div>
            <div className="stat-label">Students</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{isAdmin ? 'Admin' : 'User'}</div>
            <div className="stat-label">Your Role</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
