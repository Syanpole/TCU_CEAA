import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

interface LoginProps {
  onToggleMode: () => void;
  isRegisterMode: boolean;
  onStudentRegister: () => void;
}

const Login: React.FC<LoginProps> = ({ onToggleMode, isRegisterMode, onStudentRegister }) => {
  const { login, register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    password_confirm: '',
    email: '',
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegisterMode) {
        if (formData.password !== formData.password_confirm) {
          setError('Passwords do not match');
          return;
        }
        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          password_confirm: formData.password_confirm,
          first_name: formData.first_name,
          last_name: formData.last_name,
          role: 'user'
        });
      } else {
        await login(formData.username, formData.password);
      }
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
          // Handle field-specific errors
          const errorMessages = Object.values(errorData).flat();
          setError(errorMessages.join(', '));
        }
      } else {
        setError(isRegisterMode ? 'Registration failed' : 'Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modern-login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="tcu-logo">
            <div className="logo-circle">TCU</div>
          </div>
          <h1>TCU CEAA</h1>
          <h2>{isRegisterMode ? 'Create Admin Account' : 'Welcome Back'}</h2>
          <p>{isRegisterMode ? 'Set up your administrator account' : 'Sign in to access your dashboard'}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <div className="input-wrapper">
              <span className="input-icon">👤</span>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Enter your username"
              />
            </div>
          </div>

          {isRegisterMode && (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="first_name">First Name</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      id="first_name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder="First name"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="last_name">Last Name</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      id="last_name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder="Last name"
                    />
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <div className="input-wrapper">
                  <span className="input-icon">📧</span>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="form-input"
                    placeholder="Enter your email"
                  />
                </div>
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <span className="input-icon">🔐</span>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Enter your password"
              />
            </div>
          </div>

          {isRegisterMode && (
            <div className="form-group">
              <label htmlFor="password_confirm">Confirm Password</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type="password"
                  id="password_confirm"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  placeholder="Confirm your password"
                />
              </div>
            </div>
          )}

          <button 
            type="submit" 
            className="submit-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Please wait...
              </>
            ) : (
              isRegisterMode ? 'Create Account' : 'Sign In'
            )}
          </button>

          <div className="form-footer">
            <button
              type="button"
              onClick={onToggleMode}
              className="toggle-mode-button"
            >
              {isRegisterMode 
                ? '← Back to Sign In' 
                : "Need admin access? Create account"}
            </button>
          </div>

          {!isRegisterMode && (
            <div className="student-section">
              <div className="divider">
                <span>or</span>
              </div>
              <button
                type="button"
                onClick={onStudentRegister}
                className="student-register-button"
              >
                🎓 TCU Student Registration
              </button>
            </div>
          )}
        </form>

        {!isRegisterMode && (
          <div className="demo-credentials">
            <div className="demo-header">
              <h4>🔑 Demo Credentials</h4>
            </div>
            <div className="demo-item">
              <strong>Admin:</strong> username: admin | password: admin123
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
