import React, { useState } from 'react';
import { authService } from '../services/authService';
import './StudentRegistration.css';

interface StudentRegistrationProps {
  onBack: () => void;
  onGoToLogin: () => void;
}

const StudentRegistration: React.FC<StudentRegistrationProps> = ({ onBack, onGoToLogin }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    middleInitial: '',
    lastName: '',
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
    } else if (name === 'middleInitial') {
      // Format middle initial - capitalize and add period if needed
      let formatted = value.toUpperCase().replace(/[^A-Z.]/g, '');
      if (formatted.length > 0 && !formatted.endsWith('.')) {
        formatted = formatted.substring(0, 1) + '.';
      }
      if (formatted.length > 2) {
        formatted = formatted.substring(0, 2);
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

    try {
      // Step 1: Frontend Validation
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

      // Step 2: Verify Student Information
      try {
        const verificationResult = await authService.verifyStudent({
          studentId: formData.studentId,
          firstName: formData.firstName.trim(),
          lastName: formData.lastName.trim(),
          middleInitial: formData.middleInitial.replace('.', '').trim()
        });

        if (!verificationResult.verified) {
          setError(`Verification failed: ${verificationResult.message}`);
          setLoading(false);
          return;
        }
      } catch (verificationError: any) {
        console.error('Verification error:', verificationError);
        if (verificationError.response?.status === 403) {
          // Student not verified
          const errorData = verificationError.response?.data;
          setError(`Verification failed: ${errorData?.message || 'Student ID or Name details do not match our records. Please check your input.'}`);
        } else if (verificationError.response?.status === 400) {
          // Bad request
          const errorData = verificationError.response?.data;
          setError(`Verification error: ${errorData?.message || 'Invalid request. Please check all fields.'}`);
        } else {
          // Network or other errors
          setError('Verification failed: Unable to verify student information. Please try again later.');
        }
        setLoading(false);
        return;
      }

      // Step 3: Proceed with Registration (only if verification passed)
      await authService.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.confirmPassword,
        first_name: formData.firstName.trim(),
        last_name: formData.lastName.trim(),
        middle_initial: formData.middleInitial.trim() || '',
        student_id: formData.studentId,
        role: 'student'
      });

      setSuccess(true);
    } catch (registrationError: any) {
      console.error('Registration error:', registrationError);
      
      // Differentiate between registration errors and verification errors
      if (registrationError.response?.data) {
        const errorData = registrationError.response.data;
        
        if (typeof errorData === 'string') {
          setError(`Registration failed: ${errorData}`);
        } else if (errorData.detail) {
          setError(`Registration failed: ${errorData.detail}`);
        } else if (errorData.username) {
          setError('Registration failed: This username is already taken. Please choose a different username.');
        } else if (errorData.email) {
          setError('Registration failed: This email is already registered.');
        } else if (errorData.student_id) {
          setError('Registration failed: This student ID is already registered.');
        } else if (errorData.non_field_errors) {
          setError(`Registration failed: ${errorData.non_field_errors[0]}`);
        } else {
          const errorMessages = Object.values(errorData).flat();
          setError(`Registration failed: ${errorMessages.join(', ')}`);
        }
      } else {
        setError('Registration failed: An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="student-registration-container">
        <div className="registration-card success-card">
          <div className="success-celebration">
            <div className="celebration-particles">
              <div className="particle particle-1"></div>
              <div className="particle particle-2"></div>
              <div className="particle particle-3"></div>
              <div className="particle particle-4"></div>
              <div className="particle particle-5"></div>
              <div className="particle particle-6"></div>
            </div>
            
            <div className="success-header">
              <div className="tcu-logo-success">
                <div className="logo-circle-success">
                  <img src="/images/TCU_logo.png" alt="TCU Logo" className="tcu-logo-img-success" />
                </div>
              </div>
              <h1 className="university-name-success">Taguig City University</h1>
            </div>
            
            <div className="success-content-wrapper">
              <div className="success-icon-wrapper">
                <div className="success-checkmark">
                  <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="11" fill="url(#successGradient)" stroke="#fff" strokeWidth="2"/>
                    <path d="M8 12.5L11 15.5L16 9.5" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                    <defs>
                      <linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#4CAF50" />
                        <stop offset="100%" stopColor="#45a049" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
              </div>
              
              <div className="success-message-content">
                <h2 className="success-title">Registration Successful!</h2>
                <p className="success-subtitle">Welcome to TCU-CEAA</p>
                
                <div className="success-details">
                  <div className="success-detail-item">
                    <div className="detail-icon">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="#4CAF50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <span>Your TCU student account has been created</span>
                  </div>
                  <div className="success-detail-item">
                    <div className="detail-icon">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="#4CAF50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <span>You can now access TCU-CEAA services</span>
                  </div>
                  <div className="success-detail-item">
                    <div className="detail-icon">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="#4CAF50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <span>Start managing your academic documents</span>
                  </div>
                </div>
                
                <div className="success-actions">
                  <button
                    onClick={onGoToLogin}
                    className="success-primary-button"
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M15 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M10 17L15 12L10 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M15 12H3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    Continue to Sign In
                  </button>
                </div>
              </div>
            </div>
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
            <div className="logo-circle">
              <img src="/images/TCU_logo.png" alt="TCU Logo" className="tcu-logo-img" />
            </div>
          </div>
          <h1>Taguig City University</h1>
          <h2>Student Registration</h2>
          <p>Create your student account to access TCU-CEAA</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstName">First Name *</label>
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Enter your first name"
              />
            </div>
            <div className="form-group">
              <label htmlFor="middleInitial">Middle Initial</label>
              <input
                type="text"
                id="middleInitial"
                name="middleInitial"
                value={formData.middleInitial}
                onChange={handleInputChange}
                className="form-input"
                placeholder="M."
                maxLength={2}
              />
              <small className="form-hint">Optional (e.g., M.)</small>
            </div>
            <div className="form-group">
              <label htmlFor="lastName">Last Name *</label>
              <input
                type="text"
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Enter your last name"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="form-input"
              placeholder="your.email@gmail.com"
            />
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
              <div className="input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  placeholder="Create a password"
                  minLength={8}
                  data-has-toggle="true"
                />
                <button
                  type="button"
                  className="password-toggle-button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    // Eye open icon
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                      <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                  ) : (
                    // Eye closed icon
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password *</label>
              <div className="input-wrapper">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  placeholder="Confirm your password"
                  data-has-toggle="true"
                />
                <button
                  type="button"
                  className="password-toggle-button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                >
                  {showConfirmPassword ? (
                    // Eye open icon
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                      <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                  ) : (
                    // Eye closed icon
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  )}
                </button>
              </div>
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
              onClick={onGoToLogin}
              className="back-button"
            >
              ← Go to Sign In
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StudentRegistration;
