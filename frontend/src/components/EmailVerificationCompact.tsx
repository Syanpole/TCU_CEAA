import React, { useState, useEffect, useRef, CSSProperties } from 'react';
import { sendVerificationCode, verifyEmailCode, resendVerificationCode } from '../services/verificationService';
import './EmailVerificationCompact.css';

interface EmailVerificationProps {
  email: string;
  onVerificationSuccess: (code: string) => void;
  onCancel?: () => void;
}

const EmailVerificationCompact: React.FC<EmailVerificationProps> = ({
  email,
  onVerificationSuccess,
  onCancel
}) => {
  const overlayStyle: CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    width: '100vw',
    height: '100vh',
    minWidth: '100vw',
    minHeight: '100vh',
    maxWidth: '100vw',
    maxHeight: '100vh',
    background: '#000000',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 999999,
    padding: 0,
    margin: 0,
    boxSizing: 'border-box',
    overflow: 'hidden'
  };
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [timeLeft, setTimeLeft] = useState(600);
  const [canResend, setCanResend] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [codeSent, setCodeSent] = useState(false);
  
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft > 0) {
      setCanResend(true);
    }
  }, [resendCooldown, timeLeft]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const handleSendCode = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await sendVerificationCode(email);
      if (result.success) {
        setCodeSent(true);
        setSuccess('✓ Verification code sent to your email!');
        setTimeout(() => setSuccess(''), 4000);
        setTimeLeft(600);
        setCanResend(false);
        setResendCooldown(60);
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('Failed to send code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value.slice(-1);
    setCode(newCode);
    setError('');

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    if (index === 5 && value && newCode.join('').length === 6) {
      handleVerify(newCode.join(''));
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    const newCode = pastedData.split('').concat(Array(6).fill('')).slice(0, 6);
    setCode(newCode);
    
    if (pastedData.length === 6) {
      handleVerify(pastedData);
    }
  };

  const handleVerify = async (verificationCode?: string) => {
    const fullCode = verificationCode || code.join('');
    
    if (fullCode.length !== 6) {
      setError('Enter 6-digit code');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await verifyEmailCode(email, fullCode);
      if (result.success) {
        setSuccess('✓ Verified!');
        setTimeout(() => onVerificationSuccess(fullCode), 600);
      } else {
        setError(result.message);
        setCode(['', '', '', '', '', '']);
        inputRefs.current[0]?.focus();
      }
    } catch (err) {
      setError('Verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (!canResend || resendCooldown > 0) return;

    setIsLoading(true);
    setError('');
    setCode(['', '', '', '', '', '']);

    try {
      const result = await resendVerificationCode(email);
      if (result.success) {
        setSuccess('✓ New verification code sent!');
        setTimeout(() => setSuccess(''), 4000);
        setTimeLeft(600);
        setCanResend(false);
        setResendCooldown(60);
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('Failed to resend');
    } finally {
      setIsLoading(false);
    } 
  };

  return (
    <div className="email-verify-overlay-unique" style={overlayStyle} onClick={onCancel}>
      <div className="email-verify-modal-unique" onClick={e => e.stopPropagation()}>
        <div className="email-verify-head-unique">
          <h3>Verify Email</h3>
          <button className="email-verify-close-unique" onClick={onCancel}>×</button>
        </div>

        <p className="email-verify-text-unique">{email}</p>

        <div className={`email-verify-time-unique ${timeLeft < 60 ? 'warn' : ''}`}>
          ⏱ {formatTime(timeLeft)}
        </div>

        <div className="email-verify-code-grid-unique">
          {code.map((digit, i) => (
            <input
              key={i}
              ref={el => inputRefs.current[i] = el}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={e => handleInputChange(i, e.target.value)}
              onKeyDown={e => handleKeyDown(i, e)}
              onPaste={handlePaste}
              className="email-verify-digit-unique"
              disabled={isLoading || timeLeft === 0}
              autoFocus={i === 0}
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
            />
          ))}
        </div>

        {error && <div className="email-verify-err-unique"><span className="email-err-icon-unique">⚠️</span>{error}</div>}
        {success && <div className="email-verify-ok-unique"><span className="email-ok-icon-unique">✓</span>{success}</div>}

        {!codeSent ? (
          <div className="email-verify-actions-unique">
            <button
              className="email-verify-send-btn-unique"
              onClick={handleSendCode}
              disabled={isLoading}
            >
              {isLoading ? (
                <><span className="email-spinner-unique"></span>Sending...</>
              ) : (
                <>📧 Send Verification Code</>
              )}
            </button>
            <p className="email-verify-info-unique">Click to send a 6-digit code to your email</p>
          </div>
        ) : (
          <>
            <div className="email-verify-btns-unique">
              <button
                className="email-verify-submit-unique"
                onClick={() => handleVerify()}
                disabled={isLoading || code.join('').length !== 6 || timeLeft === 0}
              >
                {isLoading ? <><span className="email-spinner-unique"></span>Verifying...</> : 'Verify Email'}
              </button>
              
              <button
                className="email-verify-resend-unique"
                onClick={handleResend}
                disabled={!canResend || resendCooldown > 0 || isLoading}
              >
                {resendCooldown > 0 ? `Resend (${resendCooldown}s)` : '🔄 Resend Code'}
              </button>
            </div>
            <p className="email-verify-hint-unique"><span className="email-lock-icon-unique">🔒</span>Never share this code with anyone</p>
          </>
        )}
      </div>
    </div>
  );
};

export default EmailVerificationCompact;
