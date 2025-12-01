import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/authService';
import ScholarshipApplicationForm from '../scholarship/ScholarshipApplicationForm';
import './StudentsManagement.css';

interface Student {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  student_id: string;
  username: string;
  role: string;
  created_at: string;
  profile_image_url?: string;
}

interface ProfileImageProps {
  src?: string;
  alt: string;
  initials: string;
  className?: string;
  size?: 'small' | 'large';
}

// Profile Image Component with loading states
const ProfileImage: React.FC<ProfileImageProps> = ({ src, alt, initials, className = '', size = 'small' }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(false);
  }, [src]);

  const handleLoad = () => {
    setLoading(false);
    setError(false);
  };

  const handleError = () => {
    setLoading(false);
    setError(true);
  };

  return (
    <div className={`${size === 'large' ? 'profile-image-large' : 'student-avatar'} ${className}`}>
      {src && !error ? (
        <>
          {loading && (
            <div className="image-loading">
              <div className="loading-spinner-small"></div>
            </div>
          )}
          <img 
            src={src} 
            alt={alt}
            className={`${size === 'large' ? 'profile-img' : 'avatar-image'} ${loading ? 'image-hidden' : 'image-visible'}`}
            onLoad={handleLoad}
            onError={handleError}
          />
        </>
      ) : (
        <div className={size === 'large' ? 'profile-placeholder' : 'avatar-initials'}>
          {initials}
        </div>
      )}
    </div>
  );
};

interface StudentModalProps {
  student: Student | null;
  isOpen: boolean;
  mode: 'view' | 'edit';
  onClose: () => void;
  onSave?: (student: Student) => void;
  onDelete?: (studentId: number) => void;
}

// Modal Component
const StudentModal: React.FC<StudentModalProps> = ({ student, isOpen, mode, onClose, onSave, onDelete }) => {
  const [editedStudent, setEditedStudent] = useState<Student | null>(null);
  const [loading, setLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  useEffect(() => {
    if (student) {
      setEditedStudent({ ...student });
    }
  }, [student]);

  const handleSave = async () => {
    if (!editedStudent || !onSave) return;

    try {
      setLoading(true);
      const response = await apiClient.put<Student>(`/users/${editedStudent.id}/`, {
        first_name: editedStudent.first_name,
        last_name: editedStudent.last_name,
        email: editedStudent.email,
        student_id: editedStudent.student_id,
        username: editedStudent.username
      });
      onSave(response.data);
      onClose();
    } catch (error) {
      console.error('Error updating student:', error);
      alert('Failed to update student. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!student || !onDelete) return;

    try {
      setLoading(true);
      const response = await apiClient.delete(`/users/${student.id}/`);
      
      // Call onDelete to update the parent list
      onDelete(student.id);
      
      // Close delete confirm
      setShowDeleteConfirm(false);
      
      // Show success modal
      setShowSuccessModal(true);
      
      // Auto-close success modal after 2 seconds
      setTimeout(() => {
        setShowSuccessModal(false);
        onClose();
      }, 2000);
    } catch (error: any) {
      console.error('Error deleting student:', error);
      const errorMessage = error.response?.data?.error || error.response?.data?.message || 'Failed to delete student. Please try again.';
      alert(errorMessage);
      setShowDeleteConfirm(false);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !student || !editedStudent) return null;

  return (
    <div className="modal-overlay">
      <div className={`modal-content ${mode === 'view' ? 'modal-content-compact modal-content-dark' : ''}`}>
        <div className="modal-header">
          <h3 className={mode === 'view' ? 'modal-title-view' : 'modal-title-edit'}>{mode === 'view' ? 'View Profile' : 'Edit Profile'}</h3>
          <button className={`modal-close ${mode === 'view' ? 'modal-close-view' : ''}`} onClick={onClose} title="Close modal">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 6l12 12m0-12L6 18" />
            </svg>
          </button>
        </div>

        <div className="modal-body">
          <div className="profile-section">
            <ProfileImage
              src={student.profile_image_url}
              alt={`${student.first_name} ${student.last_name}`}
              initials={`${student.first_name[0]}${student.last_name[0]}`}
              size={mode === 'view' ? 'small' : 'large'}
            />
          </div>

          <div className={`form-grid ${mode === 'view' ? 'form-grid-compact' : ''}`}>
            {mode === 'view' ? (
              <>
                <div className="name-row">
                  <div className="form-group">
                    <label>First Name</label>
                    <div className="form-display">{student.first_name}</div>
                  </div>
                  <div className="form-group">
                    <label>Last Name</label>
                    <div className="form-display">{student.last_name}</div>
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Email Address</label>
                  <div className="form-display">{student.email}</div>
                </div>

                <div className="form-group">
                  <label>Student ID</label>
                  <div className="form-display">{student.student_id}</div>
                </div>

                <div className="form-group">
                  <label>Username</label>
                  <div className="form-display">{student.username}</div>
                </div>

                <div className="form-group">
                  <label>Role</label>
                  <div className="form-display">{student.role}</div>
                </div>

                <div className="form-group">
                  <label>Member Since</label>
                  <div className="form-display">
                    {new Date(student.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="form-group">
                  <label htmlFor="edit-first-name">First Name</label>
                  <input
                    id="edit-first-name"
                    type="text"
                    value={editedStudent.first_name}
                    onChange={(e) => setEditedStudent({...editedStudent, first_name: e.target.value})}
                    className="form-input"
                    placeholder="Enter first name"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="edit-last-name">Last Name</label>
                  <input
                    id="edit-last-name"
                    type="text"
                    value={editedStudent.last_name}
                    onChange={(e) => setEditedStudent({...editedStudent, last_name: e.target.value})}
                    className="form-input"
                    placeholder="Enter last name"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="edit-email">Email</label>
                  <input
                    id="edit-email"
                    type="email"
                    value={editedStudent.email}
                    onChange={(e) => setEditedStudent({...editedStudent, email: e.target.value})}
                    className="form-input"
                    placeholder="Enter email address"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="edit-student-id">Student ID</label>
                  <input
                    id="edit-student-id"
                    type="text"
                    value={editedStudent.student_id}
                    onChange={(e) => setEditedStudent({...editedStudent, student_id: e.target.value})}
                    className="form-input"
                    placeholder="Enter student ID"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="edit-username">Username</label>
                  <input
                    id="edit-username"
                    type="text"
                    value={editedStudent.username}
                    onChange={(e) => setEditedStudent({...editedStudent, username: e.target.value})}
                    className="form-input"
                    placeholder="Enter username"
                  />
                </div>

                <div className="form-group">
                  <label>Role</label>
                  <div className="form-display">{student.role}</div>
                </div>

                <div className="form-group">
                  <label>Joined Date</label>
                  <div className="form-display">
                    {new Date(student.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="modal-footer">
          {mode === 'edit' ? (
            <>
              <button 
                className="btn-danger" 
                onClick={() => setShowDeleteConfirm(true)}
                disabled={loading}
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Student
              </button>
              <div className="modal-actions">
                <button className="btn-secondary" onClick={onClose} disabled={loading}>
                  Cancel
                </button>
                <button className="btn-primary" onClick={handleSave} disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </>
          ) : (
            <button className="btn-secondary" onClick={onClose}>
              Close
            </button>
          )}
        </div>

        {/* Delete Confirmation Dialog */}
        {showDeleteConfirm && (
          <div className="delete-confirm-overlay">
            <div className="delete-confirm-modal">
              <div className="delete-confirm-header">
                <h4>Confirm Deletion</h4>
              </div>
              <div className="delete-confirm-body">
                <p>Are you sure you want to delete <strong>{student.first_name} {student.last_name}</strong>?</p>
                <p className="delete-warning">This action cannot be undone and will remove all associated data.</p>
              </div>
              <div className="delete-confirm-footer">
                <button 
                  className="btn-secondary" 
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button 
                  className="btn-danger" 
                  onClick={handleDelete}
                  disabled={loading}
                >
                  {loading ? 'Deleting...' : 'Delete Student'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Success Modal */}
        {showSuccessModal && (
          <div className="delete-confirm-overlay success-overlay">
            <div className="delete-confirm-modal success-modal">
              <div className="success-icon-container">
                <div className="success-icon">✓</div>
              </div>
              <h3 className="success-title">Successfully Deleted!</h3>
              <p className="success-message">
                Student <strong>{student.first_name} {student.last_name}</strong> has been removed from the system.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface StudentsManagementProps {
  onViewChange?: (view: string) => void;
}

const StudentsManagement: React.FC<StudentsManagementProps> = ({ onViewChange }) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [modalMode, setModalMode] = useState<'view' | 'edit'>('view');
  const [showModal, setShowModal] = useState(false);
  const [showScholarshipForm, setShowScholarshipForm] = useState(false);
  const [currentUser, setCurrentUser] = useState<Student | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Check if user is logged in
        const token = localStorage.getItem('token');
        if (!token) {
          setError('You must be logged in to access this page. Please login first.');
          setLoading(false);
          return;
        }

        // First fetch current user info
        const userResponse = await apiClient.get<Student>('/auth/profile/');
        setCurrentUser(userResponse.data);
        
        // Then fetch students list (only if user is admin)
        if (userResponse.data.role === 'admin') {
          const studentsResponse = await apiClient.get<Student[]>('/students/');
          setStudents(studentsResponse.data);
        } else {
          // If user is a student, just set empty students array
          setStudents([]);
        }
        
      } catch (err: any) {
        console.error('Error fetching data:', err);
        let errorMessage = 'Failed to load data. Please try again later.';
        
        if (err.response?.status === 401) {
          errorMessage = 'Authentication failed. Please login again.';
          // Clear invalid token
          localStorage.removeItem('token');
        } else if (err.response?.status === 403) {
          errorMessage = 'Access denied. You may not have permission to view students.';
        } else if (err.response?.status === 404) {
          errorMessage = 'API endpoint not found. Please check if the backend is running.';
        } else if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
          errorMessage = 'Cannot connect to server. Please check if the backend server is running on http://localhost:8000';
        } else if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.message) {
          errorMessage = `Error: ${err.message}`;
        }
        
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleRetry = () => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Check if user is logged in
        const token = localStorage.getItem('token');
        if (!token) {
          setError('You must be logged in to access this page. Please login first.');
          setLoading(false);
          return;
        }

        // First fetch current user info
        const userResponse = await apiClient.get<Student>('/auth/profile/');
        setCurrentUser(userResponse.data);
        
        // Then fetch students list (only if user is admin)
        if (userResponse.data.role === 'admin') {
          const studentsResponse = await apiClient.get<Student[]>('/students/');
          setStudents(studentsResponse.data);
        } else {
          // If user is a student, just set empty students array
          setStudents([]);
        }
        
      } catch (err: any) {
        console.error('Error fetching data:', err);
        let errorMessage = 'Failed to load data. Please try again later.';
        
        if (err.response?.status === 401) {
          errorMessage = 'Authentication failed. Please login again.';
          localStorage.removeItem('token');
        } else if (err.response?.status === 403) {
          errorMessage = 'Access denied. You may not have permission to view students.';
        } else if (err.response?.status === 404) {
          errorMessage = 'API endpoint not found. Please check if the backend is running.';
        } else if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
          errorMessage = 'Cannot connect to server. Please check if the backend server is running on http://localhost:8000';
        } else if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.message) {
          errorMessage = `Error: ${err.message}`;
        }
        
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  };

  const filteredStudents = students.filter(student =>
    student.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.student_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewProfile = (student: Student) => {
    setSelectedStudent(student);
    setModalMode('view');
    setShowModal(true);
  };

  const handleEditProfile = (student: Student) => {
    setSelectedStudent(student);
    setModalMode('edit');
    setShowModal(true);
  };

  const handleSaveStudent = (updatedStudent: Student) => {
    setStudents(prev => prev.map(s => s.id === updatedStudent.id ? updatedStudent : s));
  };

  const handleDeleteStudent = (studentId: number) => {
    setStudents(prev => prev.filter(s => s.id !== studentId));
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedStudent(null);
  };

  const handleStartScholarshipApplication = () => {
    setShowScholarshipForm(true);
  };

  const handleScholarshipComplete = () => {
    setShowScholarshipForm(false);
    // Could show success message or refresh applications
  };

  const handleScholarshipCancel = () => {
    setShowScholarshipForm(false);
  };

  // Show scholarship form if user is a student and form is active
  if (showScholarshipForm && currentUser && currentUser.role === 'student') {
    return (
      <ScholarshipApplicationForm
        studentInfo={{
          studentId: currentUser.student_id,
          studentName: `${currentUser.first_name} ${currentUser.last_name}`,
          yearLevel: 'College', // You might want to add this to the Student interface
          program: 'Computer Science' // You might want to add this to the Student interface
        }}
        onComplete={handleScholarshipComplete}
        onCancel={handleScholarshipCancel}
      />
    );
  }

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
          <h2 className="error-title">Error Loading Students</h2>
          <p className="error-message">{error}</p>
          <button 
            className="retry-btn"
            onClick={handleRetry}
          >
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="students-management-container">
      <div className="students-management-content">
        {/* Header */}
        <div className="management-header">
          <div className="header-content">
            <h1>{currentUser?.role === 'student' ? 'Student Dashboard' : 'Students Management'}</h1>
            <p>
              {currentUser?.role === 'student' 
                ? 'Welcome to your student dashboard. Apply for scholarships and manage your applications.'
                : 'View and manage all registered students in the TCU-CEAA system'
              }
            </p>
          </div>
          
          <div className="header-stats">
            {currentUser?.role === 'student' ? (
              <div className="scholarship-actions">
                <button 
                  className="apply-scholarship-btn"
                  onClick={handleStartScholarshipApplication}
                >
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                  Apply for Scholarship
                </button>
              </div>
            ) : (
              <>
                <div className="stat-item">
                  <div className="stat-number">{students.length}</div>
                  <div className="stat-label">Total Students</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">{filteredStudents.length}</div>
                  <div className="stat-label">Filtered Results</div>
                </div>
              </>
            )}
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
                placeholder="Search by name, email, or student ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>

        {/* Main Content */}
        {currentUser?.role === 'student' ? (
          /* Student Dashboard Content */
          <div className="student-dashboard">
            <div className="dashboard-welcome">
              <div className="welcome-card">
                <div className="welcome-header">
                  <ProfileImage
                    src={currentUser.profile_image_url}
                    alt={`${currentUser.first_name} ${currentUser.last_name}`}
                    initials={`${currentUser.first_name[0]}${currentUser.last_name[0]}`}
                    size="large"
                  />
                  <div className="welcome-info">
                    <h2>Welcome, {currentUser.first_name}!</h2>
                    <p>Student ID: {currentUser.student_id}</p>
                    <p>Email: {currentUser.email}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="scholarship-section">
              <h3>Scholarship Applications</h3>
              <div className="scholarship-options">
                <div className="scholarship-card">
                  <div className="card-header">
                    <div className="card-icon merit">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                      </svg>
                    </div>
                    <h4>Apply for Scholarship</h4>
                  </div>
                  <p>Start your scholarship application with AI-powered document verification</p>
                  <ul className="features-list">
                    <li>Merit-based and regular scholarships available</li>
                    <li>AI verification with 95% confidence</li>
                    <li>Real-time document processing</li>
                    <li>Face verification with liveness detection</li>
                    <li>Automatic grade verification</li>
                  </ul>
                  <button 
                    className="scholarship-apply-btn"
                    onClick={handleStartScholarshipApplication}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 6v6l4 2" />
                      <circle cx="12" cy="12" r="10" />
                    </svg>
                    Start Application
                  </button>
                </div>

                <div className="info-cards">
                  <div className="info-card">
                    <h5>Quick Facts</h5>
                    <ul>
                      <li>Processing time: 1-3 business days</li>
                      <li>AI confidence threshold: 95%</li>
                      <li>Merit GWA requirement: 1.75 (85%)</li>
                      <li>All documents verified automatically</li>
                    </ul>
                  </div>
                  
                  <div className="info-card">
                    <h5>Required Documents</h5>
                    <ul>
                      <li>School ID</li>
                      <li>Birth Certificate (NSO/PSA)</li>
                      <li>Certificate of Enrollment</li>
                      <li>Voter Certificates (Student & Parent)</li>
                      <li>Face verification + Photo with ID</li>
                      <li>Grades (Merit applicants only)</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Admin Students List */
          <div className="students-grid">
            {filteredStudents.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">👥</div>
                <h3>No Students Found</h3>
                <p>
                  {searchTerm 
                    ? `No students match your search "${searchTerm}"`
                    : 'No students are registered in the system yet.'
                  }
                </p>
                {searchTerm && (
                  <button 
                    className="clear-search-btn"
                    onClick={() => setSearchTerm('')}
                  >
                    Clear Search
                  </button>
                )}
              </div>
            ) : (
              filteredStudents.map((student) => (
                <div key={student.id} className="student-card">
                  <div className="student-header">
                    <ProfileImage
                      src={student.profile_image_url}
                      alt={`${student.first_name} ${student.last_name}`}
                      initials={`${student.first_name[0]}${student.last_name[0]}`}
                      size="small"
                    />
                    <div className="student-info">
                      <h3 className="student-name">
                        {student.first_name} {student.last_name}
                      </h3>
                      <p className="student-id">ID: {student.student_id}</p>
                    </div>
                  </div>
                  
                  <div className="student-details">
                    <div className="detail-row">
                      <span className="detail-label">Email:</span>
                      <span className="detail-value">{student.email}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Joined:</span>
                      <span className="detail-value">
                        {new Date(student.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                  </div>

                  <div className="student-actions">
                    <button 
                      className="action-btn view-btn"
                      onClick={() => handleViewProfile(student)}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                      </svg>
                      View Profile
                    </button>
                    <button 
                      className="action-btn edit-btn"
                      onClick={() => handleEditProfile(student)}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                      </svg>
                      Edit
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Student Modal */}
        <StudentModal
          student={selectedStudent}
          isOpen={showModal}
          mode={modalMode}
          onClose={closeModal}
          onSave={handleSaveStudent}
          onDelete={handleDeleteStudent}
        />
      </div>
    </div>
  );
};

export default StudentsManagement;