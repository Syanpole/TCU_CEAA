import React, { useState, useEffect, useRef } from 'react';
import './EmailVerificationModal.css';

interface EmailVerificationModalProps {
  isOpen: boolean;
  email: string;
  onSuccess: (token: string, user: any) => void;
  onClose: () => void;
}

const EmailVerificationModal: React.FC<EmailVerificationModalProps> = ({
  isOpen,
  email,
  onSuccess,
  onClose,
}) => {
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Cooldown timer
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  // Focus first input when modal opens
  useEffect(() => {
    if (isOpen && inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, [isOpen]);

  const handleInputChange = (index: number, value: string) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    setError('');

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all 6 digits are entered
    if (newCode.every(digit => digit !== '') && value) {
      handleVerify(newCode.join(''));
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      // Move to previous input on backspace if current is empty
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    
    // Only process if it's 6 digits
    if (/^\d{6}$/.test(pastedData)) {
      const digits = pastedData.split('');
      setCode(digits);
      setError('');
      
      // Focus last input
      inputRefs.current[5]?.focus();
      
      // Auto-submit
      handleVerify(pastedData);
    }
  };

  const handleVerify = async (verificationCode?: string) => {
    const codeToVerify = verificationCode || code.join('');
    
    if (codeToVerify.length !== 6) {
      setError('Please enter all 6 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/verify-email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          code: codeToVerify,
        }),
      });

      const data = await response.json();

      if (response.ok && data.valid) {
        setSuccess(true);
        setTimeout(() => {
          onSuccess(data.token, data.user);
        }, 1500);
      } else {
        setError(data.message || 'Invalid or expired verification code. Please try again.');
        setCode(['', '', '', '', '', '']);
        inputRefs.current[0]?.focus();
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError('Failed to verify code. Please check your connection and try again.');
      setCode(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/resend-verification-code/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setResendCooldown(60); // 60 second cooldown
        setCode(['', '', '', '', '', '']);
        inputRefs.current[0]?.focus();
        // Show success message briefly
        setError('');
        setTimeout(() => {
          setError('New verification code sent! Check your email.');
        }, 100);
        setTimeout(() => {
          setError('');
        }, 3000);
      } else {
        setError(data.message || 'Failed to resend code. Please try again.');
      }
    } catch (err) {
      console.error('Resend error:', err);
      setError('Failed to resend code. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {success ? (
          <div className="verification-success">
            <div className="success-animation">
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
            <h2 className="success-title">Email Verified!</h2>
            <p className="success-message">Redirecting to your dashboard...</p>
          </div>
        ) : (
          <>
            <div className="modal-header">
              <div className="modal-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="5" width="18" height="14" rx="2" stroke="url(#emailGradient)" strokeWidth="2"/>
                  <path d="M3 7L12 13L21 7" stroke="url(#emailGradient)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <defs>
                    <linearGradient id="emailGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#667eea" />
                      <stop offset="100%" stopColor="#764ba2" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <h2 className="modal-title">Verify Your Email</h2>
              <p className="modal-subtitle">
                We've sent a 6-digit verification code to<br />
                <strong>{email}</strong>
              </p>
            </div>

            <div className="modal-body">
              <div className="code-input-container">
                {code.map((digit, index) => (
                  <input
                    key={index}
                    ref={(el) => (inputRefs.current[index] = el)}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleInputChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    onPaste={index === 0 ? handlePaste : undefined}
                    className={`code-input ${error ? 'error' : ''} ${digit ? 'filled' : ''}`}
                    disabled={loading}
                    aria-label={`Digit ${index + 1} of verification code`}
                    title={`Enter digit ${index + 1}`}
                  />
                ))}
              </div>

              {error && (
                <div className="error-message">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                    <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <circle cx="12" cy="16" r="1" fill="currentColor"/>
                  </svg>
                  {error}
                </div>
              )}

              <div className="modal-info">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  <path d="M12 16V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <circle cx="12" cy="8" r="1" fill="currentColor"/>
                </svg>
                <span>Code expires in 15 minutes</span>
              </div>

              <button
                onClick={() => handleVerify()}
                disabled={loading || code.some(d => !d)}
                className="verify-button"
              >
                {loading ? (
                  <>
                    <span className="loading-spinner"></span>
                    Verifying...
                  </>
                ) : (
                  'Verify Email'
                )}
              </button>

              <div className="resend-section">
                <p>Didn't receive the code?</p>
                <button
                  onClick={handleResend}
                  disabled={loading || resendCooldown > 0}
                  className="resend-button"
                >
                  {resendCooldown > 0
                    ? `Resend in ${resendCooldown}s`
                    : 'Resend Code'}
                </button>
              </div>
            </div>

            <button onClick={onClose} className="close-button" aria-label="Close modal">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default EmailVerificationModal;
