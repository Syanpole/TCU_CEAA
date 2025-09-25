import React, { useState } from 'react';
import { authService } from '../services/authService';
import './ModalRegistration.css';

interface ModalRegistrationProps {
  onClose: () => void;
  onSwitchToLogin: () => void;
}

const ModalRegistration: React.FC<ModalRegistrationProps> = ({ onClose, onSwitchToLogin }) => {
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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const validateStudentId = (id: string): boolean => {
    const pattern = /^\d{2}-\d{5}$/;
    return pattern.test(id);
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
      <div className="modal-registration-container">
        <div className="modal-success-content">
          <div className="modal-success-icon">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="11" fill="#4CAF50" stroke="#fff" strokeWidth="2"/>
              <path d="M8 12.5L11 15.5L16 9.5" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2>Registration Successful!</h2>
          <p>Welcome to TCU-CEAA! Your student account has been created successfully.</p>
          <div className="modal-success-actions">
            <button onClick={onSwitchToLogin} className="modal-success-button">
              Continue to Sign In
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-registration-container">
      <div className="modal-registration-header">
        <div className="modal-tcu-logo">
          <img src="/images/TCU_logo.png" alt="TCU Logo" className="modal-logo-img" />
        </div>
        <h2>Student Registration</h2>
        <p>Create your TCU-CEAA account</p>
      </div>

      <form onSubmit={handleSubmit} className="modal-registration-form">
        {error && (
          <div className="modal-error-message">
            <span className="modal-error-icon">⚠️</span>
            {error}
          </div>
        )}

        <div className="modal-form-row">
          <div className="modal-form-group">
            <label htmlFor="modal-fullName">Full Name *</label>
            <input
              type="text"
              id="modal-fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleInputChange}
              required
              className="modal-form-input"
              placeholder="Enter your full name"
            />
          </div>
        </div>

        <div className="modal-form-row">
          <div className="modal-form-group">
            <label htmlFor="modal-email">Email Address *</label>
            <input
              type="email"
              id="modal-email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="modal-form-input"
              placeholder="your.email@gmail.com"
            />
          </div>
        </div>

        <div className="modal-form-row modal-form-row-two">
          <div className="modal-form-group">
            <label htmlFor="modal-username">Username *</label>
            <input
              type="text"
              id="modal-username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              className="modal-form-input"
              placeholder="Choose username"
            />
          </div>
          <div className="modal-form-group">
            <label htmlFor="modal-studentId">Student ID *</label>
            <input
              type="text"
              id="modal-studentId"
              name="studentId"
              value={formData.studentId}
              onChange={handleInputChange}
              required
              className="modal-form-input"
              placeholder="22-00001"
              maxLength={8}
            />
          </div>
        </div>

        <div className="modal-form-row modal-form-row-two">
          <div className="modal-form-group">
            <label htmlFor="modal-password">Password *</label>
            <div className="modal-input-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                id="modal-password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="modal-form-input"
                placeholder="Create password"
                minLength={8}
              />
              <button
                type="button"
                className="modal-password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                    <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                )}
              </button>
            </div>
          </div>
          <div className="modal-form-group">
            <label htmlFor="modal-confirmPassword">Confirm Password *</label>
            <div className="modal-input-wrapper">
              <input
                type={showConfirmPassword ? "text" : "password"}
                id="modal-confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required
                className="modal-form-input"
                placeholder="Confirm password"
              />
              <button
                type="button"
                className="modal-password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                    <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="modal-terms-section">
          <p>By registering, you agree to TCU's Terms of Service and Privacy Policy.</p>
        </div>

        <button 
          type="submit" 
          className="modal-submit-button"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="modal-loading-spinner"></span>
              Creating Account...
            </>
          ) : (
            'Create Account'
          )}
        </button>

        <div className="modal-divider">
          <span>or</span>
        </div>

        <button
          type="button"
          onClick={onSwitchToLogin}
          className="modal-switch-button"
        >
          Already have an account? Sign In
        </button>
      </form>
    </div>
  );
};

export default ModalRegistration;