import React, { useState } from 'react';
import { authService } from '../services/authService';
import './StudentRegistration.css';

interface StudentRegistrationProps {
  onBack: () => void;
}

const StudentRegistration: React.FC<StudentRegistrationProps> = ({ onBack }) => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    username: '',
    studentId: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const validateStudentId = (id: string): boolean => {
    const pattern = /^\d{2}-\d{5}$/;
    return pattern.test(id);
  };

  const validateTCUEmail = (email: string): boolean => {
    return email.toLowerCase().includes('tcu') || 
           email.toLowerCase().includes('taguig') ||
           email.toLowerCase().includes('@student.tcu.edu.ph');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    // Auto-format student ID
    if (name === 'studentId') {
      let formatted = value.replace(/\D/g, '');
      if (formatted.length > 2) {
        formatted = formatted.substring(0, 2) + '-' + formatted.substring(2, 7);
      }
      setFormData(prev => ({ ...prev, [name]: formatted }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear errors when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (!validateStudentId(formData.studentId)) {
      setError('Student ID must be in format: XX-XXXXX (e.g., 22-00001)');
      setLoading(false);
      return;
    }

    if (!validateTCUEmail(formData.email)) {
      setError('Please use a valid TCU email address');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    try {
      const [firstName, ...lastNameParts] = formData.fullName.trim().split(' ');
      const lastName = lastNameParts.join(' ');

      await authService.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.confirmPassword,
        first_name: firstName,
        last_name: lastName || '',
        student_id: formData.studentId,
        role: 'student'
      });

      setSuccess(true);
    } catch (error: any) {
      console.error('Registration error:', error);
      if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData === 'string') {
          setError(errorData);
        } else if (errorData.detail) {
          setError(errorData.detail);
        } else if (errorData.non_field_errors) {
          setError(errorData.non_field_errors[0]);
        } else {
          const errorMessages = Object.values(errorData).flat();
          setError(errorMessages.join(', '));
        }
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="student-registration-container">
        <div className="registration-card">
          <div className="success-message">
            <div className="success-icon">✅</div>
            <h2>Registration Successful!</h2>
            <p>Your TCU student account has been created successfully.</p>
            <p>You can now sign in with your credentials.</p>
            <button onClick={onBack} className="back-to-login-btn">
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="student-registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <div className="tcu-logo">
            <div className="logo-circle">TCU</div>
          </div>
          <h1>Taguig City University</h1>
          <h2>Student Registration</h2>
          <p>Create your student account to access TCU CEAA</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="fullName">Full Name *</label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder="Enter your full name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">TCU Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder="your.name@student.tcu.edu.ph"
            />
            <small className="form-hint">Use your official TCU student email</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="username">Username *</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Choose a username"
              />
            </div>
            <div className="form-group">
              <label htmlFor="studentId">Student ID *</label>
              <input
                type="text"
                id="studentId"
                name="studentId"
                value={formData.studentId}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="22-00001"
                maxLength={8}
              />
              <small className="form-hint">Format: YY-XXXXX</small>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Create a password"
                minLength={8}
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password *</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Confirm your password"
              />
            </div>
          </div>

          <div className="terms-section">
            <p className="terms-text">
              By registering, you agree to TCU's Terms of Service and Privacy Policy.
              Only enrolled TCU students are eligible for this service.
            </p>
          </div>

          <button 
            type="submit" 
            className="register-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Creating Account...
              </>
            ) : (
              'Create Student Account'
            )}
          </button>

          <div className="form-footer">
            <button
              type="button"
              onClick={onBack}
              className="back-button"
            >
              ← Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StudentRegistration;
