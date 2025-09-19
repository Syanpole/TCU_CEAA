import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './ModalLogin.css';

interface ModalLoginProps {
  onClose: () => void;
  onSwitchToRegister: () => void;
}

const ModalLogin: React.FC<ModalLoginProps> = ({ onClose, onSwitchToRegister }) => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError(''); // Clear error when user starts typing
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData.username, formData.password);
      onClose(); // Close modal on successful login
    } catch (error: any) {
      console.error('Authentication error:', error);
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
        setError('Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-login-container">
      <div className="modal-login-header">
        <div className="modal-tcu-logo">
          <img src="/images/TCU_logo.png" alt="TCU Logo" className="modal-logo-img" />
        </div>
        <h2>Welcome Back</h2>
        <p>Sign in to access your dashboard</p>
      </div>

      <form onSubmit={handleSubmit} className="modal-login-form">
        {error && (
          <div className="modal-error-message">
            <span className="modal-error-icon">⚠️</span>
            {error}
          </div>
        )}

        <div className="modal-form-group">
          <label htmlFor="modal-username">Username or Email</label>
          <input
            type="text"
            id="modal-username"
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            required
            className="modal-form-input"
            placeholder="Enter your username or email"
          />
        </div>

        <div className="modal-form-group">
          <label htmlFor="modal-password">Password</label>
          <div className="modal-input-wrapper">
            <input
              type={showPassword ? "text" : "password"}
              id="modal-password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              className="modal-form-input"
              placeholder="Enter your password"
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

        <button 
          type="submit" 
          className="modal-submit-button"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="modal-loading-spinner"></span>
              Signing in...
            </>
          ) : (
            'Sign In'
          )}
        </button>

        <div className="modal-divider">
          <span>or</span>
        </div>

        <button
          type="button"
          onClick={onSwitchToRegister}
          className="modal-switch-button"
        >
          New Student? Create Account
        </button>
      </form>
    </div>
  );
};

export default ModalLogin;