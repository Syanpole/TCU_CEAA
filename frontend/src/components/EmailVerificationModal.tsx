import React, { useState, useEffect, useRef } from 'react';
import './EmailVerificationModal.css';

interface EmailVerificationModalProps {
  email: string;
  onVerified: (verificationCode: string) => void;
  onCancel: () => void;
  onResend: () => Promise<{ success: boolean; message: string }>;
}

const EmailVerificationModal: React.FC<EmailVerificationModalProps> = ({
  email,
  onVerified,
  onCancel,
  onResend
}) => {
  const [code, setCode] = useState<string[]>(['', '', '', '', '', '']);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [timeLeft, setTimeLeft] = useState<number>(600); // 10 minutes in seconds
  const [canResend, setCanResend] = useState<boolean>(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Timer countdown
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          setCanResend(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleInputChange = (index: number, value: string) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) {
      return;
    }

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    setError('');

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all 6 digits are entered
    if (index === 5 && value) {
      const fullCode = [...newCode.slice(0, 5), value].join('');
      handleVerify(fullCode);
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    const newCode = [...code];
    
    for (let i = 0; i < pastedData.length; i++) {
      newCode[i] = pastedData[i];
    }
    
    setCode(newCode);
    
    // Focus last filled input or first empty one
    const nextIndex = Math.min(pastedData.length, 5);
    inputRefs.current[nextIndex]?.focus();

    // Auto-submit if 6 digits pasted
    if (pastedData.length === 6) {
      handleVerify(pastedData);
    }
  };

  const handleVerify = async (verificationCode?: string) => {
    const fullCode = verificationCode || code.join('');
    
    if (fullCode.length !== 6) {
      setError('Please enter all 6 digits');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Call parent's onVerified callback
      onVerified(fullCode);
    } catch (err: any) {
      setError(err.message || 'Verification failed');
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const result = await onResend();
      
      if (result.success) {
        setSuccess(result.message);
        setCode(['', '', '', '', '', '']);
        setTimeLeft(600); // Reset timer to 10 minutes
        setCanResend(false);
        inputRefs.current[0]?.focus();
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to resend code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verification-modal-overlay">
      <div className="verification-modal">
        <div className="verification-modal-header">
          <div className="verification-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 8L10.89 13.26C11.2187 13.4793 11.6049 13.5963 12 13.5963C12.3951 13.5963 12.7813 13.4793 13.11 13.26L21 8M5 19H19C19.5304 19 20.0391 18.7893 20.4142 18.4142C20.7893 18.0391 21 17.5304 21 17V7C21 6.46957 20.7893 5.96086 20.4142 5.58579C20.0391 5.21071 19.5304 5 19 5H5C4.46957 5 3.96086 5.21071 3.58579 5.58579C3.21071 5.96086 3 6.46957 3 7V17C3 17.5304 3.21071 18.0391 3.58579 18.4142C3.96086 18.7893 4.46957 19 5 19Z" stroke="#007AFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h2>Verify Your Email</h2>
          <p className="verification-email-label">
            We sent a 6-digit code to:<br />
            <strong>{email}</strong>
          </p>
        </div>

        <div className="verification-modal-body">
          {error && (
            <div className="verification-error">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 8V12M12 16H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              {error}
            </div>
          )}

          {success && (
            <div className="verification-success">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              {success}
            </div>
          )}

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
                onPaste={handlePaste}
                className={`code-input ${digit ? 'filled' : ''}`}
                disabled={loading}
                aria-label={`Digit ${index + 1}`}
              />
            ))}
          </div>

          <div className="verification-timer">
            {timeLeft > 0 ? (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                  <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Code expires in {formatTime(timeLeft)}
              </>
            ) : (
              <span className="timer-expired">Code expired</span>
            )}
          </div>

          <div className="verification-actions">
            <button
              onClick={() => handleVerify()}
              disabled={loading || code.join('').length !== 6}
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
              <span className="resend-text">Didn't receive the code?</span>
              {canResend || timeLeft === 0 ? (
                <button
                  onClick={handleResendCode}
                  disabled={loading}
                  className="resend-button"
                >
                  Resend Code
                </button>
              ) : (
                <span className="resend-disabled">
                  Resend available in {formatTime(timeLeft)}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="verification-modal-footer">
          <button onClick={onCancel} className="cancel-button" disabled={loading}>
            Cancel Registration
          </button>
        </div>

        <div className="verification-help">
          <p>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
              <path d="M12 16V12M12 8H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Check your spam folder if you don't see the email
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationModal;
