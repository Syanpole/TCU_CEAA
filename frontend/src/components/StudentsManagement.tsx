import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/authService';
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
      await apiClient.delete(`/users/${student.id}/`);
      onDelete(student.id);
      onClose();
    } catch (error) {
      console.error('Error deleting student:', error);
      alert('Failed to delete student. Please try again.');
    } finally {
      setLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  if (!isOpen || !student || !editedStudent) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>{mode === 'view' ? 'View Profile' : 'Edit Profile'}</h3>
          <button className="modal-close" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 6l12 12m0-12L6 18" />
            </svg>
          </button>
        </div>

        <div className="modal-body">
          <div className="profile-section">
            <div className="profile-image-large">
              {student.profile_image_url ? (
                <img 
                  src={student.profile_image_url} 
                  alt={`${student.first_name} ${student.last_name}`}
                  className="profile-img"
                />
              ) : (
                <div className="profile-placeholder">
                  {student.first_name[0]}{student.last_name[0]}
                </div>
              )}
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>First Name</label>
              {mode === 'edit' ? (
                <input
                  type="text"
                  value={editedStudent.first_name}
                  onChange={(e) => setEditedStudent({...editedStudent, first_name: e.target.value})}
                  className="form-input"
                />
              ) : (
                <div className="form-display">{student.first_name}</div>
              )}
            </div>

            <div className="form-group">
              <label>Last Name</label>
              {mode === 'edit' ? (
                <input
                  type="text"
                  value={editedStudent.last_name}
                  onChange={(e) => setEditedStudent({...editedStudent, last_name: e.target.value})}
                  className="form-input"
                />
              ) : (
                <div className="form-display">{student.last_name}</div>
              )}
            </div>

            <div className="form-group">
              <label>Email</label>
              {mode === 'edit' ? (
                <input
                  type="email"
                  value={editedStudent.email}
                  onChange={(e) => setEditedStudent({...editedStudent, email: e.target.value})}
                  className="form-input"
                />
              ) : (
                <div className="form-display">{student.email}</div>
              )}
            </div>

            <div className="form-group">
              <label>Student ID</label>
              {mode === 'edit' ? (
                <input
                  type="text"
                  value={editedStudent.student_id}
                  onChange={(e) => setEditedStudent({...editedStudent, student_id: e.target.value})}
                  className="form-input"
                />
              ) : (
                <div className="form-display">{student.student_id}</div>
              )}
            </div>

            <div className="form-group">
              <label>Username</label>
              {mode === 'edit' ? (
                <input
                  type="text"
                  value={editedStudent.username}
                  onChange={(e) => setEditedStudent({...editedStudent, username: e.target.value})}
                  className="form-input"
                />
              ) : (
                <div className="form-display">{student.username}</div>
              )}
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
      </div>
    </div>
  );
};

interface StudentsManagementProps {
  onViewChange?: (view: string) => void;
}

const StudentsManagement: React.FC<StudentsManagementProps> = ({ onViewChange }) => {
  const { user } = useAuth();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [modalMode, setModalMode] = useState<'view' | 'edit'>('view');
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get<Student[]>('/students/');
        setStudents(response.data);
      } catch (err) {
        console.error('Error fetching students:', err);
        setError('Failed to load students. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

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

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2 className="loading-title">Loading Students</h2>
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
            onClick={() => window.location.reload()}
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
            <h1>Students Management</h1>
            <p>View and manage all registered students in the TCU CEAA system</p>
          </div>
          
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-number">{students.length}</div>
              <div className="stat-label">Total Students</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{filteredStudents.length}</div>
              <div className="stat-label">Filtered Results</div>
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
                placeholder="Search by name, email, or student ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </div>

        {/* Students List */}
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
                  <div className="student-avatar">
                    {student.profile_image_url ? (
                      <img 
                        src={student.profile_image_url} 
                        alt={`${student.first_name} ${student.last_name}`}
                        className="avatar-image"
                      />
                    ) : (
                      <div className="avatar-initials">
                        {student.first_name[0]}{student.last_name[0]}
                      </div>
                    )}
                  </div>
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
