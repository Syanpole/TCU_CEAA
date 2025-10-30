import React, { useState, useEffect, useRef } from 'react';
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
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [timeLeft, setTimeLeft] = useState(600);
  const [canResend, setCanResend] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    handleSendCode();
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
        setSuccess('Code sent to your email!');
        setTimeLeft(600);
        setCanResend(false);
        setResendCooldown(120);
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
        setSuccess('New code sent!');
        setTimeLeft(600);
        setCanResend(false);
        setResendCooldown(120);
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
    <div className="verify-overlay" onClick={onCancel}>
      <div className="verify-modal" onClick={e => e.stopPropagation()}>
        <div className="verify-head">
          <h3>📧 Verify Email</h3>
          <button className="verify-close" onClick={onCancel}>×</button>
        </div>

        <p className="verify-email-text">{email}</p>

        <div className={`verify-time ${timeLeft < 60 ? 'warn' : ''}`}>
          ⏱ {formatTime(timeLeft)}
        </div>

        <div className="verify-code-grid">
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
              className="verify-digit"
              disabled={isLoading || timeLeft === 0}
              autoFocus={i === 0}
            />
          ))}
        </div>

        {error && <div className="verify-err">❌ {error}</div>}
        {success && <div className="verify-ok">✓ {success}</div>}

        <div className="verify-btns">
          <button
            className="verify-submit"
            onClick={() => handleVerify()}
            disabled={isLoading || code.join('').length !== 6 || timeLeft === 0}
          >
            {isLoading ? 'Verifying...' : 'Verify'}
          </button>
          
          <button
            className="verify-resend"
            onClick={handleResend}
            disabled={!canResend || resendCooldown > 0 || isLoading}
          >
            {resendCooldown > 0 ? `Resend (${resendCooldown}s)` : 'Resend'}
          </button>
        </div>

        <p className="verify-hint">🔒 Don't share this code</p>
      </div>
    </div>
  );
};

export default EmailVerificationCompact;
