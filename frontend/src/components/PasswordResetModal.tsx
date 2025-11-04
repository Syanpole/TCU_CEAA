import React, { useState } from 'react';
import axios from 'axios';
import './PasswordResetModal.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface PasswordResetModalProps {
  onClose: () => void;
  initialEmail?: string;
}

const PasswordResetModal: React.FC<PasswordResetModalProps> = ({ onClose, initialEmail = '' }) => {
  const [step, setStep] = useState<'email' | 'reset'>('email');
  const [email, setEmail] = useState(initialEmail);
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSendCode = async () => {
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/auth/request-password-reset/`, {
        email: email
      });

      if ((response.data as any).success) {
        setStep('reset');
        setError('');
      }
    } catch (error: any) {
      console.error('Send code error:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Failed to send verification code. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setError('');
    setLoading(true);

    try {
      await axios.post(`${API_URL}/api/auth/request-password-reset/`, {
        email: email
      });
      setError('');
      alert('Verification code resent to your email!');
    } catch (error: any) {
      console.error('Resend code error:', error);
      setError('Failed to resend code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (step === 'email') {
      await handleSendCode();
      return;
    }

    // Validate passwords
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      // First verify the code
      const verifyResponse = await axios.post(`${API_URL}/api/auth/verify-reset-code/`, {
        email: email,
        code: otp
      });

      if ((verifyResponse.data as any).success) {
        // Then reset the password
        const resetResponse = await axios.post(`${API_URL}/api/auth/reset-password/`, {
          email: email,
          code: otp,
          new_password: newPassword
        });

        if ((resetResponse.data as any).success) {
          setSuccess(true);
          setTimeout(() => {
            onClose();
          }, 2000);
        }
      }
    } catch (error: any) {
      console.error('Password reset error:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Failed to reset password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (step === 'email') {
    return (
      <div className="password-reset-overlay">
        <div className="password-reset-container">
          <button className="close-button-reset" onClick={onClose} aria-label="Close">
            ×
          </button>

          <div className="reset-header">
            <div className="phone-icon">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="7" y="4" width="10" height="16" rx="2" stroke="#9CA3AF" strokeWidth="1.5"/>
                <line x1="10" y1="6" x2="14" y2="6" stroke="#9CA3AF" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
            </div>
            <h2>Forgot Password</h2>
            <p>Enter your email to receive a verification code</p>
          </div>

          <form onSubmit={handleSubmit} className="reset-form">
            {error && (
              <div className="error-message-reset">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}

            <div className="form-group-reset">
              <label htmlFor="email">Email Address <span className="required">*</span></label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
                className="form-input-reset"
              />
            </div>

            <button 
              type="submit" 
              className="submit-button-reset"
              disabled={loading}
            >
              {loading ? 'Sending...' : 'Send Code'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="password-reset-overlay">
      <div className="password-reset-container">
        <button className="close-button-reset" onClick={onClose} aria-label="Close">
          ×
        </button>

        <div className="reset-header">
          <div className="phone-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="7" y="4" width="10" height="16" rx="2" stroke="#9CA3AF" strokeWidth="1.5"/>
              <line x1="10" y1="6" x2="14" y2="6" stroke="#9CA3AF" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>Reset Password</h2>
          <p>Enter the OTP code we sent to <strong>{email}</strong> <span className="required">*</span></p>
        </div>

        <form onSubmit={handleSubmit} className="reset-form">
          {error && (
            <div className="error-message-reset">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {success && (
            <div className="success-message-reset">
              <span className="success-icon">✓</span>
              Password reset successful! Redirecting to login...
            </div>
          )}

          <div className="form-group-reset">
            <label htmlFor="otp">Enter 6-digit OTP</label>
            <input
              type="text"
              id="otp"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="Enter 6-digit OTP"
              maxLength={6}
              required
              className="form-input-reset otp-input"
            />
          </div>

          <div className="form-group-reset">
            <label htmlFor="new-password">New Password <span className="required">*</span></label>
            <div className="password-input-wrapper">
              <input
                type={showNewPassword ? "text" : "password"}
                id="new-password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter your new password"
                minLength={8}
                required
                className="form-input-reset"
              />
              <button
                type="button"
                className="password-toggle-reset"
                onClick={() => setShowNewPassword(!showNewPassword)}
                aria-label={showNewPassword ? "Hide password" : "Show password"}
              >
                {showNewPassword ? (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                    <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                )}
              </button>
            </div>
            <p className="password-hint">Use 8 or more characters with a mix of letters, numbers & symbols.</p>
          </div>

          <div className="form-group-reset">
            <label htmlFor="confirm-password">Confirm New Password <span className="required">*</span></label>
            <div className="password-input-wrapper">
              <input
                type={showConfirmPassword ? "text" : "password"}
                id="confirm-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your new password"
                minLength={8}
                required
                className="form-input-reset"
              />
              <button
                type="button"
                className="password-toggle-reset"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                    <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
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
            className="submit-button-reset"
            disabled={loading || success}
          >
            {loading ? 'Submitting...' : success ? 'Success!' : 'Submit'}
          </button>

          <div className="resend-section">
            <p>Didn't get the code? {' '}
              <button 
                type="button" 
                onClick={handleResendCode}
                className="resend-link"
                disabled={loading}
              >
                Resend
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PasswordResetModal;
